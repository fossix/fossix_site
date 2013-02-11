from fossix.extensions import cache
from flask import g, render_template
import functools

cached = functools.partial(cache.cached,
                           unless= lambda: g.user is not None)

def render_page(page, title = None, content = None, **kwargs):
    return render_template(page, title = title, content = content, **kwargs)
