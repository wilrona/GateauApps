__author__ = 'Ronald'

from ...modules import *
from ..commande.models_commande import ProduitCommander, Commande, PdfTable


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix_planning = Blueprint('planning', __name__)


@prefix_planning.route('/')
@login_required
@roles_required([('super_admin', 'planning_prod')])
def index():
    menu = 'commande'
    submenu = 'planning'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    DayL = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']
    Monthly = ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aout','Sept', 'Oct', 'Nov', 'Dec']

    day = datetime.date.today().strftime('%d/%m/%Y')
    dt = datetime.datetime.strptime(day, '%d/%m/%Y')
    start = dt
    end = start + timedelta(days=7)

    list_commande = Commande.query(
        Commande.dateLiv >= start,
        Commande.dateLiv <= end
    ).order(Commande.dateLiv, Commande.timeLiv)

    data = []
    for commande in list_commande:
        if not commande.annule:
            for produit in commande.produit_commande():

                info = {}
                info['cmd_id'] = commande.key.id()
                info['unique'] = '1'
                info['dateliv'] = commande.dateLiv
                info['heureliv'] = commande.timeLiv
                info['theme'] = commande.theme
                info['client'] = commande.user
                info['produit'] = produit
                data.append(info)
    grouper = itemgetter("dateliv", "unique")

    datas = []
    for key, grp in groupby(sorted(data, key=grouper), grouper):
        temp_dict = dict(zip(["dateliv", "unique"], key))
        temp_dict['moule'] = []
        for item in grp:
            if item['produit'].type_produit() == 1:
                for moule in item['produit'].list_moule():
                    info = {}
                    # info sur le gateau
                    info['gateau'] = item['produit']

                    #info sur la commande
                    info['cmd_id'] = item['cmd_id']
                    info['time'] = item['heureliv']
                    info['theme'] = item['theme']
                    info['client'] = item['client']

                    #info sur le moule
                    info['name'] = moule.name_moule()
                    info['qte'] = moule.qte
                    if moule.identiq():
                        info['composite'] = moule.identiq().list_composition()
                    else:
                        info['composite'] = moule.list_composition()

                    info['observation'] = item['produit'].observation
                    temp_dict['moule'].append(info)

            if item['produit'].type_produit() == 2:
                info = {}
                # info sur le gateau
                info['gateau'] = item['produit']

                #info sur la commande
                info['cmd_id'] = item['cmd_id']
                info['time'] = item['heureliv']
                info['theme'] = item['theme']
                info['client'] = item['client']

                #info sur le sable
                info['name'] = item['produit'].name_produit()
                info['qte'] = item['produit'].qte
                info['composite'] = None
                info['observation'] = item['produit'].observation
                temp_dict['moule'].append(info)

            if item['produit'].type_produit() == 3:
                info = {}
                info['gateau'] = item['produit']

                #info sur la commande
                info['cmd_id'] = item['cmd_id']
                info['time'] = item['heureliv']
                info['theme'] = item['theme']
                info['client'] = item['client']

                #info sur le sable
                info['name'] = item['produit'].name_produit()
                info['qte'] = item['produit'].qte
                info['composite'] = item['produit'].list_composition()
                info['observation'] = item['produit'].observation
                temp_dict['moule'].append(info)

        datas.append(temp_dict)

    return render_template('commande/planning/index.html', **locals())


@prefix_planning.route('/refresh', methods=['POST', 'GET'])
@login_required
def index_refresh():

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))

    DayL = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']
    Monthly = ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aout','Sept', 'Oct', 'Nov', 'Dec']

    title_page = 'Liste des commandes par livraison'
    printer = request.args.get('print')

    list_commande = Commande.query(
        Commande.dateLiv >= date_start,
        Commande.dateLiv <= date_end
    ).order(Commande.dateLiv, Commande.timeLiv)

    data = []
    for commande in list_commande:
        if not commande.annule:
            for produit in commande.produit_commande():
                info = {}
                info['unique'] = '1'
                info['cmd_id'] = commande.key.id()
                info['dateliv'] = commande.dateLiv
                info['heureliv'] = commande.timeLiv
                info['theme'] = commande.theme
                info['client'] = commande.user
                info['produit'] = produit
                data.append(info)
    grouper = itemgetter("dateliv", "unique")

    datas = []
    for key, grp in groupby(sorted(data, key=grouper), grouper):
        temp_dict = dict(zip(["dateliv", "unique"], key))
        temp_dict['moule'] = []
        for item in grp:
            if item['produit'].type_produit() == 1:
                for moule in item['produit'].list_moule():
                    info = {}
                    # info sur le gateau
                    info['gateau'] = item['produit']

                    #info sur la commande
                    info['cmd_id'] = item['cmd_id']
                    info['time'] = item['heureliv']
                    info['theme'] = item['theme']
                    info['client'] = item['client']

                    #info sur le moule
                    info['name'] = moule.name_moule()
                    info['qte'] = moule.qte
                    if moule.identiq():
                        info['composite'] = moule.identiq().list_composition()
                    else:
                        info['composite'] = moule.list_composition()
                    info['observation'] = item['produit'].observation
                    temp_dict['moule'].append(info)

            if item['produit'].type_produit() == 2:
                info = {}
                # info sur le gateau
                info['gateau'] = item['produit']

                #info sur la commande
                info['cmd_id'] = item['cmd_id']
                info['time'] = item['heureliv']
                info['theme'] = item['theme']
                info['client'] = item['client']

                #info sur le sable
                info['name'] = item['produit'].name_produit()
                info['qte'] = item['produit'].qte
                info['composite'] = None
                info['observation'] = item['produit'].observation
                temp_dict['moule'].append(info)

            if item['produit'].type_produit() == 3:
                info = {}
                info['gateau'] = item['produit']

                #info sur la commande
                info['cmd_id'] = item['cmd_id']
                info['time'] = item['heureliv']
                info['theme'] = item['theme']
                info['client'] = item['client']

                #info sur le sable
                info['name'] = item['produit'].name_produit()
                info['qte'] = item['produit'].qte
                info['composite'] = item['produit'].list_composition()
                info['observation'] = item['produit'].observation
                temp_dict['moule'].append(info)

        datas.append(temp_dict)

    time_zones = pytz.timezone('Africa/Douala')
    now = datetime.datetime.now(time_zones)

    return render_template('commande/planning/index_refresh.html', **locals())


