from fossix.extensions import cache, fdb as db
from fossix.models import User
from flask import g, render_template, request, url_for, redirect
from urlparse import urlparse, urljoin
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

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
	ref_url.netloc == test_url.netloc

def redirect_url():
    for target in request.values.get('next'), request.referrer:
        if not target:
	    continue
        if is_safe_url(target):
	    return target

def redirect_back(endpoint, **values):
    target = request.form['next']
    if not target or not is_safe_url(target):
	target = url_for(endpoint, **values)
    return redirect(target)
