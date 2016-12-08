__author__ = 'Ronald'


from google.appengine.ext import ndb
from ..param.models_param import Param


class Produit(ndb.Model):
    name = ndb.StringProperty()
    prix = ndb.FloatProperty()
    type_produit = ndb.IntegerProperty()


class PrixGateaux(ndb.Model):
    interval = ndb.StringProperty()
    prix = ndb.FloatProperty()
    categorie_id = ndb.KeyProperty(kind=Param)




