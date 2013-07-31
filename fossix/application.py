from flask import Flask, g, render_template
from fossix.extensions import oid, cache, lm
from fossix.models import fdb
from fossix import views
from fossix.models import User, Content
from fossix.config import CurrentConfig
from flask.ext.login import current_user
from flask.ext.markdown import Markdown
from fossix.utils import relative_now
from sqlalchemy.orm import sessionmaker, scoped_session

__all__ = ['create_app']

APP_NAME = 'fossix'

DEFAULT_MODULES = (
    (views.main, ""),
    (views.content, ""),
    (views.account, "/account"),
)

def create_app(config=None):
    app = Flask(APP_NAME)
    modules = DEFAULT_MODULES

    for module, url_prefix in modules:
        app.register_blueprint(module, url_prefix=url_prefix)

    if config is None:
	app.config.from_object(CurrentConfig)

    configure_logging(app)
    configure_errorhandlers(app)
    configure_extensions(app)
    configure_before_handlers(app)
    configure_after_handlers(app)

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
	return fdb.session.query(User).get(int(id))

    @app.context_processor
    def setup_globals():
	recent = Content.get_recent(5)
	popular = Content.get_popular(5)

	return dict(popular=popular, recent=recent)

    app.jinja_env.filters['relative_now'] = relative_now

def configure_after_handlers(app):
    @app.teardown_appcontext
    def shutdown_session(exception=None):
	fdb.session.remove()

def configure_extensions(app):
    oid.init_app(app)
    cache.init_app(app, config={'CACHE_TYPE' : 'memcached',
				'CACHE_DEFAULT_TIMEOUT' : 86400}) # one day
    lm.init_app(app)
    lm.login_view = "account.LoginView:index"
    lm.refresh_view = "account.LoginView:index"
    lm.needs_refresh_message = {
	u"The page you are visiting needs re-authentication."
    }
    lm.needs_refresh_message_category = "info"

    Markdown(app, extensions = ["extra", "sane_lists", "codehilite",
				"smartypants", "toc"],
	     safe_mode='remove',
	     output_format="html5")

# This function also has the error pages
def configure_errorhandlers(app):
    @app.errorhandler(404)
    def not_found(e):
	return render_template('error/404.html', err=e), 404
