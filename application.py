from flask import Flask, g, session
from fossix.extensions import fdb, oid, cache
from fossix import views
from fossix.models import User
from fossix.config import DebugConfig

__all__ = ['create_app']

APP_NAME = 'fossix'

DEFAULT_MODULES = (
    (views.main, ""),
    (views.account, "/login")
)

def create_app(config=None):
    app = Flask(APP_NAME)
    modules = DEFAULT_MODULES

    for module, url_prefix in modules:
        app.register_module(module, url_prefix=url_prefix)

    if config is None:
	app.config.from_object(DebugConfig())

    configure_logging(app)
    configure_errorhandlers(app)
    configure_extensions(app)
    configure_before_handlers(app)

    return app

def configure_logging(app):
    pass

def configure_before_handlers(app):
    @app.before_request
    def lookup_current_user():
	g.user = None
	if 'openid' in session:
	    openid = session['openid']
	    g.user = User.query.filter_by(openid=openid).first()

def configure_extensions(app):
    fdb.init_app(app)
    oid.init_app(app)
    cache.init_app(app, config={'CACHE_TYPE' : 'memcached',
				'CACHE_DEFAULT_TIMEOUT' : 86400}) # one day

def configure_errorhandlers(app):
    pass
