from flask.ext.login import login_required, current_user
from flask import Module, jsonify, request, g, flash, url_for
from fossix.utils import render_template, redirect_back
from fossix.forms import ContentCreate_Form
from fossix.models import Content, Keywords, User
from fossix.extensions import fdb as db
from sqlalchemy import func

content = Module(__name__)

@content.route('/create/', methods=['GET', 'POST'])
@login_required
def create_content():
    c = Content()
    form = ContentCreate_Form(obj=c)
    if form.validate_on_submit():
	form.populate_obj(c)
	c.author_id = current_user.id
	c.category = Content.ARTICLE
	c.state = Content.REVIEW
	db.session.add(c)
	db.session.commit()
	flash('Thank you. Content submitted for review.')
	redirect_back('main.index')

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
