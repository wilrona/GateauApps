# coding=utf-8
__author__ = 'Ronald'

# -*- coding: utf-8 -*-

from ...modules import *
from ..commande.models_commande import ProduitCommander, Commande, PdfTable, ndb


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


@prefix_planning.route('/calendar_init')
def calendar_init():

    from ..agenda.view_agenda import Calandar
    calendar = Calandar.query().get()

    page_token = None
    list_event = []
    list_event2 = []

    if calendar and calendar.agendaID:
        credentials = client.OAuth2Credentials.from_json(calendar.token)
        http_auth = credentials.authorize(Http())
        service = build('calendar', 'v3', http=http_auth)


        while True:
            events = service.events().list(calendarId=calendar.agendaID, pageToken=page_token).execute()
            for event in events['items']:
                    list_event.append(event['id'])
            page_token = events.get('nextPageToken')
            if not page_token:
                break

        # for event in list_event:
        #     service.events().delete(calendarId=calendar.agendaID, eventId=event).execute()

        all_commande = Commande.query(
            Commande.annule == False
        )

        for current_commande in all_commande:

            start = datetime.datetime.combine(current_commande.dateLiv, current_commande.timeLiv)
            start_to_end = start
            start = start.strftime('%Y-%m-%dT%H:%M:%S')

            end = start_to_end + timedelta(minutes=15)
            end = end.strftime('%Y-%m-%dT%H:%M:%S')

            for produit in current_commande.produit_commande(verified=True):

                if produit.eventID not in list_event:

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

                    description += '\n\n\n'
                    description += 'Montant du produit : '+str(produit.prix)+'\n'

                    description += '\n\n\n'
                    description += 'Commande : '+str(url_for('commande.facture', id_commande=current_commande.key.id()))+'\n'
                    description += 'Accompte : '+str(current_commande.montant_versment())+'\n'
                    description += 'Montant : '+str(current_commande.montant)+'\n'

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

                    produit.eventID = events['id']
                    produit.put()

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

                description += '\n\n\n'
                description += 'Montant du produit : '+str(produit.prix)+'\n'

                description += '\n\n\n'
                description += 'Commande : '+str(url_for('commande.facture', id_commande=current_commande.key.id()))+'\n'
                description += 'Accompte : '+str(current_commande.montant_versment())+'\n'
                description += 'Montant : '+str(current_commande.montant)+'\n'

                event = service.events().get(calendarId=calendar.agendaID, eventId=produit.eventID).execute()
                event['summary'] = summary
                event['description'] = description
                event['start']['dateTime'] = start
                event['end']['dateTime'] = end

                updated_event = service.events().update(calendarId=calendar.agendaID, eventId=event['id'], body=event).execute()

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

            description += '\n\n\n'
            description += 'Montant du produit : '+str(produit.prix)+'\n'

            description += '\n\n\n'
            description += 'Commande : '+str(url_for('commande.facture', id_commande=current_commande.key.id()))+'\n'
            description += 'Accompte : '+str(current_commande.montant_versment())+'\n'
            description += 'Montant : '+str(current_commande.montant)+'\n'

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
            produit.eventID = events['id']
            produit.put()

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
        time_zones = pytz.timezone('Africa/Douala')
        date_auto_nows = datetime.datetime.now(time_zones)

        start = function.get_first_day(date_auto_nows)

        cmd_calendar = Commande.query(
            Commande.dateLiv >= start,
            Commande.annule == False
        )

        list_produit = []
        for cmd in cmd_calendar:
            # exist = False
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
                # exist = True
            # if exist:
            #     cmd.verif_calendar = True
            #     cmd.put()

        for list_prod in list_produit:

            produ = ProduitCommander.get_by_id(int(list_prod['id']))

            start = datetime.datetime.combine(produ.commande_id.get().dateLiv, produ.commande_id.get().timeLiv)
            start_to_end = start
            start = start.strftime('%Y-%m-%dT%H:%M:%S')

            end = start_to_end + timedelta(minutes=15)
            end = end.strftime('%Y-%m-%dT%H:%M:%S')

            if produ.eventID:

                exist = False

                for list_ev in list_event:

                    if list_ev['id'] == produ.eventID and list_ev['start'] != list_prod['start']:

                        exist = True

                        prod = 'Cupcake'
                        part = produ.qte
                        if produ.produit_id.get().type_produit == 1:
                            prod = 'Gateau'
                            list_part = global_part
                            part = list_part[produ.nbrPart]

                        if produ.produit_id.get().type_produit == 2:
                            prod = 'Sable'
                            part = produ.qte

                        summary = prod+' de '+produ.commande_id.get().user.get().name+' de la commande '+produ.commande_id.get().ref

                        description = 'Theme : '+produ.commande_id.get().theme+'\n'
                        description += 'Evenement : '+produ.commande_id.get().event_id.get().name+'\n'
                        description += 'Nombre de part/quantite : '+str(part)+'\n'

                        if produ.produit_id.get().type_produit == 1:
                            description += 'Categorie : '+produ.categorie_id.get().name+'\n'
                            description += 'Moule : '
                            for moule in produ.list_moule():
                                description += moule.moule_id.get().name+' ('+str(moule.qte)+'),'

                        description += '\n\n\n'
                        description += 'Montant du produit : '+str(produ.prix)+'\n'

                        description += '\n\n\n'
                        description += 'Commande : '+str(url_for('commande.facture', id_commande=produ.commande_id.get().key.id()))+'\n'
                        description += 'Accompte : '+str(produ.commande_id.get().montant_versment())+'\n'
                        description += 'Montant : '+str(produ.commande_id.get().montant)+'\n'

                        event = service.events().get(calendarId=calendar.agendaID, eventId=produ.eventID).execute()
                        event['summary'] = summary
                        event['description'] = description
                        event['start']['dateTime'] = start
                        event['end']['dateTime'] = end

                        updated_event = service.events().update(calendarId=calendar.agendaID, eventId=event['id'], body=event).execute()

                if not exist:

                    prod = 'Cupcake'
                    part = produ.qte
                    if produ.produit_id.get().type_produit == 1:
                        prod = 'Gateau'
                        list_part = global_part
                        part = list_part[produ.nbrPart]

                    if produ.produit_id.get().type_produit == 2:
                        prod = 'Sable'
                        part = produ.qte

                    summary = prod+' de '+produ.commande_id.get().user.get().name+' de la commande '+produ.commande_id.get().ref

                    description = 'Theme : '+produ.commande_id.get().theme+'\n'
                    description += 'Evenement : '+produ.commande_id.get().event_id.get().name+'\n'
                    description += 'Nombre de part/quantite : '+str(part)+'\n'

                    if produ.produit_id.get().type_produit == 1:
                        description += 'Categorie : '+produ.categorie_id.get().name+'\n'
                        description += 'Moule : '
                        for moule in produ.list_moule():
                            description += moule.moule_id.get().name+' ('+str(moule.qte)+'),'

                    description += '\n\n\n'
                    description += 'Montant du produit : '+str(produ.prix)+'\n'

                    description += '\n\n\n'
                    description += 'Commande : '+str(url_for('commande.facture', id_commande=produ.commande_id.get().key.id()))+'\n'
                    description += 'Accompte : '+str(produ.commande_id.get().montant_versment())+'\n'
                    description += 'Montant : '+str(produ.commande_id.get().montant)+'\n'

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
                    produ.eventID = events['id']
                    produ.put()

            else:

                prod = 'Cupcake'
                part = produ.qte
                if produ.produit_id.get().type_produit == 1:
                    prod = 'Gateau'
                    list_part = global_part
                    part = list_part[produ.nbrPart]

                if produ.produit_id.get().type_produit == 2:
                    prod = 'Sable'
                    part = produ.qte

                summary = prod+' de '+produ.commande_id.get().user.get().name+' de la commande '+produ.commande_id.get().ref

                description = 'Theme : '+produ.commande_id.get().theme+'\n'
                description += 'Evenement : '+produ.commande_id.get().event_id.get().name+'\n'
                description += 'Nombre de part/quantite : '+str(part)+'\n'

                if produ.produit_id.get().type_produit == 1:
                    description += 'Categorie : '+produ.categorie_id.get().name+'\n'
                    description += 'Moule : '
                    for moule in produ.list_moule():
                        description += moule.moule_id.get().name+' ('+str(moule.qte)+'),'

                description += '\n\n\n'
                description += 'Montant du produit : '+str(produ.prix)+'\n'

                description += '\n\n\n'
                description += 'Commande : '+str(url_for('commande.facture', id_commande=produ.commande_id.get().key.id()))+'\n'
                description += 'Accompte : '+str(produ.commande_id.get().montant_versment())+'\n'
                description += 'Montant : '+str(produ.commande_id.get().montant)+'\n'

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
                produ.eventID = events['id']
                produ.put()


    return 'TRUE'


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
        # else:
        #     start = datetime.datetime.combine(produit.commande_id.get().dateLiv, produit.commande_id.get().timeLiv)
        #     start_to_end = start
        #     start = start.strftime('%Y-%m-%dT%H:%M:%S')
        #
        #     end = start_to_end + timedelta(minutes=15)
        #     end = end.strftime('%Y-%m-%dT%H:%M:%S')
        #
        #     prod = 'Cupcake'
        #     part = produit.qte
        #     if produit.produit_id.get().type_produit == 1:
        #         prod = 'Gateau'
        #         list_part = global_part
        #         part = list_part[produit.nbrPart]
        #
        #     if produit.produit_id.get().type_produit == 2:
        #         prod = 'Sable'
        #         part = produit.qte
        #
        #     summary = prod+' de '+produit.commande_id.get().user.get().name+' de la commande '+produit.commande_id.get().ref
        #
        #     description = 'Theme : '+produit.commande_id.get().theme+'\n'
        #     description += 'Evenement : '+produit.commande_id.get().event_id.get().name+'\n'
        #     description += 'Nombre de part/quantite : '+str(part)+'\n'
        #
        #     if produit.produit_id.get().type_produit == 1:
        #         description += 'Categorie : '+produit.categorie_id.get().name+'\n'
        #         description += 'Moule : '
        #         for moule in produit.list_moule():
        #             description += moule.moule_id.get().name+' ('+str(moule.qte)+'),'
        #
        #     event = {
        #       'summary': summary,
        #       'description': description,
        #       'start': {
        #         'dateTime': start,
        #         'timeZone': 'Africa/Lagos',
        #       },
        #       'end': {
        #         'dateTime': end,
        #         'timeZone': 'Africa/Lagos',
        #       },
        #       'reminders': {
        #         'useDefault': True
        #       }
        #     }
        #     events = service.events().insert(calendarId=calendar.agendaID, body=event).execute()

    return 'True'


