__author__ = 'Ronald'

from views_dashboard import *

app.register_blueprint(prefix, url_prefix='/dashboard')
app.register_blueprint(prefix_param, url_prefix='/parametre')