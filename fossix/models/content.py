from fossix.extensions import fdb as db
from datetime import datetime
from sqlalchemy import func, text, and_
from fossix.models import User

# This table contains keywords that are tagged in articles
class Keywords(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    keyword = db.Column(db.String(25), nullable = False, index = True, unique =
			True)

    @staticmethod
    def get(k):
	obj = Keywords.query.filter(Keywords.keyword == k).first()
	if not obj:
	    obj = Keywords(k)

	return obj

    def __init__(self, k):
        self.keyword = k

    def __repr__(self):
        return '%s' % self.keyword

tags_assoc = db.Table('tags_assoc', db.metadata,
    db.Column('content_id', db.Integer, nullable=False),
    db.Column('content_version', db.Integer, nullable=False),
    db.Column('keyword_id', db.Integer, db.ForeignKey('keywords.id')),
    db.ForeignKeyConstraint(['content_id', 'content_version'],
			    ['content_versions.id', 'content_versions.version'])

)

class ContentMeta(db.Model):
    ARTICLE = 10
    NEWS = 20
    COMMENT = 30

    __tablename__ = 'content_meta'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    create_date = db.Column(db.DateTime, nullable = False,
			    default=text('NOW()'))
    like_count = db.Column(db.Integer, default = 0)
    read_count = db.Column(db.Integer, default = 0)
    comment_count = db.Column(db.Integer, default = 0)
    category = db.Column(db.SmallInteger, nullable = False)
    refers_to = db.Column(db.Integer, db.ForeignKey('content_meta.id'))
    teaser = db.Column(db.String(200), index = True)

    author = db.relation(User, innerjoin=True, lazy="joined")

class ContentVersions(db.Model):
    # State
    DELETED = 5
    DRAFT = 10
    UNPUBLISHED = 20
    PUBLISHED = 50

    __tablename__ = 'content_versions'
    __table_args__ = (db.PrimaryKeyConstraint('id', 'version'),)
    id = db.Column(db.Integer, db.ForeignKey(ContentMeta.id))
    version = db.Column(db.Integer, index = True, autoincrement = False,
			default = 0)
    modifier_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    modified_date = db.Column(db.DateTime, nullable = False,
			      default=text('NOW()'))
    title = db.Column(db.String(128), index = True)
    content = db.Column(db.Text, nullable = False)
    state = db.Column(db.SmallInteger, nullable = False)
    tags = db.relationship(
	'Keywords', secondary=tags_assoc,
	backref=db.backref('content_versions', lazy='dynamic'))
    modifier = db.relation(User, innerjoin=True, lazy="joined")


# This is represented as a view. We cannot do create view, or just reflect the
# table from the database since we need to know the engine and app before, but
# this is called even before configure_extensions is called.

class Content(db.Model):
    # This is a view
    __tablename__ = 'content' #db.Table('content', db.metadata)
    id = db.Column(db.Integer, db.ForeignKey(ContentMeta.id), primary_key=True)
    version = db.Column(db.Integer, index = True, autoincrement = False)
    modifier_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    modified_date = db.Column(db.DateTime, nullable = False,
			      default=text('NOW()'))
    title = db.Column(db.String(128), index = True)
    content = db.Column(db.Text, nullable = False)
    state = db.Column(db.SmallInteger, nullable = False)
    author_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    create_date = db.Column(db.DateTime, nullable = False,
			    default=text('NOW()'))
    like_count = db.Column(db.Integer, default = 0)
    read_count = db.Column(db.Integer, default = 0)
    comment_count = db.Column(db.Integer, default = 0)
    category = db.Column(db.SmallInteger, nullable = False)
    refers_to = db.Column(db.Integer, db.ForeignKey('content_meta.id'))

    tags =db. relationship(
	"Keywords", secondary=tags_assoc,
	primaryjoin=and_(id == tags_assoc.c.content_id,
			 version == tags_assoc.c.content_version),
	backref="parents"
	)

    author = db.relationship(User, foreign_keys=author_id)
    modifier = db.relationship(User, foreign_keys=modifier_id)
    content_meta = db.relationship(ContentMeta, foreign_keys=id)

    def __repr_(self):
        return 'id: %r\ntitle: %r\ndate:%r' % (self.id, self.title, self.create_date)

    def inc_read_count(self):
	self.content_meta.read_count = self.content_meta.read_count + 1
	db.session.add(self)
	db.session.commit()

    def inc_like_count(self):
	self.like_count = self.like_count + 1
	db.session.add(self)
	db.session.commit()
        return self.like_count

    def get_create_date(self):
	return self.create_date.strftime("%A %d. %B %Y")

    def is_published(self):
	return True

    def get_tags_csv(self):
	return ",".join(x.keyword for x in self.tags)

    def set_tags_csv(self,value):
	current = self.tags
	new = (x for x in value.strip().split(','))
	self.tags = []
	for tag in new:
	    if len(tag):
		self.tags.append(Keywords.get(tag.strip()))

    tags_csv = property(get_tags_csv, set_tags_csv)

    def save(self):
	if self.id is None:
	    cm = ContentMeta()
	    cm.author_id = self.author_id
	    cm.category = self.category
	    db.session.add(cm)
	    db.session.commit()
	    self.version = 0
	    self.id = cm.id

	cv = ContentVersions()
	cv.id = self.id
	cv.version = self.version + 1
	cv.modifier_id = self.author_id
	cv.title = self.title
	cv.content = self.content
	cv.state = self.state
	db.session.add(cv)
	db.session.commit()

    @staticmethod
    def get_recent(count = 5):
	c = Content.query.order_by(Content.create_date.desc()).limit(count)
	if c.count() > 0:
	    return c.all()

	return None

    @staticmethod
    def get_popular(count = 5, exclude_recent = True, recent_limit = 5):
	recent = None
	if exclude_recent:
	    recent = Content.get_recent(recent_limit)

	q = Content.query.filter()
	if recent is not None:
	    q.filter(~ Content.id.in_(c.id for c in recent))

	c = q.order_by(Content.read_count.desc(),
		       Content.like_count.desc()).limit(count)

	if c.count() > 0:
	    return c.all()

	return None
