from flask import Module, render_template, flash, Blueprint
from fossix.utils import cached, render_page
from fossix.models import Content
from flask.ext.classy import FlaskView, route

main = Blueprint('main', __name__)

class MainView(FlaskView):
    def index(self):
	recent = Content.get_recent(10)
	popular = Content.get_popular(5)
	return render_template('index.html', index_recent=recent,
			       index_popular=popular)

    def syntax(self):
	return render_template('site/syntax.html')

    def policy(self):
	return render_template('site/policy.html')

MainView.register(main, route_base="/")
