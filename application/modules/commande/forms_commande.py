__author__ = 'Ronald'


from lib.flaskext import wtf
from lib.flaskext.wtf import validators
from lib.flaskext.wtf.html5 import NumberInput
from application import function
import datetime
from lib.pytz.gae import pytz

time_zones = pytz.timezone('Africa/Douala')
date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")


def current_date(form, field):
    date = function.date_convert(field.data)
    if datetime.date.today() > date and not form.update.data:
        raise wtf.ValidationError('La date de livraison doit etre superieur ou egale a la date d\'aujourd\'huit.')


def current_time(form, field):
    time = function.time_convert(field.data)
    if function.date_convert(form.date_livre.data) == datetime.date.today():
        if function.datetime_convert(date_auto_nows).time() > time:
            raise wtf.ValidationError('l\'heure de livraison doit etre superieur a l\'heure en cours')


def concerne_existe(form, field):
    if form.exixt_at_date.data != '0':
        if not field.data:
            raise wtf.ValidationError('Information Obligatoire')



def date_anniv_existe(form, field):
    if form.exixt_at_date.data != '0':
        if not field.data:
            raise wtf.ValidationError('Information Obligatoire')
        # date = function.date_convert(field.data)
        # if date.year != datetime.date.year:
        #     raise wtf.ValidationError('La date a ete mal renseigne')



class FormCommande(wtf.Form):
    event = wtf.StringField(label='Selectionnez un evenement', validators=[validators.Required('Information Obligatoire')])
    date_livre = wtf.StringField(label='Date de livraison', validators=[validators.Required('Date obligatoire')])
    heure_livre = wtf.StringField(label='Heure de livraison', validators=[validators.Required('Date obligatoire'), current_time])
    date_anniv = wtf.StringField(label='Date d\'anniversaire', default=datetime.date.today().strftime("%d/%m/%Y"), validators=[date_anniv_existe])
    age = wtf.StringField(label='Age ', validators=[validators.Required('Information Obligatoire')])
    theme = wtf.StringField(label='Theme :', validators=[validators.Required('Information Obligatoire')])
    concerne = wtf.StringField(label='Concerne :', validators=[concerne_existe])
    exixt_at_date = wtf.HiddenField(default='0')
    info = wtf.TextAreaField(label='Autres infos pour la livraison:')
    update = wtf.BooleanField(default=False)