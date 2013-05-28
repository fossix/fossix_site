from flask import Module, render_template, flash, Blueprint
from fossix.utils import cached, render_page
from fossix.models import Content
from flask.ext.classy import FlaskView, route

main = Blueprint('main', __name__)

class MainView(FlaskView):
    def index(self):
	return render_template('index.html')

    def syntax(self):
	return render_template('site/syntax.html')

MainView.register(main, route_base="/")
