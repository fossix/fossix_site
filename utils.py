from fossix.extensions import cache
from flask import g
import functools

cached = functools.partial(cache.cached,
                           unless= lambda: g.user is not None)