@prefix_planning.route('/send_facture/<int:id_facture>')
def send_facture_test(id_facture):
    from google.appengine.api import mail
    import re
    import requests

    commande = Commande.get_by_id(int(id_facture))

    if commande.user and commande.user.get().email is not None:

        current = PdfTable.query(
            PdfTable.commande_id == commande.key
        ).get()

        client = commande.user.get().email
        client = client.lower()
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', client)

        if match and not current:

            execute = requests.get('http://creative-cake.appspot.com/commande/facture/pdf/'+str(commande.key.id())+'?send=1').content

            if (commande.mail_type == 0 or commande.mail_type == 2) and execute:
                message = mail.EmailMessage()

                create = True
                name = commande.user.get().name
                date = function.format_date(function.date_convert(commande.dateCmd), '%d/%m/%Y')
                livraison = function.format_date(function.date_convert(commande.dateLiv), '%d/%m/%Y')+' '+function.format_date(function.time_convert(commande.timeLiv), '%H:%M')
                theme = commande.theme

                template = render_template('commande/planning/email_facture.html', **locals())
                message.html = template

                message.sender = 'Creative Cake <no_reply@creative-cake.appspotmail.com>'
                if commande.mail_type == 2:
                    message.subject = 'Des modifications d\'information sur votre commande du '+ function.format_date(function.date_convert(commande.dateCmd), '%d/%m/%Y')
                else:
                    message.subject = 'Information sur votre commande du '+ function.format_date(function.date_convert(commande.dateCmd), '%d/%m/%Y')

                if request.args.get('mail') and re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', request.args.get('mail').lower()):
                    message.to = request.args.get('mail').lower()
                else:
                    message.to = client

                document = url_for('static', filename='Conditions-Generales-de-vente-CCD.pdf', _external=True)

                pdf_file = PdfTable.query(
                    PdfTable.commande_id == commande.key
                ).get()

                message.attachments = [('Facture-commande-'+commande.ref+'.pdf', pdf_file.archivoBlob),('Conditions-ventes.pdf', document)]

                send = message.send()

                # commande.mail_send = True
                commande.put()

                pdf_file.key.delete()

            if commande.mail_type == 1 and execute:
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

                if request.args.get('mail') and re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', request.args.get('mail').lower()):
                    message.to = request.args.get('mail').lower()
                else:
                    message.to = client

                pdf_file = PdfTable.query(
                    PdfTable.commande_id == commande.key
                ).get()

                message.attachments = [('Facture-commande-'+commande.ref+'.pdf', pdf_file.archivoBlob)]

                send = message.send()

                # commande.mail_send = True
                commande.put()

                pdf_file.key.delete()

    # message = mail.EmailMessage()
    #
    # create = False
    #
    # name = commande.user.get().name
    # date = function.format_date(function.date_convert(commande.dateCmd), '%d/%m/%Y')
    # livraison = function.format_date(function.date_convert(commande.dateLiv), '%d/%m/%Y')+' '+function.format_date(function.time_convert(commande.timeLiv), '%H:%M')
    # theme = commande.theme
    #
    # template = render_template('commande/planning/email_facture.html', **locals())
    # message.html = template
    #
    # message.sender = 'Creative Cake <no_reply@creative-cake.appspotmail.com>'
    # message.subject = 'Test Information sur votre commande du '+ function.format_date(function.date_convert(commande.dateCmd), '%d/%m/%Y')
    # message.to = 'celine.guemnietafo@gmail.com'
    #
    # pdf_file = PdfTable.query(
    #     PdfTable.commande_id == commande.key
    # ).get()
    #
    # message.attachments = [('Facture-commande-'+commande.ref+'.pdf', pdf_file.archivoBlob)]
    #
    # # message.attachments = [('Facture-commande-'+commande.ref+'.pdf', pdf_file.archivoBlob)]
    #
    # send = message.send()

    return 'TRUE'


