from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.openid import OpenID
from flask.ext.cache import Cache
from flask.ext.login import LoginManager

__all__ = ['oid', 'fdb', 'cache', 'lm']

fdb = SQLAlchemy()
oid = OpenID()
cache = Cache()
lm = LoginManager()
