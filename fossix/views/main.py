from fossix.extensions import cache
from flask import Module, render_template, flash, Blueprint, url_for, \
    make_response
from fossix.utils import render_page
from fossix.models import Content, fdb as db
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

    def roles(self):
	return "About roles in fossix"

    def karma(self):
	return "About karma in fossix"

    @route('/sitemap.xml', )
    def sitemap(self):
	active = []
	contents = c = content=db.session.query(Content).filter(
	    Content.category=='article').order_by(Content.modified_date).all()
	for c in contents:
	    url = url_for('content.ContentView:get', id=c.id, title=c.title)
	    modified_time = c.modified_date.date().isoformat()
	    active.append([url, modified_time])
	    sitemap = render_template('site/sitemap.xml',
				      active=active)
	response = make_response(sitemap)
	response.headers["Content-Type"] = "application/xml"
	return response

MainView.register(main, route_base="/")
