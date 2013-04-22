# -*- coding: utf-8 -*-
"""
    manage.py
    ~~~~~~~~~

    Description of the module goes here...

    :copyright: (c) 2010 by Dan Jacob.
    :license: BSD, see LICENSE for more details.
"""
import sys
import os

from flask import current_app

from flask.ext.script import Manager, prompt, prompt_pass, \
    prompt_bool, prompt_choices

from fossix import create_app
from fossix.extensions import fdb as db
from fossix.models import User
from migrate.versioning import api

fapp = create_app()
manager = Manager(fapp)

@manager.option('-u', '--username', dest="username", required=False)
@manager.option('-p', '--password', dest="password", required=False)
@manager.option('-e', '--email', dest="email", required=False)
@manager.option('-r', '--role', dest="role", required=False)
def createuser(username=None, password=None, email=None, role=None):
    """
    Create a new user
    """

    if username is None:
        while True:
            username = prompt("Username")
            user = User.query.filter(User.username==username).first()
            if user is not None:
                print "Username %s is already taken" % username
            else:
                break

    if email is None:
        while True:
            email = prompt("Email address")
            user = User.query.filter(User.email==email).first()
            if user is not None:
                print "Email %s is already taken" % email
            else:
                break

    if password is None:
        password = prompt_pass("Password")

        while True:
            password_again = prompt_pass("Password again")
            if password != password_again:
                print "Passwords do not match"
            else:
                break

    roles = (
        (User.MEMBER, "member"),
        (User.MODERATOR, "moderator"),
        (User.ADMIN, "admin"),
    )

    if role is None:
        role = prompt_choices("Role", roles, resolve=int, default=User.MEMBER)

    user = User(username=username,
                email=email,
                password=password,
                role=role)

    db.session.add(user)
    db.session.commit()

    print "User created with ID", user.id


@manager.command
def createall():
    "Creates database tables"

    db.create_all()

    if not os.path.exists(fapp.config['SQLALCHEMY_MIGRATE_REPO']):
	api.create(fapp.config['SQLALCHEMY_MIGRATE_REPO'], 'database repository')
	api.version_control(fapp.config['SQLALCHEMY_DATABASE_URI'], fapp.config['SQLALCHEMY_MIGRATE_REPO'])
    else:
	api.version_control(fapp.config['SQLALCHEMY_DATABASE_URI'], fapp.config['SQLALCHEMY_MIGRATE_REPO'],
			    api.version(fapp.config['SQLALCHEMY_MIGRATE_REPO']))

@manager.command
def dropall():
    "Drops all database tables"

    if prompt_bool("Are you sure ? You will lose all your data !"):
        db.drop_all()

@manager.command
def mailall():
    "Sends an email to all users"

    subject = prompt("Subject")
    message = prompt("Message")
    from_address = prompt("From", default="support@thenewsmeme.com")
    if prompt_bool("Are you sure ? Email will be sent to everyone!"):
        with mail.connect() as conn:
            for user in User.query:
                message = Message(subject=subject,
                                  body=message,
                                  sender=from_address,
                                  recipients=[user.email])

                conn.send(message)
import imp
from migrate.versioning import api

@manager.command
def migratedb():
    "SQLAlchemy database migration"

    migration = fapp.config['SQLALCHEMY_MIGRATE_REPO'] + '/versions/%03d_migration.py' % (api.db_version(fapp.config['SQLALCHEMY_DATABASE_URI'], fapp.config['SQLALCHEMY_MIGRATE_REPO']) + 1)
    tmp_module = imp.new_module('old_model')
    old_model = api.create_model(fapp.config['SQLALCHEMY_DATABASE_URI'], fapp.config['SQLALCHEMY_MIGRATE_REPO'])
    exec old_model in tmp_module.__dict__
    script = api.make_update_script_for_model(fapp.config['SQLALCHEMY_DATABASE_URI'], fapp.config['SQLALCHEMY_MIGRATE_REPO'], tmp_module.meta, db.metadata)
    open(migration, "wt").write(script)
    a = api.upgrade(fapp.config['SQLALCHEMY_DATABASE_URI'], fapp.config['SQLALCHEMY_MIGRATE_REPO'])
    print 'New migration saved as ' + migration
    print 'Current database version: ' + str(api.db_version(fapp.config['SQLALCHEMY_DATABASE_URI'], fapp.config['SQLALCHEMY_MIGRATE_REPO']))

@manager.shell
def make_shell_context():
    return dict(app=current_app,
                db=db,
                Post=Post,
                User=User,
                Tag=Tag,
                Comment=Comment)


manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
