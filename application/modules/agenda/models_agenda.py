__author__ = 'Ronald'

from google.appengine.ext import ndb
from oauth2client.contrib.appengine import CredentialsProperty


class Calandar(ndb.Model):
    token = ndb.TextProperty()
    agendaID = ndb.StringProperty()
    email_user = ndb.StringProperty(repeated=True)