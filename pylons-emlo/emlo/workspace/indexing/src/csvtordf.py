# -*- coding: utf-8 -*-
'''
Created on 25 Aug 2010

@author: Matthew Wilcoxson

This file converts the CSV data into valid RDF and importds it into SOlr.
Also see "relationships.py"
'''

# The 'fieldmap' module passes back the fieldname as a string.
# By using functions from 'fieldmap', we can restrict fieldnames to being hard-coded in only 
# ONE place, allowing much easier changes if a better ontology is found. (SB, 13 July 2011)

import sys
fieldmap_path = '../../../pylons/web/web/lib' 
sys.path.append( fieldmap_path )
import fieldmap
import reversemap

import sourceconfig_base

# common settings for all objects
common = { 
    'file_entity_storage_root' : '/home/dev/entitystore/' ,     # must have ending '/'
    'file_entity_uri_base' : 'http://localhost/',           # must have ending '/'
    'csv_source_directory_root' : sourceconfig_base.base,          # must have ending '/'
    'file_entity_prefix' : '_',
}

# The list of lists of csv files. (You can comment out lines to only debug specific ones)
csv_files = {
             'relationships'    : [ 'relationship.csv' ],
             'locations'        : [ 'location.csv' ],
             'comments'         : [ 'comment.csv' ],
             'images'           : [ 'image.csv' ],
             'people'           : [ 'person.csv' ],
             'works'            : [ 'work.csv' ],
             'manifestations'   : [ 'manifestation.csv' ],
             'institutions'     : [ 'institution.csv' ],
             'resources'        : [ 'resource.csv' ]
}

# The list of lists of csv files. (You can comment out lines to only debug specific ones)
test_csv_files = {
             'relationships'    : [ 'lister/cofk_lister_relationship.csv' ],
             'locations'        : [ 'lister/cofk_lister_location.csv' ],
             'comments'         : [ 'lister/cofk_lister_comment.csv' ],
             'images'           : [ 'lister/cofk_lister_image.csv' ],
             'people'           : [ 'lister/cofk_lister_person.csv' ],
             'works'            : [ 'lister/cofk_lister_work.csv' ],
             'manifestations'   : [ 'lister/cofk_lister_manifestation.csv' ],
             'institutions'     : [ 'lister/cofk_lister_institution.csv' ],
             'resources'        : [ 'lister/cofk_lister_resource.csv' ]
}

# Commonly-used namespaces
dcterms_short  =  'dcterms' 
dcterms_long   =  'http://dublincore.org/documents/dcmi-terms/'

geo_short      =  'geo'     
geo_long       =  'http://www.w3.org/2003/01/geo/'

ox_short       =  'ox'      
ox_long        = 'http://vocab.ox.ac.uk/'

geonames_short = 'geonames'
geonames_long  = 'http://www.geonames.org/ontology/'

bibo_short     = 'bibo'
bibo_long      = 'http://purl.org/ontology/bibo/'

foaf_short     = 'foaf'
foaf_long      = 'http://xmlns.com/foaf/0.1/'

bio_short      = 'bio'
bio_long       = 'http://vocab.org/bio/0.1/'

skos_short     = 'skos'
skos_long      = 'http://www.w3.org/TR/2009/REC-skos-reference-20090818/'

frbr_short     = 'frbr'
frbr_long      = 'http://purl.org/vocab/frbr/core#'

mail_short     = 'mail' 
mail_long      = 'http://vocab.ox.ac.uk/mail/'

indef_short    = 'indef'
indef_long     = 'http://vocab.ox.ac.uk/indef/'

cito_short     = 'cito'
cito_long      = 'http://vocab.ouls.ox.ac.uk/cito/'

rel_short      = 'rel'
rel_long       = 'http://purl.org/vocab/relationship/'


#
# The following conversions array holds the information to convert CSV files to RDF.
# It has the following settings:
title_singular='title_singular' # title_singular - for addition to base uri
title_plural='title_plural'     # title plural - for name of entity store
namespaces='namespaces'         # namespaces - a list of namespaces needed for the following translations
translations='translations'     # translations - the list of rdf values for each csv column name
                                # with following settings:
