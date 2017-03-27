__author__ = 'Ronald'

from ...modules import *
from ..user.models_user import Users
from ..user.forms_user import FormUser
from models_commande import Commande, Produit, Event, Param, TypeGateaux, Versement, ProduitCommander, MouleProduit, \
    Composition, Activite, PdfTable
from ..gateau.models_gateau import PrixGateaux
from forms_commande import FormCommande

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('commande', __name__)


@prefix.route('')
@login_required
@roles_required([('super_admin', 'commande')])
def index():
    menu = 'commande'
    submenu = 'commande'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    day = datetime.date.today().strftime('%d/%m/%Y')
    dt = datetime.datetime.strptime(day, '%d/%m/%Y')
    start = dt
    end = start + timedelta(days=7)

    if search:
        datas = Commande.query(
            Commande.annule == False
        ).order(-Commande.dateCmd)

        list_commande = []
        for commande in datas:

            data_commande = commande.theme+" "+commande.user.get().name
            search_function = function.find(data_commande.lower(), q)
            if search_function:
                list_commande.append(commande)

        datas = list_commande

        pagination = Pagination(css_framework='bootstrap3', page=page, total=len(datas), search=search,
                                record_name='Commandes')

        if len(datas) > 10:
            offset_start = (page - 1) * 10
            offset_end = page * 10

            datas = datas[offset_start:offset_end]
    else:

        datas = Commande.query(
            Commande.dateCmd >= start,
            Commande.dateCmd <= end,
            Commande.annule == False
        )

        pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search,
                                record_name='Commandes')

        if datas.count() > 10:
            if page == 1:
                offset = 0
            else:
                page -= 1
                offset = page * 10
            datas = datas.order(-Commande.dateCmd).fetch(limit=10, offset=offset)
        else:
            datas = datas.order(-Commande.dateCmd)

    return render_template('commande/index.html', **locals())


@prefix.route('/par_livraison')
@login_required
@roles_required([('super_admin', 'livraison_prod')])
def index_livraison():
    menu = 'commande'
    submenu = 'livraison'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    day = datetime.date.today().strftime('%d/%m/%Y')
    dt = datetime.datetime.strptime(day, '%d/%m/%Y')
    start = dt
    end = start + timedelta(days=7)

    # cal = calendar.Calendar(0)
    #
    # year = datetime.date.today().year
    #
    # if not current_month_active:
    # current_month_active = datetime.date.today().month
    #
    # if not current_day_active:
    # current_day_active = datetime.date.today().day
    #
    # cal_list = [cal.monthdatescalendar(year, i+1) for i in xrange(12)]

    if search:
        datas = Commande.query(
            Commande.annule == False
        ).order(Commande.dateLiv, Commande.timeLiv)

        list_commande = []
        for commande in datas:

            data_commande = commande.theme+" "+commande.user.get().name
            search_function = function.find(data_commande.lower(), q)
            if search_function:
                list_commande.append(commande)

        datas = list_commande

        pagination = Pagination(css_framework='bootstrap3', page=page, total=len(datas), search=search,
                                record_name='Commandes')

        if len(datas) > 10:
            offset_start = (page - 1) * 10
            offset_end = page * 10

            datas = datas[offset_start:offset_end]
    else:

        datas = Commande.query(
            Commande.dateLiv >= start,
            Commande.dateLiv <= end,
            Commande.annule == False
        )
        pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search,
                                record_name='Commandes')

        if datas.count() > 10:
            if page == 1:
                offset = 0
            else:
                page -= 1
                offset = page * 10
            datas = datas.order(Commande.dateLiv, Commande.timeLiv).fetch(limit=10, offset=offset)
        else:
            datas = datas.order(Commande.dateLiv, Commande.timeLiv)

    return render_template('commande/index.html', **locals())


def addPageNumber(canvas, doc):
    """
    Add the page number
    """
    page_num = canvas.getPageNumber()
    text = "Page #%s" % page_num
    canvas.drawRightString(200*mm, 20*mm, text)


@prefix.route('/refresh', methods=['GET', 'POST'])
@login_required
def index_refresh():

    search = False

    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    title_page = 'Liste des commandes'
    printer = request.args.get('print')

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))

    datas = Commande.query(
        Commande.dateCmd >= date_start,
        Commande.dateCmd <= date_end,
        Commande.annule == False
    ).order(-Commande.dateCmd)

    count = datas
    number_per_page = 15



    time_zones = pytz.timezone('Africa/Douala')
    now = datetime.datetime.now(time_zones)

    if printer:

        datas = datas

        import cStringIO
        output = cStringIO.StringIO()

        style = getSampleStyleSheet()
        width, height = landscape(letter)

        topMargin = 20.5*cm
        leftMargin = cm*12.5
        leftMargin2 = cm*22.5
        bottomMargin = cm/2

        p = canvas.Canvas(output, pagesize=landscape(letter))
        p.setTitle(title_page)

        pages = 1
        boucle = False
        if count.count() < number_per_page:
            boucle = True

        if not boucle:
            pages = 0
            modulo = count.count() % number_per_page
            div = count.count() / number_per_page
            if modulo:
                pages += 1
            pages += div

        for page in range(pages):

            page_num = p.getPageNumber()
            text = 'Page ' + str(page_num) + '/' + str(pages)

            string = '<font name="Times-Roman" size="24">%s</font>'
            header = string % title_page

            c = Paragraph(header, style=style['Normal'])
            wti, hti = c.wrapOn(p, width, height)
            c.drawOn(p, width - wti + 10.5*cm, 19.5*cm)

            string = '<font name="Times-Roman" size="12">%s</font>'
            date_string = string % 'Periode du '+function.format_date(date_start, '%d/%m/%Y')+' au '+function.format_date(date_end, '%d/%m/%Y')

            c = Paragraph(date_string, style=style['Normal'])
            c.wrapOn(p, width, height)
            c.drawOn(p, 11*cm, 18.5*cm)

            # Save the state of our canvas so we can draw on it
            p.saveState()

            # Header
            string = '<font name="Times-Roman" size="15">%s</font>'
            header = string % 'Creative Cake'
            header = Paragraph(header, style['Normal'])
            wi, he = header.wrapOn(p, width, height)
            header.drawOn(p, leftMargin, topMargin)

            # Footer
            string = '<font name="Times-Roman" size="8">%s</font>'
            footer = string % ''+str(function.format_date(now, '%d/%m/%Y %H:%M'))
            footer = Paragraph(footer, style['Normal'])
            wi, he = footer.wrap(width, bottomMargin)
            footer.drawOn(p, leftMargin, he)

            footer_number = Paragraph(text, style['Normal'])
            wi, he = footer_number.wrap(width, bottomMargin)
            footer_number.drawOn(p, leftMargin2, he)

            # Release the canvas
            p.restoreState()

            styleN = style["BodyText"]
            styleN.alignment = TA_LEFT
            styleBH = style["Normal"]
            styleBH.alignment = TA_LEFT

            # Headers
            ref = Paragraph('''<b>Reference</b>''', styleBH)
            client = Paragraph('''<b>Client</b>''', styleBH)
            theme = Paragraph('''<b>Theme</b>''', styleBH)
            Dcmd = Paragraph('''<b>Date Cmd</b>''', styleBH)
            Dliv = Paragraph('''<b>Date Liv.</b>''', styleBH)
            Time = Paragraph('''<b>Heure Liv.</b>''', styleBH)

            #recuperation des donnees
            datas_report = [items for items in datas]

            offset_start = page * number_per_page
            offset_end = (page + 1) * number_per_page

            datas_report = datas_report[offset_start:offset_end]

            data = [
                    [ref, client,theme, Dcmd, Dliv, Time]

                  ]

            breaking = 0
            for i in datas_report:
                ref = Paragraph(i.ref, styleN)
                client = Paragraph(i.user.get().name, styleN)
                theme = Paragraph(i.theme, styleN)
                Dcmd = Paragraph(function.format_date(i.dateCmd, '%d/%m/%Y'), styleN)
                Dliv = Paragraph(function.format_date(i.dateLiv, '%d/%m/%Y'), styleN)
                Time = Paragraph(function.format_date(i.timeLiv, '%H:%M'), styleN)
                current = [ref, client,theme, Dcmd, Dliv, Time]
                data.append(current)
                breaking += 1
                if breaking > number_per_page:
                    break

            table = Table(data, colWidths=[3*cm, 7*cm, 5*cm, 2.5*cm, 2.5*cm, 2.5*cm])

            table.setStyle(TableStyle([
                                   ('BACKGROUND',(0,0),(-1,0),'#eeeeee'),
                                   ('INNERGRID', (0,0), (-1,-1), 0.25, '#000000'),
                                   ('BOX', (0,0), (-1,-1), 0.25, '#000000')
                                ]))

            table.wrapOn(p, width, height)
            wt, ht = table.wrap(width, height)
            table.drawOn(p, 2.5*cm, height - ht - 3.5*cm)

            p.showPage()

        p.save()

        pdf_out = output.getvalue()
        output.close()

        response = make_response(pdf_out)
        response.headers["Content-Type"] = "application/pdf"

        return response
    else:

        return render_template('commande/index_refresh.html', **locals())


