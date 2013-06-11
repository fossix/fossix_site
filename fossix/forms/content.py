from flask.ext.wtf import Form, HiddenField, TextField, RecaptchaField, \
    SubmitField, ValidationError, email, url, validators, TextAreaField, \
    Field, TextInput

class ContentCreate_Form(Form):
    next = HiddenField()
    tags_csv = HiddenField()
    title = TextField("Title", validators=[validators.required(),
					   validators.Length(max=128)])
    teaser = TextAreaField("Teaser", validators=[validators.required(),
					   validators.Length(max=200)])
    content = TextAreaField("Body", validators=[validators.Required()])
    #recaptcha = RecaptchaField()
    submit = SubmitField("Submit")

class ContentEdit_Form(ContentCreate_Form):
    edit_summary = TextField("Edit Summary",
			     validators=[validators.required(),
					 validators.Length(max=128)])

class Comment_Form(Form):
    content = TextAreaField("Comment", validators=[validators.required(),
						   validators.Length(max=1024)])


class AnonComment_Form(Comment_Form):
    recaptcha = RecaptchaField()
