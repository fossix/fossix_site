from flask.ext.login import login_required, current_user
from flask import Module, jsonify, request, g, flash, url_for, redirect, json,\
    Response, abort, Blueprint, current_app, session
from fossix.utils import render_template, redirect_back, get_uniqueid
from fossix.forms import ContentCreate_Form, ContentEdit_Form, Comment_Form
from fossix.models import Content, Keywords, User, ContentVersions,\
    ContentMeta, fdb as db
from sqlalchemy import func, and_, asc
from sqlalchemy.orm.exc import NoResultFound
from markdown import markdown
from flask.ext.classy import FlaskView, route

content = Blueprint('content', __name__)

class CreateView(FlaskView):
    @login_required
    def index(self):
	form = ContentCreate_Form()
	return render_template('content/create.html', form=form)

    @login_required
    def post(self):
	state = None
	form = ContentCreate_Form()
	if request.form['submit'].lower() == 'discard':
	    return redirect(url_for('main.MainView:index'))

	if request.form['submit'].lower() == 'publish':
	    state = 'published'
	elif request.form['submit'].lower() == 'save':
	    state = 'saved'

	if state is None:
	    return abort(412)

	if form.validate_on_submit():
	    c = Content()
	    # Cannot use form's populate method, when it is trying to append
	    # tags, the version field is not yet set, since it happens in the db
	    # side. So we have to commit content and then save the tags
	    c.modifier_id=current_user.id
	    c.category='article'
	    c.title = form.title.data
	    c.content = form.content.data
	    c.teaser = form.teaser.data
	    c.state = state
	    db.session.add(c)
	    db.session.commit()
	    cv = db.session.query(ContentVersions).filter(
		ContentVersions.id == c.id).one()
	    if  cv is None:
		abort(500)
	    cv.tags_csv = form.tags_csv.data
	    db.session.commit()

	    if state == 'published':
		g.user.karma = g.user.karma + 20
		return redirect(url_for('content.ContentView:get', id=c.id,
					title=c.title))
	    else:
		return redirect(url_for('main.MainView:index'))

	return render_template('content/create.html', form=form)


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

	if request.form['submit'].lower() == 'discard':
	    flash('Edits discarded')
	    return redirect(url_for('content.ContentView:get', id=c.id,
				    title=c.title))
	state = None
	if request.form['submit'].lower() == 'publish':
	    state = 'published'
	elif request.form['submit'].lower() == 'save':
	    state = 'saved'

	if state is None:
	    abort(412)

	if form.validate_on_submit():
	    c.state = state
	    c.title = form.title.data
	    c.content = form.content.data
	    c.edit_summary = form.edit_summary.data
	    c.modifier_id=current_user.id

	    old_version = c.version
	    db.session.add(c)
	    db.session.commit()
	    c = db.session.query(Content).get(c.id)
	    c.tags_csv = form.tags_csv.data
	    db.session.commit()

	    if state == 'publish' and c.version == old_version:
		flash('No Modifications done to save.')
	    else:
		flash('Edit "{0}" Saved.'.format(c.edit_summary))
	    return redirect(url_for('content.ContentView:get', id=c.id,
				    title=c.title))

	return render_template('content/create.html', form=form)

    @login_required
    @route('preview', methods=['GET', 'POST'])
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
    def index(self):
	page = request.args.get('page')
	if page is None:
	    page = 1
	else:
	    page = int(page)
	limit = 20
	start = (page - 1) * limit
	tags = db.session.query(Keywords).order_by(asc(Keywords.keyword)).all()
	page_total = len(tags) / limit
	tags = tags[start:start+limit]
	if not tags:
	    abort(404)

	return render_template('content/tags.html', tags=tags, current=page,
			       total=page_total)

    def get(self, label):
	tag = db.session.query(Keywords).filter(Keywords.keyword == label).first()

	if not tag:
	    flash("No content is currently tagged with " + label)
	    return redirect_back('main.MainView:index')

	return render_template('content/tag.html', tag=tag)

    def get_all(self):
	tags = db.session.query(Keywords).all()
	result = []
	for tag in tags:
	    result.append({'tag': str(tag)})
	return jsonify(tags=result)

    @login_required
    def put(self, tag, action):
	# watch a particular tag
	tag = db.session.query(Keywords).filter(Keywords.keyword==tag).one()
	if tag is None:
	    abort(404)

	if action=='watch':
	    if tag not in g.user.tags:
		g.user.tags.append(tag)
	elif action=='unwatch':
	    if tag in g.user.tags:
		g.user.tags.remove(tag)

	db.session.commit()
	data = {
	    'message': "Sucessfully added tag to your watchlist"
	}

	return jsonify(data)

    @login_required
    def watched(self):
	return render_template('content/watched_tags.html')