@prefix.route('/refresh_livraison', methods=['GET', 'POST'])
@login_required
def index_refresh_livraison():
    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    title_page = 'Liste des commandes par livraison'
    printer = request.args.get('print')

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))

    datas = Commande.query(
        Commande.dateLiv >= date_start,
        Commande.dateLiv <= date_end,
        Commande.annule == False
    )

    count = datas
    number_per_page = 15

    datas = datas.order(Commande.dateLiv, Commande.timeLiv)

    time_zones = pytz.timezone('Africa/Douala')
    now = datetime.datetime.now(time_zones)

    if printer:
        import cStringIO
        output = cStringIO.StringIO()

        style = getSampleStyleSheet()
        width, height = landscape(letter)

        topMargin = 20.5*cm
        leftMargin = cm*12.5
        leftMargin2 = cm*22.5
        bottomMargin = cm/2

        p = canvas.Canvas(output, pagesize=landscape(letter))
        p.setTitle(title_page)

        pages = 1
        boucle = False
        if count.count() < number_per_page:
            boucle = True

        if not boucle:
            modulo = count.count() % number_per_page
            div = count.count() / number_per_page
            if modulo:
                pages += 1
            pages += div

        for page in range(pages):

            page_num = p.getPageNumber()
            text = 'Page ' + str(page_num) + '/' + str(pages)

            string = '<font name="Times-Roman" size="24">%s</font>'
            header = string % title_page

            c = Paragraph(header, style=style['Normal'])
            wti, hti = c.wrapOn(p, width, height)
            c.drawOn(p, width - wti + 8.5*cm, 19.5*cm)

            string = '<font name="Times-Roman" size="12">%s</font>'
            date_string = string % 'Periode du '+function.format_date(date_start, '%d/%m/%Y')+' au '+function.format_date(date_end, '%d/%m/%Y')

            c = Paragraph(date_string, style=style['Normal'])
            c.wrapOn(p, width, height)
            c.drawOn(p, 11*cm, 18.5*cm)

            # Save the state of our canvas so we can draw on it
            p.saveState()

            # Header
            string = '<font name="Times-Roman" size="15">%s</font>'
            header = string % 'Creative Cake'
            header = Paragraph(header, style['Normal'])
            wi, he = header.wrapOn(p, width, height)
            header.drawOn(p, leftMargin, topMargin)

            # Footer
            string = '<font name="Times-Roman" size="8">%s</font>'
            footer = string % ''+str(function.format_date(now, '%d/%m/%Y %H:%M'))
            footer = Paragraph(footer, style['Normal'])
            wi, he = footer.wrap(width, bottomMargin)
            footer.drawOn(p, leftMargin, he)

            footer_number = Paragraph(text, style['Normal'])
            wi, he = footer_number.wrap(width, bottomMargin)
            footer_number.drawOn(p, leftMargin2, he)

            # Release the canvas
            p.restoreState()

            styleN = style["BodyText"]
            styleN.alignment = TA_LEFT
            styleBH = style["Normal"]
            styleBH.alignment = TA_LEFT

            # Headers
            ref = Paragraph('''<b>Reference</b>''', styleBH)
            client = Paragraph('''<b>Client</b>''', styleBH)
            theme = Paragraph('''<b>Theme</b>''', styleBH)
            Dcmd = Paragraph('''<b>Date Cmd</b>''', styleBH)
            Dliv = Paragraph('''<b>Date Liv.</b>''', styleBH)
            Time = Paragraph('''<b>Heure Liv.</b>''', styleBH)

            #recuperation des donnees
            response = [items for items in datas]


            offset_start = page * number_per_page
            offset_end = (page + 1) * number_per_page

            response = response[offset_start:offset_end]

            data= [
                    [ref, client,theme, Dcmd, Dliv, Time]

                  ]

            breaking = 0
            for i in response:
                ref = Paragraph(i.ref, styleN)
                client = Paragraph(i.user.get().name, styleN)
                theme = Paragraph(i.theme, styleN)
                Dcmd = Paragraph(function.format_date(i.dateCmd, '%d/%m/%Y'), styleN)
                Dliv = Paragraph(function.format_date(i.dateLiv, '%d/%m/%Y'), styleN)
                Time = Paragraph(function.format_date(i.timeLiv, '%H:%M'), styleN)
                current = [ref, client,theme, Dcmd, Dliv, Time]
                data.append(current)
                breaking += 1
                if breaking > number_per_page:
                    break


            table = Table(data, colWidths=[3 * cm, 7 * cm, 5 * cm, 2.5*cm, 2.5* cm, 2.5* cm])

            table.setStyle(TableStyle([
                                   ('BACKGROUND',(0,0),(-1,0),'#eeeeee'),
                                   ('INNERGRID', (0,0), (-1,-1), 0.25, '#000000'),
                                   ('BOX', (0,0), (-1,-1), 0.25, '#000000')
                                ]))


            table.wrapOn(p, width, height)
            wt, ht = table.wrap(width, height)
            table.drawOn(p, 2.5*cm, height - ht - 3.5*cm)

            p.showPage()

        p.save()

        pdf_out = output.getvalue()
        output.close()

        response = make_response(pdf_out)
        response.headers["Content-Type"] = "application/pdf"

        return response
    else:
        return render_template('commande/index_refresh.html', **locals())


@prefix.route('/creer')
@login_required
@roles_required([('super_admin', 'commande'), ['edit']])
def creer():
    if not session.get('client_commande'):
        session['client_commande'] = {}
        session['evenement_commande'] = {}
        session['commande'] = []
        return redirect(url_for('commande.infosClient'))

    # session['commande'] = []
    liste_commande = session.get('commande')
    list_part = global_part

    total = 0

    for produit in liste_commande:
        montant = produit['price']
        total = total + montant

    return render_template('commande/creer.html', **locals())