@prefix_planning.route('/agenda')
def agenda():
    menu = 'commande'
    submenu = 'agenda'

    return render_template('commande/planning/agenda.html', **locals())


@prefix_planning.route('/day')
def email_day():
    import requests
    return requests.get('http://creative-cake.appspot.com/commande/planning/day/execute').content


@prefix_planning.route('/day/execute')
def email_day_execute():

    from google.appengine.api import mail

    DayL = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']
    Monthly = ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aout','Sept', 'Oct', 'Nov', 'Dec']

    day = datetime.date.today().strftime('%d/%m/%Y')
    dt = datetime.datetime.strptime(day, '%d/%m/%Y')
    start = dt
    end = start + timedelta(days=1)

    list_part = global_part

    list_commandes = Commande.query(
        Commande.dateLiv == end,
        Commande.annule == False
    ).order(Commande.dateLiv, Commande.timeLiv)


    list_commande = []
    for commande in list_commandes:
        if not commande.send and commande.new:
            list_commande.append(commande)

    message = mail.EmailMessage()

    if list_commande:
        message.html = render_template('commande/planning/email_day.html', **locals())

        for commande in list_commande:
            commande.send = True
            commande.new = False
            commande.put()
    else:
        message.html = render_template('commande/planning/email_noting.html', **locals())

    message.sender = 'Support Creative Cake Apps <no_reply@creative-cake.appspotmail.com>'
    message.subject = 'Planning de production du '+str(DayL[end.weekday()])+' '+str(end.day)+' '+str(Monthly[end.month - 1])+' '+str(end.year)
    message.to = 'celine.guemnietafo@gmail.com'
    message.send()

    return 'True'


@prefix_planning.route('/weekend')
def email_weekend():
    import requests
    return requests.get('http://creative-cake.appspot.com/commande/planning/weekend/execute').content


@prefix_planning.route('/weekend/execute')
def email_weekend_execute():

    from google.appengine.api import mail

    DayL = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']
    Monthly = ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aout','Sept', 'Oct', 'Nov', 'Dec']

    day = datetime.date.today().strftime('%d/%m/%Y')
    dt = datetime.datetime.strptime(day, '%d/%m/%Y')
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)

    list_part = global_part

    list_commandes = Commande.query(
        Commande.dateLiv >= start,
        Commande.dateLiv <= end,
        Commande.annule == False
    ).order(Commande.dateLiv, Commande.timeLiv)

    list_commande = []
    for commande in list_commandes:
        if not commande.send:
            list_commande.append(commande)

    message = mail.EmailMessage()
    if list_commande:
        message.html = render_template('commande/planning/email_week.html', **locals())
    else:
        message.html = render_template('commande/planning/email_noting_week.html', **locals())

    message.sender = 'Support Creative Cake Apps <no_reply@creative-cake.appspotmail.com>'
    message.subject = 'Planning de production de la semaine du '+str(function.format_date(start, '%d/%m/%Y'))+' au '+str(function.format_date(end, '%d/%m/%Y'))
    message.to = 'celine.guemnietafo@gmail.com'
    message.send()

    return 'True'


@prefix_planning.route('/correction')
def correction():
    list_commande = Commande.query()

    for commande in list_commande:
        commande.verif_calendar = False
        commande.put()
    return 'True'


@prefix_planning.route('/day_rappel')
def email_day_rap():
    import requests
    return requests.get('http://creative-cake.appspot.com/commande/planning/day/rappel').content


