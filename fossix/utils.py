from fossix.extensions import cache
from fossix.models import User, fdb as db
from flask import g, render_template, request, url_for, redirect
from urlparse import urlparse, urljoin
import functools
from string import Template
from datetime import datetime

cached = functools.partial(cache.cached,
                           unless= lambda: g.user is not None)

def render_page(page, title = None, content = None, **kwargs):
    return render_template(page, title = title, content = content, **kwargs)

def get_uniqueid():
    last = db.session.query(User).order_by(User.id.desc()).first()
    if last is not None:
	return 'penguin'+ str(last.id + 1)
    else:
	return 'penguin' + str(1)

def is_safe_url(target):
    if request.referrer == target:
	return 0

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
    if 'next' in request.form:
	target = request.form['next']
    else:
	target = redirect_url()

    if not target or not is_safe_url(target):
	target = url_for(endpoint, **values)

    return redirect(target)

# A tiny filter
#fapp.template_filter('strip_tags')
#def strip_tags():


class DeltaTemplate(Template):
    delimiter = "%"

# custom jinja2 filters
def relative_now(time, fmt=None):
    d = {}
    delta = datetime.now() - time
    days = delta.days
    d["y"], days = divmod(days, 365)
    d["M"], days = divmod(days, 30) # mm.. should we take 28, 30 and 31?
    d["d"] = days
    d["h"], rem = divmod(delta.seconds, 3600)
    d["m"], d["s"] = divmod(rem, 60)

    if fmt is None:
	fmt = ""
	if d["y"]:
	    fmt = fmt + "%y year" + ("s " if d["y"] > 1 else "")
	if d["M"]:
	    fmt = fmt + "%M month" + ("s " if d["M"] > 1 else "")
	if d["d"]:
	    fmt = fmt + "%d day" + ("s " if d["d"] > 1 else "")
	if d["h"] and d["d"] == 0:
	    fmt = fmt + "%h hour" + ("s" if d["h"] > 1 else "")
	if d["m"] and d["h"] == 0:
	    fmt = fmt + "%m minute" + ("s" if d["m"] > 1 else "")
	if d["s"] and d["m"] == 0:
	    fmt = fmt + "%s second" + ("s" if d["s"] > 1 else "")

    t = DeltaTemplate(fmt)
    return t.substitute(**d)
