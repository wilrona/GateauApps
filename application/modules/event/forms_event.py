__author__ = 'Ronald'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators
from models_event import Event


def unique_code_validator(form, field):
    code_unique = Event.query(
        Event.name == field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError('Ce nom est deja utilise.')
        else:
            code = Event.get_by_id(int(form.id.data))
            if code.name != field.data:
                raise wtf.ValidationError('Ce nom est deja utilise.')



class FormEvent(wtf.Form):
    id = wtf.HiddenField()
    name = wtf.StringField(label='Nom event', validators=[validators.Required(message='Champ obligatoire'), validators.length(max=50), unique_code_validator])
    at_date = wtf.BooleanField(label='Avec Date', default=True)