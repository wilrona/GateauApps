__author__ = 'Ronald'

from ...modules import *
from models_event import Event
from forms_event import FormEvent


cache = Cache(app)
prefix = Blueprint('event', __name__)

@prefix.route('/event')
@login_required
@roles_required([('super_admin', 'evenement')])
def index():
    menu = 'parametre'
    submenu = 'event'


    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = Event.query()
    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='Evenements')

    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 10
        datas.fetch(limit=10, offset=offset)

    return render_template('event/index.html', **locals())



@prefix.route('/event/edit',  methods=['GET', 'POST'])
@prefix.route('/event/edit/<int:event_id>',  methods=['GET', 'POST'])
@login_required
def edit(event_id=None):

    if event_id:
        events = Event.get_by_id(event_id)
        form = FormEvent(obj=events)
        form.id.data = event_id
    else:
        events = Event()
        form = FormEvent()

    success = False
    if form.validate_on_submit():

        events.name = form.name.data
        events.at_date = form.at_date.data
        events.put()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('event/edit.html', **locals())


@prefix.route('/event/delete/<int:event_id>')
@login_required
def delete(event_id):
    events = Event.get_by_id(event_id)
    events.key.delete()
    flash('Suppression reussie', 'success')
    return redirect(url_for('event.index'))