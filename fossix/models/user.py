from fossix.extensions import fdb as db
from datetime import datetime
from hashlib import md5

class User(db.Model):
    # user roles
    MEMBER = 20
    MODERATOR = 30
    ADMIN = 100

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), index = True, unique = True, nullable=False)
    fullname = db.Column(db.String(32))
    email = db.Column(db.String(150), unique = True, nullable = False)
    openid = db.Column(db.String(256), index  = True, unique = True)
    date_joined = db.Column(db.DateTime)
    role = db.Column(db.SmallInteger, default = MEMBER)
    karma = db.Column(db.Integer, default = 0)
    receive_email = db.Column(db.Boolean, default=False)
    email_alerts = db.Column(db.Boolean, default=False)
    suspended = db.Column(db.Boolean, default=False)

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
