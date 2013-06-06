from flask.ext.login import login_required, current_user
from flask import Module, jsonify, request, g, flash, url_for, redirect, json,\
    Response, abort
from fossix.utils import render_template, redirect_back
from fossix.forms import ContentCreate_Form, ContentEdit_Form
from fossix.models import Content, Keywords, User, ContentVersions,\
    ContentMeta, fdb as db
from sqlalchemy import func
from markdown import markdown

content = Module(__name__)

@content.route('/create/', methods=['GET', 'POST'])
@login_required
def create_content():
    form = ContentCreate_Form()
    if form.validate_on_submit():
	c = Content(state='published', modifier=current_user.id,
		    category='article')
	# Cannot user form's populate method, when it is trying to append tags,
	# the version field is not yet set, since it happens in the db side. So
	# we have to commit content and then save the tags
	c.title = form.title.data
	c.content = form.content.data
	c.teaser = form.teaser.data
	c.save()
	c.tags_csv = form.tags_csv.data
	flash('Thank you. Content submitted for review.')
	return redirect(url_for('content.view_article', id=c.id, title=c.title))

    form.next.data = request.args.get('next')

    return render_template('content/create.html', form=form)

@content.route('/__tags_get', methods=['GET', 'POST'])
def get_tags():
    tags = db.session.query(Keywords).all()
    result = []
    for tag in tags:
	result.append({'tag': str(tag)})
    return jsonify(tags=result)

@content.route('/')
@content.route('/<int:id>')
@content.route('/<title>')
@content.route('/<int:id>/<title>')
def view_article(id=None, title=None):
    c = None
    if id is not None:
	c = db.session.query(Content).get(id)

    if c is None and title is not None:
	    c = db.session.query(Content).filter(func.lower(Content.title)
						 == func.lower(title))
	    if c.count() > 0:
		c = c.one()
	    else:
		c = None

    if c is not None:
	if c.title != title or c.id != id:
	    return redirect(url_for('content.view_article', id=c.id, title=c.title))

	if not c.is_published():
	    flash(u'Content is not Published yet, please contact the moderator if you feel the content should be online')
	    return redirect_back('main.index')

	c.inc_read_count()
	return render_template('content/article.html', content=c)

    flash(u'Nothing exists with that URL, Here is the archive of all content.')
    return redirect(url_for('content.archive', content=None))

@content.route('/__preview/', methods=['POST'])
def article_preview():
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

@content.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_article(id):
    c = db.session.query(Content).get(id)
    if not c:
	abort(404)

    form = ContentEdit_Form(obj=c)
    if form.validate_on_submit():
	form.populate_obj(c)
	c.save()
	flash('Edits Saved.')
	return redirect(url_for('content.view_article', id=c.id, title=c.title))

    form.edit_summary.data = ""
    return render_template('content/create.html', form=form)

@content.route('/tag/<label>')
def tag(label):
    tag = db.session.query(Keywords).filter(Keywords.keyword == label).first()

    if not tag:
	flash("No content is currently tagged with " + label)
	return redirect_back('main.index')

    return render_template('content/tag.html', tag=tag)

@content.route('/like/<int:id>')
def like(id):
    c = Content.query.get(id)

    if not c:
	# This should never happen
	return abort(500)

    count = c.inc_like_count()
    data = {
	'content' : count,
	}

    jd = json.dumps(data)
    resp = Response(jd, status=200, mimetype='application/json')

    return resp

@content.route('/archive')
def archive():
    return render_template('content/archive.html',
			   content=db.session.query(Content).all())
