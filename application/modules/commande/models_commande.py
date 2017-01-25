__author__ = 'Ronald'

from google.appengine.ext import ndb
from ..user.models_user import Users
from ..gateau.models_gateau import Produit
from ..event.models_event import Event
from ..param.models_param import TypeGateaux, Param


class Commande(ndb.Model):
    user = ndb.KeyProperty(kind=Users)
    ref = ndb.StringProperty()
    dateCmd = ndb.DateProperty()
    dateLiv = ndb.DateProperty()
    timeLiv = ndb.TimeProperty()
    nameConcerne = ndb.StringProperty()
    dateAnniv = ndb.DateProperty()
    age = ndb.StringProperty()
    theme = ndb.StringProperty()
    montant = ndb.FloatProperty()
    event_id = ndb.KeyProperty(kind=Event)
    infos = ndb.TextProperty(indexed=False)
    annule = ndb.BooleanProperty(default=False)
    livre = ndb.BooleanProperty(default=False)
    send = ndb.BooleanProperty(default=False)
    new = ndb.BooleanProperty(default=True)
    verif_calendar = ndb.BooleanProperty(default=False)
    update = ndb.DateTimeProperty(auto_now=True)
    create = ndb.DateTimeProperty(auto_now_add=True)
    mail_send = ndb.BooleanProperty(default=False)
    mail_type = ndb.IntegerProperty(default=0)

    def produit_commande(self, verified=False):

        if not verified:
            prod_cmd = ProduitCommander.query(
                ProduitCommander.commande_id == self.key
            )
        else:
            prod_cmd = ProduitCommander.query(
                ProduitCommander.commande_id == self.key,
                ProduitCommander.annule == False
            )

        return prod_cmd

    def activite(self):
        all = Activite.query(
            Activite.commande == self.key
        )
        return all

    def versement(self):
        versement_cmd = Versement.query(
            Versement.commande_id == self.key
        ).order(-Versement.dateVers)
        return versement_cmd


class Versement(ndb.Model):
    commande_id = ndb.KeyProperty(kind=Commande)
    dateVers = ndb.DateProperty()
    montant = ndb.FloatProperty()
    send_bill = ndb.BooleanProperty(default=True)


class PrintFacture(ndb.Model):
    create = ndb.DateTimeProperty(auto_now_add=True)
    pdf = ndb.BlobProperty()
    commade_id = ndb.KeyProperty(kind=Commande)


class ProduitCommander(ndb.Model):
    impression = ndb.BooleanProperty(default=False)
    pate = ndb.BooleanProperty(default=False)
    emballage = ndb.BooleanProperty(default=False)
    qte = ndb.IntegerProperty()
    prix = ndb.FloatProperty()
    nbrPart = ndb.StringProperty()
    observation = ndb.TextProperty(indexed=False)
    categorie_id = ndb.KeyProperty(kind=Param)
    commande_id = ndb.KeyProperty(kind=Commande)
    produit_id = ndb.KeyProperty(kind=Produit)
    couleurRuban_id = ndb.KeyProperty(kind=Param)
    typeGateau_id = ndb.KeyProperty(kind=TypeGateaux)
    annule = ndb.BooleanProperty(default=False)
    termine = ndb.BooleanProperty(default=False)
    eventID = ndb.StringProperty()
    update = ndb.DateTimeProperty(auto_now=True)

    def list_moule(self):
        the_moule = MouleProduit.query(
            MouleProduit.produitCommander_id == self.key
        ).order(MouleProduit.position)

        return the_moule

    def list_moule_NIden(self):
        the_moule = MouleProduit.query(
            MouleProduit.produitCommander_id == self.key,
            MouleProduit.identique == None
        ).order(MouleProduit.position)

        return the_moule

    def list_moule__Correction(self):
        the_moule = MouleProduit.query(
            MouleProduit.produitCommander_id == self.key,
            MouleProduit.identique == None
        )
        return the_moule

    def list_moule_NIden_Count(self):
        the_moule = MouleProduit.query(
            MouleProduit.produitCommander_id == self.key,
            MouleProduit.identique == None
        ).count()

        return the_moule

    def list_composition(self):
        the_compo = Composition.query(
            Composition.produitCommander_id == self.key
        )

        return the_compo

    def list_composition_unique(self):
        the_compo = Composition.query(
            Composition.produitCommander_id == self.key
        ).get()

        return the_compo

    def type_produit(self):
        type = self.produit_id.get().type_produit
        return type

    def name_produit(self):
        type = self.produit_id.get().name
        return type

    def name_type_gateau(self):
        type = self.typeGateau_id.get().name
        return type

    def couleur_ruban(self):
        type = self.couleurRuban_id.get().name
        return type

    def name_categorie(self):
        cat = self.categorie_id.get().name
        return cat


