from flask.ext.openid import OpenID
from flask.ext.cache import Cache
from flask.ext.login import LoginManager

__all__ = ['oid', 'cache', 'lm']

oid = OpenID()
cache = Cache()
lm = LoginManager()