@prefix_planning.route('/day/rappel')
def email_day_rappel():

    from google.appengine.api import mail

    DayL = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']
    Monthly = ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aout', 'Sept', 'Oct', 'Nov', 'Dec']

    day = datetime.date.today().strftime('%d/%m/%Y')
    dt = datetime.datetime.strptime(day, '%d/%m/%Y')
    start = dt
    end = start + timedelta(days=1)

    list_part = global_part

    list_commande = Commande.query(
        Commande.dateLiv == end,
        Commande.annule == False
    ).order(Commande.dateLiv, Commande.timeLiv)

    message = mail.EmailMessage()

    if list_commande:
        indice = True
        message.html = render_template('commande/planning/email_day.html', **locals())
    else:
        message.html = render_template('commande/planning/email_noting.html', **locals())

    message.sender = 'Support Creative Cake Apps <no_reply@creative-cake.appspotmail.com>'
    message.subject = 'Rappel du planning de production du '+str(DayL[end.weekday()])+' '+str(end.day)+' '+str(Monthly[end.month - 1])+' '+str(end.year)
    message.to = 'celine.guemnietafo@gmail.com'
    message.send()

    return 'True'


@prefix_planning.route('/add_calendar/<int:id_commande>')
def calendar(id_commande):

    from ..agenda.view_agenda import Calandar
    calendar = Calandar.query().get()

    if calendar and calendar.agendaID:
        credentials = client.OAuth2Credentials.from_json(calendar.token)
        http_auth = credentials.authorize(Http())
        service = build('calendar', 'v3', http=http_auth)

        current_commande = Commande.get_by_id(id_commande)

        start = datetime.datetime.combine(current_commande.dateLiv, current_commande.timeLiv)
        start_to_end = start
        start = start.strftime('%Y-%m-%dT%H:%M:%S')

        end = start_to_end + timedelta(minutes=15)
        end = end.strftime('%Y-%m-%dT%H:%M:%S')

        for produit in current_commande.produit_commande(verified=True):

            prod = 'Cupcake'
            part = produit.qte
            if produit.produit_id.get().type_produit == 1:
                prod = 'Gateau'
                list_part = global_part
                part = list_part[produit.nbrPart]

            if produit.produit_id.get().type_produit == 2:
                prod = 'Sable'
                part = produit.qte

            summary = prod+' de '+current_commande.user.get().name+' de la commande '+current_commande.ref

            description = 'Theme : '+current_commande.theme+'\n'
            description += 'Evenement : '+current_commande.event_id.get().name+'\n'
            description += 'Nombre de part/quantite : '+str(part)+'\n'

            if produit.produit_id.get().type_produit == 1:
                description += 'Categorie : '+produit.categorie_id.get().name+'\n'
                description += 'Moule : '
                for moule in produit.list_moule():
                    description += moule.moule_id.get().name+' ('+str(moule.qte)+'),'

            event = {
              'summary': summary,
              'description': description,
              'start': {
                'dateTime': start,
                'timeZone': 'Africa/Lagos',
              },
              'end': {
                'dateTime': end,
                'timeZone': 'Africa/Lagos',
              },
              'reminders': {
                'useDefault': True
              }
            }
            events = service.events().insert(calendarId=calendar.agendaID, body=event).execute()

    return 'True'


@prefix_planning.route('/calendar_init')
def calendar_init():

    from ..agenda.view_agenda import Calandar
    calendar = Calandar.query().get()

    if calendar and calendar.agendaID:
        credentials = client.OAuth2Credentials.from_json(calendar.token)
        http_auth = credentials.authorize(Http())
        service = build('calendar', 'v3', http=http_auth)

        all_commande = Commande.query()

        for current_commande in all_commande:

            start = datetime.datetime.combine(current_commande.dateLiv, current_commande.timeLiv)
            start_to_end = start
            start = start.strftime('%Y-%m-%dT%H:%M:%S')

            end = start_to_end + timedelta(minutes=15)
            end = end.strftime('%Y-%m-%dT%H:%M:%S')

            for produit in current_commande.produit_commande(verified=True):

                prod = 'Cupcake'
                part = produit.qte
                if produit.produit_id.get().type_produit == 1:
                    prod = 'Gateau'
                    list_part = global_part
                    part = list_part[produit.nbrPart]

                if produit.produit_id.get().type_produit == 2:
                    prod = 'Sable'
                    part = produit.qte

                summary = prod+' de '+current_commande.user.get().name+' de la commande '+current_commande.ref

                description = 'Theme : '+current_commande.theme+'\n'
                description += 'Evenement : '+current_commande.event_id.get().name+'\n'
                description += 'Nombre de part/quantite : '+str(part)+'\n'

                if produit.produit_id.get().type_produit == 1:
                    description += 'Categorie : '+produit.categorie_id.get().name+'\n'
                    description += 'Moule : '
                    for moule in produit.list_moule():
                        description += moule.moule_id.get().name+' ('+str(moule.qte)+'),'

                event = {
                  'summary': summary,
                  'description': description,
                  'start': {
                    'dateTime': start,
                    'timeZone': 'Africa/Lagos',
                  },
                  'end': {
                    'dateTime': end,
                    'timeZone': 'Africa/Lagos',
                  },
                  'reminders': {
                    'useDefault': True
                  }
                }
                events = service.events().insert(calendarId=calendar.agendaID, body=event).execute()

    return 'True'