@prefix.route('/creer/gateau', methods=['GET', 'POST'])
@prefix.route('/creer/gateau/<int:gateau_id>', methods=['GET', 'POST'])
@login_required
def creerGateaux(gateau_id=None):
    produitGateau = Produit.query(
        Produit.type_produit == 1
    ).get()

    categorie_list = Param.query(
        Param.type_data == 'categories'
    ).order(Param.name)

    list_part = global_part

    typegateau_list = TypeGateaux.query(
        TypeGateaux.pr_sable == False
    ).order(TypeGateaux.name)

    moule_list = Param.query(
        Param.type_data == 'moules'
    ).order(Param.name)

    gout_creme_list = Param.query(
        Param.type_data == 'gouts cremes'
    ).order(Param.name)

    imbibage_list = Param.query(
        Param.type_data == 'imbibages'
    ).order(Param.name)

    fourrage_list = Param.query(
        Param.type_data == 'fourrages'
    ).order(Param.name)

    coulis_list = Param.query(
        Param.type_data == 'coulis'
    ).order(Param.name)

    if gateau_id or gateau_id == 0:
        current_gateau = session.get('commande')[gateau_id]

    if request.method == 'POST':

        commande = []
        if session.get('commande'):
            commande = session.get('commande')

        produit = {}

        choix_categorie = Param.get_by_id(int(request.form['categorie']))
        choix_type_gateau = TypeGateaux.get_by_id(int(request.form['typegateaux']))

        prix_gateaux = PrixGateaux.query(
            PrixGateaux.categorie_id == choix_categorie.key,
            PrixGateaux.interval == request.form['interval']
        ).get()

        if gateau_id or gateau_id == 0:

            commande[gateau_id]['type_produit'] = '1'
            commande[gateau_id]['categorie'] = str(choix_categorie.key.id())
            commande[gateau_id]['categorie_name'] = choix_categorie.name
            commande[gateau_id]['type_produit_id'] = produitGateau.name
            commande[gateau_id]['nbre_part'] = request.form['interval']
            commande[gateau_id]['type_gateau'] = str(choix_type_gateau.key.id())
            commande[gateau_id]['type_gateau_name'] = choix_type_gateau.name

            commande[gateau_id]['price'] = 0
            if prix_gateaux:
                commande[gateau_id]['price'] = prix_gateaux.prix
            commande[gateau_id]['observation'] = request.form['observation']

            commande[gateau_id]['impression'] = '0'
            if request.form.getlist('impression'):
                commande[gateau_id]['impression'] = '1'

            commande[gateau_id]['pate'] = '0'
            if request.form.getlist('pate'):
                commande[gateau_id]['pate'] = '1'

            commande[gateau_id]['moule'] = []

            current_moule = 0
            last_number = 0
            last_identique = 0
            for moules in request.form.getlist('moule_choix'):
                if current_moule == 0:
                    moule = {}
                    moule['choix'] = int(request.form.getlist('moule_choix')[current_moule])

                    choix = Param.get_by_id(int(request.form.getlist('moule_choix')[current_moule]))
                    moule['choix_name'] = choix.name
                    moule['qte'] = int(request.form.getlist('qte_moule')[current_moule])

                    moule['identique'] = []
                    nombre_identique = int(request.form.getlist('identique_moule')[current_moule])
                    moule['nbr_identique'] = nombre_identique
                    nbr_identique = nombre_identique

                    if current_moule > 0:
                        nbr_identique += last_identique

                    for x in range(last_identique, nbr_identique):

                        choix_identique = Param.get_by_id(int(request.form.getlist('moule_choix_identique')[x]))
                        if choix.name == choix_identique.name:
                            moule['nbr_identique'] -= 1
                            moule['qte'] += int(request.form.getlist('qte_moule_identique')[x])
                        else:
                            identique = {}
                            identique['moule_choix_identique'] = request.form.getlist('moule_choix_identique')[x]
                            identique['moule_choix_identique_name'] = choix_identique.name
                            identique['qte_moule_identique'] = int(request.form.getlist('qte_moule_identique')[x])
                            moule['identique'].append(identique)

                    last_identique = nbr_identique

                    moule['layer'] = []
                    nombre_layer = int(request.form.getlist('nbre_layer')[current_moule])
                    moule['nbr'] = nombre_layer
                    nbr_layer = nombre_layer
                    if current_moule > 0:
                        nbr_layer = nombre_layer + last_number

                    for x in range(last_number, nbr_layer):
                        exist = False
                        for lay in moule['layer']:
                            if lay['gout_creme'] == request.form.getlist('gout_creme')[x]:
                                moule['nbr'] -= 1
                                exist = True

                        if not exist:
                            layer = {}

                            layer['gout_creme'] = request.form.getlist('gout_creme')[x]
                            gout_creme = Param.get_by_id(int(layer['gout_creme']))
                            layer['gout_creme_name'] = gout_creme.name

                            layer['imbibage'] = request.form.getlist('imbibage')[x]
                            if int(layer['imbibage']):
                                imbibage = Param.get_by_id(int(layer['imbibage']))
                                layer['imbibage_name'] = imbibage.name

                            layer['coulis'] = request.form.getlist('coulis')[x]
                            if int(layer['coulis']):
                                coulis = Param.get_by_id(int(layer['coulis']))
                                layer['coulis_name'] = coulis.name

                            moule['layer'].append(layer)

                    last_number = nombre_layer
                    current_moule += 1
                    commande[gateau_id]['moule'].append(moule)

                else:
                    # if int(request.form.getlist('moule_choix')[current_moule]) == int(
                    #         request.form.getlist('moule_choix')[current_moule - 1]):
                    #     commande[gateau_id]['moule'][current_moule - 1]['qte'] += int(
                    #         request.form.getlist('qte_moule')[current_moule])
                    #
                    #     nombre_identique = int(request.form.getlist('identique_moule')[current_moule])
                    #     commande[gateau_id]['moule'][current_moule - 1]['nbr_identique'] += nombre_identique
                    #     nbr_identique = nombre_identique
                    #
                    #     if current_moule > 0:
                    #         nbr_identique += last_identique
                    #
                    #     for x in range(last_identique, nbr_identique):
                    #         identique = {}
                    #         identique['moule_choix_identique'] = request.form.getlist('moule_choix_identique')[x]
                    #         choix_identique = Param.get_by_id(int(request.form.getlist('moule_choix_identique')[x]))
                    #         if commande[gateau_id]['moule'][current_moule - 1]['choix_name'] == choix_identique.name:
                    #             commande[gateau_id]['moule'][current_moule - 1]['nbr_identique'] -= 1
                    #             commande[gateau_id]['moule'][current_moule - 1]['qte'] += int(
                    #                 request.form.getlist('qte_moule_identique')[x])
                    #         else:
                    #             identique['moule_choix_identique_name'] = choix_identique.name
                    #             identique['qte_moule_identique'] = request.form.getlist('qte_moule_identique')[x]
                    #             commande[gateau_id]['moule'][current_moule - 1]['identique'].append(identique)
                    #
                    #     last_identique = nbr_identique
                    #
                    #     nombre_layer = int(request.form.getlist('nbre_layer')[current_moule])
                    #     commande[gateau_id]['moule'][current_moule - 1]['nbr'] += nombre_layer
                    #     nbr_layer = nombre_layer
                    #
                    #     if current_moule > 0:
                    #         nbr_layer = nombre_layer + last_number
                    #
                    #     for x in range(last_number, nbr_layer):
                    #         exist = False
                    #         for lay in commande[gateau_id]['moule'][current_moule - 1]['layer']:
                    #             if lay['gout_creme'] == request.form.getlist('gout_creme')[x]:
                    #                 commande[gateau_id]['moule'][current_moule - 1]['nbr'] -= 1
                    #                 exist = True
                    #
                    #         if not exist:
                    #             layer = {}
                    #
                    #             layer['gout_creme'] = request.form.getlist('gout_creme')[x]
                    #             gout_creme = Param.get_by_id(int(layer['gout_creme']))
                    #             layer['gout_creme_name'] = gout_creme.name
                    #
                    #             layer['imbibage'] = request.form.getlist('imbibage')[x]
                    #             if int(layer['imbibage']):
                    #                 imbibage = Param.get_by_id(int(layer['imbibage']))
                    #                 layer['imbibage_name'] = imbibage.name
                    #
                    #             layer['coulis'] = request.form.getlist('coulis')[x]
                    #             if int(layer['coulis']):
                    #                 coulis = Param.get_by_id(int(layer['coulis']))
                    #                 layer['coulis_name'] = coulis.name
                    #
                    #             commande[gateau_id]['moule'][current_moule - 1]['layer'].append(layer)
                    #
                    #     last_number = nombre_layer
                    #     # current_moule += 1
                    # else:
                    moule = {}
                    moule['choix'] = int(request.form.getlist('moule_choix')[current_moule])
                    choix = Param.get_by_id(int(request.form.getlist('moule_choix')[current_moule]))
                    moule['choix_name'] = choix.name
                    moule['qte'] = int(request.form.getlist('qte_moule')[current_moule])

                    moule['identique'] = []
                    nombre_identique = int(request.form.getlist('identique_moule')[current_moule])
                    moule['nbr_identique'] = nombre_identique
                    nbr_identique = nombre_identique

                    if current_moule > 0:
                        nbr_identique = nbr_identique + last_identique

                    for x in range(last_identique, nbr_identique):
                        identique = {}
                        identique['moule_choix_identique'] = request.form.getlist('moule_choix_identique')[x]
                        choix_identique = Param.get_by_id(int(request.form.getlist('moule_choix_identique')[x]))
                        if choix.name == choix_identique.name:
                            moule['nbr_identique'] -= 1
                            moule['qte'] += int(request.form.getlist('qte_moule_identique')[x])
                        else:
                            identique['moule_choix_identique_name'] = choix_identique.name
                            identique['qte_moule_identique'] = request.form.getlist('qte_moule_identique')[x]
                            moule['identique'].append(identique)

                    last_identique = nbr_identique

                    moule['layer'] = []
                    nombre_layer = int(request.form.getlist('nbre_layer')[current_moule])
                    moule['nbr'] = nombre_layer
                    nbr_layer = nombre_layer

                    if current_moule > 0:
                        nbr_layer = nombre_layer + last_number

                    for x in range(last_number, nbr_layer):
                        exist = False
                        for lay in moule['layer']:
                            if lay['gout_creme'] == request.form.getlist('gout_creme')[x]:
                                moule['nbr'] -= 1
                                exist = True

                        if not exist:
                            layer = {}

                            layer['gout_creme'] = request.form.getlist('gout_creme')[x]
                            gout_creme = Param.get_by_id(int(layer['gout_creme']))
                            layer['gout_creme_name'] = gout_creme.name

                            layer['imbibage'] = request.form.getlist('imbibage')[x]
                            if int(layer['imbibage']):
                                imbibage = Param.get_by_id(int(layer['imbibage']))
                                layer['imbibage_name'] = imbibage.name

                            layer['coulis'] = request.form.getlist('coulis')[x]
                            if int(layer['coulis']):
                                coulis = Param.get_by_id(int(layer['coulis']))
                                layer['coulis_name'] = coulis.name

                            moule['layer'].append(layer)

                    last_number = nombre_layer
                    current_moule += 1
                    commande[gateau_id]['moule'].append(moule)

        else:

            produit['type_produit'] = '1'
            produit['categorie'] = str(choix_categorie.key.id())
            produit['categorie_name'] = choix_categorie.name
            produit['type_produit_id'] = produitGateau.name
            produit['nbre_part'] = request.form['interval']
            produit['type_gateau'] = str(choix_type_gateau.key.id())
            produit['type_gateau_name'] = choix_type_gateau.name

            produit['price'] = 0
            if prix_gateaux:
                produit['price'] = prix_gateaux.prix
            produit['observation'] = request.form['observation']

            produit['impression'] = '0'
            if request.form.getlist('impression'):
                produit['impression'] = '1'

            produit['pate'] = '0'
            if request.form.getlist('pate'):
                produit['pate'] = '1'

            produit['moule'] = []

            current_moule = 0
            last_number = 0
            last_identique = 0
            for moules in request.form.getlist('moule_choix'):

                if current_moule == 0:
                    moule = {}
                    moule['choix'] = int(request.form.getlist('moule_choix')[current_moule])
                    choix = Param.get_by_id(int(request.form.getlist('moule_choix')[current_moule]))
                    moule['choix_name'] = choix.name
                    moule['qte'] = int(request.form.getlist('qte_moule')[current_moule])

                    moule['identique'] = []
                    nombre_identique = int(request.form.getlist('identique_moule')[current_moule])
                    moule['nbr_identique'] = nombre_identique
                    nbr_identique = nombre_identique

                    if current_moule > 0:
                        nbr_identique = nbr_identique + last_identique

                    for x in range(last_identique, nbr_identique):
                        identique = {}
                        identique['moule_choix_identique'] = request.form.getlist('moule_choix_identique')[x]
                        choix_identique = Param.get_by_id(int(request.form.getlist('moule_choix_identique')[x]))
                        if choix.name == choix_identique.name:
                            moule['nbr_identique'] -= 1
                            moule['qte'] += int(request.form.getlist('qte_moule_identique')[x])
                        else:
                            identique['moule_choix_identique_name'] = choix_identique.name
                            identique['qte_moule_identique'] = request.form.getlist('qte_moule_identique')[x]
                            moule['identique'].append(identique)

                    last_identique = nbr_identique

                    moule['layer'] = []
                    nombre_layer = int(request.form.getlist('nbre_layer')[current_moule])
                    moule['nbr'] = nombre_layer
                    nbr_layer = nombre_layer

                    if current_moule > 0:
                        nbr_layer = nombre_layer + last_number

                    for x in range(last_number, nbr_layer):
                        exist = False
                        for lay in moule['layer']:
                            if lay['gout_creme'] == request.form.getlist('gout_creme')[x]:
                                moule['nbr'] -= 1
                                exist = True

                        if not exist:
                            layer = {}

                            layer['gout_creme'] = request.form.getlist('gout_creme')[x]
                            gout_creme = Param.get_by_id(int(layer['gout_creme']))
                            layer['gout_creme_name'] = gout_creme.name

                            layer['imbibage'] = request.form.getlist('imbibage')[x]
                            if int(layer['imbibage']):
                                imbibage = Param.get_by_id(int(layer['imbibage']))
                                layer['imbibage_name'] = imbibage.name

                            layer['coulis'] = request.form.getlist('coulis')[x]
                            if int(layer['coulis']):
                                coulis = Param.get_by_id(int(layer['coulis']))
                                layer['coulis_name'] = coulis.name

                            moule['layer'].append(layer)

                    last_number = nombre_layer
                    current_moule += 1
                    produit['moule'].append(moule)
                else:
                    # if int(request.form.getlist('moule_choix')[current_moule]) == int(request.form.getlist('moule_choix')[current_moule - 1]):
                    #
                    #     produit['moule'][current_moule - 1]['qte'] += int(request.form.getlist('qte_moule')[current_moule])
                    #
                    #     nombre_identique = int(request.form.getlist('identique_moule')[current_moule])
                    #     produit['moule'][current_moule - 1]['nbr_identique'] += nombre_identique
                    #     nbr_identique = nombre_identique
                    #
                    #     if current_moule > 0:
                    #         nbr_identique += last_identique
                    #
                    #     for x in range(last_identique, nbr_identique):
                    #         identique = {}
                    #         identique['moule_choix_identique'] = request.form.getlist('moule_choix_identique')[x]
                    #         choix_identique = Param.get_by_id(int(request.form.getlist('moule_choix_identique')[x]))
                    #         if produit['moule'][current_moule - 1]['choix_name'] == choix_identique.name:
                    #             produit['moule'][current_moule - 1]['nbr_identique'] -= 1
                    #             produit['moule'][current_moule - 1]['qte'] += int(
                    #                 request.form.getlist('qte_moule_identique')[x])
                    #         else:
                    #             identique['moule_choix_identique_name'] = choix_identique.name
                    #             identique['qte_moule_identique'] = request.form.getlist('qte_moule_identique')[x]
                    #             produit['moule'][current_moule - 1]['identique'].append(identique)
                    #
                    #     last_identique = nbr_identique
                    #
                    #     nombre_layer = int(request.form.getlist('nbre_layer')[current_moule])
                    #     produit['moule'][current_moule - 1]['nbr'] += nombre_layer
                    #     nbr_layer = nombre_layer
                    #
                    #     if current_moule > 0:
                    #         nbr_layer = nombre_layer + last_number
                    #
                    #     for x in range(last_number, nbr_layer):
                    #         exist = False
                    #         for lay in produit['moule'][current_moule - 1]['layer']:
                    #             if lay['gout_creme'] == request.form.getlist('gout_creme')[x]:
                    #                 produit['moule'][current_moule - 1]['nbr'] -= 1
                    #                 exist = True
                    #
                    #         if not exist:
                    #             layer = {}
                    #
                    #             layer['gout_creme'] = request.form.getlist('gout_creme')[x]
                    #             gout_creme = Param.get_by_id(int(layer['gout_creme']))
                    #             layer['gout_creme_name'] = gout_creme.name
                    #
                    #             layer['imbibage'] = request.form.getlist('imbibage')[x]
                    #             if int(layer['imbibage']):
                    #                 imbibage = Param.get_by_id(int(layer['imbibage']))
                    #                 layer['imbibage_name'] = imbibage.name
                    #
                    #             layer['coulis'] = request.form.getlist('coulis')[x]
                    #             if int(layer['coulis']):
                    #                 coulis = Param.get_by_id(int(layer['coulis']))
                    #                 layer['coulis_name'] = coulis.name
                    #
                    #             produit['moule'][current_moule - 1]['layer'].append(layer)
                    #
                    #     last_number = nombre_layer
                    #     # current_moule += 1
                    # else:
                    moule = {}
                    moule['choix'] = int(request.form.getlist('moule_choix')[current_moule])
                    choix = Param.get_by_id(int(request.form.getlist('moule_choix')[current_moule]))
                    moule['choix_name'] = choix.name
                    moule['qte'] = int(request.form.getlist('qte_moule')[current_moule])

                    moule['identique'] = []
                    nombre_identique = int(request.form.getlist('identique_moule')[current_moule])
                    moule['nbr_identique'] = nombre_identique
                    nbr_identique = nombre_identique

                    if current_moule > 0:
                        nbr_identique = nbr_identique + last_identique

                    for x in range(last_identique, nbr_identique):
                        identique = {}
                        identique['moule_choix_identique'] = request.form.getlist('moule_choix_identique')[x]
                        choix_identique = Param.get_by_id(int(request.form.getlist('moule_choix_identique')[x]))
                        if choix.name == choix_identique.name:
                            moule['nbr_identique'] -= 1
                            moule['qte'] += int(request.form.getlist('qte_moule_identique')[x])
                        else:
                            identique['moule_choix_identique_name'] = choix_identique.name
                            identique['qte_moule_identique'] = request.form.getlist('qte_moule_identique')[x]
                            moule['identique'].append(identique)

                    last_identique = nbr_identique

                    moule['layer'] = []
                    nombre_layer = int(request.form.getlist('nbre_layer')[current_moule])
                    moule['nbr'] = nombre_layer
                    nbr_layer = nombre_layer

                    if current_moule > 0:
                        nbr_layer = nombre_layer + last_number

                    for x in range(last_number, nbr_layer):
                        exist = False
                        for lay in moule['layer']:
                            if lay['gout_creme'] == request.form.getlist('gout_creme')[x]:
                                moule['nbr'] -= 1
                                exist = True

                        if not exist:
                            layer = {}

                            layer['gout_creme'] = request.form.getlist('gout_creme')[x]
                            gout_creme = Param.get_by_id(int(layer['gout_creme']))
                            layer['gout_creme_name'] = gout_creme.name

                            layer['imbibage'] = request.form.getlist('imbibage')[x]
                            if int(layer['imbibage']):
                                imbibage = Param.get_by_id(int(layer['imbibage']))
                                layer['imbibage_name'] = imbibage.name

                            layer['coulis'] = request.form.getlist('coulis')[x]
                            if int(layer['coulis']):
                                coulis = Param.get_by_id(int(layer['coulis']))
                                layer['coulis_name'] = coulis.name

                            moule['layer'].append(layer)

                    last_number = nombre_layer
                    current_moule += 1
                    produit['moule'].append(moule)

            commande.append(produit)

        session['commande'] = commande
        flash('Enregistement effectue avec succes', 'success')
        return redirect(url_for('commande.creer'))

    return render_template('commande/creer_gateaux.html', **locals())


