from flask.ext.login import login_required, current_user
from flask import Module, jsonify, request, g, flash, url_for
from fossix.utils import render_template, redirect_back
from fossix.forms import ContentCreate_Form
from fossix.models import Content, Keywords
from fossix.extensions import fdb as db

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