predicate='predicate'           #     predicate - what rdf to replace CSV column  name (e.g. predicate:"dcterms:identifier" )
prefix='prefix'                 #     prefix - what to add to the front of the data (e.g. prefix:"uuri:" )
store='store'                   #     store - mark if useful to store in redis, used to store ID field at moment ( store:"id" )
converter = 'converter'         #     converter - this is a function that will be called to change the data into a valid format. (e.g. converter: convert_to_rdf_date)

transient='transient'           #     transient - this predicate is to be stored in a sub resource
                                #     with following settings: 
                                #         transient - id to append to main URI (e.g. transient:"_authors")
                                #         predicate - predicate to use for new URI (e.g. predicate "mail:authors"
ignoreIfEqual='ignoreIfEqual'   #     ignoreIfEqual - ignore this piece of data if set to this value (post converter)
additional='additional'         # additional - a list of additional values to add which are not in the csv file
solr='solr'                     #     solr - an alternative name to use in solr (currently only for fields not translated to RDF)

type_fieldname = fieldmap.get_type_fieldname()

from conversionhelper import *  # For converter functions (e.g. convert to date)

conversions = [
  ############
  #
  # locations
  #
  {
    title_singular : "location",
    title_plural   : "locations",

    namespaces : {
      dcterms_short  : dcterms_long,
      geo_short      : geo_long,
      ox_short       : ox_long,
      geonames_short : geonames_long,
    },

    translations : {

      'location_id':  
      {
        predicate: fieldmap.get_core_id_fieldname(),
        prefix:    fieldmap.get_normal_id_value_prefix(),
        store: "id"
      },

      'latitude' : 
      {
        predicate: fieldmap.get_latitude_fieldname()
      },

      'longitude' : 
      {
        predicate: fieldmap.get_longitude_fieldname(),
      },

      'location_name':
      {
        predicate: fieldmap.get_location_name_fieldname()
      },

      'location_synonyms':
      {
        predicate: fieldmap.get_location_synonyms_fieldname()
      },

      'creation_timestamp':
      {
        predicate: fieldmap.get_date_created_fieldname(),
        converter: convert_to_rdf_date,
      },

      'change_timestamp': 
      {
        predicate: fieldmap.get_date_changed_fieldname(),
        converter: convert_to_rdf_date,
      },

      'creation_user':None, # ignore
      'change_user':
      {
        predicate: fieldmap.get_changed_by_user_fieldname(),
      },

      'sent_count':
      {
        predicate: fieldmap.get_total_works_sent_from_place_fieldname(),
      },

      'recd_count':
      {
        predicate: fieldmap.get_total_works_sent_to_place_fieldname(),
      },

      'mentioned_count':
      {
        predicate: fieldmap.get_total_works_mentioning_place_fieldname(),
      },
      'uuid':
        {
          predicate: fieldmap.get_core_id_fieldname(),
          prefix:    fieldmap.get_uuid_value_prefix()
          #store: "uuid"
        }
    },

    additional : {
      type_fieldname :'http://purl.org/dc/terms/Location'
    }
  },

  #########
  #
  # comments
  #
  {
    title_singular : "comment",
    title_plural   : "comments",

    namespaces : { 
      dcterms_short: dcterms_long,
      ox_short     : ox_long,
      bibo_short   : bibo_long
    },

    translations : {

      'comment_id':  
      {
        predicate: fieldmap.get_core_id_fieldname(),
        prefix:    fieldmap.get_normal_id_value_prefix(),
        store:     "id"
      },

      'comment' :
      {  
        predicate: fieldmap.get_comments_fieldname()
      },

      'creation_timestamp':
      {
        predicate: fieldmap.get_date_created_fieldname(),
        converter: convert_to_rdf_date,
      },

      'change_timestamp': 
      {
        predicate: fieldmap.get_date_changed_fieldname(),
        converter: convert_to_rdf_date,
      },

      'creation_user':None,# ignore
      'change_user':
      {
        predicate: fieldmap.get_changed_by_user_fieldname(),
      },
      'uuid':
        {
          predicate: fieldmap.get_core_id_fieldname(),
          prefix:    fieldmap.get_uuid_value_prefix()
          #store: "uuid"
        }
    },
      
    additional : {
      type_fieldname :'http://purl.org/ontology/bibo/Note'
    }
  },

  ##########
  #
  # images
  #
  {
    title_singular : "image",
    title_plural : "images",
    
    namespaces : { 
      dcterms_short: dcterms_long,
      ox_short     : ox_long,
      foaf_short   : foaf_long,
    },

    translations : {

      'image_id': 
          {
              predicate: fieldmap.get_core_id_fieldname(),
              prefix:    fieldmap.get_normal_id_value_prefix(),
              store: "id"
          },

      'image_filename':
          {
              predicate: fieldmap.get_image_source_fieldname(),
          },

      'thumbnail':
          {
              predicate: fieldmap.get_thumbnail_fieldname(),
          },

      'display_order':
          {
              predicate: fieldmap.get_image_display_order_fieldname(),
          },

      'credits':
          {
              predicate: fieldmap.get_image_credits_fieldname(),
          },

      'creation_timestamp':
          {
              predicate: fieldmap.get_date_created_fieldname(),
              converter: convert_to_rdf_date,
          },

      'change_timestamp': 
          {
              predicate: fieldmap.get_date_changed_fieldname(),
              converter: convert_to_rdf_date,
          },

      'creation_user':None, # ignore
      'change_user':
      {
        predicate: fieldmap.get_changed_by_user_fieldname(),
      },
      'uuid':
        {
          predicate: fieldmap.get_core_id_fieldname(),
          prefix:    fieldmap.get_uuid_value_prefix()
          #store: "uuid"
        }
    },
    
    additional : {
      type_fieldname :'http://purl.org/dc/dcmitype/Image'
    }
  },
  #########
  #
  # works
  #
  {
    title_singular : "work",
    title_plural   : "works",

    namespaces : {
      dcterms_short: dcterms_long,
      ox_short     : ox_long,
      foaf_short   : foaf_long,
      bio_short    : bio_long,
      skos_short   : skos_long,
      frbr_short   : frbr_long,
      mail_short   : mail_long,
      indef_short  : indef_long,
      cito_short   : cito_long,
    },

    translations : {

      'work_id':
      {
        predicate: fieldmap.get_core_id_fieldname(),
        prefix:    fieldmap.get_normal_id_value_prefix(),
        store:     "id"
      },

      'iwork_id':
      {
        predicate: fieldmap.get_core_id_fieldname(),
        prefix   : fieldmap.get_integer_id_value_prefix(),
      },

      'original_catalogue':
      {
        predicate: fieldmap.get_catalogue_fieldname(),
      },

      'abstract':
      {
        predicate: fieldmap.get_abstract_fieldname(),
      },

      'description':
      {
        predicate: fieldmap.get_work_description_fieldname(),
      },

      'authors_as_marked':
      {
        predicate: fieldmap.get_as_marked_fieldname_end(),
        transient: {
          transient: "_authors",
          predicate: fieldmap.get_authors_fieldname_start() 
        },
      },

      'authors_uncertain':
      {
        predicate: fieldmap.get_uncertainty_flag_uncertain(),
        transient: {
          transient:"_authors",
          predicate: fieldmap.get_authors_fieldname_start() 
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      },

      'authors_inferred':
      {
        predicate: fieldmap.get_uncertainty_flag_inferred(),
        transient: {
          transient: "_authors",
          predicate: fieldmap.get_authors_fieldname_start()
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      },

      'destination_as_marked':
      {
        predicate: fieldmap.get_as_marked_fieldname_end(),
        transient: {
          transient: "_destination",
          predicate: fieldmap.get_destination_fieldname_start() 
        },
      },

      'destination_uncertain':
      {
        predicate: fieldmap.get_uncertainty_flag_uncertain(),
        transient: {
          transient: "_destination",
          predicate: fieldmap.get_destination_fieldname_start()
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      },

      'destination_inferred':
      {
        predicate: fieldmap.get_uncertainty_flag_inferred(),
        transient: {
          transient: "_destination",
          predicate: fieldmap.get_destination_fieldname_start()
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      },

      'origin_as_marked':
      {
        predicate: fieldmap.get_as_marked_fieldname_end(),
        transient: {
          transient: "_origin",
          predicate: fieldmap.get_origin_fieldname_start()
        },
      },

      'origin_inferred':
      {
        predicate: fieldmap.get_uncertainty_flag_inferred(),
        transient: {
          transient: "_origin",
          predicate: fieldmap.get_origin_fieldname_start() 
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      },

      'origin_uncertain':
      {
        predicate: fieldmap.get_uncertainty_flag_uncertain(),
        transient: {
          transient: "_origin",
          predicate: fieldmap.get_origin_fieldname_start() 
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      },

      'original_calendar':
      {
        predicate: fieldmap.get_original_calendar_fieldname(),
      },

      'addressees_as_marked':
      {
        predicate: fieldmap.get_as_marked_fieldname_end(),
        transient: {
          transient: "_addressees",
          predicate: fieldmap.get_addressees_fieldname_start()
        },
      },

      'addressees_uncertain':
      {
        predicate: fieldmap.get_uncertainty_flag_uncertain(),
        transient: {
          transient: "_addressees",
          predicate:  fieldmap.get_addressees_fieldname_start()
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      },

      'addressees_inferred':
      {
        predicate: fieldmap.get_uncertainty_flag_inferred(),
        transient: {
          transient: "_addressees",
          predicate:  fieldmap.get_addressees_fieldname_start()
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      },

      'date_of_work_std_year':
      {
        predicate: fieldmap.get_year_fieldname(),
        transient: {
          transient: "_started",
          predicate: fieldmap.get_period_start_fieldname() 
        },
      },

      'date_of_work_std_month':
      {
        predicate:  fieldmap.get_month_fieldname(),
        transient: {
          transient:"_started",
          predicate: fieldmap.get_period_start_fieldname() 
        },
      },

      'date_of_work_std_day':
      {
        predicate: fieldmap.get_day_fieldname(),
        transient: {
          transient:"_started",
          predicate: fieldmap.get_period_start_fieldname() 
        },
      },


      'date_of_work_uncertain':
      {
        predicate: fieldmap.get_uncertainty_flag_uncertain(),
        transient: {
          transient:"_started",
          predicate: fieldmap.get_period_start_fieldname() 
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      },

      'date_of_work_inferred':
      {
        predicate: fieldmap.get_uncertainty_flag_inferred(),
        transient: {
          transient: "_started",
          predicate: fieldmap.get_period_start_fieldname() 
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      },

      'date_of_work_approx':
      {
        predicate: fieldmap.get_uncertainty_flag_approx(),
        transient: {
          transient: "_started",
          predicate: fieldmap.get_period_start_fieldname() 
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      },

      'date_of_work2_std_year':
      {
        predicate: fieldmap.get_year_fieldname(),
        transient: {
          transient: "_completed",
          predicate: fieldmap.get_period_end_fieldname() 
        },
      },

      'date_of_work2_std_month':
      {
        predicate: fieldmap.get_month_fieldname(),
        transient: {
          transient: "_completed",
          predicate: fieldmap.get_period_end_fieldname() 
        },
      },

      'date_of_work2_std_day':
      {
        predicate: fieldmap.get_day_fieldname(),
        transient: {
          transient: "_completed",
          predicate: fieldmap.get_period_end_fieldname() 
        },
      },

      'date_of_work_std_is_range':
      {
        predicate: fieldmap.get_date_range_fieldname(),
        converter: convert_to_rdf_boolean,
      },

      'date_of_work_as_marked':
      {
        predicate: fieldmap.get_date_as_marked_fieldname(),
      },

      'language_of_work':
      {
        predicate: fieldmap.get_language_fieldname(),
      },

      'work_is_translation':
      {
        predicate: fieldmap.get_is_translation_fieldname(),
        converter: convert_to_rdf_boolean,
      },

      'ps':
      {
        predicate: fieldmap.get_postscript_fieldname(),
      },

      'explicit':
      {
        predicate: fieldmap.get_excipit_fieldname(), # Should this be called "explicit"?? (No, I don't
      },                                             # think so. Some researchers seem to like 
                                                     # 'excipit', some like 'explicit', can't please
                                                     # them all. But they've now gone for 'excipit'.)
      'incipit':
      {
        predicate: fieldmap.get_incipit_fieldname(),
      },

      'keywords':
      {
        predicate: fieldmap.get_keywords_fieldname(),
      },

      'editors_notes': None, #ignore, as on CofK this field is for private notes
      'edit_status': None,   #ignore, as on CofK this field is not currently used

      'creation_timestamp':
      {
        predicate: fieldmap.get_date_created_fieldname(),
        converter: convert_to_rdf_date,
      },

      'change_timestamp': 
      {
        predicate: fieldmap.get_date_changed_fieldname(),
        converter: convert_to_rdf_date,
      },

      'date_of_work_std':
      {
        predicate: None, 
        solr: 'started_date_sort',
        converter: convert_to_solr_date,
      },

      'date_of_work_std_gregorian':
      {
        predicate: None,
        solr: 'started_date_gregorian_sort',
        converter: convert_to_solr_date,
      },

      'accession_code':
      {
        predicate: fieldmap.get_source_of_data_fieldname(),
      },

      'work_to_be_deleted':None, # ignore
      'relevant_to_cofk':None, # ignore
      'creation_user':None, # ignore
      'change_user':
      {
        predicate: fieldmap.get_changed_by_user_fieldname(),
      },
      'uuid':
        {
          predicate: fieldmap.get_core_id_fieldname(),
          prefix:    fieldmap.get_uuid_value_prefix()
          #store: "uuid"
        }
    },

    additional : {
      type_fieldname :'http://purl.org/net/biblio#Letter'
    }
  },


  ########
  #
  # People
  #
  {
    title_singular : "person",
    title_plural   : "people",
    
    namespaces : {
      dcterms_short: dcterms_long,
      ox_short     : ox_long,
      foaf_short   : foaf_long,
      bio_short    : bio_long,
      rel_short    : rel_long,
      skos_short   : skos_long,
      indef_short  : indef_long,
    },

    translations : {

      'person_id':
      {
        predicate: fieldmap.get_core_id_fieldname(),
        prefix:    fieldmap.get_normal_id_value_prefix(),
        store: "id"
      },

      'iperson_id':
      {
        predicate: fieldmap.get_core_id_fieldname(),
        prefix:    fieldmap.get_integer_id_value_prefix(),
      },

      'is_organisation':
      {
        predicate: fieldmap.get_is_organisation_fieldname(),
        converter: convert_to_rdf_boolean,
      }, 

      'date_of_birth_day':
      {
        predicate: fieldmap.get_day_fieldname(),
        transient: {
          transient:"_date_of_birth",
          predicate: fieldmap.get_birth_fieldname() 
        },
      }, 

      'date_of_birth_month':
      {
        predicate: fieldmap.get_month_fieldname(),
        transient: {
          transient:"_date_of_birth",
          predicate: fieldmap.get_birth_fieldname() 
        },
      }, 

      'date_of_birth_year':
      {
        predicate: fieldmap.get_year_fieldname(),
        transient: {
          transient:"_date_of_birth",
          predicate: fieldmap.get_birth_fieldname() 
        },
      }, 

      'date_of_birth_inferred':
      {
        predicate: fieldmap.get_uncertainty_flag_inferred(),
        transient: {
          transient:"_date_of_birth",
          predicate: fieldmap.get_birth_fieldname() 
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      }, 

      'date_of_birth_uncertain':
      {
        predicate: fieldmap.get_uncertainty_flag_uncertain(),
        transient: {
          transient:"_date_of_birth",
          predicate: fieldmap.get_birth_fieldname() 
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      }, 

      'date_of_birth_approx':
      {
        predicate: fieldmap.get_uncertainty_flag_approx(),
        transient: {
          transient:"_date_of_birth",
          predicate: fieldmap.get_birth_fieldname() 
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      }, 

      'person_aliases':
      {
        predicate: fieldmap.get_person_titles_or_roles_fieldname(),
      }, 

      'skos_altlabel':
      {
        predicate: fieldmap.get_alias_fieldname(),
      }, 

      'foaf_name':
      {
        predicate: fieldmap.get_person_name_fieldname(), 
                               # could do with adding firstName, givenName, surname...
      },                       # yeah well, we're not going to, data model is frozen for now.

      'date_of_death_day':
      {
        predicate: fieldmap.get_day_fieldname(),
        transient: {
          transient:"_date_of_death",
          predicate: fieldmap.get_death_fieldname() 
        },
      }, 

      'date_of_death_month':
      {
        predicate: fieldmap.get_month_fieldname(),
        transient: {
          transient:"_date_of_death",
          predicate: fieldmap.get_death_fieldname()
        },
      }, 

      'date_of_death_year':
      {
        predicate: fieldmap.get_year_fieldname(),
        transient: {
          transient:"_date_of_death",
          predicate: fieldmap.get_death_fieldname()
        },
      }, 

      'date_of_death_inferred':
      {
        predicate: fieldmap.get_uncertainty_flag_inferred(),
        transient: {
          transient:"_date_of_death",
          predicate: fieldmap.get_death_fieldname()
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      }, 

      'date_of_death_uncertain':
      {
        predicate: fieldmap.get_uncertainty_flag_uncertain(),
        transient: {
          transient:"_date_of_death",
          predicate: fieldmap.get_death_fieldname()
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      }, 

      'date_of_death_approx':
      {
        predicate: fieldmap.get_uncertainty_flag_approx(),
        transient: {
          transient:"_date_of_death",
          predicate: fieldmap.get_death_fieldname()
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      }, 

      'gender':
      {
        predicate: fieldmap.get_gender_fieldname(),
        converter:convert_people_gender,
      },                

      'creation_timestamp':
      {
        predicate: fieldmap.get_date_created_fieldname(),
        converter: convert_to_rdf_date,
      },

      'change_timestamp': 
      {
        predicate: fieldmap.get_date_changed_fieldname(),
        converter: convert_to_rdf_date,
      },

      'date_of_death':
      {
        predicate: None,
        solr: 'date_of_death_sort',
        converter: convert_to_solr_date,
      },

      'date_of_birth':
      {
        predicate: None,
        solr: 'date_of_birth_sort',
        converter: convert_to_solr_date,
      },

      'skos_hiddenlabel':None,
      'creation_user':None,
      'change_user':
      {
        predicate: fieldmap.get_changed_by_user_fieldname(),
      },

      'sent_count':
      {
        predicate: fieldmap.get_total_works_written_by_agent_fieldname(),
      },

      'recd_count':
      {
        predicate: fieldmap.get_total_works_recd_by_agent_fieldname(),
      },

      'mentioned_count':
      {
        predicate: fieldmap.get_total_works_mentioning_agent_fieldname(),
      },

      'further_reading':
      {
        predicate: fieldmap.get_person_further_reading_fieldname(),
      },
      'uuid':
        {
          predicate: fieldmap.get_core_id_fieldname(),
          prefix:    fieldmap.get_uuid_value_prefix()
          #store: "uuid"
        }
    },
    
    additional : {#
      type_fieldname :'http://xmlns.com/foaf/0.1/Agent' # Agents can be either people or organisations
    }
  },

  ###############
  #
  # manifestations
  #

  {
    title_singular : "manifestation",
    title_plural : "manifestations",

    namespaces : {
      dcterms_short: dcterms_long,
      ox_short     : ox_long,
      indef_short  : indef_long ,
      mail_short   : mail_long,
      foaf_short   : foaf_long,
      bio_short    : bio_long,
      skos_short   : skos_long,
      frbr_short   : frbr_long,
      bibo_short   : bibo_long,
    },

    translations : {

      'manifestation_id': 
      {
        predicate: fieldmap.get_core_id_fieldname(),
        prefix:    fieldmap.get_normal_id_value_prefix(),
        store: "id"
      },

      'manifestation_type': 
      {
        predicate: fieldmap.get_manifestation_type_fieldname(),
        converter: convert_manifestation_type,
      },

      'number_of_pages_of_document': 
      {
        predicate: fieldmap.get_number_of_pages_of_document_fieldname(),
      },

      'id_number_or_shelfmark': 
      {
        predicate: fieldmap.get_core_id_fieldname(),
        prefix: fieldmap.get_shelfmark_value_prefix(),
      },

      'manifestation_creation_calendar': 
      {
        predicate: fieldmap.get_original_calendar_fieldname(),
      },

      'manifestation_creation_date_year': 
      {
        predicate: fieldmap.get_year_fieldname(),
        transient: {
          transient:"_created",
          predicate: fieldmap.get_creation_date_fieldname() },
      },

      'manifestation_creation_date_month': 
      {
        predicate: fieldmap.get_month_fieldname(),
        transient: {
          transient:"_created",
          predicate: fieldmap.get_creation_date_fieldname() },
      },

      'manifestation_creation_date_day': 
      {
        predicate: fieldmap.get_day_fieldname(),
        transient: {
          transient:"_created",
          predicate: fieldmap.get_creation_date_fieldname() },
      },

      'manifestation_creation_date_inferred':
      {
        predicate: fieldmap.get_uncertainty_flag_inferred(),
        transient: {
          transient:"_created",
          predicate: fieldmap.get_creation_date_fieldname() 
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      },

      'manifestation_creation_date_uncertain': 
      {
        predicate: fieldmap.get_uncertainty_flag_uncertain(),
        transient: {
          transient:"_created",
          predicate: fieldmap.get_creation_date_fieldname() 
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      },

      'manifestation_creation_date_approx': 
      {
        predicate: fieldmap.get_uncertainty_flag_approx(),
        transient: {
          transient:"_created",
          predicate: fieldmap.get_creation_date_fieldname() 
        },
        converter: convert_to_rdf_boolean,
        ignoreIfEqual: 'false',
      },

      'language_of_manifestation': 
      {
        predicate: fieldmap.get_language_fieldname(), 
      },

      'manifestation_ps': 
      {
        predicate: fieldmap.get_postscript_fieldname(),
      },

      'manifestation_incipit': 
      {
        predicate: fieldmap.get_incipit_fieldname(),
      },

      'manifestation_excipit': 
      {
        predicate: fieldmap.get_excipit_fieldname(),
      },

      'seal': 
      {
        predicate: fieldmap.get_seal_fieldname(),
      },

      'paper_type_or_watermark': 
      {
        predicate: fieldmap.get_paper_type_fieldname(),
      },

      'paper_size': 
      {
        predicate: fieldmap.get_paper_size_fieldname(),
      },

      'postage_marks': 
      {
        predicate: fieldmap.get_postage_mark_fieldname(),
      },

      'printed_edition_details': 
      {
        predicate: fieldmap.get_printed_edition_details_fieldname(),
      },

      'endorsements': 
      {
        predicate: fieldmap.get_endorsements_fieldname(),
      },

      'address': 
      {
        predicate: fieldmap.get_manifestation_address_fieldname(),
      },

      'number_of_pages_of_text': 
      {
        predicate: fieldmap.get_number_of_pages_of_text_fieldname(),
      },

      'non_letter_enclosures': 
      {
        predicate: fieldmap.get_non_letter_enclosures_fieldname(),
      },

      'manifestation_is_translation': 
      {
        predicate: fieldmap.get_is_translation_fieldname(),
        converter: convert_to_rdf_boolean,
      },

      'creation_timestamp':
      {
        predicate: fieldmap.get_date_created_fieldname(),
        converter: convert_to_rdf_date,
      },

      'change_timestamp': 
      {
        predicate: fieldmap.get_date_changed_fieldname(),
        converter: convert_to_rdf_date,
      },

      'manifestation_creation_date':
      {
        predicate: None,
        solr: 'creation_date_sort',
        converter: convert_to_solr_date,
      },

      'manifestation_creation_date_gregorian': 
      {
        predicate: None,
        solr:"creation_date_gregorian_sort",
        converter: convert_to_solr_date,
      },

      'creation_user':None, # ignore
      'change_user':
      {
        predicate: fieldmap.get_changed_by_user_fieldname(),
      },
      'uuid':
        {
          predicate: fieldmap.get_core_id_fieldname(),
          prefix:    fieldmap.get_uuid_value_prefix()
          #store: "uuid"
        }
    },

    additional : {
      type_fieldname :'http://purl.org/vocab/frbr/core#Manifestation'
    }
  },


  ########
  #
  # Institutions
  #
  {
    title_singular : "institution",
    title_plural : "institutions",

    namespaces : {
      dcterms_short : dcterms_long,
      ox_short      : ox_long,
      geonames_short: geonames_long,
    },

    translations : {

      'institution_id':
      {
        predicate: fieldmap.get_core_id_fieldname(),
        prefix:    fieldmap.get_normal_id_value_prefix(),
        store:     "id"
      },

      'institution_city':
      {
        predicate: fieldmap.get_repository_city_fieldname(),
      },

      'institution_city_synonyms':
      {
        predicate: fieldmap.get_repository_alternate_city_fieldname(),
      },

      'institution_country':
      {
        predicate: fieldmap.get_repository_country_fieldname(),
      },

      'institution_country_synonyms':
      {
        predicate: fieldmap.get_repository_alternate_country_fieldname(),
      },

      'institution_name':
      {
        predicate: fieldmap.get_repository_name_fieldname(),
      },

      'institution_synonyms':
      {
        predicate: fieldmap.get_repository_alternate_name_fieldname(),
      },

      'creation_timestamp':
      {
        predicate: fieldmap.get_date_created_fieldname(),
        converter: convert_to_rdf_date,
      },

      'change_timestamp': 
      {
        predicate: fieldmap.get_date_changed_fieldname(),
        converter: convert_to_rdf_date,
      },

      'creation_user':None, # ignore
      'change_user':
      {
        predicate: fieldmap.get_changed_by_user_fieldname(),
      },

      'document_count':
      {
        predicate: fieldmap.get_total_docs_in_repos_fieldname(),
      },
      'uuid':
        {
          predicate: fieldmap.get_core_id_fieldname(),
          prefix:    fieldmap.get_uuid_value_prefix()
          #store: "uuid"
        }
    },

    additional : {
      type_fieldname :'http://purl.org/vocab/aiiso/schema#Institution'
    }
  },

  ########
  #
  # resources
  #
  {
    title_singular : "resource",
    title_plural : "resources",

    namespaces : {
      dcterms_short: dcterms_long,
      ox_short     : ox_long,
    },

    translations : {

      'resource_id': 
      {
        predicate: fieldmap.get_core_id_fieldname(),
        prefix:    fieldmap.get_normal_id_value_prefix(),
        store:     "id"
      },

      'resource_details': 
      {
        predicate: fieldmap.get_resource_details_fieldname(),
      },

      'resource_name': 
      {
        predicate: fieldmap.get_resource_title_fieldname(),
      },

      'resource_url': 
      {
        predicate: fieldmap.get_resource_url_fieldname(),
        converter: convert_to_local_url,
      },


      'creation_timestamp':
      {
        predicate: fieldmap.get_date_created_fieldname(),
        converter: convert_to_rdf_date,
      },

      'change_timestamp': 
      {
        predicate: fieldmap.get_date_changed_fieldname(),
        converter: convert_to_rdf_date,
      },

      'creation_user':None, # ignore
      'change_user':
      {
        predicate: fieldmap.get_changed_by_user_fieldname(),
      },
      'uuid':
        {
          predicate: fieldmap.get_core_id_fieldname(),
          prefix:    fieldmap.get_uuid_value_prefix()
          #store: "uuid"
        }
    },

    additional : {
      type_fieldname :'http://www.w3.org/2000/01/rdf-schema#Resource'
    }
  },
]

#----------------------------------------------------------------------------------------------

if __name__ == '__main__':
  print 'Listing conversion values:'
  print ''
  first_col_width = 15
  indent = ' '
  bigger_indent = indent.ljust( first_col_width + len(indent) + 1 )
  fieldsep = '----------------------'

  for conv in conversions:
    title = ''
    if conv.has_key( 'title_singular' ):
      title = conv['title_singular'].capitalize()
      print ''
      print '************************' + title + '************************'
    #endif
    for key, val in conv.items():
      if key == 'translations':
        #--------------------------------
        # Main bit of mapping SQL -> Solr
        #--------------------------------
        print ''
        for sql_column_name, translated in val.items():
          if type( translated ) == dict:
            print title + ': SQL column name "' + sql_column_name + '" {' 
            for first_half, second_half in translated.items():
              if str( first_half ) == 'predicate':
                print ''
              #endif
              print indent + first_half.ljust( first_col_width ) + ' ' + unicode( second_half )
              if type( second_half ) == str:
                funclist = reversemap.get_functions_returning_value( second_half )
                if len( funclist ) > 0:
                  print bigger_indent + 'Returned from fieldmap by: ' + unicode( funclist )
                  print ''
                #endif

              #----------------------------
              # 'Transient' part of mapping
              #----------------------------
              elif type( second_half ) == dict:
                if second_half.has_key( 'predicate' ):
                  funclist = reversemap.get_functions_returning_value( second_half['predicate'] )
                  if len( funclist ) > 0:
                    print bigger_indent + 'Predicate returned from fieldmap by: ' + unicode(funclist)
                    print ''
                  #endif
                #endif
              #endif
            #endfor
            print '}' 
            print fieldsep

          #----------------------------------
          # No mapping from SQL field to Solr
          #----------------------------------
          else:
            print title + ': SQL column name "' + sql_column_name + '": ' + unicode( translated )
            print ''
            print fieldsep
          #endif
          print ''
        #endfor
      else:
        break # we're really just interested in documenting translations here
      #endif
    #endfor
  #endfor
#endif

#----------------------------------------------------------------------------------------------
