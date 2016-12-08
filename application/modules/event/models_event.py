__author__ = 'Ronald'


from google.appengine.ext import ndb


class Event(ndb.Model):
    name = ndb.StringProperty()
    at_date = ndb.BooleanProperty(default=False)


