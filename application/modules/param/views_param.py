__author__ = 'Ronald'


from ...modules import *
from models_param import Param
from forms_param import FormConfig


cache = Cache(app)
prefix = Blueprint('config', __name__)


@prefix.route('/config/<name_data>')
@login_required
@roles_required([('super_admin', 'categorie', 'couleur_ruban', 'moules', 'coulis', 'imbibages', 'gouts_cremes', 'fourrages', 'couleur_cup', 'topping')])
def index(name_data):
    menu = 'parametre'
    submenu = name_data

    if name_data not in global_config:
        return redirect(url_for('parametre.index'))

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = Param.query(
        Param.type_data == name_data
    )
    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='Types Gateaux')

    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 10
        datas = datas.order(Param.name).fetch(limit=10, offset=offset)
    else:
        datas = datas.order(Param.name)

    return render_template('config/index.html', **locals())


@prefix.route('/config/<name_data>/edit',  methods=['GET', 'POST'])
@prefix.route('/config/<name_data>/edit/<int:data_id>',  methods=['GET', 'POST'])
@login_required
def edit(name_data, data_id=None):

    if data_id:
        datas = Param.get_by_id(data_id)
        form = FormConfig(obj=datas)
        form.id.data = data_id
    else:
        datas = Param()
        form = FormConfig()

    form.type_data.data = name_data

    success = False
    if form.validate_on_submit():

        datas.name = form.name.data
        datas.type_data = form.type_data.data
        datas.put()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('config/edit.html', **locals())


