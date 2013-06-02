from fossix.models import fdb as db
from datetime import datetime
from hashlib import md5
from sqlalchemy import Table

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
	return '<User %r>' % (self.username)

    def avatar(self, size):
	return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() \
	    + '?d=mm&s=' + str(size)

    def is_admin(self):
	if self.id == 1 or self.role == self.ADMIN:
	    return True

	return False

    def is_moderator(self):
	# or I should be a moderator to edit
	return self.is_admin() or self.role >= self.MODERATOR

    def is_author(self, content):
	if content:
	    # check if the user is the owner
	    if content.author_id == self.id:
		return True

	return False

    def is_editor(self, content = None):
	return self.is_author(content) or self.is_moderator()
