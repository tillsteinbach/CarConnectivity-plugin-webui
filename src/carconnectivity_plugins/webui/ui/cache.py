""" Cache configuration for the webui. """
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})
