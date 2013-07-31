from fossix.extensions import cache
from flask import Module, render_template, flash, Blueprint, url_for, \
    make_response
from fossix.utils import render_page
from fossix.models import Content, User, Keywords, fdb as db
from flask.ext.classy import FlaskView, route
from datetime import datetime, timedelta

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
	week_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
	month_ago = (datetime.now() - timedelta(days=30)).date().isoformat()

	# some static pages, update here when there are new pages
	sitemap = []
	sitemap.append([url_for('main.MainView:index'), week_ago, 'daily'])
	sitemap.append([url_for('content.ArchiveView:index'), week_ago, 'monthly'])
	sitemap.append([url_for('main.MainView:syntax'), month_ago, 'monthly'])
	sitemap.append([url_for('main.MainView:policy'), month_ago, 'monthly'])
	sitemap.append([url_for('content.TagsView:index'), week_ago, 'weekly'])
	sitemap.append([url_for('content.ContentView:index'), week_ago, 'weekly'])

	contents = db.session.query(Content).filter(
	    Content.category=='article').order_by(Content.modified_date).all()
	for c in contents:
	    url = url_for('content.ContentView:get', id=c.id, title=c.title)
	    modified_time = c.modified_date.date().isoformat()
	    cfreq = 'monthly'
	    sitemap.append([url, modified_time, cfreq])

	users = db.session.query(User).all()
	for c in users:
	    url = url_for('account.ProfileView:get', username=c.username)
	    modified_time = week_ago
	    cfreq = 'weekly'
	    sitemap.append([url, modified_time, cfreq])

	keywords = db.session.query(Keywords).all()
	for tag in keywords:
	    url = url_for('content.TagsView:get', label=tag)
	    modified_time = month_ago
	    cfreq = 'monthly'
	    sitemap.append([url, modified_time, cfreq])

	sitemap_resp = render_template('site/sitemap.xml', sitemap=sitemap),

	response = make_response(sitemap_resp)
	response.headers["Content-Type"] = "application/xml"
	return response

MainView.register(main, route_base="/")
