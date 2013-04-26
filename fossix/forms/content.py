from flask.ext.wtf import Form, HiddenField, TextField, RecaptchaField, \
    SubmitField, ValidationError, email, url, validators, TextAreaField, \
    Field, TextInput

# Taken from the WTForms docs site
class TagListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return u', '.join(self.data)
        else:
            return u''

    def __init__(self, label='', validators=None, remove_duplicates=True,
		 **kwargs):
	self.remove_duplicates = remove_duplicates

    def process_formdata(self, valuelist):
	if valuelist:
	    self.data = [x.strip() for x in valuelist[0].split(',')]
	else:
	    self.data = []

	if self.remove_duplicates:
	    self.data = list(self._remove_duplicates(self.data))

    @classmethod
    def _remove_duplicates(cls, seq):
	"""Remove duplicates in a case insensitive, but case preserving manner"""
	d = {}
	for item in seq:
	    if item.lower() not in d:
		d[item.lower()] = True
		yield item

class ContentCreate_Form(Form):
    next = HiddenField()
    tags_csv = HiddenField()
    title = TextField("Title", validators=[validators.required(), validators.Length(max=128)])
    content = TextAreaField("Body", validators=[validators.Required()])
    recaptcha = RecaptchaField()
    submit = SubmitField("Submit")
