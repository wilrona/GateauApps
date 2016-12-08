__author__ = 'wilrona'

from ...modules import *
from application import login_manager
from models_user import Users, UserRole, Roles, ndb
from ..profil.models_profil import Profil, ProfilRole
from forms_user import FormUser, FormLogin, FormPassword

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('user', __name__)
prefix_param = Blueprint('user_param', __name__)
prefix_home = Blueprint('home', __name__)


@login_manager.user_loader
def load_user(userid):
    return Users.get_by_id(userid)


@prefix_home.route('/', methods=['POST', 'GET'])
def index():

    account_admin = 'admin@creativeCake'
    pass_admin = hashlib.sha224('password@creativeCake').hexdigest()

    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    admin_role = Roles.query(
        Roles.valeur == 'super_admin'
    ).get()

    exist_super_admin = 0
    exist = False
    if admin_role:
        exist_super_admin = UserRole.query(
            UserRole.role_id == admin_role.key
        ).count()

    if exist_super_admin >= 1:
        exist = True

    form = FormLogin(request.form)

    if form.validate_on_submit():
        try:
            password = hashlib.sha224(form.password.data).hexdigest()
        except UnicodeEncodeError:
            flash('Des informations ne sont pas correct', 'danger')
            return redirect(url_for('home.index'))

        user_login = Users.query(
            ndb.OR(
                Users.email == form.email.data,
                Users.login == form.email.data,
            ),
            Users.password == password
        ).get()

        if user_login is None:
            if account_admin == form.email.data and pass_admin == password:

                role_user = Roles()
                role_user.valeur = 'super_admin'
                insert_role = role_user.put()

                user_login = Users()
                user_login.login = account_admin
                user_login.password = pass_admin
                user_login.name = 'Super Administrateur'
                user_login.is_enabled = True
                insert_user = user_login.put()

                user_role = UserRole()
                user_role.role_id = insert_role
                user_role.user_id = insert_user
                user_role.put()

                flash('Compte de l\'administrateur configure avec succes', 'success')
                return redirect(url_for('home.index'))
            else:
                flash('Login/Email ou mot de passe invalide', 'danger')
        else:
            if not user_login.is_active():
                flash('Votre compte est desactive. Contactez l\'administrateur', 'danger')
                return redirect(url_for('home.index'))

            #implementation de l'heure local
            time_zones = pytz.timezone('Africa/Douala')
            date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

            session['user_id'] = user_login.key.id()
            session['commande'] = []
            user_login.logged = True
            user_login.date_last_logged = function.datetime_convert(date_auto_nows)
            this_login = user_login.put()

            if current_user.has_roles([('super_admin', 'dashboard')]):
                return redirect(url_for('dashboard.index'))
            else:
                return redirect(url_for('commande.index'))

    return render_template('user/login.html', **locals())


@prefix.route('/logout')
def logout():
    change = None

    if 'user_id' in session:
        UserLogout = Users.get_by_id(int(session.get('user_id')))
        UserLogout.logged = False
        change = UserLogout.put()

    if change:
        session.pop('user_id')

    return redirect(url_for('home.index'))



@prefix_param.route('/user')
@login_required
@roles_required([('super_admin', 'user')])
def index():
    menu = 'parametre'
    submenu = 'user'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    users = Users.query(Users.login != 'admin@creativeCake', Users.client == False)

    if search:

        list_user = []
        for user in users:

            data_user = user.name
            search_function = function.find(data_user.lower(), q)
            if search_function:
                list_user.append(user)

        users = list_user

        pagination = Pagination(css_framework='bootstrap3', page=page, total=len(users), search=search, record_name='Commandes')

        if len(users) > 10:
            offset_start = (page - 1) * 10
            offset_end = page * 10
            users = users[offset_start:offset_end]

    else:

        pagination = Pagination(css_framework='bootstrap3', page=page, total=users.count(), search=search, record_name='users')

        if users.count() > 10:
            if page == 1:
                offset = 0
            else:
                page -= 1
                offset = page * 10
            users = users.fetch(limit=10, offset=offset)

    return render_template('user/index.html', **locals())



@prefix_param.route('/user/edit',  methods=['GET', 'POST'])
@prefix_param.route('/user/edit/<int:user_id>',  methods=['GET', 'POST'])
@login_required
def edit(user_id=None):

    if user_id:
        users = Users.get_by_id(user_id)
        form = FormUser(obj=users)
        form.id.data = user_id
        form.profil.data = users.profil_id.id()
    else:
        users = Users()
        form = FormUser()

    form.client.data = 0

    form.profil.choices = [(0, 'Selectionnez un profil')]
    for choice in Profil.query():
        profilRole = ProfilRole.query(ProfilRole.profil_id == choice.key).count()
        if profilRole:
            form.profil.choices.append((choice.key.id(), choice.name))

    success = False
    if form.validate_on_submit():

        profil = None
        if form.profil.data:

            profil = Profil.get_by_id(int(form.profil.data))

            if users.profil_id and users.profil_id != profil.key and user_id:
                role_del = ProfilRole.query(
                    ProfilRole.profil_id == users.profil
                )

                for role_del in role_del:
                    remove_role = UserRole.query(
                        UserRole.role_id == role_del.role_id,
                        UserRole.user_id == users.key
                    ).get()

                    remove_role.key.delete()

            users.profil_id = profil.key

        users.name = form.name.data
        users.phone = form.phone.data
        users.email = form.email.data
        users.login = form.login.data


        from random import choice
        from string import digits

        code = list()
        for i in range(5):
            code.append(choice(digits))

        users.pin = int(''.join(code))

        UserCreate = users.put()


        if form.profil.data:
            all_role = ProfilRole.query(
                    ProfilRole.profil_id == profil.key
            )

            # insertion de chaque role a l'utilisateur cree
            UserCreate = Users.get_by_id(UserCreate.id())

            for role in all_role:
                UserRoles = UserRole()
                UserRoles.role_id = role.role_id
                UserRoles.user_id = UserCreate.key
                UserRoles.edit = role.edit
                UserRoles.delete = role.delete
                UserRoles.put()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('user/edit.html', **locals())


