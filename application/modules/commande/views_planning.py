__author__ = 'Ronald'

from ...modules import *
from ..commande.models_commande import ProduitCommander, Commande


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