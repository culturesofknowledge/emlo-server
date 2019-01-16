'''
Created on 4 Nov 2010

@author: dev
'''

# pythons
import codecs
import csv
import datetime
import decimal
import sys
import time
import urllib
import io
import os.path

import solr
import fastcsv

import csvtordf
import relationships
import solrconfig

fieldmap_path = '../../../pylons/web/web/lib'
sys.path.append( fieldmap_path )
import fieldmap

# These two lines are hacks. They switch the default encoding to utf8 so that the command line will convert UTF8 + Ascii to UTF8
reload(sys)
sys.setdefaultencoding("utf8")


lat_min = decimal.Decimal("-90")
lat_max = decimal.Decimal("90")
long_min = decimal.Decimal("-180")
long_max = decimal.Decimal("180")

   
def plural_to_singular( plural ):
    if plural == 'people' :
        return "person"
   
    return plural[:-1]

def add_solr( item, key, value ):
    if key in item :
        try:
            item[key].append( value )
        except AttributeError:
            item[key] = [item[key], value]

        #currentitem = item[key]
        #if isinstance( currentitem, list) :
        #    item[key].append( value )
        #else :
        #    item[key] = [currentitem, value]
    else :
        item[key] = value


def add( solr_item, predicate, object, prefix=None, transient=None, relationship=None ):
    
    if transient :
        solr_key = "%s-%s" % ( transient[csvtordf.predicate], predicate )
    else :
        solr_key = predicate
        
    if prefix :
        solr_key = "%s-%s" % ( solr_key, prefix )
        solr_value = "%s%s" % ( prefix, object )
    else :
        solr_value = object
        
    if relationship :
        solr_key = "%s-%s" % ( solr_key, relationship )
         
    add_solr( solr_item, solr_key, solr_value )
        
    return


def create_uri( base, typey, uid ):  # base ends with "/"
    return "".join([base, typey, "/", uid])


def create_uri_quick( baseAndType, uid ):  # baseAndType ends with "/"
    return baseAndType + uid


def add_to_solr( sol, items ):
    total = len( items )
    start = 0
    batch = 1000
  
    while start < total:
        # print start,
        sol.add_many( items[start:start + batch], False )
        start += batch


def GenerateIds( _, red_ids ):
    #
    # This used to Create ID's for all entities but now it just stores their uuids
    # The uuids are used in the relation matching
    #
    errored = False

    red_ids.flushdb()

    for con in csvtordf.conversions:
 
        id_field = con[csvtordf.title_singular] + "_id"
        for csv_file in csvtordf.csv_files[con[csvtordf.title_plural]]:

            print "  - " + csv_file
            
            csv_file_location = csvtordf.common['csv_source_directory_root'] + csv_file

            if os.path.isfile(csv_file_location) :

                with fastcsv.Reader(io.open(csv_file_location)) as reader :

                    csv_row = reader.next()

                    idPosition = csv_row.index(id_field)
                    uuidPosition = csv_row.index("uuid")
                    published = csv_row.index("published")

                    for csv_row in reader:

                        if csv_row[published] != "1" :
                            continue

                        editid = csv_row[idPosition].strip()
                        red_ids.set( editid, csv_row[uuidPosition] )


        # Rest a while, you've worked hard enough
        time.sleep(0.1)  # point one second
    
    return errored


def ClearSolrData( indexing ):
    #
    # Clear settings
    #
    print " - Removing existing data from staging Solr cores:"
    
    for index in indexing:
        sol = solr.SolrConnection( solrconfig.solr_urls_stage[index] )
        sol.delete_query( "*:*" )
        sol.commit()
        sol.close()
        
        print "   - " + index + " emptied." 

    sol = solr.SolrConnection( solrconfig.solr_urls_stage['all'] )
    if len(indexing) == 8 :
        # We need to delete everything so do it quickly
        sol.delete_query( "*:*" )

    else :
        for index in indexing:
            sol.delete_query( "object_type:" + plural_to_singular( index ) )
        
    sol.commit()
    sol.close()
    
    print '   - "all" cleared of selected objects'

def SolrOptimize( indexing ):
    #
    # Clear settings
    #
    print " - Optimize Solr data"

    for index in indexing:
        sol = solr.SolrConnection( solrconfig.solr_urls_stage[index] )
        sol.optimize()
        sol.close()

        print "   - " + index + " optimized."

    sol = solr.SolrConnection( solrconfig.solr_urls_stage['all'] )

    sol.optimize()
    sol.close()

    print '   - all optimized.'