@prefix_param.route('/user/edit_password/<int:user_id>',  methods=['GET', 'POST'])
def password(user_id):

    users = Users.get_by_id(user_id)
    form = FormPassword()

    success = False
    if form.validate_on_submit():

        users.password = hashlib.sha224(form.password.data).hexdigest()
        users.put()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('user/password.html', **locals())

@prefix_param.route('/user/active/<int:user_id>',  methods=['GET', 'POST'])
def active(user_id):

    users = Users.get_by_id(user_id)

    if users.is_active():
        users.is_enabled = False
    else:
        users.is_enabled = True

    users.put()
    flash('Enregistement effectue avec succes', 'success')
    return redirect(url_for('user_param.index'))

@prefix_param.route('/user/pin/<int:user_id>',  methods=['GET', 'POST'])
def random(user_id):

    users = Users.get_by_id(user_id)

    from random import choice
    from string import digits

    code = list()
    for i in range(4):
        code.append(choice(digits))

    users.pin = int("".join(code))


    users.put()
    flash('Enregistement effectue avec succes', 'success')
    return redirect(url_for('user_param.index'))



@prefix_param.route('/user/permission/<int:user_id>', methods=['GET', 'POST'])
@login_required
def permission(user_id):

    user = Users.get_by_id(user_id)

    # liste des roles lie a l'utiliasteur en cours
    attrib = UserRole.query(
        UserRole.user_id == user.key
    )
    attrib_list = [role.role_id.get().key.id() for role in attrib]

    # liste des roles lie a l'utiliasteur en cours avec le droit d'edition
    edit = UserRole.query(
        UserRole.user_id == user.key,
        UserRole.edit == True
    )
    edit_list = [role.role_id.get().key.id() for role in edit]

    # liste des roles lie a l'utiliasteur en cours avec le droit de suppression
    delete = UserRole.query(
        UserRole.user_id == user.key,
        UserRole.delete == True
    )
    delete_list = [role.role_id.get().key.id() for role in delete]


    liste_role = []
    data_role = Roles.query(
        Roles.valeur != 'super_admin'
    )

    for role in data_role:
        if not role.parent:
            module = {}
            module['titre'] = role.titre
            module['id'] = role.key.id()
            enfants = Roles.query(
                Roles.parent == role.key
            )
            module['role'] = []
            for enfant in enfants:
                rol = {}
                rol['id'] = enfant.key.id()
                rol['titre'] = enfant.titre
                rol['action'] = enfant.action
                module['role'].append(rol)
            liste_role.append(module)

    # liste des profils de l'application
    list_profil = Profil.query(
        Profil.active == True
    )
    # and current_user.has_roles([('super_admin', 'user_permission')], ['edit'])
    success = False
    if request.method == 'POST':

        form_attrib = request.form.getlist('attrib')

        # if not form_attrib and attrib_list:
        #     flash('Les utilisateurs ne doivent pas exister sans permission dans l\'application', 'warning')
        #     return redirect(url_for('user_param.permission', user_id=user_id))
        # elif form_attrib:
        #     user.is_enabled = True
        #     user.put()

        form_edit = request.form.getlist('edit')
        form_delete = request.form.getlist('delete')

        # liste des roles lie au profil et supprimer ce qui ne sont plus attribue
        current_profil_role = UserRole.query(
            UserRole.user_id == user.key
        )
        for current in current_profil_role:
            if current.role_id.get().key.id() not in form_attrib:
                current.key.delete()

        # Insertion des roles et authorisation en provenance du formulaire
        for attrib in form_attrib:

            role_form = Roles.get_by_id(int(attrib))

            profil_role_exist = UserRole.query(
                UserRole.role_id == role_form.key,
                UserRole.user_id == user.key
            ).get()

            if profil_role_exist:
                if attrib in form_edit:
                    profil_role_exist.edit = True
                else:
                    profil_role_exist.edit = False

                if attrib in form_delete:
                    profil_role_exist.delete = True
                else:
                    profil_role_exist.delete = False

                profil_role_exist.put()
            else:
                profil_role_create = UserRole()
                profil_role_create.role_id = role_form.key
                profil_role_create.user_id = user.key
                if attrib in form_edit:
                    profil_role_create.edit = True
                else:
                    profil_role_create.edit = False

                if attrib in form_delete:
                    profil_role_create.delete = True
                else:
                    profil_role_create.delete = False

                profil_role_create.put()

        success = True
        flash('Enregistement effectue avec succes', 'success')

    return render_template('user/permission.html', **locals())

