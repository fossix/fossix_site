from fossix.models import fdb as db

# This table contains keywords that are tagged in articles
class Keywords(db.Model):
    __table__ = db.metadata.tables['keywords']

    @staticmethod
    def get(k):
	obj = db.session.query(Keywords).filter(Keywords.keyword == k).first()
	if not obj:
	    obj = Keywords(k)

	return obj

    def __init__(self, k):
        self.keyword = k

    def __repr__(self):
        return '%s' % self.keyword