@prefix_planning.route('/send_facture_cron')
def send_facture_cron():
    import requests
    return requests.get('http://creative-cake.appspot.com/commande/planning/send_facture').content


@prefix_planning.route('/send_facture')
def send_facture():
    from google.appengine.api import mail
    import re

    all_commande = Commande.query(
        Commande.mail_send == False
    )

    for commande in all_commande:
        if commande.user and commande.user.get().email is not None:
            client = commande.user.get().email
            client = client.lower()
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', client)

            if (commande.mail_type == 0 or commande.mail_type == 2) and match:
                message = mail.EmailMessage()

                create = True
                name = commande.user.get().name
                date = function.format_date(function.date_convert(commande.dateCmd), '%d/%m/%Y')
                livraison = function.format_date(function.date_convert(commande.dateLiv), '%d/%m/%Y')+' '+function.format_date(function.time_convert(commande.timeLiv), '%H:%M')
                theme = commande.theme

                template = render_template('commande/planning/email_facture.html', **locals())
                message.html = template

                message.sender = 'Creative Cake <no_reply@creative-cake.appspotmail.com>'
                if commande.mail_type == 2:
                    message.subject = 'Des modifications d\'information sur votre commande du '+ function.format_date(function.date_convert(commande.dateCmd), '%d/%m/%Y')
                else:
                    message.subject = 'Information sur votre commande du '+ function.format_date(function.date_convert(commande.dateCmd), '%d/%m/%Y')
                message.to = client

                document = url_for('static', filename='Conditions-Generales-de-vente-CCD.pdf', _external=True)

                pdf_file = PdfTable.query(
                    PdfTable.commande_id == commande.key
                ).get()

                message.attachments = [('Facture-commande-'+commande.ref+'.pdf', pdf_file.archivoBlob),('Conditions-ventes.pdf', document)]

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