def StoreRelations( _, red_rel, red_ids ):
    #
    # open the relationship file and store the relations
    # using the UUID's and not the silly id in the file...
    #
    print " - Clearing old relationships."
    red_rel.flushdb( )

    error = False
    error_rel = []
    for csv_file in csvtordf.csv_files['relationships']:

        print "  - " + csv_file,

        csv_file_location = csvtordf.common['csv_source_directory_root'] + csv_file

        with fastcsv.Reader(io.open(csv_file_location)) as reader :

            csv_row = reader.next()

            leftNamePosition = csv_row.index("left_table_name")
            rightNamePosition = csv_row.index("right_table_name")
            leftValPosition = csv_row.index("left_id_value")
            rightValPosition = csv_row.index("right_id_value")
            typePosition = csv_row.index("relationship_type")

            try :
                publishedPosition = csv_row.index("published")
            except:
                publishedPosition = -1

            record_count = 0
            for record in reader:

                if publishedPosition != -1 and record[publishedPosition] != "1":
                    continue

                record_count += 1

                if record_count % 10000 == 0:
                    print str(record_count),
                    time.sleep( 0.1 )  # 0.1 seconds (about 10 seconds in total)

                left_thing = record[leftNamePosition][11:]  # remove "cofk_union_"
                right_thing = record[rightNamePosition][11:]  # remove "cofk_union_"
                relationship_type = record[typePosition][11:]  # remove "cofk_union_"

                try:
                    left_to_right_rel, right_to_left_rel = relationships.getRdfRelationshipsLeftRight( left_thing, relationship_type, right_thing )

                    left, right = red_ids.mget( [record[leftValPosition], record[rightValPosition]] )

                    if left is not None and right is not None:
                        #red_rel.sadd( left, "::".join( [left_to_right_rel, right, right_thing] ) )
                        #red_rel.sadd( right, "::".join( [right_to_left_rel, left, left_thing] ) )
                        red_rel.rpush( left, left_to_right_rel, right, right_thing )
                        red_rel.rpush( right, right_to_left_rel, left, left_thing )
                    else :
                        pass  # Reference to a missing ID. Needs to be removed in EMLO-EDIT

                except :
                    error = True
                    if relationship_type not in error_rel:
                        error_rel.append(relationship_type)
                        print "Error - Problem with relationship: " + left_thing, right_thing, relationship_type + " (Does it need adding to relationships.py?)"
                        print "Number:" + str(record_count - 1) + " Record:" + str(record)

            print ""


    return error


def generateAdditional(singular, record, solr_item):

    if singular == "location" :

        if "latitude" in record and "longitude" in record:

            latitude = record["latitude"]
            longitude = record["longitude"]

            if latitude != "" and longitude != "" :
                latitude_dec = decimal.Decimal(latitude)
                longitude_dec = decimal.Decimal(longitude)

                if lat_min <= latitude_dec <= lat_max and long_min <= longitude_dec <= long_max:
                    add_solr( solr_item, "geo", record["latitude"] + "," + record["longitude"] )
                    # TODO: Add a uncertainty over a position, i.e. a radius ofa cirlce around a point. Large for just countries, small for streets and houses. Solr fieldneeds library adding.
                    #add_solr( solr_item, "geo_rpt", "Circle(" + record["latitude"] + "," + record["longitude"] + " d=0.01)" )

                else:
                    print( "Incorrect Lat/Long: ", latitude_dec, longitude_dec, "for", id )


        if "location_name" in record:
            country = record["location_name"]
        else :
            country = "unknown"


def FillRdfAndSolr( indexing, _, red_temp, __ ):

    # We no longer generate RDF.
    FillSolr( indexing, red_temp )


