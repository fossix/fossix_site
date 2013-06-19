from fossix.models import fdb as db
from datetime import datetime
from sqlalchemy import func, text, and_, Table, Column, Integer, ForeignKey, \
    and_, ForeignKeyConstraint, select
from sqlalchemy.orm import relationship, backref, column_property, foreign
from fossix.models import User, Keywords
from flask import g

tags_assoc = Table('tags_assoc', db.metadata, autoload=True)

class ContentMeta(db.Model):
    __table__ = db.metadata.tables['content_meta']

    author = relationship(User, innerjoin=True, lazy="joined")


class ContentVersions(db.Model):
    __table__ = db.metadata.tables['content_versions']

    modifier = relationship(User, innerjoin=True, lazy="joined")
    meta = relationship(ContentMeta, innerjoin=True, lazy="joined", backref='history')

    tags = relationship(Keywords, secondary=tags_assoc,
			lazy=True, backref='content_history')

    def get_tags_csv(self):
	return ",".join(x.keyword for x in self.tags)

    def set_tags_csv(self, value):
	new = (x for x in value.strip().split(','))
	self.tags = []
	for tag in new:
	    if len(tag):
		self.tags.append(Keywords.get(tag.strip()))

    tags_csv = property(get_tags_csv, set_tags_csv)


class Content(db.Model):
    __table__ = Table(
	'content', db.metadata,
	Column('id', Integer, primary_key=True),
	Column('version', Integer),
	Column('author_id', Integer, ForeignKey('users.id')),
	Column('modifier_id', Integer, ForeignKey('users.id')),
	Column('refers_to', Integer, ForeignKey('content.id')),
	autoload=True, extend_existing=True
    )

    __table_args__ = (
	ForeignKeyConstraint(
	    ['id', 'version'],
	    ['ContentVersions.id', 'ContentVersions.version']),
    )
    author = relationship(User, primaryjoin='Content.author_id == User.id')
    modifier = relationship(User, primaryjoin='Content.modifier_id == User.id')
    history = relationship(ContentVersions,
			   primaryjoin=
			   foreign(__table__.c.id) == ContentVersions.id)
    tags = relationship(Keywords, secondary=tags_assoc,
			primaryjoin=
			and_(
	    __table__.c.id == foreign(tags_assoc.c.content_id),
	    __table__.c.version == foreign(tags_assoc.c.content_version)),
			secondaryjoin=
			Keywords.id==foreign(tags_assoc.c.keyword_id),
			lazy=True, backref='contents')

    meta = relationship(ContentMeta,
			primaryjoin=foreign(__table__.c.id) == ContentMeta.id)

    comments = relationship('Content', order_by='asc(Content.create_date)')

    def __repr_(self):
        return 'id: %r\ntitle: %r\ndate:%r' % (self.id, self.title, self.create_date)

    def inc_read_count(self):
	self.meta.read_count = self.meta.read_count + 1
	return self.meta.read_count

    def inc_like_count(self):
	self.meta.like_count = self.meta.like_count + 1
	return self.meta.like_count

    def dec_like_count(self):
	self.meta.like_count = self.meta.like_count - 1
	return self.meta.like_count

    def inc_comment_count(self):
	self.meta.comment_count = self.meta.comment_count + 1
	return self.meta.comment_count

    def dec_comment_count(self):
	self.meta.comment_count = self.meta.comment_count - 1
	return self.meta.comment_count

    def get_create_date(self):
	return self.create_date.strftime("%A %d. %B %Y")

    def is_published(self):
	return True

    def get_tags_csv(self):
	return ",".join(x.keyword for x in self.tags)

    def set_tags_csv(self, value):
	current = self.tags
	new = (x for x in value.strip().split(','))
	self.tags = []
	for tag in new:
	    if len(tag):
		self.tags.append(Keywords.get(tag.strip()))

    tags_csv = property(get_tags_csv, set_tags_csv)

    @staticmethod
    def get_recent(count = 5):
	c = db.session.query(Content).filter(Content.category=='article').order_by(Content.create_date.desc()).limit(count)
	if c.count() > 0:
	    return c.all()

	return None

    @staticmethod
    def get_popular(count = 5, exclude_recent = True, recent_limit = 5):
	recent = None
	if exclude_recent:
	    recent = Content.get_recent(recent_limit)

	if recent is None:
	    recent = []
	q = db.session.query(Content).filter(Content.category=='article')
	c = q.filter(~Content.id.in_(c.id for c in recent)).order_by(
	    Content.read_count.desc(),
	    Content.like_count.desc()).limit(count)

	if c.count() > 0:
	    return c.all()

	return None
