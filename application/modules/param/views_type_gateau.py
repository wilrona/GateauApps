__author__ = 'Ronald'

from ...modules import *
from models_param import TypeGateaux
from forms_param import FormTypeGateau


cache = Cache(app)
prefix_type_gateau = Blueprint('type_gateau', __name__)


@prefix_type_gateau.route('/type-gateaux')
@login_required
@roles_required([('super_admin', 'type_gateaux')])
def index():
    menu = 'parametre'
    submenu = 'type_gateaux'


    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = TypeGateaux.query()
    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='Types Gateaux')

    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 10
        datas = datas.order(TypeGateaux.name).fetch(limit=10, offset=offset)
    else:
        datas = datas.order(TypeGateaux.name)

    return render_template('typeGateau/index.html', **locals())



@prefix_type_gateau.route('/type-gateaux/edit',  methods=['GET', 'POST'])
@prefix_type_gateau.route('/type-gateaux/edit/<int:data_id>',  methods=['GET', 'POST'])
@login_required
def edit(data_id=None):

    if data_id:
        datas = TypeGateaux.get_by_id(data_id)
        form = FormTypeGateau(obj=datas)
        form.id.data = data_id
    else:
        datas = TypeGateaux()
        form = FormTypeGateau()

    success = False
    if form.validate_on_submit():

        datas.name = form.name.data
        datas.pr_sable = form.pr_sable.data
        datas.put()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('typeGateau/edit.html', **locals())


@prefix_type_gateau.route('/type-gateaux/delete/<int:data_id>')
@login_required
def delete(data_id):
    events = TypeGateaux.get_by_id(data_id)
    events.key.delete()
    flash('Suppression reussie', 'success')
    return redirect(url_for('type_gateau.index'))