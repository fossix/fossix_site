from fossix.models import fdb as db
from datetime import datetime
from hashlib import md5
from sqlalchemy import Table

class Identity(db.Model):
    __table__ = Table('identity', db.metadata, autoload=True)

class User(db.Model):
    __table__ = Table('users', db.metadata, autoload=True)

    def is_authenticated(self):
	return True

    def is_anonymous(self):
	return False

    def is_active(self):
	return not self.suspended

    def get_id(self):
	return unicode(self.id)

    def __repr__(self):
	return self.username

    def avatar(self, size):
	return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() \
	    + '?d=mm&s=' + str(size)

    def is_super(self):
	return self.role == 'superuser'

    def is_admin(self):
	return self.is_super or self.role == 'administrator'

    def is_moderator(self):
	# or I should be a moderator to edit
	return self.is_admin() or self.role in ('moderator', 'superuser')

    def is_author(self, content):
	if content:
	    # check if the user is the owner
	    if content.author_id == self.id:
		return True

	return False

    def is_editor(self, content = None):
	return self.is_author(content) or self.is_moderator()