@prefix_planning.route('/update_calendar/<int:id_commande>')
def calendar_update(id_commande):

    from ..agenda.view_agenda import Calandar
    calendar = Calandar.query().get()

    if calendar and calendar.agendaID:

        credentials = client.OAuth2Credentials.from_json(calendar.token)
        http_auth = credentials.authorize(Http())
        service = build('calendar', 'v3', http=http_auth)

        current_commande = Commande.get_by_id(id_commande)

        start = datetime.datetime.combine(current_commande.dateLiv, current_commande.timeLiv)
        start_to_end = start
        start = start.strftime('%Y-%m-%dT%H:%M:%S')

        end = start_to_end + timedelta(minutes=15)
        end = end.strftime('%Y-%m-%dT%H:%M:%S')

        for produit in current_commande.produit_commande(verified=True):

            if produit.eventID:

                prod = 'Cupcake'
                part = produit.qte
                if produit.produit_id.get().type_produit == 1:
                    prod = 'Gateau'
                    list_part = global_part
                    part = list_part[produit.nbrPart]

                if produit.produit_id.get().type_produit == 2:
                    prod = 'Sable'
                    part = produit.qte

                summary = prod+' de '+current_commande.user.get().name+' de la commande '+current_commande.ref

                description = 'Theme : '+current_commande.theme+'\n'
                description += 'Evenement : '+current_commande.event_id.get().name+'\n'
                description += 'Nombre de part/quantite : '+str(part)+'\n'

                if produit.produit_id.get().type_produit == 1:
                    description += 'Categorie : '+produit.categorie_id.get().name+'\n'
                    description += 'Moule : '
                    for moule in produit.list_moule():
                        description += moule.moule_id.get().name+' ('+str(moule.qte)+'),'

                event = service.events().get(calendarId=calendar.agendaID, eventId=produit.eventID).execute()
                event['summary'] = summary
                event['description'] = description
                event['start']['dateTime'] = start
                event['end']['dateTime'] = end

                updated_event = service.events().update(calendarId=calendar.agendaID, eventId=event['id'], body=event).execute()

    return 'True'

@prefix_planning.route('/add_event/auto')
def calendar_event():

    from ..agenda.view_agenda import Calandar
    from dateutil import parser

    calendar = Calandar.query().get()

    if calendar and calendar.agendaID:

        credentials = client.OAuth2Credentials.from_json(calendar.token)
        http_auth = credentials.authorize(Http())
        service = build('calendar', 'v3', http=http_auth)

        list_event = []
        page_token = None
        while True:
            events = service.events().list(calendarId=calendar.agendaID, pageToken=page_token).execute()
            for event in events['items']:
                if parser.parse(event['start']['dateTime']).replace(tzinfo=None) >= datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time()):
                    ev = {}
                    ev['id'] = event['id']
                    ev['start'] = parser.parse(event['start']['dateTime']).replace(tzinfo=None)
                    ev['summary'] = event['summary']
                    list_event.append(ev)
            page_token = events.get('nextPageToken')
            if not page_token:
                break

        cmd_calendar = Commande.query(
            Commande.verif_calendar == False
        )

        list_produit = []
        for cmd in cmd_calendar:
            exist = False
            for produit in cmd.produit_commande(verified=True):
                product = {}
                prod = 'Cupcake'
                if produit.produit_id.get().type_produit == 1:
                    prod = 'Gateau'
                if produit.produit_id.get().type_produit == 2:
                    prod = 'Sable'
                product['summary'] = prod+' de '+cmd.user.get().name+' de la commande '+cmd.ref
                product['start'] = datetime.datetime.combine(cmd.dateLiv, cmd.timeLiv)
                product['id'] = produit.key.id()
                list_produit.append(product)
                exist = True
            if exist:
                cmd.verif_calendar = True
                cmd.put()

        for list_prod in list_produit:
            for list_ev in list_event:
                if list_ev['summary'] == list_prod['summary'] and list_ev['start'] == list_prod['start']:
                    produ = ProduitCommander.get_by_id(int(list_prod['id']))
                    if not produ.eventID:
                        produ.eventID = list_ev['id']
                        produ.put()
                    else:

                        start = datetime.datetime.combine(produ.commande_id.get().dateLiv, produ.commande_id.get().timeLiv)
                        start_to_end = start
                        start = start.strftime('%Y-%m-%dT%H:%M:%S')

                        end = start_to_end + timedelta(minutes=15)
                        end = end.strftime('%Y-%m-%dT%H:%M:%S')

                        prod = 'Cupcake'
                        part = produit.qte
                        if produit.produit_id.get().type_produit == 1:
                            prod = 'Gateau'
                            list_part = global_part
                            part = list_part[produit.nbrPart]

                        if produit.produit_id.get().type_produit == 2:
                            prod = 'Sable'
                            part = produit.qte

                        summary = prod+' de '+produ.commande_id.get().user.get().name+' de la commande '+produ.commande_id.get().ref

                        description = 'Theme : '+produ.commande_id.get().theme+'\n'
                        description += 'Evenement : '+produ.commande_id.get().event_id.get().name+'\n'
                        description += 'Nombre de part/quantite : '+str(part)+'\n'

                        if produit.produit_id.get().type_produit == 1:
                            description += 'Categorie : '+produit.categorie_id.get().name+'\n'
                            description += 'Moule : '
                            for moule in produit.list_moule():
                                description += moule.moule_id.get().name+' ('+str(moule.qte)+'),'

                        event = service.events().get(calendarId=calendar.agendaID, eventId=produit.eventID).execute()
                        event['summary'] = summary
                        event['description'] = description
                        event['start']['dateTime'] = start
                        event['end']['dateTime'] = end

                        updated_event = service.events().update(calendarId=calendar.agendaID, eventId=event['id'], body=event).execute()

    return 'True'


