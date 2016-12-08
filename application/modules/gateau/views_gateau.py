__author__ = 'Ronald'

from ...modules import *
from models_gateau import PrixGateaux, Produit, Param
from forms_gateau import FormPrixGateaux



cache = Cache(app)
prefix = Blueprint('gateau', __name__)

@prefix.route('/')
@login_required
@roles_required([('super_admin', 'produit')])
def index():
    menu = 'gateau'
    submenu = 'list_gateau'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    for key, value in global_listes_gateaux.iteritems():
        exist_product = Produit.query(Produit.name == value).count()
        if not exist_product:
            product = Produit()
            product.name = value
            product.prix = 0.0
            product.type_produit = int(key)
            product.put()

    datas = Produit.query()
    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='Produits')

    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 10
        datas = datas.fetch(limit=10, offset=offset)

    return render_template('gateau/index.html', **locals())




@prefix.route('/produit/edit/<int:gateau_id>',  methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'gateau'), ['edit']])
def edit(gateau_id):

    gateau = Produit.get_by_id(gateau_id)

    success = False
    if request.method == 'POST':
        if float(request.form['prix']) > 0:
            gateau.prix = float(request.form['prix'])
            gateau.put()

            flash('Enregistement effectue avec succes', 'success')
            success = True

    return render_template('gateau/edit.html', **locals())


# @prefix.route('/gateau/edit',  methods=['GET', 'POST'])
# @prefix.route('/gateau/edit/<int:gateau_id>',  methods=['GET', 'POST'])
# @login_required
# @roles_required([('super_admin', 'gateau'), ['edit']])
# def edit(gateau_id=None):
#
#     if gateau_id:
#         gateau = Gateau.get_by_id(gateau_id)
#         form = FormGateau(obj=gateau)
#         form.id.data = gateau_id
#     else:
#         gateau = Gateau()
#         form = FormGateau()
#
#     liste_category = global_categorie
#     list_part = global_part
#
#     success = False
#     if form.validate_on_submit():
#
#         gateau.name = form.name.data
#         gateau.prix = float(form.prix.data)
#         gateau.category = form.category.data
#         gateau.part = form.part.data
#         gateau.gateau = True
#         gateau.put()
#
#         flash('Enregistement effectue avec succes', 'success')
#         success = True
#
#     return render_template('gateau/edit.html', **locals())



@prefix.route('/prix-gateaux')
@login_required
@roles_required([('super_admin', 'prix_gateaux')])
def param_price():
    menu = 'gateau'
    submenu = 'prix_gateau'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    list_part = global_part

    datas = PrixGateaux.query()
    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='Produits')

    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 10
        datas = datas.order(PrixGateaux.interval).fetch(limit=10, offset=offset)
    else:
        datas = datas.order(PrixGateaux.interval)

    return render_template('gateau/prix_gateaux.html', **locals())


@prefix.route('/prix-gateaux/edit',  methods=['GET', 'POST'])
@prefix.route('/prix-gateaux/edit/<int:gateau_id>',  methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'gateau'), ['edit']])
def param_price_edit(gateau_id=None):

    if gateau_id:
        data = PrixGateaux.get_by_id(gateau_id)
        form = FormPrixGateaux(obj=data)
        form.id.data = data.key.id()
        form.categorie.data = data.categorie_id.id()
    else:
        data = PrixGateaux()
        form = FormPrixGateaux()

    form.categorie.choices = [(0, 'Selectionnez une categorie')]
    for choice in Param.query(Param.type_data == 'categories'):
        form.categorie.choices.append((choice.key.id(), choice.name))

    list_part = global_part

    success = False
    if form.validate_on_submit():

        data.interval = form.interval.data
        data.prix = float(form.prix.data)

        categorie = Param.get_by_id(int(form.categorie.data))
        data.categorie_id = categorie.key
        data.put()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('gateau/edit_price_gateaux.html', **locals())