def FillSolr( indexing, red_temp ):
    """
    Generate a solr entry for each object
    """
    
    uri_base = csvtordf.common['file_entity_uri_base']
    sol_all = solr.SolrConnection( solrconfig.solr_urls_stage['all'] )

    core_id_name = fieldmap.get_core_id_fieldname()
    uri_prefix = fieldmap.get_uri_value_prefix()
    date_added_name = fieldmap.get_date_added_fieldname()

    for con in csvtordf.conversions:
    
        if con[csvtordf.title_plural] in indexing :
    
            singular = con[csvtordf.title_singular]
            plural = con[csvtordf.title_plural]
           
            print "- Converting " + plural

            sol = solr.SolrConnection( solrconfig.solr_urls_stage[plural] )
           
            # Keep track of what is happening with these
            timeStart = time.time()
            record_count = 0
            record_skip = 0
           
            id_field = singular + "_id"
            uri_base_with_type = uri_base + singular + "/"
           
            now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ" )
           
            csvs = csvtordf.csv_files[plural]  # This is more than likely to be a single csv only
           
            for csv_file in csvs:
                #
                # open each csvfile and output to entity store as rdf
                #
                csv_file_location = csvtordf.common['csv_source_directory_root'] + csv_file
                print "  - CSV file:  " + csv_file_location

                csv_records = []
                csv_codec_file = None

                if os.path.isfile(csv_file_location) :
                   csv_codec_file = codecs.open( csv_file_location, encoding="utf-8", mode="rb")
                   csv_records = csv.DictReader( csv_codec_file, restval="" )

                   csv_fields = csv_records.fieldnames

                   published_flag = "published" in csv_fields # Check for column while we switch over formats
               
                translation_errors = []
                solr_list = []

                for record in csv_records :

                    record_count += 1

                    if published_flag and record["published"] != "1":
                        continue

                    uid = record["uuid"]
                    uri = create_uri_quick( uri_base_with_type, uid )

                    solr_item = {
                        "uuid" : uid,
                        "uri" : "//emlo.bodleian.ox.ac.uk/" + uid,
                        "object_type" : singular,
                        date_added_name : now
                    }

                    add( solr_item, core_id_name, uri, uri_prefix )
                   
                    #
                    # Add predicates and objects from csv
                    #
                   
                    # entity.add_namespaces(con[csvtordf.namespaces])
                   
                    translations = con[csvtordf.translations]
                    for field in csv_fields: 
                       
                        if field not in translations :
                            if field not in translation_errors:
                                translation_errors.append(field)
                                print "Warning: '" + field + "' not found in csvtordf.py file. Skipping that particular field."
                        else :
                            translation = translations[field]
                          
                            if translation and ( translation[csvtordf.predicate] or translation[csvtordf.solr] ):
                                data = ''
                                if field in record :
                                    data = record[field].strip()
                                else :
                                    print "Warning: '" + str(field) + "' not found in record. Record:" + str(record) + " . Skipping that particular field."

                                if data != '' :
                                  
                                    # Convert data if a function present
                                    if csvtordf.converter in translation :
                                        converter = translation[csvtordf.converter]
                                        data = converter(data)
                                      
                                    # check to see whether we need to ignore this value
                                    if csvtordf.ignoreIfEqual not in translation or translation[csvtordf.ignoreIfEqual] != data :
                                       
                                        if translation[csvtordf.predicate] :
                                            prefix = translation.get( csvtordf.prefix, None )
                                            transient = translation.get( csvtordf.transient, None )
                                          
                                            add( solr_item, translation[csvtordf.predicate], data, prefix=prefix, transient=transient )
                                      
                                        else:  # translation[csvtordf.solr]:
                                            add_solr( solr_item, translation[csvtordf.solr], data )


                    #
                    # Add additional predicates not in CSV files
                    #
                    additional = con[csvtordf.additional]
                    for predicate, obj in additional.iteritems():
                        add( solr_item, predicate, obj )


                    # create additional fields from existing
                    generateAdditional( singular, record, solr_item )


                    #
                    # Add relationships
                    #

                    #members = red_temp.smembers( uid )  # get relationships
                    members = red_temp.lrange( uid, 0, -1 )  # get all relationships

                    if members :
                        # if entity :
                        #     entity.add_namespaces( relationships.namespaces )

                        uuid_related = []

                        for i in xrange(0,len(members),3) :

                            relation = members[i]
                            uid_related = members[i+1]
                            type_related = members[i+2]

                            uri_relationship = create_uri( uri_base, type_related, uid_related )
                            add( solr_item, relation , uri_relationship, relationship=type_related )

                            uuid_related.append( uid_related )

                        add( solr_item, "uuid_related" , uuid_related )

                        # if entity:
                        #    entity.commit()

                        # print solr_item
                    else :
                       if singular == 'work' :
                           add( solr_item, "uuid_related" , [] )

                    if members or singular == 'work' :
                        solr_list.append(solr_item) # only add it if it is related to something or a work on it's own...
                    else :
                        record_skip += 1

                    if record_count % 5000 == 0:
                        print "  - add to solr to", record_count
                        add_to_solr( sol, solr_list )
                        add_to_solr( sol_all, solr_list )

                        del solr_list[:]

                        # rest a while, give something else a chance!
                        time.sleep(0.1)


                print "  - adding to solr last to", record_count
                add_to_solr( sol, solr_list )
                add_to_solr( sol_all, solr_list )

                del solr_list[:]

                if csv_codec_file is not None:
                    csv_codec_file.close()


            print "  - committing", record_count-record_skip, "from", record_count
            sol.commit()
            sol_all.commit()

            sol.close()

            timeEnd = time.time()
            print "- Done. Added " + str(record_count) + " records in %0.1f seconds." % ( timeEnd - timeStart)
    
    
    print '- Committing to solr "all" repository'  

    sol_all.close()
    

def SwitchSolrCores( indexing ) :

    print '- Switching from staging cores'

    for core_name, solr_url_stage in solrconfig.solr_urls_stage.iteritems():

        if core_name in indexing or ( core_name == 'all' and len(indexing) == 8 ) :

            # http://localhost:8983/solr/admin/cores?action=swap&core=people&other=people_stage
            swapurl = solrconfig.solr_base_url + 'admin/cores?action=swap'

            swapurl += '&core=' + solr_url_stage.replace( solrconfig.solr_base_url, '' )
            swapurl += '&other=' + solrconfig.solr_urls[core_name].replace( solrconfig.solr_base_url, '' )

            print "Switching ", core_name, ":", swapurl

            urllib.urlopen( swapurl )


    

    
    
    
    
