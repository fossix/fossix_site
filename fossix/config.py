import os

class DefaultConfig(object):
    DATABASE_CONNECT_OPTIONS = {}

    SECRET_KEY = 'SOME_SECURE_PHRASE'

    CSRF_ENABLED = True
    CSRF_SESSION_KEY = "A_SECURE_PHRASE_TO_PROTECT_FORMS"

    CACHE_TYPE = 'memcached'
    CACHE_MEMCACHED_SERVERS = ['127.0.0.1:11211']
    CACHE_DEFAULT_TIMEOUT = 604800	# One day

    # Site specific configuration
    SITE_TITLE = 'Fossix'
    SITE_NAME = 'Fossix.org'
    SITE_URL = 'http://fossix.org'
    SITE_MOTTO = 'Let\'s give back to the community'
    SITE_SUBTITLE = 'The Opensource way'

    RECAPTCHA_PUBLIC_KEY = "YOUR_RECAPTCHA_PUBLIC_KEY"
    RECAPTCHA_PRIVATE_KEY = "YOUR_RECAPTCHA_PRIVATE_KEY"
    RECAPTCHA_OPTIONS = ""

    ARCHIVE_PAGE_LIMIT = 10
    COMMENT_LOAD_LIMIT = 5

def get_dburi(dbcon, server, port, dbname, user, password):
    uri = dbcon + "://"
    if server:
	if user:
	    uri = uri + user + ":" + password + "@"
	uri = uri + server + ":" + str(port)

    uri = uri + "/" + dbname

    return uri

class DebugConfig(DefaultConfig):

    _basedir = os.path.abspath(os.path.dirname(__file__))

    DEBUG = True
    SQLALCHEMY_ECHO = False
    DB_SERVER = 'localhost'
    DB_PORT = 5432
    DB_NAME = 'fossix'
    DB_USER = 'user'
    DB_PASSWD  = 'db_password'

    SQLALCHEMY_DATABASE_URI = get_dburi('postgresql', DB_SERVER, DB_PORT,
					DB_NAME,DB_USER, DB_PASSWD)

    SQLALCHEMY_MIGRATE_REPO = os.path.join(_basedir, 'fdb_repo')
    SITE_CDN = '/static'

class OnlineConfig(DefaultConfig):
    DEBUG = False

CurrentConfig=DebugConfig()
