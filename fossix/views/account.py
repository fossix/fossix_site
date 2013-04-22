from flask import Module, render_template, request, session, g, redirect, \
    url_for, flash
from fossix.utils import cached, render_page, get_uniqueid
from fossix.forms import OpenID_LoginForm, ProfileEdit_Form
from fossix.extensions import oid, fdb as db
from fossix.models import User

account = Module(__name__)

@oid.after_login
def create_or_login(resp):
    session['openid'] = resp.identity_url
    user = User.query.filter_by(openid=resp.identity_url).first()
    if user is None:
	# There will be multiple hashes given for the same user, so use email to
	# search for user, rather than the identity_url
	user = User.query.filter_by(email=resp.email).first()
	if user is not None:
	    print "updating openid"
	    user.openid = resp.identity_url
	    flash(u'You already have an account in fossix. I updated your openid')
	    db.session.add(user)
	    db.session.commit()

    if user is not None:
        flash(u'Successfully signed in')
        g.user = user
        return redirect(oid.get_next_url())

    return redirect(url_for('account.create_profile', next=oid.get_next_url(),
                            name=resp.fullname or resp.nickname,
                            email=resp.email))

@account.route('/', methods=("GET", "POST"))
@oid.loginhandler
def login():
    if g.user is not None:
	return redirect(oid.get_next_url())
    login_form = OpenID_LoginForm(next=request.args.get("next"))
    if login_form.validate_on_submit():
	openid = request.form.get('openid')
	if openid:
	    return oid.try_login(openid,
				 ask_for=['email', 'fullname', 'nickname'])

    else:
	login_form.next.data = oid.get_next_url()
	return render_template("account/login.html", form=login_form,
			       error = oid.fetch_error())

@account.route('/create/', methods=['GET', 'POST'])
def create_profile():
    if g.user is not None or 'openid' not in session:
        return redirect(url_for('main.index'))

    form = ProfileEdit_Form(next=oid.get_next_url())
    if form.validate_on_submit():
	user = User()
	user.openid = session['openid']
	form.populate_obj(user)
	db.session.add(user)
	db.session.commit()
	flash(u'Profile successfully created')
	return redirect(oid.get_next_url())

    form.username.data = get_uniqueid()
    print form.username.data
    form.name.data = request.args['name']
    form.email.data = request.args['email']
    return render_template('account/edit_profile.html', form=form)

@account.route('/logout')
def logout():
    session.pop('openid', None)
    flash(u'You were signed out')
    return redirect(oid.get_next_url())
