from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.openid import OpenID
from flask.ext.cache import Cache

__all__ = ['oid', 'fdb']

fdb = SQLAlchemy()
oid = OpenID()
cache = Cache()
