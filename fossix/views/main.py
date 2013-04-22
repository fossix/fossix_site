from flask import Module, render_template, flash
from fossix.utils import cached, render_page

main = Module(__name__)

#@cached()
@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html')