@prefix.route('/creer/cupcake', methods=['GET', 'POST'])
@prefix.route('/creer/cupcake/<int:gateau_id>', methods=['GET', 'POST'])
@login_required
def creerCupcake(gateau_id=None):
    produitGateau = Produit.query(
        Produit.type_produit == 3
    ).get()

    typegateau_list = TypeGateaux.query(
        TypeGateaux.pr_sable == False
    ).order(TypeGateaux.name)

    gout_creme_list = Param.query(
        Param.type_data == 'gouts cremes'
    ).order(Param.name)

    imbibage_list = Param.query(
        Param.type_data == 'imbibages'
    ).order(Param.name)

    fourrage_list = Param.query(
        Param.type_data == 'fourrages'
    ).order(Param.name)

    coulis_list = Param.query(
        Param.type_data == 'coulis'
    ).order(Param.name)

    couleur_list = Param.query(
        Param.type_data == 'couleurs cup'
    ).order(Param.name)

    topping_list = Param.query(
        Param.type_data == 'topping'
    ).order(Param.name)

    current_gateau = None
    if gateau_id or gateau_id == 0:
        current_gateau = session.get('commande')[gateau_id]

    if request.method == 'POST':

        commande = []
        if session.get('commande'):
            commande = session.get('commande')

        if gateau_id or gateau_id == 0:

            commande[gateau_id]['type_produit'] = '3'
            commande[gateau_id]['type_produit_id'] = produitGateau.name

            commande[gateau_id]['price'] = 0
            if produitGateau:
                commande[gateau_id]['price'] = produitGateau.prix * int(request.form['nbre_part'])

            commande[gateau_id]['observation'] = request.form['observation']

            commande[gateau_id]['impression'] = '0'
            if request.form['input_impression'] == '1':
                commande[gateau_id]['impression'] = '1'

            commande[gateau_id]['pate'] = '0'
            if request.form['input_pate'] == '1':
                commande[gateau_id]['pate'] = '1'

            commande[gateau_id]['nbre_part'] = request.form['nbre_part']

            choix_type_gateau = TypeGateaux.get_by_id(int(request.form['typegateaux']))

            commande[gateau_id]['type_gateau'] = str(choix_type_gateau.key.id())
            commande[gateau_id]['type_gateau_name'] = choix_type_gateau.name

            commande[gateau_id]['gout_creme'] = request.form['gout_creme']
            gout_creme = Param.get_by_id(int(request.form['gout_creme']))
            commande[gateau_id]['gout_creme_name'] = gout_creme.name

            commande[gateau_id]['imbibage'] = request.form['imbibage']
            if int(request.form['imbibage']):
                imbibage = Param.get_by_id(int(request.form['imbibage']))
                commande[gateau_id]['imbibage_name'] = imbibage.name

            commande[gateau_id]['coulis'] = request.form['coulis']
            if int(request.form['coulis']):
                coulis = Param.get_by_id(int(request.form['coulis']))
                commande[gateau_id]['coulis_name'] = coulis.name

            commande[gateau_id]['fourrage'] = request.form['fourrage']
            if int(request.form['fourrage']):
                fourrage = Param.get_by_id(int(request.form['fourrage']))
                commande[gateau_id]['fourrage_name'] = fourrage.name

            commande[gateau_id]['couleur_cup'] = request.form['couleur_cup']
            if int(request.form['couleur_cup']):
                couleur_cup = Param.get_by_id(int(request.form['couleur_cup']))
                commande[gateau_id]['couleur_cup_name'] = couleur_cup.name

            commande[gateau_id]['topping'] = request.form['topping']
            if int(request.form['topping']):
                topping = Param.get_by_id(int(request.form['topping']))
                commande[gateau_id]['topping_name'] = topping.name

        else:

            for x in range(0, int(request.form['nbre_layer'])):
                produit = {}
                produit['type_produit'] = '3'
                produit['type_produit_id'] = produitGateau.name

                produit['price'] = 0
                if produitGateau:
                    produit['price'] = produitGateau.prix * int(request.form.getlist('nbre_part')[x])

                produit['observation'] = request.form.getlist('observation')[x]

                produit['impression'] = '0'
                if request.form.getlist('input_impression')[x] == '1':
                    produit['impression'] = '1'

                produit['pate'] = '0'
                if request.form.getlist('input_pate')[x] == '1':
                    produit['pate'] = '1'

                produit['nbre_part'] = request.form.getlist('nbre_part')[x]

                choix_type_gateau = TypeGateaux.get_by_id(int(request.form.getlist('typegateaux')[x]))

                produit['type_gateau'] = str(choix_type_gateau.key.id())
                produit['type_gateau_name'] = choix_type_gateau.name

                produit['gout_creme'] = request.form.getlist('gout_creme')[x]
                gout_creme = Param.get_by_id(int(request.form.getlist('gout_creme')[x]))
                produit['gout_creme_name'] = gout_creme.name

                produit['imbibage'] = request.form.getlist('imbibage')[x]
                if int(request.form.getlist('imbibage')[x]):
                    imbibage = Param.get_by_id(int(request.form.getlist('imbibage')[x]))
                    produit['imbibage_name'] = imbibage.name

                produit['coulis'] = request.form.getlist('coulis')[x]
                if int(request.form.getlist('coulis')[x]):
                    coulis = Param.get_by_id(int(request.form.getlist('coulis')[x]))
                    produit['coulis_name'] = coulis.name

                produit['fourrage'] = request.form.getlist('fourrage')[x]
                if int(request.form.getlist('fourrage')[x]):
                    fourrage = Param.get_by_id(int(request.form.getlist('fourrage')[x]))
                    produit['fourrage_name'] = fourrage.name

                produit['couleur_cup'] = request.form.getlist('couleur_cup')[x]
                if int(request.form.getlist('couleur_cup')[x]):
                    couleur_cup = Param.get_by_id(int(request.form.getlist('couleur_cup')[x]))
                    produit['couleur_cup_name'] = couleur_cup.name

                produit['topping'] = request.form.getlist('topping')[x]
                if int(request.form.getlist('topping')[x]):
                    topping = Param.get_by_id(int(request.form.getlist('topping')[x]))
                    produit['topping_name'] = topping.name

                commande.append(produit)

        session['commande'] = commande

        flash('Enregistement effectue avec succes', 'success')
        return redirect(url_for('commande.creer'))

    return render_template('commande/creer_cupcake.html', **locals())


@prefix.route('/creer/sable', methods=['GET', 'POST'])
@prefix.route('/creer/sable/<int:gateau_id>', methods=['GET', 'POST'])
@login_required
def creerSable(gateau_id=None):
    produitGateau = Produit.query(
        Produit.type_produit == 2
    ).get()

    form_list = TypeGateaux.query(
        TypeGateaux.pr_sable == True
    )

    couleur_ruban = Param.query(
        Param.type_data == 'couleurs rubans'
    ).order(Param.name)

    if gateau_id or gateau_id == 0:
        current_gateau = session.get('commande')[gateau_id]

    if request.method == 'POST':

        commande = []
        if session.get('commande'):
            commande = session.get('commande')

        produit = {}

        choix_type_gateau = TypeGateaux.get_by_id(int(request.form['forme']))
        choix_ruban = Param.get_by_id(int(request.form['ruban']))

        if gateau_id or gateau_id == 0:

            commande[gateau_id]['type_produit'] = '2'
            commande[gateau_id]['type_produit_id'] = produitGateau.name
            commande[gateau_id]['nbre_part'] = request.form['qte']
            commande[gateau_id]['type_gateau'] = str(choix_type_gateau.key.id())
            commande[gateau_id]['type_gateau_name'] = choix_type_gateau.name
            commande[gateau_id]['ruban'] = request.form['ruban']
            commande[gateau_id]['ruban_name'] = choix_ruban.name

            commande[gateau_id]['price'] = 0
            if produitGateau:
                commande[gateau_id]['price'] = produitGateau.prix * int(request.form['qte'])
            commande[gateau_id]['observation'] = request.form['observation']

            commande[gateau_id]['impression'] = '0'
            if request.form.getlist('impression'):
                commande[gateau_id]['impression'] = '1'

            commande[gateau_id]['pate'] = '0'
            if request.form.getlist('pate'):
                commande[gateau_id]['pate'] = '1'

            commande[gateau_id]['emballage'] = '0'
            if request.form.getlist('emballage'):
                commande[gateau_id]['emballage'] = '1'

        else:

            produit['type_produit'] = '2'
            produit['type_produit_id'] = produitGateau.name
            produit['nbre_part'] = request.form['qte']
            produit['type_gateau'] = str(choix_type_gateau.key.id())
            produit['type_gateau_name'] = choix_type_gateau.name
            produit['ruban'] = request.form['ruban']
            produit['ruban_name'] = choix_ruban.name

            produit['price'] = 0
            if produitGateau:
                produit['price'] = produitGateau.prix * int(request.form['qte'])
            produit['observation'] = request.form['observation']

            produit['impression'] = '0'
            if request.form.getlist('impression'):
                produit['impression'] = '1'

            produit['pate'] = '0'
            if request.form.getlist('pate'):
                produit['pate'] = '1'

            produit['emballage'] = '0'
            if request.form.getlist('emballage'):
                produit['emballage'] = '1'

            commande.append(produit)

        session['commande'] = commande

        flash('Enregistement effectue avec succes', 'success')
        return redirect(url_for('commande.creer'))

    return render_template('commande/creer_sable.html', **locals())


