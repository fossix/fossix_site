from fossix.extensions import fdb as db
from datetime import datetime
from sqlalchemy import func
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

ContentTags = db.Table('tags_assoc',
		       db.Column('content_id', db.Integer, db.ForeignKey('content.id')),
		       db.Column('keyword_id', db.Integer, db.ForeignKey('keywords.id')))

class Content(db.Model):

    DRAFT = 10
    REVIEW = 20
    UNPUBLISHED = 30
    PUBLISHED = 40

    ARTICLE = 10
    NEWS = 20

    __table_name__ = 'content'
    id = db.Column(db.Integer, primary_key = True)
    author_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    title = db.Column(db.String(128), index = True, unique = True)
    category = db.Column(db.SmallInteger, nullable = False)
    create_date = db.Column(db.DateTime, nullable = False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable = False)
    like_count = db.Column(db.Integer, default = 0)
    read_count = db.Column(db.Integer, default = 0)
    comment_count = db.Column(db.Integer, default = 0)
    state = db.Column(db.SmallInteger, index = True, nullable = False)
    tags = db.relationship('Keywords', secondary=ContentTags,
			   backref=db.backref('contents', lazy='dynamic'))

    author = db.relation(User, innerjoin=True, lazy="joined")

    def __repr_(self):
        return 'id: %r\ntitle: %r\ndate:%r' % (self.id, self.title, self.create_date)

    def inc_read_count(self):
	self.read_count = self.read_count + 1
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
        return self.state == self.PUBLISHED

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

    @staticmethod
    def get_recent(count = 5):
        c = Content.query.filter(Content.state
				 == Content.REVIEW).order_by(Content.create_date.desc()).limit(count)
	if c.count() > 0:
	    return c.all()

	return None

    @staticmethod
    def get_popular(count = 5, exclude_recent = True, recent_limit = 5):
	recent = None
	if exclude_recent:
	    recent = Content.get_recent(recent_limit)

	q = Content.query.filter(Content.state == Content.REVIEW)
	if recent is not None:
	    q.filter(~ Content.id.in_(c.id for c in recent))

	return q.order_by(Content.read_count.desc(),
			  Content.like_count.desc()).limit(count)