@prefix_planning.route('/send_rappel_anniversaire')
def send_rappel_anniversaire():
    from google.appengine.api import mail
    import re

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones)

    prev_year = int(date_auto_nows.year) - 1
    prev_date_auto_nows = date_auto_nows.replace(year=prev_year)

    date_send_15 = prev_date_auto_nows + datetime.timedelta(days=15)

    date_send_7 = prev_date_auto_nows + datetime.timedelta(days=7)

    all_commande = Commande.query(
        Commande.dateLiv == date_send_15
    )

    # message = mail.EmailMessage()
    # template = render_template('commande/planning/email_facture.html', **locals())
    # message.html = template
    # message.sender = 'Creative Cake <no_reply@creative-cake.appspotmail.com>'
    # message.subject = 'Des modifications d\'information sur votre commande du '+ function.format_date(function.date_convert(commande.dateCmd), '%d/%m/%Y')
    # message.to = client
    # send = message.send()

    return 'True'


@prefix_planning.route('/facture/save')
def facturePDF_save():

    import re
    import requests

    all_commande = Commande.query(
        Commande.mail_send == False
    )

    for current_facture in all_commande:

        current = PdfTable.query(
            PdfTable.commande_id == current_facture.key
        ).get()

        if current_facture.user and current_facture.user.get().email is not None:
            client = current_facture.user.get().email
            client = client.lower()
            match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', client)
            # current_facture = Commande.get_by_id(facture_id)
            if match and not current:
                execute = requests.get('http://creative-cake.appspot.com/commande/facture/pdf/'+str(current_facture.key.id())+'?send=1').content
    return 'true'


