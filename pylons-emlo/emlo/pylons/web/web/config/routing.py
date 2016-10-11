"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper

def make_map(config):
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False
    map.explicit = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    # CUSTOM ROUTES HERE
    default_action = 'index' # 'updating' #
    
    map.connect('/', controller='home', action=default_action)
    map.connect('/index', controller='home', action=default_action)
    map.connect('/index/', controller='home', action=default_action)
    map.connect('/home', controller='home', action=default_action)
    map.connect('/home/', controller='home', action=default_action)

    map.connect('/advanced', controller='search', action='index')
    map.connect('/advanced/', controller='search', action='index')
    #map.connect('/search', controller='search', action='index')
    #map.connect('/search/', controller='search', action='index')
    #map.connect('/search/results', controller='search', action='results')
    #map.connect('/search/results/', controller='search', action='results')

    #map.connect('/browse', controller='browse', action='index')
    #map.connect('/browse/', controller='browse', action='index')
    #map.connect('/browse/{action}', controller='browse')

    #map.connect('/profile/{action}/{id}' )

    map.connect('/collection', controller='emlo_collections', action='index')
    map.connect('/collections', controller='emlo_collections', action='index')
    map.connect('/catalogue', controller='emlo_collections', action='index')
    map.connect('/catalogues', controller='emlo_collections', action='index')

    map.connect('/{controller}/{action}/{id}') # profile/{action}/id
    map.connect('/{controller}/{action}') # search/results, browse/{action}

    map.connect('/{controller}/', action='index') # contribute, technical, about, home, search, browse
    map.connect('/{controller}', action='index') # contribute, technical, about, home, search, browse

    return map
