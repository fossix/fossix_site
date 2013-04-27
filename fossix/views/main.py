from flask import Module, render_template, flash
from fossix.utils import cached, render_page
from fossix.models import Content

main = Module(__name__)

#@cached()
@main.route('/')
@main.route('/index')
def index():
    c = Content.query.all()
    return render_template('index.html', c=c)
