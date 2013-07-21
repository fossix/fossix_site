"""
This file is where we put all view information which is operated when a user is
already logged in or for logging in/out.
"""

from flask import Module, render_template, request, session, g, redirect, \
    url_for, flash, Blueprint
from fossix.utils import render_page, get_uniqueid, redirect_url, \
    redirect_back, is_safe_url
from fossix.forms import OpenID_LoginForm, ProfileEdit_Form
from fossix.extensions import oid
from fossix.models import User, Keywords, Identity, fdb as db
from flask.ext.login import login_user, logout_user, \
    login_required, fresh_login_required, confirm_login
from flask.ext.classy import FlaskView

account = Blueprint('account', __name__)

@oid.after_login
def create_or_login(resp):
    session['openid'] = resp.identity_url
    user = None
    identity = db.session.query(Identity).filter_by(url=resp.identity_url).first()
    if identity:
	user = db.session.query(User).get(identity.user_id)

    if user is not None:
	if g.user.is_authenticated():
	    confirm_login()
        g.user = user
	login_user(user, remember=True)
	flash(u'Successfully signed in')
	return redirect_back('main.MainView:index')

    return redirect(url_for('account.ProfileView:create', next=oid.get_next_url(),
                            name=resp.fullname or resp.nickname,
                            email=resp.email))

class LoginView(FlaskView):
    @oid.loginhandler
    def index(self):
	if g.user.is_authenticated():
	    return redirect(url_for('main.MainView:index'))

	login_form = OpenID_LoginForm(next=request.args.get("next"))
	return render_template("account/login.html", form=login_form,
			       error = oid.fetch_error())

    def post(self):
	login_form = OpenID_LoginForm()
	if login_form.validate_on_submit():
	    openid = request.form.get('openid')
	    if openid:
		return oid.try_login(openid,
				     ask_for=['email', 'fullname', 'nickname'])

	else:
	    return render_template("account/login.html", form=login_form,
				   error = oid.fetch_error())

    def logout(self):
	session.pop('openid', None)
	logout_user()
	flash(u'You were signed out')
	return redirect(oid.get_next_url())

class ProfileView(FlaskView):
    @login_required
    def index(self):
	return self.get(g.user.username)

    def get(self, username):
	if username:
	    u = db.session.query(User).filter(User.username == username)
	    if u.count() > 0:
		u = u.one()
	    else:
		flash('No user named ' + username)
		return redirect(url_for('content.ContentView:index'))
	elif g.user.is_authenticated():
	    u = g.user

	return render_template('account/profile.html', user=u)

    def create(self):
	form = ProfileEdit_Form(next=oid.get_next_url())
	form.fullname.data=request.args.get('name')
	form.email.data=request.args.get('email')
	form.username.data=get_uniqueid()
	if g.user is not None and g.user.is_authenticated() or 'openid' not in session:
	    return redirect(url_for('main.MainView:index'))

	return render_template('account/create_profile.html', form=form)

    def post(self):
	if g.user.is_authenticated():
	    return self.update_profile()
	else:
	    return self.create_profile()

    def create_profile(self):
	form = ProfileEdit_Form()
	if form.validate_on_submit():
	    user = User()
	    form.populate_obj(user)
	    identity = Identity()
	    db.session.add(user)
	    db.session.commit()

	    identity.url = session['openid']
	    user.identity.append(identity)
	    db.session.commit()

	    flash(u'Profile created')
	    login_user(user, False)
	    return redirect(oid.get_next_url())

	return render_template('account/create_profile.html', form=form)

    def update_profile(self):
	form = ProfileEdit_Form()
	user = g.user
	if form.validate_on_submit():
	    form.populate_obj(user)
	    db.session.add(user)
	    db.session.commit()
	    flash("Profile updated")
	    return redirect_back('main.MainView:index')

	return render_template('account/edit_profile.html', form=form)

    @fresh_login_required
    def edit(self):
	form = ProfileEdit_Form(obj=g.user)
	form.next.data = redirect_url()
	return render_template('account/edit_profile.html', form=form)


# Register all classy views
LoginView.register(account)
ProfileView.register(account)
