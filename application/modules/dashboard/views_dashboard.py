__author__ = 'Ronald'

from ...modules import *
from ..commande.models_commande import Commande, Users

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
    submenu = 'dashboard'

    current_day = datetime.date.today()

    commandes = Commande.query(
        Commande.annule == False
    )

    montant_commande = 0
    montant_livraison = 0
    cmd_day_next = 0
    cmd_day = 0

    total_cmd = 0

    montant_livraison_paid = 0

    mont_liv_global = 0
    mont_liv_paid_global = 0

    for commande in commandes:

        if commande.dateCmd.month == current_day.month:
            montant_commande += commande.montant
            total_cmd += 1

        if commande.dateLiv.month == current_day.month:
            montant_livraison += commande.montant
            montant_livraison_paid += commande.montant_versment()

            if commande.dateLiv == current_day:
                cmd_day += 1

            if commande.dateLiv > current_day:
                cmd_day_next += 1

        if commande.dateLiv <= current_day:
            mont_liv_global += commande.montant
            mont_liv_paid_global += commande.montant_versment()

    clients = Users.query(
        Users.client == True
    )
    nbr_client = 0
    for cliente in clients:
        if cliente.date_create and cliente.date_create.month == current_day.month:
            nbr_client += 1

    return render_template('dashboard/index.html', **locals())


@prefix.route('/rapport/ventes')
@login_required
@roles_required([('super_admin', 'dashboard')])
def rapport_vente():
    title_page = 'Rapport des ventes'
    menu = 'dashboard'
    submenu = 'rapport_vente'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones)

    start = function.get_first_day(date_auto_nows)
    end = function.get_last_day(date_auto_nows)

    datas = Commande.query(
        Commande.annule == False,
        Commande.dateCmd >= start,
        Commande.dateCmd <= end
    ).order(Commande.dateCmd)

    if search:

        list_commande = []
        for commande in datas:

            data_commande = commande.ref+" "+commande.user.get().name
            search_function = function.find(data_commande.lower(), q)
            if search_function:
                list_commande.append(commande)

        datas = list_commande

    total_montant = 0
    for commande in datas:
        total_montant += commande.montant

    return render_template('dashboard/rapport_vente.html', **locals())


@prefix.route('/rapport/recouvrements')
@login_required
@roles_required([('super_admin', 'dashboard')])
def rapport_recouvrement():

    title_page = 'Rapport des recouvrements'
    menu = 'dashboard'
    submenu = 'rapport_recouvrement'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones)
    first_day = function.get_first_day(date_auto_nows) - datetime.timedelta(days=1)

    start = function.get_first_day(first_day)
    end = function.get_last_day(first_day)

    datas = Commande.query(
        Commande.annule == False,
        Commande.dateLiv >= start,
        Commande.dateLiv <= end
    ).order(Commande.dateLiv)

    if search:

        list_commande = []
        for commande in datas:

            data_commande = commande.ref+" "+commande.user.get().name
            search_function = function.find(data_commande.lower(), q)
            if search_function:
                list_commande.append(commande)

        datas = list_commande

    total_montant = 0
    total_versment = 0
    for commande in datas:
        total_montant += commande.montant
        total_versment += commande.montant_versment()

    return render_template('dashboard/rapport_recouvrement.html', **locals())


@prefix.route('/rapport/recouvrements/refresh', methods=['GET', 'POST'])
@login_required
def rapport_recouvrement_refresh():

    title_page = 'Rapport des recouvrements'
    printer = request.args.get('print')

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
        search = request.form['search']
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))
        search = request.args.get('search')

    datas = Commande.query(
        Commande.annule == False,
        Commande.dateLiv >= date_start,
        Commande.dateLiv <= date_end
    ).order(Commande.dateLiv)

    count = datas.count()

    if search:
        title_page += ' (Mot cherche: '+search+')'

        list_commande = []
        for commande in datas:
            data_commande = commande.ref+" "+commande.user.get().name
            search_function = function.find(data_commande.lower(), search)
            if search_function:
                list_commande.append(commande)
        datas = list_commande
        count = len(datas)


    total_montant = 0
    total_versment = 0
    for commande in datas:
        total_montant += commande.montant
        total_versment += commande.montant_versment()

    number_per_page = 20

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
        if count < number_per_page:
            boucle = True

        if not boucle:
            pages = 0
            modulo = count % number_per_page
            div = count / number_per_page
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
            montant = Paragraph('''<b>Montant</b>''', styleBH)
            accompte = Paragraph('''<b>Accompte</b>''', styleBH)
            reste = Paragraph('''<b>Reste</b>''', styleBH)

            #recuperation des donnees
            datas_report = [items for items in datas]

            offset_start = page * number_per_page
            offset_end = (page + 1) * number_per_page
            datas_report = datas_report[offset_start:offset_end]

            data = [
                [ref, client, montant, accompte, reste]
            ]

            breaking = 0
            for i in datas_report:
                ref = Paragraph(i.ref, styleN)
                client = Paragraph(i.user.get().name, styleN)
                montant = Paragraph(str(function.format_price(i.montant)), styleN)
                accompte = Paragraph(str(function.format_price(i.montant_versment())), styleN)
                reste = Paragraph(str(function.format_price((i.montant - i.montant_versment()))), styleN)
                current = [ref, client,montant, accompte, reste]
                data.append(current)
                breaking += 1
                if breaking > number_per_page:
                    break

            table = Table(data, colWidths=[5*cm, 6*cm, 5*cm, 3.5*cm, 3*cm])

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

        return render_template('dashboard/rapport_recouvrement_refresh.html', **locals())


@prefix.route('/rapport/ventes/refresh', methods=['GET', 'POST'])
@login_required
def rapport_vente_refresh():

    title_page = 'Rapport des ventes'
    printer = request.args.get('print')

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
        search = request.form['search']
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))
        search = request.args.get('search')



    datas = Commande.query(
        Commande.dateCmd >= date_start,
        Commande.dateCmd <= date_end,
        Commande.annule == False
    )

    count = datas.count()

    if search:
        title_page += ' (Mot cherche: '+search+')'

        list_commande = []
        for commande in datas:
            data_commande = commande.ref+" "+commande.user.get().name
            search_function = function.find(data_commande.lower(), search)
            if search_function:
                list_commande.append(commande)
        datas = list_commande
        count = len(datas)

    total_montant = 0
    for commande in datas:
        total_montant += commande.montant

    number_per_page = 20

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
        if count < number_per_page:
            boucle = True

        if not boucle:
            pages = 0
            modulo = count % number_per_page
            div = count / number_per_page
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
            montant = Paragraph('''<b>Montant</b>''', styleBH)

            #recuperation des donnees
            datas_report = [items for items in datas]

            offset_start = page * number_per_page
            offset_end = (page + 1) * number_per_page
            datas_report = datas_report[offset_start:offset_end]

            data = [
                [ref, client, montant]
            ]

            breaking = 0
            for i in datas_report:
                ref = Paragraph(i.ref, styleN)
                client = Paragraph(i.user.get().name, styleN)
                montant = Paragraph(str(function.format_price(i.montant)), styleN)
                current = [ref, client,montant]
                data.append(current)
                breaking += 1
                if breaking > number_per_page:
                    break

            table = Table(data, colWidths=[5.5*cm, 9.5*cm, 7.5*cm])

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

        return render_template('dashboard/rapport_vente_refresh.html', **locals())


@prefix_param.route('/')
@login_required
def index():
    title_page = 'Parametrages'
    menu = 'parametre'

    return render_template('dashboard/parametre.html', **locals())
