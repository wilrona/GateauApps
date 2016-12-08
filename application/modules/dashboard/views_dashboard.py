__author__ = 'Ronald'

from ...modules import *
from ..commande.models_commande import Produit, Users, ndb

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('dashboard', __name__)
prefix_param = Blueprint('parametre', __name__)


@prefix.route('/')
@login_required
@roles_required([('super_admin', 'dashboard')])
def index():
    title_page = 'Tableau de bord'
    menu = 'dashboard'

    commande_encours = 0

    client = 0
    gateaux = 0




    # Statistiques des commandes
    stat_cmd_cours = 0
    stat_cmd_livre = 0
    stat_cmd_annule = 0
    stat_cmd_total = 0


    # # Statistiques des ventes
    # ventes = Commande_has_gateaux.query(
    #     ndb.OR(
    #         Commande_has_gateaux.livre == False,
    #         Commande_has_gateaux.livre == True
    #     ),
    #     Commande_has_gateaux.annule == False
    # )

    vente_cours = 0
    vente_ancienne = 0
    vente_total = 0

    # #implementation de l'heure local
    # time_zones = pytz.timezone('Africa/Douala')
    # date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")
    #
    # month_current = function.datetime_convert(date_auto_nows).month
    #
    # all_vente = 0
    # for vente in ventes:
    #     all_vente += vente.prix
    #     if function.date_convert(vente.commande_id.get().date_cmd).month == month_current:
    #         vente_cours += vente.prix
    #
    # vente_ancienne = all_vente - vente_cours
    # vente_total = all_vente

    return render_template('dashboard/index.html', **locals())



@prefix_param.route('/')
@login_required
def index():

    title_page = 'Parametrages'
    menu = 'parametre'

    return render_template('dashboard/parametre.html', **locals())