@prefix.route('/creer/delete/<int:produit_id>')
@login_required
def delete(produit_id):
    commande = session.get('commande')
    commande.pop(produit_id)
    flash('Suppression effectuee avec succes', 'success')

    return redirect(url_for('commande.creer'))


@prefix.route('/creer/gateau/modele/moule')
@login_required
def moule():
    moule_list = Param.query(
        Param.type_data == 'moules'
    ).order(Param.name)

    gout_creme_list = Param.query(
        Param.type_data == 'gouts cremes'
    ).order(Param.name)

    imbibage_list = Param.query(
        Param.type_data == 'imbibages'
    ).order(Param.name)

    fourrage_list = Param.query(
        Param.type_data == 'fourrages'
    ).order(Param.name)

    coulis_list = Param.query(
        Param.type_data == 'coulis'
    ).order(Param.name)

    return render_template('commande/model/moule.html', **locals())


@prefix.route('/creer/gateau/modele/layer')
@login_required
def layer():
    typegateau_list = TypeGateaux.query(
        TypeGateaux.pr_sable == False
    ).order(TypeGateaux.name)

    gout_creme_list = Param.query(
        Param.type_data == 'gouts cremes'
    ).order(Param.name)

    imbibage_list = Param.query(
        Param.type_data == 'imbibages'
    ).order(Param.name)

    fourrage_list = Param.query(
        Param.type_data == 'fourrages'
    ).order(Param.name)

    coulis_list = Param.query(
        Param.type_data == 'coulis'
    ).order(Param.name)

    couleur_list = Param.query(
        Param.type_data == 'couleurs cup'
    ).order(Param.name)

    topping_list = Param.query(
        Param.type_data == 'topping'
    ).order(Param.name)

    return render_template('commande/model/layer.html', **locals())


@prefix.route('/creer/gateau/modele/identique')
@login_required
def identique_moule():
    moule_list = Param.query(
        Param.type_data == 'moules'
    ).order(Param.name)

    return render_template('commande/model/identique.html', **locals())


@prefix.route('/commander/ajustement/<int:gateau_id>', methods=['GET', 'POST'])
@login_required
def ProduitAjustementPrix(gateau_id):
    current_commande = session.get('commande')[gateau_id]

    success = False

    if request.method == 'POST' and request.form['ajuster']:
        session.get('commande')[gateau_id]['price'] = float(request.form['ajuster'])
        success = True

    return render_template('commande/commande_ajustement.html', **locals())


@prefix.route('/commander/infos', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'commande'), ['edit']])
def infosClient():

    creation = True
    client_list = Users.query(Users.client == True)
    form_client = FormUser()
    if session.get('client_commande'):
        if session.get('client_commande')['id']:
            form_client.id.data = session.get('client_commande')['id']
        form_client.name.data = session.get('client_commande')['name']
        form_client.email.data = session.get('client_commande')['email']
        form_client.phone.data = session.get('client_commande')['phone']

    form_client.client.data = 1
    form_client.profil.choices = [(0, 'Selectionnez un profil')]

    forme = FormCommande()
    if session.get('evenement_commande') and request.method != 'POST':
        event_give = Event.get_by_id(int(session.get('evenement_commande')['event_id']))
        forme.event.data = str(event_give.key.id())
        forme.theme.data = session.get('evenement_commande')['theme']

        forme.exixt_at_date.data = '0'
        if session.get('evenement_commande')['exixt_at_date']:
            forme.exixt_at_date.data = '1'

        forme.date_anniv.data = session.get('evenement_commande')['date_anniv']
        forme.age.data = session.get('evenement_commande')['age']
        forme.concerne.data = session.get('evenement_commande')['concerne']
        forme.date_livre.data = session.get('evenement_commande')['date_liv']
        forme.heure_livre.data = session.get('evenement_commande')['heure_liv']
        forme.info.data = session.get('evenement_commande')['autre']

    theme = False
    if forme.exixt_at_date.data != '0':
        theme = True

    list_event = Event.query()

    if request.method == 'POST':

        client_exist = None
        if form_client.id.data:
            client_exist = Users.get_by_id(int(form_client.id.data))
            form_client.name.data = client_exist.name
            form_client.email.data = client_exist.email
            form_client.phone.data = client_exist.phone

        if form_client.validate_on_submit() and forme.validate_on_submit():

            session['client_commande'] = {}
            session['evenement_commande'] = {}

            Client = {}
            Client['id'] = None
            if client_exist:
                Client['id'] = client_exist.key.id()

            Client['name'] = form_client.name.data
            Client['email'] = form_client.email.data
            Client['phone'] = form_client.phone.data
            Client['accompte'] = 0.0
            session['client_commande'] = Client

            evenement = {}
            event_select = Event.get_by_id(int(forme.event.data))
            evenement['event_id'] = event_select.key.id()
            evenement['event_name'] = event_select.name
            evenement['theme'] = forme.theme.data
            evenement['exixt_at_date'] = False
            if forme.exixt_at_date.data != '0':
                evenement['exixt_at_date'] = True
            evenement['date_anniv'] = forme.date_anniv.data
            evenement['age'] = forme.age.data
            evenement['concerne'] = forme.concerne.data
            evenement['date_liv'] = forme.date_livre.data
            evenement['heure_liv'] = forme.heure_livre.data
            evenement['autre'] = forme.info.data

            session['evenement_commande'] = evenement

            return redirect(url_for('commande.creer'))

    return render_template('commande/infos_client.html', **locals())


@prefix.route('/commander/recapitulatif', methods=['GET', 'POST'])
@login_required
def recap_commande():
    liste_commande = session.get('commande')
    list_part = global_part

    total = 0

    for produit in liste_commande:
        montant = produit['price']
        total = total + montant

    total_accompte = total
    if session.get('client_commande')['accompte']:
        total_accompte = total - session.get('client_commande')['accompte']

    return render_template('commande/recapitulatif.html', **locals())


@prefix.route('/creer/accompte', methods=['GET', 'POST'])
@login_required
def accompte_commande():
    current_commande = session.get('client_commande')

    success = False

    if request.method == 'POST' and request.form['accompte']:
        session.get('client_commande')['accompte'] = float(request.form['accompte'])
        success = True

    return render_template("commande/commande_accompte.html", **locals())


@prefix.route('/creer/annuler')
@login_required
def annuler():
    session['commande'] = []
    session['client_commande'] = []
    session['evenement_commande'] = []

    return redirect(url_for('commande.creer'))


@prefix.route('/commander/find/customer/', methods=['POST'])
@login_required
def find_customer():
    customer_id = int(request.json['client'])

    customer = Users.get_by_id(customer_id)

    data = json.dumps({
        'id': customer.key.id(),
        'name': customer.name,
        'email': customer.email,
        'phone': customer.phone,
        'statut': 'OK'
    })

    return data


