__author__ = 'Ronald'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators
from models_param import TypeGateaux, Param


def unique_code_validator(form, field):
    code_unique = TypeGateaux.query(
        TypeGateaux.name == field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError('Ce nom est deja utilise.')
        else:
            code = TypeGateaux.get_by_id(int(form.id.data))
            if code.name != field.data:
                raise wtf.ValidationError('Ce nom est deja utilise.')


def unique_code_validator_config(form, field):
    code_unique = Param.query(
        Param.name == field.data,
        Param.type_data == form.type_data.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError('Ce nom est deja utilise.')
        else:
            code = Param.get_by_id(int(form.id.data))
            if code.name != field.data:
                raise wtf.ValidationError('Ce nom est deja utilise.')


class FormTypeGateau(wtf.Form):
    id = wtf.HiddenField()
    name = wtf.StringField(label='Nom type gateau', validators=[validators.Required(message='Champ obligatoire'), validators.length(max=50), unique_code_validator])
    pr_sable = wtf.BooleanField(label='Utilise pour produit sable', default=False)


class FormConfig(wtf.Form):
    id = wtf.HiddenField()
    type_data = wtf.HiddenField()
    name = wtf.StringField(label='Nom ', validators=[validators.Required(message='Champ obligatoire'), validators.length(max=50), unique_code_validator_config])