@prefix_planning.route('/delete_event/<int:id_produit>')
def calendar_event_delete(id_produit):

    from ..agenda.view_agenda import Calandar

    calendar = Calandar.query().get()

    if calendar and calendar.agendaID:

        credentials = client.OAuth2Credentials.from_json(calendar.token)
        http_auth = credentials.authorize(Http())
        service = build('calendar', 'v3', http=http_auth)

        produit = ProduitCommander.get_by_id(id_produit)

        if produit.eventID:
            service.events().delete(calendarId=calendar.agendaID, eventId=produit.eventID).execute()
            produit.eventID = None
            produit.put()
        else:
            start = datetime.datetime.combine(produit.commande_id.get().dateLiv, produit.commande_id.get().timeLiv)
            start_to_end = start
            start = start.strftime('%Y-%m-%dT%H:%M:%S')

            end = start_to_end + timedelta(minutes=15)
            end = end.strftime('%Y-%m-%dT%H:%M:%S')

            prod = 'Cupcake'
            part = produit.qte
            if produit.produit_id.get().type_produit == 1:
                prod = 'Gateau'
                list_part = global_part
                part = list_part[produit.nbrPart]

            if produit.produit_id.get().type_produit == 2:
                prod = 'Sable'
                part = produit.qte

            summary = prod+' de '+produit.commande_id.get().user.get().name+' de la commande '+produit.commande_id.get().ref

            description = 'Theme : '+produit.commande_id.get().theme+'\n'
            description += 'Evenement : '+produit.commande_id.get().event_id.get().name+'\n'
            description += 'Nombre de part/quantite : '+str(part)+'\n'

            if produit.produit_id.get().type_produit == 1:
                description += 'Categorie : '+produit.categorie_id.get().name+'\n'
                description += 'Moule : '
                for moule in produit.list_moule():
                    description += moule.moule_id.get().name+' ('+str(moule.qte)+'),'

            event = {
              'summary': summary,
              'description': description,
              'start': {
                'dateTime': start,
                'timeZone': 'Africa/Lagos',
              },
              'end': {
                'dateTime': end,
                'timeZone': 'Africa/Lagos',
              },
              'reminders': {
                'useDefault': True
              }
            }
            events = service.events().insert(calendarId=calendar.agendaID, body=event).execute()

    return 'True'

@prefix_planning.route('/send_facture/<int:id_facture>')
def send_facture_test(id_facture):
    from google.appengine.api import mail

    commande = Commande.get_by_id(int(id_facture))

    message = mail.EmailMessage()

    create = False

    name = commande.user.get().name
    date = function.format_date(function.date_convert(commande.dateCmd), '%d/%m/%Y')
    livraison = function.format_date(function.date_convert(commande.dateLiv), '%d/%m/%Y')+' '+function.format_date(function.time_convert(commande.timeLiv), '%H:%M')
    theme = commande.theme

    template = render_template('commande/planning/email_facture.html', **locals())
    message.html = template

    message.sender = 'Creative Cake <no_reply@creative-cake.appspotmail.com>'
    message.subject = 'Test Information sur votre commande du '+ function.format_date(function.date_convert(commande.dateCmd), '%d/%m/%Y')
    message.to = 'celine.guemnietafo@gmail.com'

    pdf_file = PdfTable.query(
        PdfTable.commande_id == commande.key
    ).get()

    message.attachments = [('Facture-commande-'+commande.ref+'.pdf', pdf_file.archivoBlob)]

    # message.attachments = [('Facture-commande-'+commande.ref+'.pdf', pdf_file.archivoBlob)]

    send = message.send()

    return 'TRUE'