@prefix_planning.route('/send_solde_last_week/<all>')
@prefix_planning.route('/send_solde_last_week')
def send_solde_last_week(all=None):

    from google.appengine.api import mail

    DayL = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']
    Monthly = ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aout','Sept', 'Oct', 'Nov', 'Dec']

    all_commande = Commande.query(
        Commande.mail_type != 1,
        Commande.annule == False
    ).order(Commande.mail_type, Commande.dateLiv, Commande.timeLiv)

    commande_to_send = []

    for commande in all_commande:

        day = commande.dateLiv.strftime('%d/%m/%Y')
        dt = datetime.datetime.strptime(day, '%d/%m/%Y')

        start = dt - timedelta(days=dt.weekday())

        current_day = datetime.date.today().strftime('%d/%m/%Y')
        current_dt = datetime.datetime.strptime(current_day, '%d/%m/%Y')

        current_start = current_dt - timedelta(days=(current_dt.weekday() + 7))

        montant = commande.montant

        montant_versement = commande.montant_versment()

        montant_restant = montant - montant_versement

        if start == current_start and montant_restant > 0:
            commande_to_send.append(commande)


    if commande_to_send:

        message = mail.EmailMessage()

        passe = True

        current_day = datetime.date.today().strftime('%d/%m/%Y')
        current_dt = datetime.datetime.strptime(current_day, '%d/%m/%Y')

        current_start = current_dt - timedelta(days=(current_dt.weekday() + 7))
        current_end = current_start + timedelta(days=6)

        template = render_template('commande/planning/email_commande_solde.html', **locals())

        if not all:
            message.html = template

            message.sender = 'Commande Creative Cake Apps <no_reply@creative-cake.appspotmail.com>'
            message.subject = 'Commande non solde de la semaine du '+ function.format_date(function.datetime_convert(current_start), '%d/%m/%Y')+' au '+function.format_date(function.datetime_convert(current_end), '%d/%m/%Y')
            # message.to = 'wilrona@gmail.com'
            message.to = 'celine.guemnietafo@gmail.com'

            send = message.send()
        else:
            return template

    return str(all)




@prefix_planning.route('/send_solde/<all>')
@prefix_planning.route('/send_solde')
def send_solde(all=None):

    from google.appengine.api import mail

    DayL = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']
    Monthly = ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aout','Sept', 'Oct', 'Nov', 'Dec']

    all_commande = Commande.query(
        Commande.mail_type != 1,
        Commande.annule == False
    ).order(Commande.mail_type, Commande.dateLiv, Commande.timeLiv)

    commande_to_send = []

    for commande in all_commande:

        current_day = datetime.date.today().strftime('%d/%m/%Y')
        current_dt = datetime.datetime.strptime(current_day, '%d/%m/%Y')

        current_start = current_dt - timedelta(days=(current_dt.weekday()))

        montant = commande.montant

        montant_versement = commande.montant_versment()

        montant_restant = montant - montant_versement

        if commande.dateLiv < function.date_convert(current_start) and  montant_restant > 0:
            commande_to_send.append(commande)

    if commande_to_send:

        message = mail.EmailMessage()

        passe = False

        template = render_template('commande/planning/email_commande_solde.html', **locals())

        if not all:
            message.html = template

            message.sender = 'Commande Creative Cake Apps <no_reply@creative-cake.appspotmail.com>'
            message.subject = 'Total des commandes non solde a nos jours'
            # message.to = 'wilrona@gmail.com'
            message.to = 'celine.guemnietafo@gmail.com'

            send = message.send()
        else:
            return template

    return 'True'