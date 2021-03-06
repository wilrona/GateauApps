__author__ = 'wilrona'

from google.appengine.ext import ndb
from ..role.models_role import Roles
from ..profil.models_profil import Profil


class Users(ndb.Model):

    date_create = ndb.DateTimeProperty(auto_now=True)
    login = ndb.StringProperty()
    password = ndb.StringProperty()

    is_enabled = ndb.BooleanProperty(default=False)
    name = ndb.StringProperty()
    email = ndb.StringProperty(default=None)
    phone = ndb.StringProperty()
    logged = ndb.BooleanProperty(default=False)
    date_last_logged = ndb.DateTimeProperty()
    profil_id = ndb.KeyProperty(kind=Profil)

    client = ndb.BooleanProperty(default=False)
    pin = ndb.IntegerProperty()

    def is_active(self):
        return self.is_enabled

    def is_authenticated(self):
        return self.logged

    def is_anonymous(self):
        return False

    def full_name(self):
        full_name = ''+str(self.name)+''
        return full_name

    def has_roles(self, requirements, accesibles=None):

        user_role = UserRole.query(
            UserRole.user_id == self.key
        )

        user_roles = [role.role_id.get().valeur for role in user_role]

        # has_role() accepts a list of requirements
        for requirement in requirements:
            if isinstance(requirement, (list, tuple)):
                # this is a tuple_of_role_names requirement
                tuple_of_role_names = requirement
                authorized = False
                for role_name in tuple_of_role_names:
                    if role_name in user_roles:
                        # tuple_of_role_names requirement was met: break out of loop
                        authorized = True

                        if accesibles and role_name != 'super_admin':
                            role = Roles.query(
                                Roles.valeur == role_name
                            ).get()

                            role_user = UserRole.query(
                                UserRole.user_id == self.key,
                                UserRole.role_id == role.key
                            ).get()

                            for accesible in accesibles:
                                if accesible == 'edit' and not role_user.edit:
                                    authorized = False
                                    break
                                if accesible == 'delete' and not role_user.delete:
                                    authorized = False
                                    break
                        else:
                            break
                if not authorized:
                    return False                    # tuple_of_role_names requirement failed: return False
                else:
                    return True
            else:
                # this is a role_name requirement
                role_name = requirement

                # the user must have this role
                if not role_name in user_roles:
                    return False                    # role_name requirement failed: return False
                else:
                    if accesibles and role_name != 'super_admin':

                        role = Roles.query(
                                Roles.valeur == role_name
                        ).get()

                        role_user = UserRole.query(
                            UserRole.user_id == self.key,
                            UserRole.role_id == role.key
                        ).get()

                        for accesible in accesibles:
                            if accesible == 'edit' and not role_user.edit:
                                return False
                            if accesible == 'delete' and not role_user.delete:
                                return False

        # All requirements have been met: return True
        return True


class UserRole(ndb.Model):
    user_id = ndb.KeyProperty(kind=Users)
    role_id = ndb.KeyProperty(kind=Roles)
    edit = ndb.BooleanProperty()
    delete = ndb.BooleanProperty()


class Horaire(ndb.Model):
    date_start = ndb.DateProperty()
    montant = ndb.FloatProperty()
    user = ndb.KeyProperty(kind=Users)






