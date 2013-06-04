from flask.ext.wtf import Form, HiddenField, TextField, RecaptchaField, \
    SubmitField, ValidationError, required, email, url, validators
from flask.ext.wtf.html5 import URLField, EmailField
from fossix.models import User, fdb as db

class OpenID_LoginForm(Form):
    next = HiddenField()
    openid = URLField("OpenID", validators=
		       [required("You didn't enter a OpenID URL"),
			url("OpenID must be a valid URL")])

    submit = SubmitField("Login")


class ProfileEdit_Form(Form):

    def check_uniqueid(self, field):
	users = db.session.query(User).filter_by(username=field.data)
	if users.count() > 0 and users.first().email != self.email.data:
	    raise validators.ValidationError('Username already exists, please try another')

    next = HiddenField()
    fullname = TextField("Name")
    email = EmailField("Email", validators=
		       [required("You have to provide an email address")])
    username = TextField("Nick Name", validators=[check_uniqueid])
    recaptcha = RecaptchaField()
    submit = SubmitField("Update Profile")