@prefix.route('/creer/terminer')
@login_required
def commande_terminer():
    info_client = session.get('client_commande')

    if info_client['id']:
        client_id = Users.get_by_id(int(info_client['id']))
        client_id = client_id.key
    else:
        Client = Users()
        Client.name = info_client['name']
        Client.phone = info_client['phone']
        Client.email = info_client['email']
        Client.client = True
        client_id = Client.put()

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    event_commande = session.get('evenement_commande')
    commande_list = session.get('commande')

    commande = Commande()
    commande.user = client_id
    commande.dateCmd = function.date_convert(date_auto_nows)
    commande.dateLiv = function.date_convert(event_commande['date_liv'])
    commande.timeLiv = function.time_convert(event_commande['heure_liv'])
    commande.infos = event_commande['autre']
    commande.theme = event_commande['theme']
    commande.age = event_commande['age']

    number_commande = Commande.query().count()
    number_commande += 1
    current_year = function.date_convert(date_auto_nows).year
    format_ref = "CC/" + str(current_year) + '/' + str(number_commande)

    commande.ref = format_ref

    if event_commande['exixt_at_date']:
        commande.nameConcerne = event_commande['concerne']
        commande.dateAnniv = function.date_convert(event_commande['date_anniv'])

    total = 0
    for produit in commande_list:
        montant = produit['price']
        total = total + montant
    commande.montant = total

    event_cmd = Event.get_by_id(int(event_commande['event_id']))
    commande.event_id = event_cmd.key


    day = datetime.date.today().strftime('%d/%m/%Y')
    dt = datetime.datetime.strptime(day, '%d/%m/%Y')
    start = dt
    end = start + timedelta(days=1)

    import requests
    dateLivar = commande.dateLiv

    if float(info_client['accompte']) and float(info_client['accompte']) == commande.montant:
        commande.mail_solde = 1

    commande = commande.put()


    user_curent = Users.get_by_id(int(request.args.get('user')))
    activite = Activite()
    activite.entite = 'Commande'
    activite.action = 1
    activite.infos = 'Creation de la commande'
    activite.user = user_curent.key
    activite.date = function.datetime_convert(date_auto_nows)
    activite.commande = commande
    activite.put()

    # Ajout du versement en cours
    if info_client['accompte']:
        versement = Versement()
        versement.commande_id = commande
        versement.dateVers = function.date_convert(date_auto_nows)
        versement.montant = float(info_client['accompte'])
        versement.put()

    # Ajout des produits de la commande
    for produits in commande_list:
        # insertionn des gateaux
        if produits['type_produit'] != '3':

            produit = ProduitCommander()
            produit.commande_id = commande

            if produits['type_produit'] == '1':
                categorie = Param.get_by_id(int(produits['categorie']))
                produit.categorie_id = categorie.key

                produit.qte = 1
                produit.nbrPart = produits['nbre_part']

            if produits['type_produit'] == '2':
                produit.qte = int(produits['nbre_part'])

                ruban = Param.get_by_id(int(produits['ruban']))
                produit.couleurRuban_id = ruban.key

                if produits['emballage'] == '1':
                    produit.emballage = True

            type_produit = Produit.query(Produit.type_produit == int(produits['type_produit'])).get()
            produit.produit_id = type_produit.key

            produit.observation = produits['observation']

            if produits['impression'] == '1':
                produit.impression = True

            if produits['pate'] == '1':
                produit.pate = True

            produit.prix = produits['price']
            type_gateau = TypeGateaux.get_by_id(int(produits['type_gateau']))
            produit.typeGateau_id = type_gateau.key
            produit_save = produit.put()

            # gestions des moules des produits gateaux
            if produits['type_produit'] == '1':

                position = 1
                for moule in produits['moule']:

                    moule_produit = MouleProduit()

                    moule_choice = Param.get_by_id(int(moule['choix']))
                    moule_produit.moule_id = moule_choice.key

                    moule_produit.qte = int(moule['qte'])
                    moule_produit.produitCommander_id = produit_save

                    moule_produit.position = position

                    moule_save = moule_produit.put()

                    position += 1

                    layer_position = 1
                    for layer in moule['layer']:
                        composition = Composition()
                        composition.position = layer_position
                        composition.mouleProduit_id = moule_save

                        if int(layer['coulis']):
                            coulis = Param.get_by_id(int(layer['coulis']))
                            composition.coulis_id = coulis.key

                        if int(layer['gout_creme']):
                            gout_creme = Param.get_by_id(int(layer['gout_creme']))
                            composition.goutcreme_id = gout_creme.key

                        if int(layer['imbibage']):
                            imbibage = Param.get_by_id(int(layer['imbibage']))
                            composition.imbibage_id = imbibage.key

                        composition.put()
                        layer_position += 1

                    # ajout des moules identiques
                    for identique in moule['identique']:
                        moule_identique = MouleProduit()
                        moule_identique.produitCommander_id = produit_save

                        Identic = Param.get_by_id(int(identique['moule_choix_identique']))
                        moule_identique.moule_id = Identic.key

                        moule_identique.qte = int(identique['qte_moule_identique'])
                        moule_identique.identique = moule_save.id()
                        moule_identique.put()

        # ajout des layers pour les produits cupcake
        if produits['type_produit'] == '3':
            layer_position = 1

            produit = ProduitCommander()
            produit.commande_id = commande

            type_produit = Produit.query(Produit.type_produit == int(produits['type_produit'])).get()
            produit.produit_id = type_produit.key

            produit.observation = produits['observation']

            produit.qte = int(produits['nbre_part'])
            if produits['impression'] == '1':
                produit.impression = True

            if produits['pate'] == '1':
                produit.pate = True

            produit.prix = produits['price']
            type_gateau = TypeGateaux.get_by_id(int(produits['type_gateau']))
            produit.typeGateau_id = type_gateau.key
            produit_save = produit.put()

            composition = Composition()
            composition.position = layer_position
            composition.produitCommander_id = produit_save

            if int(produits['coulis']):
                coulis = Param.get_by_id(int(produits['coulis']))
                composition.coulis_id = coulis.key

            if int(produits['fourrage']):
                fourrage = Param.get_by_id(int(produits['fourrage']))
                composition.fourage_id = fourrage.key

            if int(produits['gout_creme']):
                gout_creme = Param.get_by_id(int(produits['gout_creme']))
                composition.goutcreme_id = gout_creme.key

            if int(produits['imbibage']):
                imbibage = Param.get_by_id(int(produits['imbibage']))
                composition.imbibage_id = imbibage.key

            if int(produits['couleur_cup']):
                couleur_cup = Param.get_by_id(int(produits['couleur_cup']))
                composition.couleur_cup_id = couleur_cup.key

            if int(produits['topping']):
                topping = Param.get_by_id(int(produits['topping']))
                composition.topping_id = topping.key

            composition.put()

    if dateLivar == end:
        send = requests.get("http://creative-cake.appspot.com/commande/planning/day/rappel").content

    # try:
    #     calendrier = requests.get("http://creative-cake.appspot.com/commande/planning/add_calendar/"+str(commande.id())).content
    # except requests.exceptions.ConnectionError as e:
    #     pass


    session['commande'] = []
    session['client_commande'] = []
    session['evenement_commande'] = []

    return redirect(url_for('commande.facture', id_commande=commande.id()))


@prefix.route('/facture/<int:id_commande>')
@login_required
def facture(id_commande):
    list_part = global_part
    commande = Commande.get_by_id(id_commande)

    produit_commande = ProduitCommander.query(
        ProduitCommander.commande_id == commande.key
    )
    
    update = False
    if commande.dateLiv >= datetime.date.today():
        update = True

    total = commande.montant
    versement = commande.montant_versment()

    return render_template('commande/facture.html', **locals())


@prefix.route('/facture/annuler/<int:id_commande>')
@login_required
@roles_required([('super_admin', 'annuler_facture_commande')])
def facture_annuler(id_commande):

    import requests
    commande = Commande.get_by_id(id_commande)

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")


    user_curent = Users.get_by_id(int(request.args.get('user')))
    activite = Activite()
    activite.entite = 'Annulation/Relance'
    activite.action = 4

    if commande.annule:
        commande.annule = False
        produit_commande = ProduitCommander.query(
            ProduitCommander.commande_id == commande.key
        )
        for produit in produit_commande:
            # try:
            #     requests.get("http://creative-cake.appspot.com/commande/planning/delete_event/"+str(produit.key.id())).content
            # except requests.exceptions.ConnectionError as e:
            #     pass
            produit.annule = False
            produit.put()
        activite.infos = 'Relance de la commande'
        flash('Relance effectue avec succes', 'success')
    else:
        commande.annule = True
        commande.verif_calendar = False
        produit_commande = ProduitCommander.query(
            ProduitCommander.commande_id == commande.key
        )
        for produit in produit_commande:
            try:
                requests.get("http://creative-cake.appspot.com/commande/planning/delete_event/"+str(produit.key.id())).content
            except requests.exceptions.ConnectionError as e:
                pass
            produit.annule = True
            produit.put()
        activite.infos = 'Annulation de la commande'
        flash('Annulation effectue avec succes', 'success')

    commande.put()

    activite.user = user_curent.key
    activite.date = function.datetime_convert(date_auto_nows)
    activite.commande = commande.key
    activite.put()

    return redirect(url_for('commande.facture', id_commande=id_commande))


