from flask.ext.login import login_required, current_user
from flask import Module, jsonify, request, g, flash, url_for, redirect, json,\
    Response
from fossix.utils import render_template, redirect_back
from fossix.forms import ContentCreate_Form
from fossix.models import Content, Keywords, User
from fossix.extensions import fdb as db
from sqlalchemy import func
from markdown import markdown

content = Module(__name__)

@content.route('/create/', methods=['GET', 'POST'])
@login_required
def create_content():
    form = ContentCreate_Form()
    if form.validate_on_submit():
	c = Content(author=g.user, state=Content.REVIEW,
		    author_id=current_user.id, category=Content.ARTICLE)
	form.populate_obj(c)
	db.session.add(c)
	db.session.commit()
	flash('Thank you. Content submitted for review.')
	return redirect(url_for('content.view_article', title=c.title))

    form.next.data = request.args.get('next')

    return render_template('content/create.html', form=form)

@content.route('/__tags_get', methods=['GET', 'POST'])
def get_tags():
    tags = Keywords.query.all()
    result = []
    for tag in tags:
	result.append({'tag': str(tag)})
    return jsonify(tags=result)

@content.route('/<title>')
def view_article(title):
    c = Content.query.filter(func.lower(Content.title) == func.lower(title))

    if c and c.count() == 1:
	c = c.one()
    else:
	c = get_recent(1)[0]
	if not c:
	    c = abort(404)

    author = User.query.get(c.author_id)
    return render_template('content/article.html', content=c, author=author)

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
    c = Content.query.get(id)
    if not c:
	abort(404)

    form = ContentCreate_Form(obj=c)
    if form.validate_on_submit():
	form.populate_obj(c)
	db.session.add(c)
	db.session.commit()
	flash('Edits Saved.')
	return redirect(url_for('content.view_article', title=c.title))

    return render_template('content/create.html', form=form)

@content.route('/tag/<label>')
def tag(label):
    tag = Keywords.query.filter(Keywords.keyword == label).first()

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
    return render_template('content/archive.html', content=Content.query.all())
