from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

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
       self.engine = create_engine(url, echo=True)
       self.Model = declarative_base()
       self.metadata = MetaData()
       self.metadata.bind = self.engine
       self.session = sessionmaker(bind=self.engine, expire_on_commit=False)()

DB_SERVER = 'localhost'
DB_PORT = 5432
DB_NAME = 'fossix'
DB_USER = 'fossguy'
DB_PASSWD  = 'db_password'

fdb = SQLBase(get_dburi('postgresql', DB_SERVER, DB_PORT,
			DB_NAME,DB_USER, DB_PASSWD))
fdb.metadata.reflect(views=True)

from fossix.models.user import User, Identity
from fossix.models.content import Content, Keywords, ContentVersions, ContentMeta
