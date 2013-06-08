from flask.ext.login import login_required, current_user
from flask import Module, jsonify, request, g, flash, url_for, redirect, json,\
    Response, abort
from fossix.utils import render_template, redirect_back
from fossix.forms import ContentCreate_Form, ContentEdit_Form
from fossix.models import Content, Keywords, User, ContentVersions,\
    ContentMeta, fdb as db
from sqlalchemy import func
from markdown import markdown
from flask.ext.classy import FlaskView

content = Module(__name__)

class CreateView(FlaskView):
    @login_required
    def index(self):
	self.form = ContentCreate_Form()
	return render_template('content/create.html', form=self.form)

    @login_required
    def post(self):
	if self.form.validate_on_submit():
	    c = Content(state='published', modifier=current_user.id,
			category='article')
	    # Cannot use form's populate method, when it is trying to append
	    # tags, the version field is not yet set, since it happens in the db
	    # side. So we have to commit content and then save the tags
	    c.title = self.form.title.data
	    c.content = self.form.content.data
	    c.teaser = self.form.teaser.data
	    c.save()
	    c.tags_csv = self.form.tags_csv.data
	    flash('Thank you. Content submitted for review.')
	    return redirect(url_for('content.view_article', id=c.id,
				    title=c.title))

	return redirect(url_for('get', form=self.form))


class EditView(FlaskView):
    @login_required
    def get(self, id):
	self.id = id
	c = db.session.query(Content).get(id)
	if not c:
	    abort(404)

	form = ContentEdit_Form(obj=c)
	form.edit_summary.data = ""
	return render_template('content/create.html', form=form)

    @login_required
    def post(self, id):
	c = db.session.query(Content).get(id)
	if not c:
	    abort(404)

	form = ContentEdit_Form(obj=c)
	if form.validate_on_submit():
	    form.populate_obj(c)
	    c.save()
	    flash('Edit "{0}" Saved.'.format(c.edit_summary))
	    return redirect(url_for('content.ContentView:get', id=c.id,
				    title=c.title))

	return self.get(id)

    @login_required
    def preview(self):
	content = request.form.get('content')
	title = request.form.get('title')
	if title is None or title == "":
	    title = "No Title"

	    result = {'content':markdown(content,
				 extensions = ["extra", "sane_lists",
					       "codehilite", "smartypants"],
				 safe_mode='remove',
				 output_format="html5"), 'title':title}

	    return jsonify(result);


class TagsView(FlaskView):
    def get(self, label):
	tag = db.session.query(Keywords).filter(Keywords.keyword == label).first()

	if not tag:
	    flash("No content is currently tagged with " + label)
	    return redirect_back('main.index')

	return render_template('content/tag.html', tag=tag)

    def get_all(self):
	tags = db.session.query(Keywords).all()
	result = []
	for tag in tags:
	    result.append({'tag': str(tag)})
	return jsonify(tags=result)


class ContentView(FlaskView):
    route_base = '/'
    def index(self):
	c = Content.get_recent(1)[0]
	if c is None:
	    flash(u'Nothing exists :-(.')
	    return redirect(url_for('main.index'))

	c.inc_read_count()
	return render_template('content/article.html', content=c)

    def get(self, id, title=None):
	redir = False
	c = db.session.query(Content).get(id)
	if c is None and title is not None:
	    c = db.session.query(Content).filter(func.lower(Content.title)
						 == func.lower(title))
	    if c.count() > 0:
		c = c.one()
		redir = True
	    else:
		c = None
	else:
	    if title != c.title:
		redir = True

	if c is None:
	    flash("Invalid URL or Content not available")
	    return redirect(url_for('content.ContentView:index'))

	if redir:
	    return redirect(url_for('content.ContentView:get', id=c.id,
				    title=c.title))

	c.inc_read_count()
	return render_template('content/article.html', content=c)

    def archive(self):
	return render_template('content/archive.html',
			       content=db.session.query(Content).all())

    def like(self, id):
	c = db.session.query(Content).get(id)

	if not c:
	    return abort(500)

	count = c.inc_like_count()
	data = {
	    'content' : count,
	}

	jd = json.dumps(data)
	resp = Response(jd, status=200, mimetype='application/json')

	return resp


CreateView.register(content)
EditView.register(content)
TagsView.register(content)
ContentView.register(content)
