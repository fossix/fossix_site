from flask import Flask, g
from fossix.extensions import fdb, oid, cache, lm
from fossix import views
from fossix.models import User, Content
from fossix.config import DebugConfig
from flask.ext.login import current_user
from flask.ext.markdown import Markdown

__all__ = ['create_app']

APP_NAME = 'fossix'

DEFAULT_MODULES = (
    (views.main, ""),
    (views.account, "/account"),
    (views.content, "/content"),
)

def create_app(config=None):
    app = Flask(APP_NAME)
    modules = DEFAULT_MODULES

    for module, url_prefix in modules:
        app.register_blueprint(module, url_prefix=url_prefix)

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
	g.user = current_user

    # for login manager
    @lm.user_loader
    def load_user(id):
	return User.query.get(int(id))

    @app.context_processor
    def setup_globals():
	recent = Content.get_recent(5)
	popular = Content.get_popular(5, False)

	return dict(popular=popular, recent=recent)


def configure_extensions(app):
    fdb.init_app(app)
    oid.init_app(app)
    cache.init_app(app, config={'CACHE_TYPE' : 'memcached',
				'CACHE_DEFAULT_TIMEOUT' : 86400}) # one day
    lm.init_app(app)
    lm.login_view = "account.LoginView:index"

    Markdown(app, extensions = ["extra", "sane_lists", "codehilite",
				"smartypants"],
	     safe_mode='remove',
	     output_format="html5")

def configure_errorhandlers(app):
    pass