class MouleProduit(ndb.Model):
    qte = ndb.IntegerProperty()
    produitCommander_id = ndb.KeyProperty(kind=ProduitCommander)
    moule_id = ndb.KeyProperty(kind=Param)
    identique = ndb.IntegerProperty()
    position = ndb.IntegerProperty()

    def list_composition(self):
        the_compo = Composition.query(
            Composition.mouleProduit_id == self.key
        ).order(Composition.position)
        return the_compo

    def list_composition_count(self):
        the_compo = Composition.query(
            Composition.mouleProduit_id == self.key
        ).count()
        return the_compo

    def identiq(self):
        identique = None
        if self.identique:
            identique = MouleProduit.get_by_id(self.identique)
        return identique

    def name_moule(self):
        moule = self.moule_id.get().name
        return moule

    def nbre_identique(self):
        nbr = MouleProduit.query(
            MouleProduit.identique == int(self.key.id())
        )
        return nbr

    def nbre_identique_count(self):
        nbr = MouleProduit.query(
            MouleProduit.identique == self.key.id()
        ).count()
        return nbr


class Composition(ndb.Model):
    quantite = ndb.IntegerProperty()
    position = ndb.IntegerProperty()
    produitCommander_id = ndb.KeyProperty(kind=ProduitCommander)
    fourage_id = ndb.KeyProperty(kind=Param)
    goutcreme_id = ndb.KeyProperty(kind=Param)
    imbibage_id = ndb.KeyProperty(kind=Param)
    coulis_id = ndb.KeyProperty(kind=Param)
    topping_id = ndb.KeyProperty(kind=Param)
    couleur_cup_id = ndb.KeyProperty(kind=Param)
    mouleProduit_id = ndb.KeyProperty(kind=MouleProduit)

    def name_fourage(self):
        name = None
        if self.fourage_id:
            name = self.fourage_id.get().name

        return name

    def name_goutcreme(self):
        name = None
        if self.goutcreme_id:
            name = self.goutcreme_id.get().name

        return name

    def name_imbibage(self):
        name = None
        if self.imbibage_id:
            name = self.imbibage_id.get().name

        return name

    def name_coulis(self):
        name = None
        if self.coulis_id:
            name = self.coulis_id.get().name

        return name

    def name_topping(self):
        name = None
        if self.topping_id:
            name = self.topping_id.get().name

        return name

    def name_couleur_cup(self):
        name = None
        if self.couleur_cup_id:
            name = self.couleur_cup_id.get().name

        return name


class Activite(ndb.Model):
    entite = ndb.StringProperty()
    action = ndb.IntegerProperty()
    infos = ndb.StringProperty()
    date = ndb.DateTimeProperty()
    user = ndb.KeyProperty(kind=Users)
    commande = ndb.KeyProperty(kind=Commande)


class PdfTable(ndb.Model):
    archivoBlob = ndb.BlobProperty()
    commande_id = ndb.KeyProperty(kind=Commande)
    date = ndb.DateTimeProperty(auto_now_add=True)