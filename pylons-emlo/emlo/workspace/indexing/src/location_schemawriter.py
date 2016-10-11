# -*- coding: utf-8 -*-
'''
Created on 22nd July 2011

@author: Sushila Burgess

This script writes out a schema.xml file for the 'locations' Solr core.
'''

# The 'fieldmap' module passes back the fieldname as a string.
# By using functions from 'fieldmap', we can restrict fieldnames to being hard-coded in only 
# ONE place, allowing much easier changes if a better ontology is found. (SB, 13 July 2011)

import sys
fieldmap_path = '/home/dev/subversion/trunk/pylons/web/web/lib' 
sys.path.append( fieldmap_path )
from fieldmap import *

from schemautils import write_field, write_copyfield, write_start_marker, write_end_marker, \
                        write_section_heading

#--------------------------------------------------------------------------------------------------

def write_required_fields(): #{ -- curly brace is a cheat to help with jumping to matching brace

  print ''
  write_section_heading( 'required' )
  print ''

  write_field( name="id", type="string", indexed="true", stored="true", required="true" ) 

  write_field( name="sid", type="tint", indexed="true", stored="true", required="true", \
               comment = 'short id' )

  print ''

  write_field( name=get_uuid_fieldname(), 
               type="string", indexed="true", stored="true", required="true" ) 

  write_field( name=get_uri_fieldname(), 
               type="string", indexed="true", stored="true", required="true" ) 

  write_field( name=get_id_fieldname(), 
               type="string", indexed="true", stored="true", required="true", 
               comment = 'location_id' )
  
# End of write_required_fields
#}  -- curly brace is a cheat to help with jumping to matching brace
#--------------------------------------------------------------------------------------------------

def write_optional_fields( called_from = 'locations' ): #{

  if called_from == 'all':
    heading_text = 'locations'
  else:
    heading_text = 'optional'
  #endif

  write_section_heading( heading_text )
  
  if called_from != 'all':
    write_field( name="rdf:type", type="string", indexed="false", stored="true" ) 
  
  write_field( name=get_location_name_fieldname(), 
               type="text", indexed="true", stored="true" ) 

  write_field( name=get_location_synonyms_fieldname(), 
               type="text", indexed="true", stored="true" ) 

  write_field( name=get_latitude_fieldname(), 
               type="string", indexed="true", stored="true", multiValued="false" ) 

  write_field( name=get_longitude_fieldname(), 
               type="string", indexed="true", stored="true", multiValued="false" ) 

  write_field( name=get_total_works_sent_from_place_fieldname(), 
               type="int", indexed="false", stored="true" ) 

  write_field( name=get_total_works_sent_to_place_fieldname(), 
               type="int", indexed="false", stored="true" ) 

  write_field( name=get_total_works_mentioning_place_fieldname(), 
               type="int", indexed="false", stored="true" ) 

  if called_from != 'all': #{
    write_field( name=get_date_added_fieldname(), 
                 type="tdate", indexed="true", stored="true" ) 

    write_field( name=get_date_created_fieldname(), 
                 type="tdate", indexed="true", stored="true", 
                 comment = 'creation_timestamp' )

    write_field( name=get_date_changed_fieldname(), 
                 type="tdate", indexed="true", stored="true", 
                 comment = 'change_timestamp' )

    write_field( name=get_changed_by_user_fieldname(), 
                 type="string", indexed="false", stored="true", 
                 comment = 'change_user' )
  #}

# End of write_optional_fields
#}  -- curly brace is a cheat to help with jumping to matching brace
#--------------------------------------------------------------------------------------------------

def write_relations( called_from = 'locations' ): #{ -- curly brace helps with jumping to matching brace!

  print ''
  print ''
  write_section_heading( 'Links from locations' )
  print ''

  write_field( name=get_works_with_origin_fieldname(), 
               type="string", indexed="true", stored="true", multiValued="true", 
               comment = 'type-was_sent_from' )
  
  write_field( name=get_works_with_destination_fieldname(), 
               type="string", indexed="true", stored="true", multiValued="true", 
               comment = 'type-was_sent_to' )
  
  write_field( name=get_people_born_at_place_fieldname(), 
               type="string", indexed="true", stored="true", multiValued="true", 
               comment = 'type-was_born_in_location' )
  
  write_field( name=get_people_who_died_at_place_fieldname(), 
               type="string", indexed="true", stored="true", multiValued="true" )
  
  write_field( name=get_people_who_visited_place_fieldname(), 
               type="string", indexed="true", stored="true", multiValued="true" )
  
  if called_from != 'all': #{
    write_field( name=get_relations_to_comments_fieldname(), 
                 type="string", indexed="true", stored="true", multiValued="true" ) 

    write_field( name=get_works_in_which_mentioned_fieldname(), 
                 type="string", indexed="true", stored="true", multiValued="true", 
                 comment = 'type-mentions_place' )

    write_field( name=get_relations_to_resource_fieldname(), 
                 type="string", indexed="true", stored="true", multiValued="true", 
                 comment = 'type-is_related_to' )
  #}
  
  write_end_marker( 'links from locations' )

# End of 'write_relations'
#}  -- curly brace is a cheat to help with jumping to matching brace
#--------------------------------------------------------------------------------------------------

def write_additional():  #{

  print ''
  print ''
  write_section_heading( 'additional' ) 
  print ''

  write_field( name="timestamp_indexed", type="tdate", indexed="true", stored="true", 
               multiValued="false", default="NOW" ) 

  write_field( name="object_type", type="string", indexed="true", stored="true", required="true", 
               default="location" ) 
  
  write_field( name="browse", type="alphaOnlySort", indexed="true", stored="false", 
               multiValued="false" ) 

  write_field( name="default_search_field", type="text", indexed="true", stored="false", 
               multiValued="true" ) 

#}
#--------------------------------------------------------------------------------------------------

def write_copyfields( called_from = 'locations' ): #{

  if called_from == 'all':
    write_section_heading( 'locations copyFields' )
  write_section_heading( '<copyField source="SOURCE" dest="DEST"/>' )

  if called_from != 'all':
    write_copyfield( source=get_uuid_fieldname(), dest="id" )
  
  print ''

  write_copyfield( source=get_location_name_fieldname(),    dest="default_search_field" )
  write_copyfield( source=get_location_synonyms_fieldname(),dest="default_search_field" )

  if called_from != 'all':
    write_copyfield( source=get_location_name_fieldname(),    dest="browse" )
#}
#--------------------------------------------------------------------------------------------------

def write_mainfields(): #{ -- curly brace is a cheat to help with jumping to matching brace

  write_start_marker( 'locations' )

  write_required_fields()

  write_optional_fields()

  write_relations()

  write_additional()

  write_end_marker( 'locations' )

# End of write_mainfields
#}  -- curly brace is a cheat to help with jumping to matching brace
#----------------------------------------------------------------------------------------------

if __name__ == '__main__':

  myself = sys.argv[0]
  print '<!-- Auto-generated by ' + myself + ' -->'
  if len( sys.argv ) > 1:
    parm = sys.argv[1]
    if parm.upper() == 'M':
      write_mainfields()
    elif parm.upper() == 'C':
      write_copyfields()
    else:
      print 'Unknown argument: "' + parm + '". Expected M for main fields or C for copy fields.'
  else:
    write_mainfields()
    write_copyfields()
#endif

#----------------------------------------------------------------------------------------------