@prefix_planning.route('/send_facture')
def send_facture():
    from google.appengine.api import mail
    import re

    all_commande = Commande.query(
        Commande.mail_send == False
    )

    for commande in all_commande:
        if commande.user.get().email:
            client = commande.user.get().email
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', client)

            if commande.mail_type == 0 and match:
                message = mail.EmailMessage()

                create = True
                name = commande.user.get().name
                date = function.format_date(function.date_convert(commande.dateCmd), '%d/%m/%Y')
                livraison = function.format_date(function.date_convert(commande.dateLiv), '%d/%m/%Y')+' '+function.format_date(function.time_convert(commande.timeLiv), '%H:%M')
                theme = commande.theme

                template = render_template('commande/planning/email_facture.html', **locals())
                message.html = template

                message.sender = 'Creative Cake <no_reply@creative-cake.appspotmail.com>'
                message.subject = 'Information sur votre commande du '+ function.format_date(function.date_convert(commande.dateCmd), '%d/%m/%Y')
                message.to = client

                document = url_for('static', filename='Conditions-Generales-de-vente-CCD.pdf', _external=True)

                pdf_file = PdfTable.query(
                    PdfTable.commande_id == commande.key
                ).get()

                message.attachments = [('Facture-commande-'+commande.ref+'.pdf', pdf_file.archivoBlob),('Condition-vente.pdf', document)]

                send = message.send()

                commande.mail_send = True
                commande.put()

                pdf_file.key.delete()

            if commande.mail_type == 1 and match:
                message = mail.EmailMessage()

                create = False
                name = commande.user.get().name
                date = function.format_date(function.date_convert(commande.dateCmd), '%d/%m/%Y')
                livraison = function.format_date(function.date_convert(commande.dateLiv), '%d/%m/%Y')+' '+function.format_date(function.time_convert(commande.timeLiv), '%H:%M')
                theme = commande.theme

                template = render_template('commande/planning/email_facture.html', **locals())
                message.html = template


                message.sender = 'Creative Cake <no_reply@creative-cake.appspotmail.com>'
                message.subject = 'Solde de votre commande '+ function.format_date(function.date_convert(commande.dateCmd), '%d/%m/%Y')
                message.to = client

                pdf_file = PdfTable.query(
                    PdfTable.commande_id == commande.key
                ).get()

                message.attachments = [('Facture-commande-'+commande.ref+'.pdf', pdf_file.archivoBlob)]

                send = message.send()

                commande.mail_send = True
                commande.put()

                pdf_file.key.delete()

    return 'True'


