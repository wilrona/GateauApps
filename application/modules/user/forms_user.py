__author__ = 'wilrona'

from lib.flaskext import wtf
from lib.flaskext.wtf import validators
from models_user import Users
from ...modules import *


def unique_email_validator(form, field):
    """ email must be unique"""
    user_manager = Users.query(
        Users.email == field.data
    ).count()
    if user_manager >= 1 and field.data:
        if not form.id.data:
            raise wtf.ValidationError('Cette adresse email est deja utilise.')
        else:
            code = Users.get_by_id(int(form.id.data))
            if code.email != field.data:
                raise wtf.ValidationError('Cette adresse email est deja utilise.')


def password_validator(form, field):
        """ Password must have one lowercase letter, one uppercase letter and one digit."""
        # Convert string to list of characters
        password = list(field.data)
        password_length = len(password)

        # Count lowercase, uppercase and numbers
        lowers = uppers = digits = 0
        for ch in password:
            if ch.islower():
                lowers += 1
            if ch.isupper():
                uppers += 1
            if ch.isdigit():
                digits += 1

        # Password must have one lowercase letter, one uppercase letter and one digit
        is_valid = password_length >= 6 and lowers and uppers and digits
        if not is_valid:
            raise wtf.ValidationError('Le mot de passe doit avoir au moin 6 caracteres avec une lettre minuscule, une lettre majuscule et un chiffre')


def password_convert(form, field):
    try:
        password = hashlib.sha224(field.data).hexdigest()
    except UnicodeEncodeError:
        raise wtf.ValidationError('les informations du mode passe ne sont pas correct.')


def execpt_login(form, field):
    if not form.client.data and not field.data:
        raise wtf.ValidationError('Information obligatoire')


def client_id_required(form, field):
    if not form.client.data:
        if not field.data:
            raise wtf.ValidationError('Selection du profil obligatoire.')


class FormLogin(wtf.Form):
    email = wtf.StringField('Email ou login', validators=[validators.Required()])
    password = wtf.PasswordField('Mot de passe', [validators.Required("Le mot de passe est requis.")])
    submit = wtf.SubmitField("Connexion")


class FormUser(wtf.Form):
    id = wtf.HiddenField()
    client = wtf.HiddenField()
    name = wtf.StringField(label='Nom et prenom :', validators=[validators.Required('information obligatoire')])
    phone = wtf.StringField(label='Telephone :', validators=[validators.Required('information obligatoire')])
    email = wtf.StringField(label='Adresse email :')
    login = wtf.StringField(label='login de connexion :', validators=[execpt_login])
    profil = wtf.SelectField(label='Selection d\'un profil :', coerce=int, default=0)


class FormPassword(wtf.Form):
    password = wtf.PasswordField(label='Mot de passe', validators=[validators.Required('Mot de passe obligatoire'), password_validator, password_convert])
    retype_password = wtf.PasswordField(label='Ressaisir le mot de passe', validators=[validators.EqualTo('password', message='Les mots de passe ne sont pas similaires.')])