class ContentView(FlaskView):
    def index(self):
	c = Content.get_recent(1)
	if c is None:
	    abort(404)

	c = c[0]
	form = None
	if c is None:
	    flash(u'Nothing exists :-(.')
	    return redirect(url_for('main.MainView:index'))

	c.inc_read_count()
	if g.user.is_authenticated():
	    form = Comment_Form()
	    form.refers_to.data = c.id

	return render_template('content/article.html', content=c, comment=form)

    def get(self, id, title=None):
	form = None
	redir = False

	# id would always be an int
	try:
	    id = int(id)
	except ValueError:
	    return redirect(url_for('content.ContentView:index'))

	c = db.session.query(Content).get(id)
	if c is not None and c.category!='article':
	    abort(404)

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
	if g.user.is_authenticated():
	    form = Comment_Form()
	    form.content.data = ""
	    form.refers_to.data = c.id

	return render_template('content/article.html', content=c, comment=form)

    @login_required
    def vote(self, id, vote):
	c = db.session.query(Content).get(id)

	if not c:
	    return abort(500)

	if vote =='down':
	    count = c.dec_like_count()
	else:
	    count = c.inc_like_count()

	data = {
	    'count' : count,
	    'id' : id,
	}

	db.session.commit()

	jd = json.dumps(data)
	resp = Response(jd, status=200, mimetype='application/json')
	db.session.expire_all()

	return resp

    # The search function taken form
    # http://lowmanio.co.uk/blog/entries/postgresql-full-text-search-and-sqlalchemy/
    def search(self):
	terms = request.args.get('search')
	q = db.session.query(Content).filter('content.search_vector '\
						 '@@ plainto_tsquery(:sterms)')
	q = q.params(sterms=terms)
	q = q.add_column(func.ts_headline('pg_catalog.english',
					  Content.content,
					  func.plainto_tsquery(terms),
					  'MaxFragments=5,FragmentDelimiter=|||,'\
					      'StartSel="<span class=""shighlight"">", '\
					      'StopSel = "</span>", ',
					  ))

	q = q.add_column(func.ts_headline('pg_catalog.english',
					  Content.title,
					  func.plainto_tsquery(terms),
					  'HighlightAll=TRUE, '\
					      'StartSel="<span class=""shighlight"">", '\
					      'StopSel = "</span>"'))

	q = q.order_by('ts_rank_cd(content.search_vector, '\
			   'plainto_tsquery(:sterms)) DESC')

	results = [(entry, fragments.split('|||'), title) for entry, fragments,
		   title in q]

	return render_template('content/search.html', term=terms,
			       results=results)


class CommentView(FlaskView):
    def get(self, id, last=0):
	# id would always be an int
        # This error comes when old fossix urls are accessed (comment/reply/<id>
	try:
	    id = int(id)
	except ValueError:
            abort(404)
        
	c = db.session.query(Content).get(id)
	if c is None or (c.category != 'book' and c.category != 'article'):
	    data = {
		'html': "",
		'last': 0,
		'parent': id,
	    }
	else:
	    last = int(last)
	    limit = current_app.config['COMMENT_LOAD_LIMIT']
	    comments = c.comments[last:last + limit]
	    html = render_template('content/comment.html', comments=comments,
				   parent=c)
	    last = last + len(comments)

	    data = {
		'html': html,
		'last': last,
		'parent': id,
	    }

	jd = json.dumps(data)
	resp = Response(jd, status=200, mimetype='application/json')

	return resp

    @login_required
    def post(self, id):
	c = db.session.query(Content).get(id)

        if c is None:
	    abort(404)

	form = Comment_Form()

	if form.validate_on_submit():
	    comment = Content()
	    comment.category = 'comment'
	    comment.state = 'published'
	    comment.modifier_id = g.user.id
	    c.inc_comment_count()
	    form.populate_obj(comment)
	    db.session.add(comment)
	    db.session.commit()
	    db.session.expire_all()
	    # Since we opted not to destroy objects after commit, we need to
	    # query again to get the latest posted comment
	    c = db.session.query(Content).get(id)
	    return redirect(url_for('.ContentView:get', id=id, title="test"));

	return render_template('content/article.html', content=c, comment=form)


class ArchiveView(FlaskView):
    def index(self):
	return self.get(1)

    def get(self, page):
	if not str(page).isdigit():
	    page = 0

	page_limit = session.get('archive_page_limit') or \
	    current_app.config['ARCHIVE_PAGE_LIMIT']

	end = (int(page) * page_limit)
	start = end - page_limit

	c = content=db.session.query(Content).filter(
	    Content.category=='article')
	if c.count() == 0:
	    flash("No content yet to show in archives.")
	    return redirect_back('main.MainView:index')

	c = c.all()
	contents = c[start:end]

	if not contents:
	    abort(404)

	more = False
	less = False

	if len(c) > end:
	    more = int(page) + 1

	if start >= page_limit:
	    less = int(page) - 1

	return render_template('content/archive.html', content=contents,
			       more=more, less=less)

CreateView.register(content)
EditView.register(content)
TagsView.register(content)
ContentView.register(content)
CommentView.register(content)
ArchiveView.register(content)
