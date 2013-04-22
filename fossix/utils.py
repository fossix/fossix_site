from fossix.extensions import cache, fdb as db
from fossix.models import User
from flask import g, render_template
import functools

cached = functools.partial(cache.cached,
                           unless= lambda: g.user is not None)

def render_page(page, title = None, content = None, **kwargs):
    return render_template(page, title = title, content = content, **kwargs)

def get_uniqueid():
    last = User.query.order_by(User.id.desc()).first()
    if last is not None:
	return 'penguin'+ str(last.id) + str(1)
    else:
	return 'penguin' + str(1)
