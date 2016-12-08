__author__ = 'Ronald'


from views_type_gateau import *
from views_param import *

app.register_blueprint(prefix_type_gateau, url_prefix='/parametre')
app.register_blueprint(prefix, url_prefix='/parametre')
