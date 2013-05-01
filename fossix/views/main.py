from flask import Module, render_template, flash
from fossix.utils import cached, render_page
from fossix.models import Content

main = Module(__name__)

#@cached()
@main.route('/')
@main.route('/index')
def index():
    c = Content.get_recent(5)
    p = Content.get_popular(5, False)
    return render_template('index.html', recent=c, popular=p)

@main.route('/syntax')
def show_md_syntax():
    return "Here will come the syntax page"
