import os

class DefaultConfig(object):
    _basedir = os.path.abspath(os.path.dirname(__file__))

    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'fapp.db')
    SQLALCHEMY_MIGRATE_REPO = os.path.join(_basedir, 'fdb_repo')
    DATABASE_CONNECT_OPTIONS = {}

    SECRET_KEY = 'SecretKeyForSessionSigning'

    CSRF_ENABLED=True
    CSRF_SESSION_KEY="somethingimpossibletoguess"

    CACHE_TYPE='memcached'
    CACHE_MEMCACHED_SERVERS=['127.0.0.1:11211']
    CACHE_DEFAULT_TIMEOUT=604800	# One day
