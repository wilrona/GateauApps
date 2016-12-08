__author__ = 'Ronald'

from views_commande import *
from views_planning import *

app.register_blueprint(prefix, url_prefix='/commande')
app.register_blueprint(prefix_planning, url_prefix='/commande/planning')