@prefix_planning.route('/facture/save')
def facturePDF_save():

    import re

    all_commande = Commande.query(
        Commande.mail_send == False
    )

    for current_facture in all_commande:
        if current_facture.user and current_facture.user.get().email is not None:
            client = current_facture.user.get().email
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', client)
            # current_facture = Commande.get_by_id(facture_id)
            if match and (current_facture.mail_type == 0 or current_facture.mail_type == 1):
                import cStringIO
                output = cStringIO.StringIO()

                style = getSampleStyleSheet()
                width, height = portrait(letter)

                topMargin = 19.5*cm
                # leftMargin = cm*12.5
                # leftMargin2 = cm*22.5
                bottomMargin = cm/2

                p = canvas.Canvas(output, pagesize=portrait(letter))
                p.setTitle('Facture_Commande')
                image = ImageReader(url_for('static', filename='Bande.jpg', _external=True))
                wi, hi = image.getSize()
                p.drawImage(url_for('static', filename='Bande.jpg', _external=True), 0, height - hi, width=width, height=hi, preserveAspectRatio=False)

                string = '<font name="Times-Italic" size="24">%s</font>'
                string_2 = '<font name="Times-Bold" size="24">%s</font>'
                ref = string % current_facture.ref
                header = string_2 % 'Facture : '+ref
                c = Paragraph(header, style=style['Title'])
                wti, hti = c.wrapOn(p, width, height)
                c.drawOn(p, width - wti, topMargin)

                string = '<font name="Times-Italic" size="12">%s</font>'
                string_2 = '<font name="Times-Bold" size="12">%s</font>'
                name = string % current_facture.user.get().name
                show_name = string_2 % ' Nom client : '+name
                c = Paragraph(show_name, style=style['Code'])
                wti_name, hti_name = c.wrapOn(p, width, height)
                c.drawOn(p, width - wti_name, topMargin - 1.5*cm)

                string = '<font name="Times-Italic" size="12">%s</font>'
                string_2 = '<font name="Times-Bold" size="12">%s</font>'
                email = string % current_facture.user.get().email
                show_email = string_2 % ' Email : '+email
                c = Paragraph(show_email, style=style['Code'])
                wti_name, hti_name = c.wrapOn(p, width, height)
                c.drawOn(p, width - wti_name, topMargin - 2*cm)

                string = '<font name="Times-Italic" size="12">%s</font>'
                string_2 = '<font name="Times-Bold" size="12">%s</font>'
                phone = string % current_facture.user.get().phone
                show_phone = string_2 % ' Telephone : '+phone
                c = Paragraph(show_phone, style=style['Code'])
                wti_name, hti_name = c.wrapOn(p, width, height)
                c.drawOn(p, width - wti_name, topMargin - 2.5*cm)


                string = '<font name="Times-Italic" size="16">%s</font>'
                string_2 = '<font name="Times-Bold" size="16">%s</font>'
                phone = string % current_facture.theme

                styleBH = style["Title"]
                styleBH.alignment = TA_CENTER

                show_phone = string_2 % ' Theme : '+phone
                c = Paragraph(show_phone, style=styleBH)
                wti_name, hti_name = c.wrapOn(p, width, height)
                c.drawOn(p, width - wti_name, topMargin - 4*cm)


                string = '<font name="Times-Italic" size="12">%s</font>'
                string_2 = '<font name="Times-Bold" size="12">%s</font>'
                date = string % function.format_date(current_facture.dateCmd, "%d/%m/%Y")
                show_date = string_2 % ' Date commande : '+date
                c = Paragraph(show_date, style=style['Code'])
                wti, hti = c.wrapOn(p, width, height)
                c.drawOn(p, width - wti + 10.5*cm, topMargin - 1.5*cm)

                string = '<font name="Times-Italic" size="12">%s</font>'
                string_2 = '<font name="Times-Bold" size="12">%s</font>'
                date = string % function.format_date(current_facture.dateLiv, "%d/%m/%Y") +' '+ string % function.format_date(current_facture.timeLiv, "%H:%M")
                show_date = string_2 % ' Date Livraison : '+date
                c = Paragraph(show_date, style=style['Code'])
                wti, hti = c.wrapOn(p, width, height)
                c.drawOn(p, width - wti + 10.5*cm, topMargin - 2*cm)

                string = '<font name="Times-Italic" size="12">%s</font>'
                string_2 = '<font name="Times-Bold" size="12">%s</font>'
                title = string % current_facture.event_id.get().name
                show_date = string_2 % ' Evenement : '+title
                c = Paragraph(show_date, style=style['Code'])
                wti, hti = c.wrapOn(p, width, height)
                c.drawOn(p, width - wti + 10.5*cm, topMargin - 2.5*cm)

                total = 0
                for produit in current_facture.produit_commande(True):
                    montant = produit.prix
                    total = total + montant

                total_accompte = total
                accompte = 0
                for versement in current_facture.versement():
                    total_accompte = total - versement.montant
                    accompte += versement.montant


                styleN = style["Italic"]
                styleN.alignment = TA_LEFT
                styleBH = style["Italic"]
                styleBH.alignment = TA_LEFT

                # Headers
                design = Paragraph('''<b>Designation</b>''', styleBH)
                qte = Paragraph('''<b>Quantite</b>''', styleBH)
                montant = Paragraph('''<b>Montant</b>''', styleBH)

                #recuperation des donnees
                datas = [items for items in current_facture.produit_commande(True)]

                data = [
                            [design, qte, montant]
                       ]

                for i in datas:

                    text_design = ''
                    text_qte = ''
                    text_montant = ''
                    string = '<font name="Times-Italic" size="11">%s</font>'
                    string_2 = '<font name="Times-Bold" size="11">%s</font>'
                    list_part = global_part

                    if i.produit_id.get().type_produit == 1:
                        text_design += string % i.produit_id.get().name +' - '+ string_2 % i.typeGateau_id.get().name
                        text_design += ' | '
                        text_design += string_2 % 'Categorie :' +' '+ string % i.categorie_id.get().name
                        text_design += ' | '
                        moule_count = 1
                        for moule in i.list_moule_NIden():
                            text_design += string_2 % 'moule'+ string_2 % str(moule_count)
                            text_design += string % '('
                            text_design += string_2 % 'Type : '
                            text_design += string % moule.name_moule()+', '
                            text_design += string_2 % 'Qte : '
                            text_design += string % str(moule.qte) +', '

                            layer_count = 1
                            for layer in moule.list_composition():
                                text_design += string_2 % 'Layer' + string_2 % str(layer_count) + string_2 % ' : '
                                text_design += string % layer.name_goutcreme() + ', '
                                if layer.imbibage_id:
                                    text_design += string % layer.name_imbibage() + ', '
                                if layer.coulis_id:
                                    text_design += string % layer.name_coulis() + ', '
                                layer_count += 1

                            text_design += ") "
                            moule_count += 1

                            if moule.nbre_identique_count():
                                for identique in moule.nbre_identique():
                                    text_design +=  " | "
                                    text_design += string_2 % 'Moule '+str(moule_count)
                                    text_design += string % 'Layer identique aux layers du'
                                    text_design += string_2 % 'moule' +str(moule_count - 1)
                                    text_design += string % '('
                                    text_design += string_2 % 'Type :'
                                    text_design += string % identique.name_moule()
                                    text_design += string_2 % 'Qte :'
                                    text_design += string % identique.qte + ", "
                                    moule_count += 1

                        if i.impression and not i.pate:
                            text_design += ' | '
                            text_design += string % 'Impression'
                        if i.pate and not i.impression:
                            text_design += ' | '
                            text_design += string % 'Pate'
                        if i.pate and i.impression:
                            text_design += ' | '
                            text_design += string % 'Impression & Pate'

                        text_design += ' | '
                        text_design += string_2 % 'Observation :' + '' + string % i.observation

                        text_qte = string % '['+ string % list_part[i.nbrPart]+ string % ']'
                        text_montant = string % str(function.format_price(i.prix))


                    if i.produit_id.get().type_produit == 2:
                        text_design += string % i.produit_id.get().name +' - '+ string_2 % i.typeGateau_id.get().name +' '+string_2 % i.couleurRuban_id.get().name
                        text_design += ' | '

                        if i.emballage:
                            text_design += string % 'Emballage |'
                        else:
                            text_design += string % 'Sans Emballage |'

                        if i.impression and not i.pate:
                            text_design += string % 'Impression' + ' | '
                        if i.pate and not i.impression:
                            text_design += string % 'Pate' + ' | '
                        if i.pate and i.impression:
                            text_design += string % 'Impression & Pate' + ' | '

                        text_design += string_2 % 'Observation :' + '' + string % i.observation

                        text_qte = string % i.qte
                        text_montant = string % str(function.format_price(i.prix))


                    if i.produit_id.get().type_produit == 3:
                        text_design += string % i.produit_id.get().name +' - '+ string_2 % i.typeGateau_id.get().name
                        text_design += ' | '


                        for compos in i.list_composition():
                            text_design += string_2 % 'Gout de creme : ' + string % compos.name_goutcreme()
                            text_design += ' | '
                            text_design += string_2 % 'Fourrage : ' + string % compos.name_fourage()

                            if compos.coulis_id:
                                text_design += ' | '
                                text_design += string_2 % 'Coulis : ' + string % compos.name_coulis()

                            if compos.imbibage_id:
                                text_design += string_2 % 'Imbibage : ' + string % compos.name_imbibage()
                                text_design += ' | '

                            if compos.topping_id:
                                text_design += ' | '
                                text_design += string_2 % 'Topping : ' + string % compos.name_topping()

                            if compos.couleur_cup_id:
                                text_design += ' | '
                                text_design += string_2 % 'Couleur Cup : ' + string % compos.name_couleur_cup()


                        text_design += ' | '
                        text_design += string_2 % 'Observation :' + '' + string % i.observation

                        text_qte = string % i.qte
                        text_montant = string % str(function.format_price(i.prix))



                    design = Paragraph(text_design, styleN)
                    qte = Paragraph(text_qte, styleN)
                    montant = Paragraph(text_montant, styleN)
                    current = [design, qte, montant]
                    data.append(current)

                tot = string % function.format_price(total)
                data.append([Paragraph(string_2 % 'TOTAL', styleN), '' , Paragraph(tot, styleN)])
                acco = string % function.format_price(accompte)
                data.append([Paragraph(string_2 % 'Accompte', styleN), '', Paragraph(acco, styleN)])
                reste = string % function.format_price(total_accompte)
                data.append([Paragraph(string_2 % 'Reste a payer', styleN), '', Paragraph(reste, styleN)])

                table = Table(data, colWidths=[10*cm, 5*cm, 5*cm])

                table.setStyle(TableStyle([
                                       ('BACKGROUND',(0,0),(-1,0),'#ffdcea'),
                                       ('TEXTCOLOR', (0,0),(-1,0),'#ffffff'),
                                       ('INNERGRID', (0,0), (-1,-1), 0.25, '#000000'),
                                       ('BOX', (0,0), (-1,-1), 0.25, '#000000'),
                                       ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                                    ]))


                table.wrapOn(p, width, height)
                wt, ht = table.wrap(width, height)
                table.drawOn(p, width - wt - 0.9*cm, height - ht - hi - 6*cm)



                devis = 'La devise est le Franc CFA'
                c = Paragraph(devis, style=style['Italic'])
                wd, hd = c.wrapOn(p, width, ht)
                c.drawOn(p, width - wd + 0.9*cm, bottomMargin + 3.5*cm)

                image = ImageReader(url_for('static', filename='font-color-2.jpg', _external=True))
                wi, hi = image.getSize()
                p.drawImage(url_for('static', filename='font-color-2.jpg', _external=True), 0, bottomMargin - 1*cm, width=width, height=hi, preserveAspectRatio=False)


                time_zones = pytz.timezone('Africa/Douala')
                date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")
                string = '<font name="Times-Italic" size="8">%s</font>'
                devis = string % 'genere le '+ string % function.format_date(function.datetime_convert(date_auto_nows), '%d/%m/%Y %H:%M')
                c = Paragraph(devis, style=style["Italic"])
                wd, hd = c.wrapOn(p, width, ht)
                c.drawOn(p, width - wd + 0.9*cm, bottomMargin)


                styleBH = style["Italic"]
                styleBH.alignment = TA_CENTER
                devis = 'CREATIVE CAKE, marque de SO.INVEST Ets., BP 4219 Douala'
                c = Paragraph(devis, styleBH)
                wd, hd = c.wrapOn(p, width, ht)
                c.drawOn(p, width - wd, bottomMargin * 4)

                devis = 'Tel: 651221122 / 655353506 / 698987515'
                c = Paragraph(devis, styleBH)
                wd, hd = c.wrapOn(p, width, ht)
                c.drawOn(p, width - wd, bottomMargin * 3)

                devis = 'info@creative-cake-design.com / www.creative-cake-design.com'
                c = Paragraph(devis, styleBH)
                wd, hd = c.wrapOn(p, width, ht)
                c.drawOn(p, width - wd, bottomMargin * 2)

                devis = 'RC/DLA/2013/A/705 - P097800367635W'
                c = Paragraph(devis, styleBH)
                wd, hd = c.wrapOn(p, width, ht)
                c.drawOn(p, width - wd, bottomMargin)

                p.showPage()
                p.save()
                pdf_out = output.getvalue()


                blob = PdfTable()
                blob.archivoBlob = pdf_out
                blob.commande_id = current_facture.key
                blob.put()
    return 'true'