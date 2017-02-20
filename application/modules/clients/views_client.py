__author__ = 'Ronald'

from ...modules import *
from ..user.models_user import Users
from ..user.forms_user import FormUser
# from ..commande.models_commande import Commande

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('clients', __name__)


@prefix.route('/')
@login_required
@roles_required([('super_admin', 'client')])
def index():
    menu = 'client'
    submenu = 'list'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1



    datas = Users.query(Users.client == True)

    if search:

        list_user = []
        for user in datas:

            data_user = user.name
            search_function = function.find(data_user.lower(), q)
            if search_function:
                list_user.append(user)

        datas = list_user

        pagination = Pagination(css_framework='bootstrap3', page=page, total=len(datas), search=search, record_name='Commandes')

        if len(datas) > 10:
            offset_start = (page - 1) * 10
            offset_end = page * 10
            datas = datas[offset_start:offset_end]

    else:

        pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='Clients')
        if datas.count() > 10:
            if page == 1:
                offset = 0
            else:
                page -= 1
                offset = page * 10
            datas = datas.fetch(limit=10, offset=offset)

    return render_template('client/index.html', **locals())


@prefix.route('/edit',  methods=['GET', 'POST'])
@prefix.route('/edit/<int:client_id>',  methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'client'), ['edit']])
def edit(client_id=None):

    from ..profil.models_profil import Profil, ProfilRole

    if client_id:
        users = Users.get_by_id(client_id)
        form = FormUser(obj=users)
        form.id.data = client_id
    else:
        users = Users()
        form = FormUser()

    form.client.data = 1

    form.profil.choices = [(0, 'Selectionnez un profil')]

    success = False
    if form.validate_on_submit():

        users.name = form.name.data
        users.phone = form.phone.data
        users.email = form.email.data
        users.client = True
        users.put()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('user/edit.html', **locals())


@prefix.route('/delete/<int:client_id>')
@login_required
def delete(client_id):

    from ..commande.models_commande import Commande

    client = Users.get_by_id(client_id)

    commande_client = Commande.query(
        Commande.user == client.key
    ).count()

    if not commande_client:
        client.key.delete()
        flash('Suppression reussie', 'success')
    else:
        flash('Ce client possede des commandes dans l\'application', 'warning')

    return redirect(url_for('clients.index'))

