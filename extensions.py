from flask.ext.openid import OpenID
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache

fdb = SQLAlchemy()
oid = OpenID()
cache = Cache()
