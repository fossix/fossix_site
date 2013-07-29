from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from fossix.config import CurrentConfig

def get_dburi(dbcon, server, port, dbname, user, password):
    uri = dbcon + "://"
    if server:
	if user:
	    uri = uri + user + ":" + password + "@"
	uri = uri + server + ":" + str(port)

    uri = uri + "/" + dbname

    return uri

class SQLBase:
    def __init__(self, url):
	self.engine = create_engine(url,
				   echo=CurrentConfig.SQLALCHEMY_ECHO)
	self.Model = declarative_base()
	self.metadata = MetaData()
	self.metadata.bind = self.engine
	# expire_on_commit is set to false, because it is need for setting the
	# proper tags after a save as saved contents will not be shown in content
	# view
	self.session = scoped_session(sessionmaker(bind=self.engine,
						   expire_on_commit=False))


DB_SERVER = CurrentConfig.DB_SERVER
DB_PORT = CurrentConfig.DB_PORT
DB_NAME = CurrentConfig.DB_NAME
DB_USER = CurrentConfig.DB_USER
DB_PASSWD = CurrentConfig.DB_PASSWD

fdb = SQLBase(get_dburi('postgresql', DB_SERVER, DB_PORT,
			DB_NAME,DB_USER, DB_PASSWD))
fdb.metadata.reflect(views=True)

from fossix.models.models import Keywords
from fossix.models.user import User, Identity
from fossix.models.content import Content, ContentVersions, ContentMeta
