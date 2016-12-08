__author__ = 'Ronald'

from ...modules import *
from models_agenda import Calandar


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('agenda', __name__)


@prefix.route('/agenda')
@login_required
def index():
    submenu = 'agenda'

    calendar = Calandar.query().get()
    datas = []

    user = True
    if not calendar:
        user = False

    agenda = False
    if calendar and calendar.agendaID:
        agenda = True

    if calendar:
        credentials = client.OAuth2Credentials.from_json(calendar.token)
        http_auth = credentials.authorize(Http())
        service = build('calendar', 'v3', http_auth)

        page_token = None
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()

            for calendar_list_entry in calendar_list['items']:
                if calendar_list_entry['id'] == calendar.agendaID:
                    item = {'name': calendar_list_entry['summary'], 'id': calendar_list_entry['id']}
                    datas.append(item)
            page_token = calendar_list.get('nextPageToken')

            if not page_token:
                break

    return render_template('agenda/index.html', **locals())


@prefix.route('/agenda/creer')
@login_required
def create():

    calendar = Calandar.query().get()
    credentials = client.OAuth2Credentials.from_json(calendar.token)
    http_auth = credentials.authorize(Http())
    service = build('calendar', 'v3', http_auth)

    calendar_infos = {
        'summary': 'CC_Planning_Prod',
        'timeZone': 'Africa/Douala'
    }

    created_calendar = service.calendars().insert(body=calendar_infos).execute()

    calendar.agendaID = created_calendar['id']
    calendar.put()

    return redirect(url_for('agenda.index'))


@prefix.route('/agenda/delete')
@login_required
def delete():
    calendar = Calandar.query().get()

    credentials = client.OAuth2Credentials.from_json(calendar.token)
    http_auth = credentials.authorize(Http())
    service = build('calendar', 'v3', http_auth)

    data_user = calendar.email_user

    for user in data_user:
        service.acl().delete(calendarId=calendar.agendaID, ruleId=user).execute()

    service.calendars().delete(calendarId=calendar.agendaID).execute()

    calendar.agendaID = None
    calendar.email_user = []
    calendar.put()

    return redirect(url_for('agenda.index'))


@prefix.route('/agenda/delete/connexion')
@login_required
def deleteConnexion():

    calendar = Calandar.query().get()

    calendar.key.delete()

    return redirect(url_for('agenda.index'))


@prefix.route('/agenda/adduser', methods=['GET', 'POST'])
@login_required
def AddUser():

    calendar = Calandar.query().get()

    credentials = client.OAuth2Credentials.from_json(calendar.token)
    http_auth = credentials.authorize(Http())
    service = build('calendar', 'v3', http_auth)

    if request.method == 'POST':

        data = []
        if calendar.email_user:
            data = calendar.email_user

        rule = {
            'scope': {
                'type': 'user',
                'value': request.form['email'],
            },
            'role': 'reader'
        }

        created_rule = service.acl().insert(calendarId=calendar.agendaID, body=rule).execute()

        user = created_rule['id']

        if not user in data:
            data.append(user)

        calendar.email_user = data
        calendar.put()

    return render_template('agenda/user_list.html', **locals())


@prefix.route('/agenda/deleteuser/<int:idrole>')
@login_required
def DeleteUser(idrole):

    calendar = Calandar.query().get()

    credentials = client.OAuth2Credentials.from_json(calendar.token)
    http_auth = credentials.authorize(Http())
    service = build('calendar', 'v3', http_auth)

    data = calendar.email_user
    user = data[idrole]

    service.acl().delete(calendarId=calendar.agendaID, ruleId=user).execute()

    data = data.remove(user)

    calendar.email_user = []
    if data:
       calendar.email_user = data
    calendar.put()

    return render_template('agenda/user_list.html', **locals())


@prefix.route('/agenda/oauth2callback')
@login_required
def oauth2callback():
    calandars = Calandar()

    scope = [
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/calendar'
    ]

    flow = client.flow_from_clientsecrets(
            os.path.join(os.path.dirname(__file__), 'client_secret.json'),
            scope=scope,
            redirect_uri=url_for("agenda.oauth2callback", _external=True)
    )
    flow.params['access_type'] = 'offline'
    flow.params['approval_prompt'] = 'force'

    if 'code' not in request.args:
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)
    else:
        auth_code = request.args.get('code')
        credentials = flow.step2_exchange(auth_code)

        calandars.token = str(credentials.to_json())
        calandars.put()
        return redirect(url_for('agenda.index'))
