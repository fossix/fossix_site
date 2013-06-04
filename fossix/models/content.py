from fossix.models import fdb as db
from datetime import datetime
from sqlalchemy import func, text, and_, Table, Column, Integer, ForeignKey, \
    and_, ForeignKeyConstraint
from sqlalchemy.orm import relationship, backref
from fossix.models import User
from flask import g

# This table contains keywords that are tagged in articles
class Keywords(db.Model):
    __table__ = db.metadata.tables['keywords']

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

tags_assoc = Table('tags_assoc', db.metadata, autoload=True)

class ContentMeta(db.Model):
    __table__ = db.metadata.tables['content_meta']

    author = relationship(User, innerjoin=True, lazy="joined")


class ContentVersions(db.Model):
    __table__ = db.metadata.tables['content_versions']

    modifier = relationship(User, innerjoin=True, lazy="joined")
    meta = relationship(ContentMeta, innerjoin=True, lazy="joined")
    tags = relationship(Keywords, secondary=tags_assoc,
			lazy=True, backref='content_versions')


class Content(db.Model):
    __table__ = Table(
	'content', db.metadata,
	Column('id', Integer, primary_key=True),
	Column('version', Integer),
	Column('author_id', Integer, ForeignKey('users.id')),
	Column('modifier_id', Integer, ForeignKey('users.id')),
	autoload=True, extend_existing=True
    )

    __table_args__ = (
	ForeignKeyConstraint(
	    ['id', 'version'],
	    ['content_versions.id', 'content_versions.version']),
    )
    author = relationship(User, primaryjoin='Content.author_id == User.id')
    modifier = relationship(User, primaryjoin='Content.modifier_id == User.id')

    def __init__(self, state, modifier, category):
	self.state = state
	self.modifier_id = modifier
	self.category = category

    def __repr_(self):
        return 'id: %r\ntitle: %r\ndate:%r' % (self.id, self.title, self.create_date)

    def inc_read_count(self):
	cm = db.session.query(ContentMeta).get(self.id)
	if cm is not None:
	    cm.read_count = cm.read_count + 1
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

    def set_tags_csv(self, value):
	current = self.history.tags
	new = (x for x in value.strip().split(','))
	self.history.tags = []
	for tag in new:
	    if len(tag):
		self.tags.append(db.session.query(Keywords).get(tag.strip()))
	pass

    tags_csv = property(get_tags_csv, set_tags_csv)

    def save(self):
	db.session.add(self)
	db.session.commit()
	print self.id, self.version

    @staticmethod
    def get_recent(count = 5):
	c = db.session.query(Content).order_by(Content.create_date.desc()).limit(count)
	if c.count() > 0:
	    return c.all()

	return None

    @staticmethod
    def get_popular(count = 5, exclude_recent = True, recent_limit = 5):
	recent = None
	if exclude_recent:
	    recent = Content.get_recent(recent_limit)

	q = db.session.query(Content).filter()
	if recent is not None:
	    q.filter(~ Content.id.in_(c.id for c in recent))

	c = q.order_by(Content.read_count.desc(),
		       Content.like_count.desc()).limit(count)

	if c.count() > 0:
	    return c.all()

	return None
