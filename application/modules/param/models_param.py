__author__ = 'Ronald'


from google.appengine.ext import ndb


class Param(ndb.Model):
    name = ndb.StringProperty()
    type_data = ndb.StringProperty()


class TypeGateaux(ndb.Model):
    name = ndb.StringProperty()
    pr_sable = ndb.BooleanProperty(default=False)