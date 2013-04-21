import os

class DefaultConfig(object):
    DATABASE_CONNECT_OPTIONS = {}

    SECRET_KEY = 'SecretKeyForSessionSigning'

    CSRF_ENABLED = True
    CSRF_SESSION_KEY = "somethingimpossibletoguess"

    CACHE_TYPE = 'memcached'
    CACHE_MEMCACHED_SERVERS = ['127.0.0.1:11211']
    CACHE_DEFAULT_TIMEOUT = 604800	# One day

    # Site specific configuration
    SITE_TITLE = 'Fossix'
    SITE_NAME = 'Fossix.org'
    SITE_URL = 'http://fossix.org'
    SITE_MOTTO = ''

class DebugConfig(DefaultConfig):
    DEBUG = True

    _basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'fapp.db')
    SQLALCHEMY_MIGRATE_REPO = os.path.join(_basedir, 'fdb_repo')
    SITE_CDN = 'http://fcdn.fossix.org/fossix'