@prefix.route('/facture/versement/<int:id_commande>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'versement_facture')])
def facture_versement(id_commande):
    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    current_date = function.date_convert(date_auto_nows)

    commande = Commande.get_by_id(id_commande)

    if request.method == 'GET' and request.args.get('delete'):

        vers_del = Versement.get_by_id(int(request.args.get('delete')))

        user_curent = Users.get_by_id(int(request.args.get('user')))
        activite = Activite()
        activite.entite = 'Versement'
        activite.action = 3
        activite.infos = 'Suppression realise de '+str(vers_del.montant)
        activite.user = user_curent.key
        activite.date = current_date
        activite.commande = commande.key
        activite.put()


        vers_del.key.delete()

        return redirect(url_for('commande.facture_versement', id_commande=id_commande))

    if request.method == "POST":

        user_curent = Users.get_by_id(int(request.form['user']))
        activite = Activite()
        activite.entite = 'Versement'
        activite.action = 1
        activite.infos = 'Versement realise de '+str(request.form['versement'])
        activite.user = user_curent.key
        activite.date = function.datetime_convert(date_auto_nows)
        activite.commande = commande.key
        activite.put()

        vers = Versement()
        vers.montant = float(request.form['versement'])
        vers.dateVers = current_date
        vers.commande_id = commande.key
        vers.put()

        verse_amount = 0
        for versement in commande.versement():
            verse_amount += versement.montant

        if verse_amount == commande.montant:
            commande.mail_type = 1

        commande.mail_send = False
        commande.put()

        return redirect(url_for('commande.facture_versement', id_commande=id_commande))

    versements = Versement.query(
        Versement.commande_id == commande.key
    ).order(-Versement.dateVers)

    total_a_payer = commande.montant
    accompte = 0
    versement_cmd = Versement.query(
        Versement.commande_id == commande.key
    )
    for versement in versement_cmd:
        total_a_payer = total_a_payer - versement.montant
        accompte += versement.montant

    return render_template('commande/facture_versement.html', **locals())


@prefix.route('/commander/edit/infos/<int:id_commande>', methods=['POST', 'GET'])
@login_required
@roles_required([('super_admin', 'update_facture')])
def UpdateCommande(id_commande):

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    commande = Commande.get_by_id(id_commande)

    activite = Activite()
    activite.entite = 'Commande'
    activite.action = 2

    client_list = Users.query(Users.client == True)
    form_client = FormUser()

    if request.method == 'GET':
        form_client.id.data = commande.user.get().key.id()
        form_client.name.data = commande.user.get().name
        form_client.email.data = commande.user.get().email
        form_client.phone.data = commande.user.get().phone

    form_client.client.data = 1
    form_client.profil.choices = [(0, 'Selectionnez un profil')]

    forme = FormCommande()
    if request.method == 'GET':
        forme.event.data = str(commande.event_id.get().key.id())
        forme.theme.data = commande.theme

        forme.exixt_at_date.data = '0'
        if commande.nameConcerne:
            forme.exixt_at_date.data = '1'

        forme.date_anniv.data = function.date_convert(commande.dateAnniv).strftime('%d/%m/%Y')
        forme.age.data = commande.age
        forme.concerne.data = commande.nameConcerne
        forme.date_livre.data = function.date_convert(commande.dateLiv).strftime('%d/%m/%Y')
        forme.heure_livre.data = commande.timeLiv
        forme.info.data = commande.infos
    forme.update.data = True

    theme = False
    if forme.exixt_at_date.data != '0':
        theme = True

    list_event = Event.query()

    button_create = True

    if request.method == 'POST':

        user_curent = Users.get_by_id(int(request.form['user']))

        cli_dif = False
        if 'client_exist' in request.form:
            client_exist = Users.get_by_id(int(request.form['client_exist']))

            if client_exist.key.id() != commande.user.get().key.id():

                cli_dif = True

                activite.infos = "Modification des informations du clients"
                activite.user = user_curent.key
                activite.date = function.datetime_convert(date_auto_nows)
                activite.commande = commande.key
                activite.put()
            else:

                name_dif = False
                if 'name' in request.form and request.form['name'] != client_exist.name:
                    name_dif = True

                email_dif = False
                if 'email' in request.form and client_exist.email != request.form['email']:
                    email_dif = True

                phone_dif = False
                if 'phone' in request.form and client_exist.phone != request.form['phone']:
                    phone_dif = True

                if name_dif or email_dif or phone_dif:

                    cli_dif = True

                    activite.infos = "Modification des informations du clients"
                    activite.user = user_curent.key
                    activite.date = function.datetime_convert(date_auto_nows)
                    activite.commande = commande.key
                    activite.put()

            form_client.id.data = client_exist.key.id()

            if 'name' in request.form:
                client_exist.name = request.form['name']
                form_client.name.data = request.form['name']
            else:
                form_client.name.data = commande.user.get().name

            if 'email' in request.form:
                client_exist.email = request.form['email']
                form_client.email.data = request.form['email']
            else:
                form_client.email.data = commande.user.get().email

            if 'phone' in request.form:
                client_exist.phone = request.form['phone']
                form_client.phone.data = request.form['phone']
            else:
                form_client.phone.data = commande.user.get().phone

            client_exist.put()

        else:
            client_exist = Users()
            client_exist.name = request.form['name']
            client_exist.email = request.form['email']
            client_exist.phone = request.form['phone']
            client_exist.client = True

            client_exist.put()

            form_client.id.data = client_exist.key.id()
            form_client.name.data = client_exist.name
            form_client.email.data = client_exist.email
            form_client.phone.data = client_exist.phone

            cli_dif = True

            activite.infos = "Modification des informations du clients"
            activite.user = user_curent.key
            activite.date = function.datetime_convert(date_auto_nows)
            activite.commande = commande.key
            activite.put()



        liv_dif = False
        tim_dif = False
        the_dif = False
        if form_client.validate_on_submit() and forme.validate_on_submit():

            commande.user = client_exist.key
            event_select = Event.get_by_id(int(forme.event.data))
            commande.event_id = event_select.key

            if commande.dateLiv != function.date_convert(forme.date_livre.data):
                liv_dif = True
            if commande.timeLiv != function.time_convert(forme.heure_livre.data):
                tim_dif = True
            if commande.theme != forme.theme.data:
                the_dif = True

            commande.dateLiv = function.date_convert(forme.date_livre.data)
            commande.timeLiv = function.time_convert(forme.heure_livre.data)
            commande.theme = forme.theme.data
            commande.dateAnniv = function.date_convert(forme.date_anniv.data)
            commande.age = forme.age.data
            commande.nameConcerne = forme.concerne.data
            commande.infos = forme.info.data

            commande.mail_type = 2
            commande.mail_send = False

            commande.put()

            if cli_dif or liv_dif or tim_dif or the_dif:
                # import requests
                # try:
                #     calendrier = requests.get("http://creative-cake.appspot.com/commande/planning/update_calendar/"+str(commande.key.id())).content
                # except requests.exceptions.ConnectionError as e:
                #     pass

                activite.infos = "Modification des informations de l'evenement"
                activite.user = user_curent.key
                activite.date = function.datetime_convert(date_auto_nows)
                activite.commande = commande.key
                activite.put()

            return redirect(url_for('commande.facture', id_commande=id_commande))

    return render_template('commande/infos_client.html', **locals())


@prefix.route('/update/gateau/<int:id_commande>', methods=['GET', 'POST'])
@prefix.route('/update/gateau/<int:id_commande>/<int:gateau_id>', methods=['GET', 'POST'])
@login_required
def updateGateaux(id_commande, gateau_id=None):

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    produitGateau = Produit.query(
        Produit.type_produit == 1
    ).get()

    categorie_list = Param.query(
        Param.type_data == 'categories'
    ).order(Param.name)

    list_part = global_part

    typegateau_list = TypeGateaux.query(
        TypeGateaux.pr_sable == False
    ).order(TypeGateaux.name)

    moule_list = Param.query(
        Param.type_data == 'moules'
    ).order(Param.name)

    gout_creme_list = Param.query(
        Param.type_data == 'gouts cremes'
    ).order(Param.name)

    imbibage_list = Param.query(
        Param.type_data == 'imbibages'
    ).order(Param.name)

    fourrage_list = Param.query(
        Param.type_data == 'fourrages'
    ).order(Param.name)

    coulis_list = Param.query(
        Param.type_data == 'coulis'
    ).order(Param.name)

    current_commande = Commande.get_by_id(id_commande)


    activite = Activite()
    activite.entite = 'Gateaux'

    if gateau_id:
        current_gateau = ProduitCommander.get_by_id(gateau_id)
        
        current_commande.verif_calendar = False
        if request.method == 'POST':
            current_commande.mail_type = 2
            current_commande.mail_send = False
        current_commande.put()

        activite.action = 2
        activite.infos = 'Modification du gateau de la commande'
    else:
        current_gateau = ProduitCommander()

        activite.action = 1
        activite.infos = 'Ajout du gateau a la commande'


    if request.method == 'POST':

        choix_categorie = Param.get_by_id(int(request.form['categorie']))
        choix_type_gateau = TypeGateaux.get_by_id(int(request.form['typegateaux']))

        prix_gateaux = PrixGateaux.query(
            PrixGateaux.categorie_id == choix_categorie.key,
            PrixGateaux.interval == request.form['interval']
        ).get()

        current_gateau.categorie_id = choix_categorie.key
        current_gateau.nbrPart = request.form['interval']
        current_gateau.typeGateau_id = choix_type_gateau.key
        current_gateau.observation = request.form['observation']
        current_gateau.commande_id = current_commande.key
        current_gateau.prix = float(request.form['prix'])
        current_gateau.produit_id = produitGateau.key

        current_gateau.impression = False
        if request.form.getlist('impression'):
            current_gateau.impression = True

        current_gateau.pate = False
        if request.form.getlist('pate'):
            current_gateau.pate = True

        parent_layer = []
        for layerss in request.form.getlist('moule_layer_delete'):
            compo = Composition.get_by_id(int(layerss))
            parent_layer.append(compo.mouleProduit_id)
            compo.key.delete()

        for rest_layer in parent_layer:
            composit = Composition.query(
                Composition.mouleProduit_id == rest_layer
            ).order(Composition.position)
            i = 1
            for compo in composit:
                compo.position = i
                compo.put()
                i += 1

        for ident in request.form.getlist('moule_identique_delete'):
            identi = MouleProduit.get_by_id(int(ident))
            identi.key.delete()

        for moul in request.form.getlist('moule_delete'):
            identi = MouleProduit.get_by_id(int(moul))

            for identique in identi.nbre_identique():
                identique.key.delete()

            for layers in identi.list_composition():
                layers.key.delete()

            identi.key.delete()

        current_moule = 0
        last_number = 0
        last_identique = 0
        position = 1
        for moules in request.form.getlist('moule_choix'):

            choix = Param.get_by_id(int(moules))

            gateau_moule = MouleProduit.query(
                MouleProduit.moule_id == choix.key,
                MouleProduit.produitCommander_id == current_gateau.key,
                MouleProduit.position == position
            ).get()

            if gateau_moule:

                gateau_moule.qte = int(request.form.getlist('qte_moule')[current_moule])
                gateau_moule = gateau_moule.put()

                nombre_identique = int(request.form.getlist('identique_moule')[current_moule])
                nbr_identique = nombre_identique

                if current_moule > 0:
                    nbr_identique += last_identique

                for x in range(last_identique, nbr_identique):
                    choix_identique = Param.get_by_id(int(request.form.getlist('moule_choix_identique')[x]))
                    if choix_identique.name == choix.name:
                        flash('Le moule identique du moule ' + str(
                            current_moule + 1) + ' n\'a pas ete pris en compte car elle comporte les memes carateristiques que le moule parent',
                              'warning')
                    else:
                        identique = MouleProduit.query(
                            MouleProduit.moule_id == choix_identique.key,
                            MouleProduit.identique == gateau_moule.id()
                        ).get()

                        if identique:
                            identique.qte = int(request.form.getlist('qte_moule_identique')[x])
                            identique.put()
                        else:
                            identique = MouleProduit()
                            identique.moule_id = choix_identique.key
                            identique.identique = gateau_moule.id()
                            identique.qte = int(request.form.getlist('qte_moule_identique')[x])
                            identique.put()

                last_identique = nbr_identique

                nombre_layer = int(request.form.getlist('nbre_layer')[current_moule])
                nbr_layer = nombre_layer
                if current_moule > 0:
                    nbr_layer = nombre_layer + last_number

                position_layer = 1
                for x in range(last_number, nbr_layer):

                    gout_creme = Param.get_by_id(int(request.form.getlist('gout_creme')[x]))

                    layers = Composition.query(
                        Composition.mouleProduit_id == gateau_moule,
                        Composition.goutcreme_id == gout_creme.key,
                        Composition.position == position_layer
                    ).get()

                    if layers:
                        layers.goutcreme_id = gout_creme.key

                        layers.imbibage_id = None
                        if int(request.form.getlist('imbibage')[x]):
                            imbibage = Param.get_by_id(int(request.form.getlist('imbibage')[x]))
                            layers.imbibage_id = imbibage.key

                        layers.coulis_id = None
                        if int(request.form.getlist('coulis')[x]):
                            coulis = Param.get_by_id(int(request.form.getlist('coulis')[x]))
                            layers.coulis_id = coulis.key

                        layers.put()
                        position_layer += 1

                    else:

                        imbibage = None
                        if int(request.form.getlist('imbibage')[x]):
                            imbibage = Param.get_by_id(int(request.form.getlist('imbibage')[x]))
                            imbibage = imbibage.key

                        coulis = None
                        if int(request.form.getlist('coulis')[x]):
                            coulis = Param.get_by_id(int(request.form.getlist('coulis')[x]))
                            coulis = coulis.key

                        exit_new_layer = Composition.query(
                            Composition.mouleProduit_id == gateau_moule,
                            Composition.goutcreme_id == gout_creme.key
                        ).get()

                        if exit_new_layer:
                            exit_new_layer.imbibage_id = None
                            if imbibage:
                                exit_new_layer.imbibage_id = imbibage

                            exit_new_layer.coulis_id = None
                            if coulis:
                                exit_new_layer.coulis_id = coulis

                            exit_new_layer.put()
                        else:
                            layers = Composition()

                            layers.mouleProduit_id = gateau_moule

                            layers.goutcreme_id = gout_creme.key

                            layers.imbibage_id = None
                            if imbibage:
                                layers.imbibage_id = imbibage

                            layers.coulis_id = None
                            if coulis:
                                layers.coulis_id = coulis

                            layers.position = position_layer

                            layers.put()

                        position_layer += 1

                last_number = nombre_layer
                current_moule += 1
                position += 1

            else:

                existe_gateau_moule = MouleProduit.query(
                    MouleProduit.moule_id == choix.key,
                    MouleProduit.produitCommander_id == current_gateau.key
                ).get()

                if existe_gateau_moule:
                    if existe_gateau_moule.position != position:
                        existe_gateau_moule.qte = int(request.form.getlist('qte_moule')[current_moule])
                    else:
                        existe_gateau_moule.qte += int(request.form.getlist('qte_moule')[current_moule])
                    gateau_moule = existe_gateau_moule.put()

                else:
                    gateau_moule = MouleProduit()
                    gateau_moule.produitCommander_id = current_gateau.key
                    gateau_moule.moule_id = choix.key
                    gateau_moule.qte = int(request.form.getlist('qte_moule')[current_moule])
                    gateau_moule.position = position
                    gateau_moule = gateau_moule.put()

                nombre_identique = int(request.form.getlist('identique_moule')[current_moule])
                nbr_identique = nombre_identique

                if current_moule > 0:
                    nbr_identique += last_identique

                for x in range(last_identique, nbr_identique):
                    choix_identique = Param.get_by_id(int(request.form.getlist('moule_choix_identique')[x]))

                    if choix_identique.name == choix.name:
                        flash('Le moule identique du moule ' + str(
                            current_moule + 1) + ' n\'a pas ete pris en compte car elle comporte les memes carateristiques que le moule parent',
                              'warning')
                    else:
                        identique = MouleProduit()
                        identique.moule_id = choix_identique.key
                        identique.identique = gateau_moule.id()
                        identique.qte = int(request.form.getlist('qte_moule_identique')[x])
                        identique.put()

                last_identique = nbr_identique

                nombre_layer = int(request.form.getlist('nbre_layer')[current_moule])
                nbr_layer = nombre_layer
                if current_moule > 0:
                    nbr_layer = nombre_layer + last_number

                position_layer = 1
                for x in range(last_number, nbr_layer):

                    gout_creme = Param.get_by_id(int(request.form.getlist('gout_creme')[x]))

                    exist_layer = Composition.query(
                        Composition.mouleProduit_id == gateau_moule,
                        Composition.goutcreme_id == gout_creme.key
                    ).get()

                    if not exist_layer:

                        layers = Composition()

                        layers.mouleProduit_id = gateau_moule

                        layers.goutcreme_id = gout_creme.key

                        layers.imbibage_id = None
                        if int(request.form.getlist('imbibage')[x]):
                            imbibage = Param.get_by_id(int(request.form.getlist('imbibage')[x]))
                            layers.imbibage_id = imbibage.key

                        layers.coulis_id = None
                        if int(request.form.getlist('coulis')[x]):
                            coulis = Param.get_by_id(int(request.form.getlist('coulis')[x]))
                            layers.coulis_id = coulis.key
                        layers.position = position_layer
                        layers.put()
                    else:
                        exist_layer.imbibage_id = None
                        if int(request.form.getlist('imbibage')[x]):
                            imbibage = Param.get_by_id(int(request.form.getlist('imbibage')[x]))
                            exist_layer.imbibage_id = imbibage.key

                        exist_layer.coulis_id = None
                        if int(request.form.getlist('coulis')[x]):
                            coulis = Param.get_by_id(int(request.form.getlist('coulis')[x]))
                            exist_layer.coulis_id = coulis.key

                        exist_layer.put()
                    position_layer += 1

                last_number = nombre_layer
                current_moule += 1
                position += 1

        current_gateau.put()

        user_curent = Users.get_by_id(int(request.form['user']))

        activite.user = user_curent.key
        activite.date = function.datetime_convert(date_auto_nows)
        activite.commande = current_commande.key
        activite.put()

        # Quand on modifie le gateau, on change les informations de ce produit (la description)

        flash('Enregistement effectue avec succes', 'success')
        return redirect(url_for('commande.facture', id_commande=current_gateau.commande_id.get().key.id()))

    return render_template('commande/update_gateaux.html', **locals())


@prefix.route('/update/cupcake/<int:id_commande>', methods=['GET', 'POST'])
@prefix.route('/update/cupcake/<int:id_commande>/<int:gateau_id>', methods=['GET', 'POST'])
@login_required
def updateCupcake(id_commande, gateau_id=None):

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    produitGateau = Produit.query(
        Produit.type_produit == 3
    ).get()

    typegateau_list = TypeGateaux.query(
        TypeGateaux.pr_sable == False
    ).order(TypeGateaux.name)

    gout_creme_list = Param.query(
        Param.type_data == 'gouts cremes'
    ).order(Param.name)

    imbibage_list = Param.query(
        Param.type_data == 'imbibages'
    ).order(Param.name)

    fourrage_list = Param.query(
        Param.type_data == 'fourrages'
    ).order(Param.name)

    coulis_list = Param.query(
        Param.type_data == 'coulis'
    ).order(Param.name)

    couleur_list = Param.query(
        Param.type_data == 'couleurs cup'
    ).order(Param.name)

    topping_list = Param.query(
        Param.type_data == 'topping'
    ).order(Param.name)

    current_commande = Commande.get_by_id(id_commande)

    activite = Activite()
    activite.entite = "Cupcake"

    if gateau_id:
        current_gateau = ProduitCommander.get_by_id(gateau_id)        
        
        current_commande.verif_calendar = False
        if request.method == 'POST':
            current_commande.mail_type = 2
            current_commande.mail_send = False
        current_commande.put()

        activite.action = 2
        activite.infos = 'Modification du Cupcake de la commande'
    else:
        current_gateau = ProduitCommander()

        activite.action = 1
        activite.infos = 'Creation du Cupcake de la commande'

    if request.method == 'POST':

        current_gateau.observation = request.form['observation']
        current_gateau.commande_id = current_commande.key
        current_gateau.produit_id = produitGateau.key
        current_gateau.prix = float(request.form['prix'])

        if request.form['input_impression'] == '1':
            current_gateau.impression = True

        if request.form['input_pate'] == '1':
            current_gateau.pate = True

        current_gateau.qte = int(request.form['nbre_part'])

        choix_type_gateau = TypeGateaux.get_by_id(int(request.form['typegateaux']))
        current_gateau.typeGateau_id = choix_type_gateau.key

        composition = current_gateau.list_composition_unique()

        composition.goutcreme_id = None
        if request.form['gout_creme']:
            gout_creme = Param.get_by_id(int(request.form['gout_creme']))
            composition.goutcreme_id = gout_creme.key

        composition.imbibage_id = None
        if int(request.form['imbibage']):
            imbibage = Param.get_by_id(int(request.form['imbibage']))
            composition.imbibage_id = imbibage.key

        composition.coulis_id = None
        if int(request.form['coulis']):
            coulis = Param.get_by_id(int(request.form['coulis']))
            composition.coulis_id = coulis.key

        composition.fourage_id = None
        if int(request.form['fourrage']):
            fourrage = Param.get_by_id(int(request.form['fourrage']))
            composition.fourage_id = fourrage.key

        composition.couleur_cup_id = None
        if int(request.form['couleur_cup']):
            couleur_cup = Param.get_by_id(int(request.form['couleur_cup']))
            composition.couleur_cup_id = couleur_cup.key

        composition.topping_id = None
        if int(request.form['topping']):
            topping = Param.get_by_id(int(request.form['topping']))
            composition.topping_id = topping.key

        composition.put()

        current_gateau.put()

        user_curent = Users.get_by_id(int(request.form['user']))

        activite.user = user_curent.key
        activite.date = function.datetime_convert(date_auto_nows)
        activite.commande = current_commande.key
        activite.put()

        flash('Enregistement effectue avec succes', 'success')
        return redirect(url_for('commande.facture', id_commande=id_commande))

    return render_template('commande/update_cupcake.html', **locals())


@prefix.route('/update/sable/<int:id_commande>', methods=['GET', 'POST'])
@prefix.route('/update/sable/<int:id_commande>/<int:gateau_id>', methods=['GET', 'POST'])
@login_required
def updateSable(id_commande, gateau_id=None):

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    produitGateau = Produit.query(
        Produit.type_produit == 2
    ).get()

    form_list = TypeGateaux.query(
        TypeGateaux.pr_sable == True
    )

    couleur_ruban = Param.query(
        Param.type_data == 'couleurs rubans'
    ).order(Param.name)

    current_commande = Commande.get_by_id(id_commande)

    activite = Activite()
    activite.entite = "Sable"

    if gateau_id:
        current_gateau = ProduitCommander.get_by_id(gateau_id)
        
        current_commande.verif_calendar = False
        if request.method == 'POST':
            current_commande.mail_type = 2
            current_commande.mail_send = False
        current_commande.put()

        activite.action = 2
        activite.infos = 'Modification du Sable de la commande'
    else:
        current_gateau = ProduitCommander()

        activite.action = 1
        activite.infos = 'Creation du Sable de la commande'

    if request.method == 'POST':

        choix_type_gateau = TypeGateaux.get_by_id(int(request.form['forme']))
        choix_ruban = Param.get_by_id(int(request.form['ruban']))

        current_gateau.qte = int(request.form['qte'])
        current_gateau.typeGateau_id = choix_type_gateau.key
        current_gateau.couleurRuban_id = choix_ruban.key
        current_gateau.commande_id = current_commande.key
        current_gateau.produit_id = produitGateau.key

        current_gateau.observation = request.form['observation']
        current_gateau.prix = float(request.form['prix'])

        if request.form.getlist('impression'):
            current_gateau.impression = True

        if request.form.getlist('pate'):
            current_gateau.pate = True

        if request.form.getlist('emballage'):
            current_gateau.emballage = True

        current_gateau.put()

        user_curent = Users.get_by_id(int(request.form['user']))

        activite.user = user_curent.key
        activite.date = function.datetime_convert(date_auto_nows)
        activite.commande = current_commande.key
        activite.put()


        flash('Enregistement effectue avec succes', 'success')
        return redirect(url_for('commande.facture', id_commande=id_commande))

    return render_template("commande/update_sable.html", **locals())


@prefix.route('/correction')
def correction():
    all_commande = Commande.query().order(Commande.dateCmd)

    # show = []
    #
    #
    # count = 1
    for commande in all_commande:
        # try:
        #     client = commande.user.get().name
        #     year_cmd = commande.dateCmd.year
        #     commande.ref = 'CC/'+str(year_cmd)+'/'+str(count)
        #     commande.put()
        #     count += 1
        # except AttributeError:
        #     commande.key.delete()
        # try:
        #
        # except AttributeError
        # show.append((commande.user.get().name, commande.user))

        accompte = 0
        for versement in commande.versement():
            accompte += versement.montant

        if commande.montant == accompte:
            commande.mail_type = 1
        commande.mail_send = False
        commande.put()


    # all_user = Users.query(
    #     Users.client == True
    # )
    #
    #
    #
    # for user in all_user:
    #     client = user.email
    #     match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', client)
    #     show.append((user.name, user.email))

    return 'TRUE'


@prefix.route('/check_pin', methods=['GET', 'POST'])
def check_pin():

    send = False

    url = None
    if request.args.get('url'):
        url = request.args.get('url')

    if request.method == 'POST' and request.form['code']:
        code = int(request.form['code'])

        user = Users.query(
            Users.pin == code
        ).get()

        if user:
            send = True

    return render_template('commande/check_pin.html', **locals())


@prefix.route('/facture/pdf/<int:facture_id>')
def facturePDF(facture_id):

    current_facture = Commande.get_by_id(facture_id)

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
    show_email = string_2 % ' Email : '+email.lower()
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

    accompte = 0
    for versement in current_facture.versement():
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
    reste_payer = total - accompte
    reste = string % function.format_price(reste_payer)
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

    if request.args.get('send'):
        blob = PdfTable()
        blob.archivoBlob = pdf_out
        blob.commande_id = current_facture.key
        blob.put()
        return 'true'
    else:
        output.close()

        response = make_response(pdf_out)
        response.headers["Content-Type"] = "application/pdf"

        return response
