from flask.ext.wtf import Form, HiddenField, TextField, RecaptchaField, \
    SubmitField, ValidationError, required, email, url
from fossix.models import User

class OpenID_LoginForm(Form):
    next = HiddenField()
    openid = TextField("OpenID", validators=
		       [required("You didn't enter a OpenID URL"),
			url("OpenID must be a valid URL")])

    submit = SubmitField("Login")


class ProfileEdit_Form(Form):

    def check_uniqueid(self, field):
	users = User.query.filter_by(username=field.data)
	if users.count() > 0:
	    raise validators.ValidationError('Username already exists, please try another')

    next = HiddenField()
    name = TextField("Name", validators=
		       [required("You have to provide a Name")])
    email = TextField("Email", validators=
		       [required("You have to provide an email address")])
    username = TextField("Nick Name", validators=[check_uniqueid])
