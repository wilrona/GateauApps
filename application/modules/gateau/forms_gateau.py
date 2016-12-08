__author__ = 'Ronald'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators
from models_gateau import Produit, PrixGateaux, Param
from lib.flaskext.wtf.html5 import NumberInput


def unique_code_validator(form, field):
    code_unique = Produit.query(
        Produit.name == field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError('Ce nom est deja utilise.')
        else:
            code = Produit.get_by_id(int(form.id.data))
            if code.name != field.data:
                raise wtf.ValidationError('Ce nom est deja utilise.')


class FormGateau(wtf.Form):
    id = wtf.HiddenField()
    name = wtf.StringField(label='Nom du gateau :',  validators=[validators.Required(message='Champs obligatoire'), validators.length(max=50), unique_code_validator])
    prix = wtf.StringField(label='Prix Minimum :', widget=NumberInput(), validators=[validators.Required(message='Prix obligatoire')])
    category = wtf.StringField(label=' Categorie', validators=[validators.Required('Champs obligatoire')])
    part = wtf.StringField(label='Nombre de part', validators=[validators.Required('Champs obligatoire')])


class FormAutre(wtf.Form):
    id = wtf.HiddenField()
    name = wtf.StringField(label='Nom du produit :',  validators=[validators.Required(message='Champs obligatoire'), validators.length(max=50), unique_code_validator])
    prix = wtf.StringField(label='Prix :', widget=NumberInput(), validators=[validators.Required(message='Prix obligatoire')])


def compare_part_interval(form, field):

    code_send = Param.get_by_id(int(field.data))
    code_unique = PrixGateaux.query(
        PrixGateaux.categorie_id == code_send.key
    )
    if code_unique:
        same_param = PrixGateaux.query(
            PrixGateaux.interval == form.interval.data,
            PrixGateaux.categorie_id == code_send.key
        ).get()
        if not form.id.data:
            if same_param:
                raise wtf.ValidationError('Cette categorie avec cet interval de part existe deja.')
        else:
            code = PrixGateaux.get_by_id(int(form.id.data))
            if same_param != code:
                raise wtf.ValidationError('Cette categorie avec cet interval de part existe deja.')


class FormPrixGateaux(wtf.Form):
    id = wtf.HiddenField()
    interval = wtf.StringField(label='Nombre de part :', validators=[validators.Required(message='Champ obligatoire')])
    prix = wtf.StringField(label='Prix Minimum :', widget=NumberInput(), validators=[validators.Required(message='Champ obligatoire')])
    categorie = wtf.SelectField(label='Votre categorie :', coerce=int, validators=[validators.Required(message='Champ obligatoire'), compare_part_interval])