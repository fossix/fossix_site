from fossix.extensions import fdb as db
from datetime import datetime

class User(db.Model):
    # user roles
    USER = 10
    MEMBER = 20
    MODERATOR = 30
    ADMIN = 100

    # __bind_key__ = 'user'
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), index = True, unique = True, nullable=False)
    fullname = db.Column(db.String(32))
    email = db.Column(db.String(150), unique = True, nullable = False)
    openid = db.Column(db.String(256), index  = True, unique = True)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.SmallInteger, default = USER)
    karma = db.Column(db.Integer, default = 0)
    receive_email = db.Column(db.Boolean, default=False)
    email_alerts = db.Column(db.Boolean, default=False)
    #posts = db.relationship('Content', backref = 'author', lazy = 'dynamic')
