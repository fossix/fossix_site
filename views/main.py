from flask import Module
from fossix.utils import cached

main = Module(__name__)

@cached()
@main.route('/')
@main.route('/index')
def index():
    return "hello, World!"
