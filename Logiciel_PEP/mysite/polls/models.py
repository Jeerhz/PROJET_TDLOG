import datetime
import uuid
from uuid import UUID
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import RegexValidator, MinLengthValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.files.storage import FileSystemStorage
from django.db.migrations.serializer import BaseSerializer
from django.db.migrations.writer import MigrationWriter
from django.db.models import Sum, Max
from django.core.mail import send_mail, get_connection
from django.urls import reverse_lazy
from django.conf import settings
from multiselectfield import MultiSelectField
from .widgets import SelectSearch
from datetime import date
from datetime import timedelta
import os


IMAGE_STORAGE = FileSystemStorage(location="/static/polls/img")
DOC_STORAGE = "polls/"
IMAGE_UPLOAD = os.path.join(settings.BASE_DIR, "/polls/static/polls/img")


class JE(models.Model):
    nom = models.CharField(max_length=200)
    raison_sociale = models.CharField(max_length=200)
    rue = models.CharField(max_length=200)
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=10)
    siret = models.CharField(
        max_length=14,
        validators=[
            RegexValidator(r"^[0-9]+$", _("This field must only contain digits")),
            MinLengthValidator(14, "This field must contain exactly 14 characters."),
        ],
    )
    APE = models.CharField(
        max_length=5,
        validators=[
            RegexValidator(r"^[0-9]{4}[A-Za-z]$", _("The expected format is 0000A."))
        ],
    )
    TVA = models.CharField(
        max_length=13,
        validators=[
            RegexValidator(
                r"^[A-Za-z]{2}[0-9]{11}$",
                _("The expected format is 2 letters and 11 digits"),
            ),
            MinLengthValidator(13, "This field must contain exactly 13 characters."),
        ],
    )
    IBAN = models.CharField(
        max_length=34,
        validators=[
            RegexValidator(r"^[A-Z0-9]+$", _("Special characters are not allowed."))
        ],
    )
    BIC = models.CharField(
        max_length=34,
        validators=[
            RegexValidator(r"^[A-Z0-9]+$", _("Special characters are not allowed."))
        ],
    )
    check_order = models.CharField(max_length=50)
    logo = models.ImageField(upload_to="static/polls/img/")
    chiffres_affaires = models.FloatField(
        default=0.0, validators=[MinValueValidator(0)]
    )
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    base_urssaf = models.FloatField(default=46.6)
    taux_ATMP = models.FloatField(default=0.66)
    taux_cotisations = models.FloatField(default=29.9)

    def __str__(self):
        return self.nom

    def default():
        new_je = JE()
        new_je.nom = "PEP"
        new_je.raison_sociale = "Junior-Entreprise des Ponts"
        new_je.rue = "6-8 Avenue Blaise Pascal"
        new_je.ville = "Champs-sur-Marne"
        new_je.code_postal = "77420"
        new_je.siret = "01234567890123"
        new_je.APE = "0000A"
        new_je.TVA = "AA01234567890"
        new_je.IBAN = "FR000000000000000000000"
        new_je.BIC = "0000000000000000000000"
        new_je.check_order = "ORDRE_CHEQUE"
        new_je.logo = "/static/polls/img/bdc.png"
        new_je.chiffres_affaires = 0.0
        return new_je
    
    def president(self):
        prez = Member.objects.filter(je=self, poste='PRESIDENT').first()
        return prez




class JESerializer(BaseSerializer):
    def serialize(self):
        # Customize the serialization logic for the 'JE' model
        return "JE.objects.get(pk={})".format(repr(self.value.pk)), {
            "from polls.models import JE"
        }


# Register the JESerializer for the 'JE' model
MigrationWriter.register_serializer(models.Model, JESerializer)

# To Provide default values directly without a database query
default_je_data = {
    "nom": "PEP",
    "raison_sociale": "Junior-Entreprise des Ponts",
    "rue": "6-8 Avenue Blaise Pascal",
    "ville": "Champs-sur-Marne",
    "code_postal": "77420",
    "siret": "01234567890123",
    "APE": "0000A",
    "TVA": "AA01234567890",
    "IBAN": "FR000000000000000000000",
    "BIC": "0000000000000000000000",
    "check_order": "ORDRE_CHEQUE",
    "logo": "/static/polls/img/bdc.png",
    "chiffres_affaires": 0.0,
    "id": "bab6b8bec2744faeb6343c6a40968534",
}


class Client(models.Model):
    class Type(models.TextChoices):
        GRANDE_ENTREPRISE = "GRANDE_ENTREPRISE", "Grande entreprise"
        SECTEUR_PUBLIC = "SECTEUR_PUBLIC", "Secteur Public"
        START_UP_ET_TPE = "START_UP_ET_TPE", "Start-up et TPE"
        PME = "PME", "Petite et moyenne entreprise"
        ETI = "ETI", "Entreprise de taille intermédiaire"
        ASSOCIATION = "ASSOCIATION", "Association"

    class Secteur(models.TextChoices):
        INDUSTRIE = "INDUSTRIE", "Industrie"
        DISTRIBUTION = "DISTRIBUTION", "Distribution"
        SECTEUR_PUBLIC = "SECTEUR_PUBLIC", "Secteur Public"
        CONSEIL = "CONSEIL", "Conseil"
        TRANSPORT = "TRANSPORT", "Transport"
        NUMERIQUE = "NUMERIQUE", "Numérique"
        BTP = "BTP", "BTP"
        ENERGIE = "ENERGIE", "Énergie"
        ADMINISTRATIF = "ADMINISTRATIF", "Administratif"
        RECHERCHE = "RECHERCHE", "Recherche"
        TELECOM = "TELECOM", "Télécom"
        FINANCECOMPTA = "FINANCECOMPTA", "Finance-compta"
        AUTRE = "AUTRE", "Autre"

    TITRE_CHOIX = (("M.", "M."), ("Mme", "Mme"))
    nom_societe = models.CharField(max_length=200)
    raison_sociale = models.CharField(max_length=150)
    rue = models.CharField(max_length=300)
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=20)
    country = models.CharField(max_length=100, verbose_name="pays")
    # titre_representant_legale = models.CharField(max_length = 5, choices=TITRE_CHOIX)
    # nom_representant_legale = models.CharField(max_length = 100)
    # prenom_representant_legale = models.CharField(max_length = 100)
    # fonction_representant_legale = models.CharField(max_length = 100)
    je = models.ForeignKey(JE, on_delete=models.CASCADE)
    logo = models.ImageField(
        upload_to="static/polls/img/",
        default="media/polls/Logo_Ecole_des_Ponts_ParisTech.svg.png",
    )
    remarque = models.TextField(blank=True, null=True, default="")
    description = models.TextField(max_length=10000, null=True)
    secteur = models.CharField(
        max_length=20,
        choices=Secteur.choices,
        default=Secteur.SECTEUR_PUBLIC,
        help_text="Sélectionnez le secteur d'activité du client.",
    )
    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.SECTEUR_PUBLIC,
        help_text="Sélectionnez le type d'entreprise.",
    )

    def derniere_mission(self):
        etude = Etude.objects.filter(client=self).order_by("numero").first()
        return etude

    def representants(self):
        return Representant.objects.filter(client=self)

    def __str__(self):
        return self.nom_societe

    def get_display_dict(self):
        return {
            "Nom de société": self.nom_societe,
            "Raison sociale": self.raison_sociale,
            "Adresse": self.rue + "\n" + self.ville + "\n" + self.code_postal,
            "Pays": self.country,
        }

    def get_title_details(self):
        return "Détails du client"

    def createForm(**kwargs):
        return AddClient()

    def retrieveForm(form, **kwargs):
        if "files" in kwargs.keys():
            return AddClient(form, kwargs["files"])
        else:
            return AddClient(form)

    def modifyForm(instance):
        return AddClient(instance=instance)

    def save(self, *args, **kwargs):
        # Save the instance using the parent class method
        print("Calling save method...")  # Debugging statement
        super(Client, self).save(*args, **kwargs)
        print("Save method completed.")  # Debuggin

    def modifier_description(self, nv_description):
        self.description = nv_description
        self.save()


class Representant(models.Model):
    class Demarchage(models.TextChoices):
        A_CONTACTER = "A_CONTACTER", "A contacter"
        ATTENTE_REPONSE = "ATTENTE_REPONSE", "Attente d'un retour"
        RELANCER = "RELANCER", "A relancer"
        RETOUR_RECU = "RETOUR_RECU", "Retour reçu"
        ETUDE_CREEE = "ETUDE_CREEE", "Étude créée"

    TITRE_CHOIX = (("M.", "M."), ("Mme", "Mme"))
    titre = models.CharField(max_length=5, choices=TITRE_CHOIX)
    first_name = models.CharField(max_length=200, verbose_name="prénom")
    last_name = models.CharField(max_length=200, verbose_name="nom")
    mail = models.EmailField(max_length=200)
    phone_number = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="téléphone"
    )
    # je = models.ForeignKey(JE, on_delete=models.CASCADE)
    remarque = models.TextField(blank=True, null=True, default="RAS")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    fonction = models.CharField(max_length=100, null=True)
    contact_recent = models.BooleanField(default=False, blank=True, null=True)
    date_mail = models.DateField(
        default=datetime.date(1747, 1, 1), blank=True, null=True
    )
    contenu_mail = models.CharField(
        max_length=5000,
        blank=True,
        null=True,
        default=" Bonjour {{titre}} {{last_name}}, Je me permets de vous contacter au nom de la Junior Entrprise des Ponts. J'ai remarqué que nous avons effectué une mission pour vous il y a deux ans...",
    )
    date_reponse = models.DateField(
        default=datetime.date(1747, 1, 1), blank=True, null=True
    )
    contenu_reponse = models.CharField(
        max_length=5000, default="rien", blank=True, null=True
    )
    demarchage = models.CharField(
        max_length=40, choices=Demarchage.choices, default=Demarchage.A_CONTACTER
    )

    def maj_demarchage(self):
        if self.demarchage == "ATTENTE_REPONSE":
            if datetime.today() - timedelta(days=60) > self.date_mail:
                self.demarchage == "RELANCER"
            elif self.date_reponse > self.date_mail:
                self.demarchage == "RETOUR_RECU"

    def attente_duree(self):
        if self.demarchage == "ATTENTE_REPONSE" or self.demarchage == "RELANCER":
            return datetime.today() - self.date_mail
        elif self.demarchage == "RETOUR_RECU":
            return datetime.today() - self.date_reponse

    def __str__(self):
        return self.first_name + " " + self.last_name

    def get_display_dict(self):
        return {
            "Prénom": self.first_name,
            "Nom": self.last_name,
            "Email": self.mail,
            "Numéro de téléphone": self.phone_number,
        }

    def get_title_details(self):
        return "Détails du représentant"

    def createForm(**kwargs):
        return AddRepresentant()

    def retrieveForm(form, **kwargs):
        if "files" in kwargs.keys():
            return AddRepresentant(form, kwargs["files"])
        else:
            return AddRepresentant(form)

    def modifyForm(instance):
        return AddRepresentant(instance=instance)

    def default():
        # Create a JE instance with the provided default values
        default_je = JE(**default_je_data)

        return Student(
            titre="M.",
            first_name="Antony",
            last_name="Feord",
            mail="antony.feord@eleves.enpc.fr",
            phone_number="+27",
            je=default_je,
        )

    def save(self, *args, **kwargs):
        id_client = kwargs.pop("id_client", None)
        expediteur = kwargs.pop("expediteur", None)
        if id_client is not None:
            client = Client.objects.get(id=id_client)
            self.client = client
            if not self.je:
                self.je = client.je

        self.maj_demarchage()
        super(Representant, self).save(*args, **kwargs)


class Student(models.Model):
    class Departement(models.TextChoices):
        IMI = "IMI", "IMI"
        SEGF = "SEGF", "SEGF"
        GMM = "GMM", "GMM"
        _1A = "1A", "1A"
        GCC = "GCC", "GCC"
        VET = "VET", "VET"
        GI = "GI", "GI"
        AUTRE = "AUTRE", "Autre"

    class Promotion(models.TextChoices):
        P022 = "2022", "2022"
        P023 = "2023", "2023"
        P024 = "2024", "2024"
        P025 = "2025", "2025"
        P026 = "2026", "2026"
        P027 = "2027", "2027"
        DD = "DD", "Double-diplome"
        MS = "MS", "Master Spécialisé"
        AUTRE = "AUTRE", "Autre"

    TITRE_CHOIX = (("M.", "M."), ("Mme", "Mme"))
    titre = models.CharField(max_length=5, choices=TITRE_CHOIX)
    first_name = models.CharField(max_length=200, verbose_name="prénom")
    last_name = models.CharField(max_length=200, verbose_name="nom")
    mail = models.EmailField(max_length=200)
    phone_number = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="téléphone"
    )
    adress = models.CharField(max_length=300, null=True, verbose_name="rue")
    ville = models.CharField(max_length=300, null=True, default="Champs-sur-Marne")
    code_postal = models.CharField(max_length=10, null=True, default="77420")
    country = models.CharField(max_length=100, null=True, verbose_name="pays")
    promotion = models.CharField(
        max_length=200, choices=Promotion.choices, default=Promotion.P026
    )
    departement = models.CharField(
        max_length=20, choices=Departement.choices, default=Departement.AUTRE
    )
    je = models.ForeignKey(JE, on_delete=models.CASCADE, null=True)
    numero_ss = models.CharField(
        max_length=14,
        validators=[
            RegexValidator(r"^[0-9]+$", _("This field must only contain digits"))
        ],
        default="0",
        verbose_name="n° de sécurité sociale",
    )
    remarque = models.TextField(blank=True, null=True, default="")

    def __str__(self):
        return self.first_name + " " + self.last_name

    def is_member(self):
        return getattr(self, "member", None)

    def get_display_dict(self):
        return {
            "Prénom": self.first_name,
            "Nom": self.last_name,
            "Email": self.mail,
            "Numéro de téléphone": self.phone_number,
            "Promotion": self.promotion,
            "Departement": self.departement,
        }

    def get_title_details(self):
        return "Détails de l'étudiant"

    def createForm(**kwargs):
        return AddStudent()

    def retrieveForm(form, **kwargs):
        if "files" in kwargs.keys():
            return AddStudent(form, kwargs["files"])
        else:
            return AddStudent(form)

    def modifyForm(instance):
        return AddStudent(instance=instance)

    def nb_candidatures(self):
        return Candidature.objects.filter(eleve=self).count()

    def nb_etudes_realisees(self):
        return (
            AssignationJEH.objects.filter(eleve=self)
            .values("phase__etude")
            .distinct()
            .count()
        )

    def missions_realisees(self):
        phases_ids = (
            AssignationJEH.objects.filter(eleve=self)
            .values_list("phase_id", flat=True)
            .distinct()
        )
        phases = Phase.objects.filter(id__in=phases_ids)
        etudes_ids = phases.values_list("etude_id", flat=True).distinct()
        etudes = Etude.objects.filter(id__in=etudes_ids)
        return etudes

    def phases_etude(self, etude):
        return (
            AssignationJEH.objects.filter(eleve=self, phase__etude=etude)
            .distinct()
            .values_list("phase", flat=True)
        )

    def default():
        # Create a JE instance with the provided default values
        default_je = JE(**default_je_data)

        return Student(
            titre="M.",
            first_name="Edgar",
            last_name="Duc",
            mail="edgar.duc@eleves.enpc.fr",
            phone_number="+33783654605",
            adress="7 Allée des Sorbiers, 77420 Champs-sur-Marne",
            country="France",
            promotion="025",
            je=default_je,
        )


class StudentCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV File")


class ClientCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV File")


class CustomUserManager(BaseUserManager):
    def create_user(
        self, email, password=None, je=None, student=None, titre=None, **extra_fields
    ):
        if not email:
            raise ValueError("The Email field must be set")
        if "is_superuser" not in extra_fields or not extra_fields.get(
            "is_superuser", False
        ):
            if not je:
                raise ValueError("The JE association is required for regular users")

        email = self.normalize_email(email)
        user = self.model(
            email=email, je=je, student=student, titre=titre, **extra_fields
        )

        if password:
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # Note: 'je' n'est pas nécessaire pour un superutilisateur.
        return self.create_user(email, password, **extra_fields)


class Member(AbstractUser):
    class Poste(models.TextChoices):
        PRESIDENT = "PRESIDENT", "président"
        VICE_PRESIDENT = "VICE_PRESIDENT", "vice-président"
        TRESORIER = "TRESORIER", "Trésorier"
        VICE_TRESORIER = "VICE_TRESORIER", "vice-trésorier"
        SECRETAIRE_GENERALE = "SECRETAIRE_GENERALE", "secrétaire générale"
        CHEF_DE_PROJET = "CHEF_DE_PROJET", "chef de projet"
        DIRECTEUR_COMMERCIALE = "DIRECTEUR_COMMERCIALE", "directeur commerciale"
        DIRECTEUR_PROJET = "DIRECTEUR_PROJET", "directeur projet"
        DSI = "DSI", "DSI"
        RESPONSABLE_QUALITE = "RESPONSABLE_QUALITE", "responsable_qualite"
        DIRECTEUR_COMMUNICATION = "DIRECTEUR_COMMUNICATION", "directeur communication"
        DIRECTEUR_RSE = "DIRECTEUR_RSE", "directeur RSE"
        INDEFINI = "INDEFINI", "Indéfini"

    TITRE_CHOIX = (("M.", "M."), ("Mme", "Mme"))
    je = models.ForeignKey("JE", on_delete=models.CASCADE, null=True)
    student = models.OneToOneField(
        "Student", on_delete=models.CASCADE, null=True, related_name="member"
    )
    titre = models.CharField(max_length=5, choices=TITRE_CHOIX)
    email = models.EmailField(max_length=200, primary_key=True)
    photo = models.ImageField(
        upload_to="static/polls/img/", default="/static/polls/img/undraw_profile.svg"
    )  # local
    # photo = models.ImageField(upload_to='polls/', null=True, blank=True) #Par defaut S3
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    poste = models.CharField(
        max_length=40, choices=Poste.choices, blank=True, null=True
    )

    def __str__(self):
        return self.student.__str__()

    def createForm(**kwargs):
        return AddMember()

    def retrieveForm(form, **kwargs):
        if "files" in kwargs.keys():
            return AddMember(form, kwargs["files"])
        else:
            return AddMember(form)

    def modifyForm(instance):
        return AddMember(instance=instance)

    def get_display_dict(self):
        return self.student.get_display_dict()

    def get_title_details(self):
        return self.student.get_title_details()

    def chiffres_affaires(self):
        return self.je.chiffres_affaires

    def save(self, *args, **kwargs):
        self.username = self.email  # Set username to email
        super().save(*args, **kwargs)
        try:
            param = self.parametres
        except ObjectDoesNotExist:
            role = self.poste
            num_tel = ""

            # Check if self.student is not None before accessing phone_number
            if self.student is not None and self.student.phone_number is not None:
                num_tel = "Tel: " + self.student.phone_number

            signature = f"{role} chez {self.je.__str__()}\n{num_tel}\n"
            param = ParametresUtilisateur(membre=self, signature=signature)
            param.save()

    def signature_mail(self):
        if self.parametres.signature:
            return self.parametres.signature
        role = self.poste
        num_tel = ""
        if self.student.phone_number is not None:
            num_tel = "Tel: " + self.student.phone_number

        return role + " chez " + self.je.__str__() + "\n" + num_tel + "\n"


class ParametresUtilisateur(models.Model):
    membre = models.OneToOneField(
        Member, on_delete=models.CASCADE, related_name="parametres"
    )
    param_statut_etude_ec = models.BooleanField(default=True, verbose_name="En cours")
    param_statut_etude_ed = models.BooleanField(
        default=True, verbose_name="En discussion"
    )
    param_statut_etude_t = models.BooleanField(default=True, verbose_name="Terminée")
    param_col_etude_numero = models.BooleanField(default=True, verbose_name="Numéro")
    param_col_etude_titre = models.BooleanField(default=True, verbose_name="Titre")
    param_col_etude_client = models.BooleanField(default=True, verbose_name="Client")
    param_col_etude_responsable = models.BooleanField(
        default=True, verbose_name="Responsable"
    )
    param_col_etude_montant_HT = models.BooleanField(
        default=False, verbose_name="Montant HT"
    )
    param_col_etude_remarque = models.BooleanField(
        default=True, verbose_name="Remarque"
    )
    param_col_etude_avancement = models.BooleanField(
        default=True, verbose_name="Avancement"
    )
    signature = models.TextField(
        max_length=200, default="", blank=True, verbose_name="Signature Mail"
    )

    def __str__(self):
        return "Paramètres " + self.membre.__str__()

    def nombre_colonnes(self):
        boolean_fields = [
            field
            for field in self._meta.fields
            if isinstance(field, models.BooleanField)
        ]
        count = 0
        for boolean_field in boolean_fields:
            field_name = boolean_field.name
            if getattr(self, field_name):
                count += 1
        return count


class Etude(models.Model):
    class Departement(models.TextChoices):
        IMI = "IMI", "IMI"
        SEGF = "SEGF", "SEGF"
        GMM = "GMM", "GMM"
        _1A = "1A", "1A"
        GCC = "GCC", "GCC"
        VET = "VET", "VET"
        GI = "GI", "GI"
        AUTRE = "AUTRE", "Autre"

    class Status(models.TextChoices):
        EN_NEGOCIATION = "EN_NEGOCIATION", "En négociation"
        EN_COURS = "EN_COURS", "En cours"
        TERMINEE = "TERMINEE", "Terminée"

    class TypeConvention(models.TextChoices):
        CADRE = "Convention cadre"
        ETUDE = "Convention d'étude"

    class Departement(models.TextChoices):
        IMI = "IMI", "IMI"
        SEGF = "SEGF", "SEGF"
        GMM = "GMM", "GMM"
        _1A = "1A", "1A"
        GCC = "GCC", "GCC"
        VET = "VET", "VET"
        GI = "GI", "GI"
        AUTRE = "AUTRE", "Autre"

    class Mandat(models.TextChoices):
        M025 = "025", "025"
        M026 = "026", "026"
        M027 = "027", "027"

    titre = models.CharField(max_length=500)
    numero = models.IntegerField(blank=True, null=True)
    description = models.TextField(max_length=10000, blank=True)
    problematique = models.TextField(max_length=500, blank=True)
    debut = models.DateField(default=timezone.now, blank=True, null=True)
    resp_qualite = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="qualite_etudes",
        verbose_name="qualité",
    )
    responsable = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="responsable_etudes",
        verbose_name="suiveur",
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    client_interlocuteur = models.ForeignKey(
        Representant, on_delete=models.CASCADE, related_name="client_interlocuteur"
    )
    client_representant_legale = models.ForeignKey(
        Representant,
        on_delete=models.CASCADE,
        related_name="client_representant_legale",
    )
    je = models.ForeignKey(JE, on_delete=models.CASCADE)
    frais_dossier = models.FloatField(default=0, verbose_name="frais de dossier")
    taux_tva = models.FloatField(default=20, verbose_name="% TVA")
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.EN_NEGOCIATION
    )
    type_convention = models.CharField(
        max_length=30,
        choices=TypeConvention.choices,
        blank=True,
        verbose_name="Type de convention",
    )
    mandat = models.CharField(
        max_length=30,
        choices=Mandat.choices,
        default=Mandat.M026,
        blank=True,
        verbose_name="mandat",
    )
    departement = MultiSelectField(
        choices=Departement.choices, default=Departement.AUTRE
    )

    id_url = models.UUIDField(primary_key=False, editable=True, unique=False)
    date_debut_recrutement = models.DateField(
        blank=True, null=True, verbose_name="Debut du recrutement"
    )
    date_fin_recrutement = models.DateField(
        blank=True, null=True, verbose_name="Fin du recrutement"
    )
    remarque = models.TextField(blank=True, null=True, default="")
    raison_contact = models.TextField(blank=True, null=True, default="")
    contexte = models.TextField(blank=True, null=True, default="")
    objectifs = models.TextField(blank=True, null=True, default="")
    periode_de_garantie = models.IntegerField(default=90)

    methodologie = models.TextField(blank=True, null=True, default="")
    element_a_fournir = models.TextField(
        blank=True, null=True, default="", verbose_name="éléments à fournir du client"
    )

    paragraphe_intervenant_devis = models.TextField(
        default="Pour réaliser votre étude, nous rechercherons un ou des étudiants de l’École des Ponts ParisTech. Les cours dispensés à l’École tel(s) que [exemples(s) de cours qui peuvent être utile pour réaliser la mission], apportent aux étudiants les outils nécessaires pour [ce en quoi l'étude va consister]. Ils auront donc les connaissances requises pour [ce que veut le client]."
    )
    cahier_des_charges = models.JSONField(default=dict)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Etat_Doc:
        EN_COURS = "En cours"
        PAS_NECESSAIRE = "Pas nécessaire"
        TROP_TOT = "Trop tôt"
        CONFIDENTIEL = "Confidentiel"
        SIGNE = "Signé"
        SUR_DRIVE = "Sur Drive"
        PAS_SUR_DRIVE = "Pas sur Drive"
        PAS_FAIT = "Pas Fait"
        SANS_SUITE = "Sans suite"
        PAYEE = "Payée"
        EMISE = "Emise"
        PLUS_NECESSAIRE = "Plus nécessaire"
        A_VERIFIER = "A vérifier"
        PAS_A_JOUR = "Pas à jour"
        DOCUMENTS_LEGAUX = "Documents légaux ?"
        FAIT = "Fait"

    # Define a function to return the default dictionary for 'suivi_document'
    def default_suivi_document():
        return {
            "Devis": {
                "status": Etude.Etat_Doc.TROP_TOT,
                "date": None,
                "remarque": "remarque",
            },
            "CE": {
                "status": Etude.Etat_Doc.TROP_TOT,
                "date": None,
                "remarque": "remarque",
            },
            "Validation des Intervenants": {
                "status": Etude.Etat_Doc.TROP_TOT,
                "date": None,
                "remarque": "remarque",
            },
            "RDM": {
                "status": Etude.Etat_Doc.TROP_TOT,
                "date": None,
                "remarque": "remarque",
            },
            "Facture d'Acompte": {
                "status": Etude.Etat_Doc.TROP_TOT,
                "date": None,
                "remarque": "remarque",
            },
            "PVRF": {
                "status": Etude.Etat_Doc.TROP_TOT,
                "date": None,
                "remarque": "remarque",
            },
            "Facture de Solde": {
                "status": Etude.Etat_Doc.TROP_TOT,
                "date": None,
                "remarque": "remarque",
            },
            "QS Etudiant": {
                "status": Etude.Etat_Doc.TROP_TOT,
                "date": None,
                "remarque": "remarque",
            },
            "QS Client": {
                "status": Etude.Etat_Doc.TROP_TOT,
                "date": None,
                "remarque": "remarque",
            },
            "BV (Etudiants payés)": {
                "status": Etude.Etat_Doc.TROP_TOT,
                "date": None,
                "remarque": "remarque",
            },
            "Echange Client": {
                "status": Etude.Etat_Doc.TROP_TOT,
                "date": None,
                "remarque": "remarque",
            },
            "Livrables": {
                "status": Etude.Etat_Doc.TROP_TOT,
                "date": None,
                "remarque": "remarque",
            },
        }

    suivi_document = models.JSONField(default=default_suivi_document)

    def __str__(self):
        return self.titre

    def ref(self):
        current_year = self.date_creation.year
        current_year_last_two_digits = current_year % 100
        return f"{current_year_last_two_digits}e{self.numero:02d}"

    def get_display_dict(self):
        intermediary_dict = {
            "Titre": self.titre,
            "Description": self.description,
            "Numéro": self.numero,
            "Client": str(self.client),
            "Début": self.debut,
            "Fin": self.fin(),
            "Responsable": str(self.responsable),
            "Nombre de JEH": self.nb_JEH(),
            "Montant HT": self.montant_HT_total(),
        }
        return intermediary_dict

    def get_li_students(self):
        phases = Phase.objects.filter(etude=self)
        student_set = set()
        for phase in phases:
            student_set.update(phase.li_eleves())
        return student_set

    def get_title_details(self):
        return "Détails de la mission"

    def liste_doc(self):
        return []

    def duree_semaine(self):
        phases = Phase.objects.filter(etude=self)
        if phases.exists():
            duree = max(
                phase.duree_semaine + phase.debut_relatif
                for phase in phases
                if phase.duree_semaine is not None and phase.debut_relatif is not None
            )
            return duree
        else:
            return 0

    def fin(self):
        if self.debut and self.duree_semaine():
            return self.debut + datetime.timedelta(weeks=self.duree_semaine())
        else:
            return None

    def nb_JEH(self):
        phases = Phase.objects.filter(etude=self)
        total_JEH = (
            sum(phase.nb_JEH for phase in phases if phase.nb_JEH is not None)
            if phases.exists()
            else 0
        )
        return total_JEH

    def nb_phases(self):
        phases = Phase.objects.filter(etude=self)
        nombres_de_phases = len(phases)
        return nombres_de_phases

    def montant_phase_HT(self):
        phases = Phase.objects.filter(etude=self)
        total_montant_HT = (
            sum(
                phase.montant_HT_par_JEH * phase.nb_JEH
                for phase in phases
                if phase.montant_HT_par_JEH is not None and phase.nb_JEH is not None
            )
            if phases.exists()
            else 0
        )
        return total_montant_HT

    def montant_HT_total(self):
        return self.frais_dossier + self.montant_phase_HT()

    def TVA(self):
        return (self.taux_tva / 100) * self.montant_HT_total()

    def total_ttc(self):
        return (1 + self.taux_tva / 100) * self.montant_HT_total()

    def charges_URSSAF(self):
        return (
            self.nb_JEH() * self.je.base_urssaf * self.je.taux_cotisations / 100
            if self.nb_JEH()
            else 0
        )

    def retributions_totales(self):
        phases = Phase.objects.filter(etude=self)
        return (
            sum(
                phase.retributions()
                for phase in phases
                if phase.retributions() is not None
            )
            if phases.exists()
            else 0
        )

    def marge_JE(self):
        return (
            self.montant_HT_total()
            - self.retributions_totales()
            - self.charges_URSSAF()
        )

    def get_bon_commandes(self):
        return BonCommande.objects.filter(etude=self)

    def facture_solde(self):
        factures = Facture.objects.filter(etude=self).order_by("numero_facture")
        fac_solde = None
        for facture in factures:
            if facture.type_facture == facture.Status.SOLDE:
                fac_solde = facture
        return fac_solde

    def save(self, *args, **kwargs):
        if not self.id_url:
            self.id_url = uuid.uuid4()

        # Save the instance first to ensure it has an ID
        if not self.pk:
            super().save(*args, **kwargs)

        duree = self.duree_semaine()
        if duree is not None and duree < 0:
            raise ValueError("La durée de semaine doit être positive.")

        if (
            self.date_debut_recrutement
            and self.date_fin_recrutement
            and self.date_debut_recrutement > self.date_fin_recrutement
        ):
            raise ValueError(
                "La date de début de recrutement doit être avant la date de fin de recrutement."
            )

        if self.numero is None:
            max_numero = (
                Etude.objects.aggregate(max_numero=Max("numero"))["max_numero"] or 0
            )
            self.numero = max_numero + 1

        super().save(*args, **kwargs)
        if self.type_convention == "Convention d'étude":
            try:
                ConventionEtude.objects.get(etude=self)
            except:
                new_ce = ConventionEtude(etude=self)
                new_ce.save()
        elif self.type_convention == "Convention cadre":
            try:
                ConventionCadre.objects.get(etude=self)
            except:
                new_cc = ConventionCadre(etude=self)
                new_cc.save()

    def createForm(**kwargs):
        return AddEtude()

    def retrieveForm(form, **kwargs):
        if "files" in kwargs.keys():
            return AddEtude(form, kwargs["files"])
        else:
            return AddEtude(form)

    def modifyForm(instance):
        return AddEtude(instance=instance)

    def numero_AP(self, nom_doc):
        return f"{self.numero}{nom_doc}"

    def nombre_phases(self):
        return Phase.objects.filter(etude=self).count()

    def phases(self):
        phases = Phase.objects.filter(etude=self).order_by("numero")
        return phases

    def ce_editable(self):
        return self.responsable is not None and self.resp_qualite is not None

    def convention_edited(self):
        if self.type_convention == "Convention d'étude":
            return ConventionEtude.objects.filter(etude=self).exists()
        elif self.type_convention == "Convention cadre":
            return ConventionCadre.objects.filter(etude=self).exists()
        else:
            return False

    def convention(self):
        if self.type_convention == "Convention d'étude":
            return ConventionEtude.objects.filter(etude=self).first()
        elif self.type_convention == "Convention cadre":
            return ConventionCadre.objects.filter(etude=self).first()

    def nouveau_num_avenant_ce(self):
        list_num = self.convention().avenants_modification.values_list(
            "numero", flat=True
        )
        if len(list_num) == 0:
            return 1
        else:
            return max(list_num) + 1

    def devis_editable(self):
        return self.responsable is not None and self.resp_qualite is not None

    def devis_edited(self):
        return Devis.objects.filter(etude_id=self.id).exists()

    def get_devis(self):
        devis = self.devis.first()
        if devis:
            return devis
        else:
            return None

    def rdm_edited(self):
        return RDM.objects.filter(etude=self).exists()

    def progress_percentage(self):
        duree = self.duree_semaine()
        if duree is None or duree == 0:
            return 0
        total_duration = duree * 7
        if total_duration > 0:
            progress = (timezone.now().date() - self.debut).days
            return int(max(min(100, (progress / total_duration) * 100), 0))
        else:
            return 0


class Facture(models.Model):
    class Status(models.TextChoices):
        ACOMPTE = "Facture d'acompte"
        INTERMEDIAIRE = "Facture intermédiaire"
        SOLDE = "Facture de solde"

    # class TVA(models.TextChoices):
    # FRANCE = 20
    # ETRANGER = 0
    etude = models.ForeignKey(
        "Etude", on_delete=models.CASCADE, related_name="factures"
    )
    facturé = models.BooleanField(default=False)
    pourcentage_JEH = models.FloatField(default=30)
    pourcentage_frais = models.FloatField(default=30)
    type_facture = models.CharField(
        max_length=100, choices=Status.choices, default=Status.ACOMPTE
    )
    numero_facture = models.IntegerField(null=True)
    #fac_frais = models.FloatField(default=0)
    # montant_HT=models.FloatField(default=30)
    TVA_per = models.IntegerField(default=20)
    date_emission = models.DateField(null=True)
    date_echeance = models.DateField(null=True)
    facture_pdf = models.FileField(upload_to="factures/pdfs/", null=True, blank=True)

    def __str__(self):
        if self.date_emission:
            current_year = self.date_emission.year
            current_year_last_two_digits = current_year % 100
            return f"{current_year_last_two_digits}{self.numero_facture:03d}"
        else:
            return f"{self.numero_facture:03d}"
    def ref(self):
        if self.date_emission:
            if isinstance(self.date_emission, str):
                current_year = datetime.strptime(self.date_emission, "%Y-%m-%d").year
            else:
                current_year = self.date_emission.year
            current_year_last_two_digits = current_year % 100
            return f"{current_year_last_two_digits}{self.numero_facture:03d}"
        else:
            return f"{self.numero_facture:03d}"

    def bdc(self):
        if self.etude.type_convention == "Convention cadre":
            asso_bdc_fac = AssociationFactureBDC.objects.filter(facture=self).first()

            return asso_bdc_fac.bon_de_commande
        else:
            return None

    def fac_JEH(self):
        if self.etude.type_convention == "Convention cadre":
            bdc = self.bdc()
            if bdc is not None:
                return bdc.montant_phase_HT() * (self.pourcentage_JEH / 100)
            else:
                return 0
        else:
            return self.etude.montant_phase_HT() * (self.pourcentage_JEH / 100)

    def fac_frais(self):
        if self.etude.type_convention == "Convention cadre":
            return self.bdc().frais_dossier * (self.pourcentage_frais / 100)
        else:
            return self.etude.frais_dossier * (self.pourcentage_frais / 100)

    def phases_fac(self):
        if self.etude.type_convention == "Convention cadre":
            return self.bdc().phases()
        else:
            return Phase.objects.filter(etude=self.etude).order_by("numero")

    def montant_HT(self):
        return self.fac_JEH() + self.fac_frais()

    def montant_TVA(self):
        return self.TVA_per * (self.montant_HT()) / 100

    def montant_TTC(self):
        return (self.TVA_per + 100) * (self.montant_HT()) / 100

    def je(self):
        return self.etude.je

    def save(self, *args, **kwargs):
        id_etude = kwargs.pop("id_etude")
        etude = Etude.objects.get(id=id_etude)
        self.etude = etude
        #self.etude = etude
        #self.fac_frais = self.etude.frais_dossier * (self.pourcentage_frais / 100)
        if not self.numero_facture:
            current_year= date.today().year
            je_act= etude.je
            max_numero = Facture.objects.filter(
                date_emission__year=current_year,  # Filter by year
                etude__je=je_act  # Filter by je_act
            ).aggregate(Max('numero_facture'))['numero_facture__max'] 
            self.numero_facture = max_numero + 1
        super(Facture, self).save(*args, **kwargs)


class AssociationFactureBDC(models.Model):
    bon_de_commande = models.ForeignKey(
        "BonCommande", on_delete=models.CASCADE, related_name="associations_facture"
    )
    facture = models.ForeignKey(
        "Facture", on_delete=models.CASCADE, related_name="associations_bdc_fac"
    )

class BV(models.Model):
    
    etude = models.ForeignKey(
        "Etude", on_delete=models.CASCADE, related_name="bvs"
    )
    eleve = models.ForeignKey(
        "Student", on_delete=models.CASCADE, related_name="bvs"

    )
    numero_bv = models.IntegerField(null=True)
    

    
    date_emission = models.DateField(null=True)
    # il faut les assignations jehs, dictionaire ?
    # il faut la ref au rdm ou au dernier avenant
    nb_JEH = models.IntegerField(null=True)
    retr_brute = models.FloatField(null=True)

    def __str__(self):
        if self.date_emission:
            current_year = self.date_emission.year
            current_year_last_two_digits = current_year % 100
            return f"{current_year_last_two_digits}{self.numero_bv:03d}"
        else:
            return f"{self.numero_bv:03d}"

    def ref_rdm(self):
        if self.etude.type_convention == "Convention cadre":
            asso_bdc_fac = AssociationFactureBDC.objects.filter(facture=self).first()

            return asso_bdc_fac.bon_de_commande
        else:
             
            rdm = RDM.objects.filter(etude=self.etude, eleve=self.eleve).first()
            if rdm:
                dernier_avenant = rdm.dernier_avenant()
                if dernier_avenant:
                    return dernier_avenant.ref()
                else:
                    return rdm.ref()
                
            else:
                return None

    def je(self):
        return self.etude.je

    def save(self):
        
        if not self.numero_bv:
            current_year= date.today().year
            je_act= self.je()
            max_numero = BV.objects.filter(
                date_emission__year=current_year,  # Filter by year
                etude__je=je_act  # Filter by je_act
            ).aggregate(Max('numero_bv'))['numero_bv__max'] 
            if max_numero:
                self.numero_bv = max_numero + 1
            else:
                self.numero_bv =   1
        super(BV, self).save()

class Devis(models.Model):
    etude = models.ForeignKey("Etude", on_delete=models.CASCADE, related_name="devis")
    numero = models.IntegerField()
    date_signature = models.DateField(blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)
    date = models.DateField(default=date.today)

    def ref(self):
        ref_etude = self.etude.ref()
        return f"{ref_etude}pv"

    def date_devis(self):
        date = timezone.now()
        self.date = date
        return date

    def save(self, *args, **kwargs):
        if self.numero is None:
            self.numero = len(self.etude.devis.all()) + 1
        super(Devis, self).save(*args, **kwargs)

    def __str__(self):
        current_year = timezone.now().year
        current_year_last_two_digits = current_year % 100
        return f"{current_year_last_two_digits}e{self.etude.numero}D"

    def signe(self):
        return self.date_signature is not None


class PV(models.Model):
    etude = models.ForeignKey("Etude", on_delete=models.CASCADE, related_name="pv")
    numero = models.IntegerField(blank=True, null=True)
    date_signature = models.DateField(blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)
    date = models.DateField(default=date.today)

    class Type(models.TextChoices):
        PVRF = "PVRF", "Procés verbale de recette finale"
        PVRI = "PVRI", "Procés verbale de recette intermédiaire"

    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.PVRF,
        help_text="Sélectionnez le type de procés verbale.",
    )

    def ref(self):
        ref_etude = self.etude.ref()
        if self.type == "PVRF":
            return f"{ref_etude}pvrf"
        else:
            return f"{ref_etude}pvri"

    def date_pv(self):
        date = timezone.now()
        self.date = date
        return date

    def save(self, *args, **kwargs):
        if self.numero is None:
            self.numero = len(self.etude.devis.all()) + 1
        super(Devis, self).save(*args, **kwargs)

    def __str__(self):
        current_year = timezone.now().year
        current_year_last_two_digits = current_year % 100
        return f"{current_year_last_two_digits}e{self.etude.numero}D"

    def signe(self):
        return self.date_signature is not None


class ConventionEtude(models.Model):
    etude = models.ForeignKey(
        "Etude", on_delete=models.CASCADE, related_name="conventions_etude"
    )
    date_signature = models.DateField(blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)

    def __str__(self):
        current_year = timezone.now().year
        current_year_last_two_digits = current_year % 100
        return f"{current_year_last_two_digits}e{self.etude.numero:02d}ce"

    def signe(self):
        return self.date_signature is not None


class ConventionCadre(models.Model):
    etude = models.ForeignKey(
        "Etude", on_delete=models.CASCADE, related_name="conventions_cadre"
    )
    date_signature = models.DateField(blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)

    def __str__(self):
        current_year = timezone.now().year
        current_year_last_two_digits = current_year % 100
        return f"{current_year_last_two_digits}e{self.etude.numero}cc"

    def signe(self):
        return self.date_signature is not None


class AvenantRuptureConventionEtude(models.Model):
    ce = models.ForeignKey(
        "ConventionEtude", on_delete=models.CASCADE, related_name="avenants"
    )
    date_signature = models.DateField(blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)

    def __str__(self):
        current_year = timezone.now().year
        current_year_last_two_digits = current_year % 100
        return f"{current_year_last_two_digits}e{self.etude.numero}acc{self.numero}"


class AvenantConventionEtude(models.Model):
    ce = models.ForeignKey(
        "ConventionEtude",
        on_delete=models.CASCADE,
        related_name="avenants_modification",
    )
    numero = models.IntegerField()
    ancien_frais_dossier = models.FloatField(blank=True, null=True)
    nouveau_frais_dossier = models.FloatField(blank=True, null=True)
    date_signature = models.DateField(blank=True, null=True)
    objet = models.TextField(blank=True, null=True)
    avenant_budget = models.BooleanField(blank=True, null=True, default=False)
    avenant_delais = models.BooleanField(blank=True, null=True, default=False)

    def __str__(self):
        current_year = timezone.now().year
        current_year_last_two_digits = current_year % 100
        return (
            f"{current_year_last_two_digits}e{self.ce.etude.numero}ac{self.numero:02d}"
        )

    def save(self, *args, **kwargs):
        if self.numero is None:
            nb_avenants = max(AvenantConventionEtude.objects.filter(ce=self.ce))
            self.numero = nb_avenants + 1
        super(AvenantConventionEtude, self).save(*args, **kwargs)

    def modif_budget(self):
        modifs_jeh = self.phases_modif_jeh
        modif_frais_dossier = False
        if (
            self.ancien_frais_dossier is not None
            and self.nouveau_frais_dossier is not None
        ):
            modif_frais_dossier = (
                self.ancien_frais_dossier != self.nouveau_frais_dossier
            )
        return modifs_jeh.exists() or modif_frais_dossier

    def modif_planning(self):
        modifs_duree = self.phases_modif_duree
        suppressions = self.phases_supprimees
        return modifs_duree.exists() or suppressions.exists()


class SuppressionPhase(models.Model):
    avenant_ce = models.ForeignKey(
        "AvenantConventionEtude",
        on_delete=models.CASCADE,
        related_name="phases_supprimees",
    )
    phase = models.ForeignKey(
        "Phase", on_delete=models.CASCADE, related_name="suppression"
    )


class ModificationDureePhase(models.Model):
    avenant_ce = models.ForeignKey(
        "AvenantConventionEtude",
        on_delete=models.CASCADE,
        related_name="phases_modif_duree",
    )
    phase = models.ForeignKey(
        "Phase", on_delete=models.CASCADE, related_name="modif_duree"
    )
    ancienne_duree = models.IntegerField()
    nouvelle_duree = models.IntegerField()


class ModificationDebutPhase(models.Model):
    avenant_ce = models.ForeignKey(
        "AvenantConventionEtude",
        on_delete=models.CASCADE,
        related_name="phases_modif_debut",
    )
    phase = models.ForeignKey(
        "Phase", on_delete=models.CASCADE, related_name="modif_debut"
    )
    ancien_debut = models.IntegerField()
    nouveau_debut = models.IntegerField()


class ModificationJEHPhase(models.Model):
    avenant_ce = models.ForeignKey(
        "AvenantConventionEtude",
        on_delete=models.CASCADE,
        related_name="phases_modif_jeh",
    )
    phase = models.ForeignKey(
        "Phase", on_delete=models.CASCADE, related_name="modif_jeh"
    )
    ancien_nombre_JEH = models.IntegerField()
    nouveau_nombre_JEH = models.IntegerField()


class BonCommande(models.Model):
    numero = models.IntegerField()
    remarque = models.TextField(blank=True, null=True)
    etude = models.ForeignKey(
        "Etude", on_delete=models.CASCADE, related_name="etude_bdc"
    )
    frais_dossier = models.FloatField(default=0, verbose_name="frais de dossier")
    objectifs = models.TextField(blank=True, null=True, default="")
    cahier_des_charges = models.JSONField(default=dict)
    debut = models.DateField(default=timezone.now, blank=True, null=True)
    acompte_pourcentage = models.IntegerField(default=30)
    periode_de_garantie = models.IntegerField(default=90)

    # methode phase, duree
    def phases(self):
        asso_bdc = (
            AssociationPhaseBDC.objects.filter(bon_de_commande=self)
            .order_by("phase__numero")
            .all()
        )
        if asso_bdc:
            phases = [association.phase for association in asso_bdc]
            if len(phases) > 0:
                return phases
            else:
                return None
        else:
            return None

    def nb_phases(self):
        return len(self.phases())

    def duree_semaine(self):
        phases = self.phases()
        if phases:
            duree = max(
                phase.duree_semaine + phase.debut_relatif
                for phase in phases
                if phase.duree_semaine is not None and phase.debut_relatif is not None
            )
            return duree
        else:
            return 0

    def fin(self):
        if self.debut and self.duree_semaine():
            return self.debut + datetime.timedelta(weeks=self.duree_semaine())
        else:
            return None

    def factures(self):
        asso_bdc_facs = AssociationFactureBDC.objects.filter(bon_de_commande=self).all()

        return [asso_bdc_fac.facture for asso_bdc_fac in asso_bdc_facs]

    def montant_phase_HT(self):
        phases = self.phases()
        if phases is None:
            return 0
        else:
            total_montant_HT = (
                sum(
                    phase.montant_HT_par_JEH * phase.nb_JEH
                    for phase in phases
                    if phase.montant_HT_par_JEH is not None and phase.nb_JEH is not None
                )
                if phases[0]
                else 0
            )
            return total_montant_HT

    def montant_HT_total(self):
        return self.frais_dossier + self.montant_phase_HT()

    def save(self, *args, **kwargs):
        if self.numero is None:
            self.numero = self.etude.numero * 100
        super(BonCommande, self).save(*args, **kwargs)

    def ref(self):
        return str(f"{self.etude.ref()}bc{self.numero}")

    def __str__(self):
        return str(self.numero).zfill(3)

    def delete(self, *args, **kwargs):
        all_assoc_phase = self.associations_phase.all()
        for assoc in all_assoc_phase:
            assoc.phase.delete()

        all_assoc_facture = self.associations_facture.all()
        for assoc in all_assoc_facture:
            assoc.facture.delete()

        # Call the original delete() method
        super().delete(*args, **kwargs)


class AssociationPhaseBDC(models.Model):
    bon_de_commande = models.ForeignKey(
        "BonCommande", on_delete=models.CASCADE, related_name="associations_phase"
    )
    phase = models.ForeignKey(
        "Phase", on_delete=models.CASCADE, related_name="associations_bdc"
    )


class RDM(models.Model):
    etude = models.ForeignKey("Etude", on_delete=models.CASCADE, related_name="rdm")
    eleve = models.ForeignKey("Student", on_delete=models.CASCADE, related_name="rdm")
    date_signature = models.DateField(blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)

    def __str__(self):
        current_year = timezone.now().year
        current_year_last_two_digits = current_year % 100
        initials = self.eleve.first_name[0] + self.eleve.last_name[0]
        return f"{current_year_last_two_digits}e{self.etude.numero:02d}rdm-{initials}"

    def ref(self):
        current_year = timezone.now().year
        current_year_last_two_digits = current_year % 100
        initials = self.eleve.first_name[0] + self.eleve.last_name[0]
        return f"{current_year_last_two_digits}e{self.etude.numero:02d}rdm-{initials}"
    
    def dernier_avenant(self):
        avenant = AvenantRDM.objects.filter(
                rdm=self,  
                date_signature__isnull=False  
            ).order_by('-date_signature').first()
        return avenant

    def signe(self):
        return self.date_signature is not None


class AvenantRuptureRDM(models.Model):
    rdm = models.ForeignKey("RDM", on_delete=models.CASCADE, related_name="avenants")
    date_signature = models.DateField(blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)


class AvenantRDM(models.Model):
    rdm = models.ForeignKey(
        "RDM", on_delete=models.CASCADE, related_name="avenants_modification"
    )
    numero = models.IntegerField()
    date_signature = models.DateField(blank=True, null=True)
    remarque = models.TextField(blank=True, null=True)

    def __str__(self):
        current_year = timezone.now().year
        current_year_last_two_digits = current_year % 100
        return f"{current_year_last_two_digits}e{self.rdm.etude.numero:02d}ardm{self.numero}"

    def save(self, *args, **kwargs):
        if self.numero is None:
            avenant = AvenantRDM.objects.filter(
                rdm=self.rdm,  
                date_signature__isnull=False  
            ).order_by('-date_signature').first()
            if avenant:
                self.numero = avenant.numero + 1
            else:
                self.numero = 1
        super(AvenantRDM, self).save(*args, **kwargs)


class ModificationPhaseRDM(models.Model):
    avenant_rdm = models.ForeignKey(
        "AvenantRDM", on_delete=models.CASCADE, related_name="phases_modif_jeh"
    )
    phase = models.ForeignKey(
        "Phase", on_delete=models.CASCADE, related_name="modif_jeh_rdm"
    )
    ancien_nombre_JEH = models.IntegerField()
    nouveau_nombre_JEH = models.IntegerField()


class BA(models.Model):
    eleve = models.ForeignKey("Student", on_delete=models.CASCADE, related_name="ba")
    number = models.IntegerField(default=604)


class Phase(models.Model):
    etude = models.ForeignKey(Etude, on_delete=models.CASCADE, related_name="etude")
    debut_relatif = models.IntegerField(default=0)
    duree_semaine = models.IntegerField(default=2)
    date_debut = models.DateField(default=date.today)
    date_fin = models.DateField(default=date.today)
    titre = models.CharField(max_length=200)
    description = models.TextField(max_length=5000, blank=True)
    nb_JEH = models.IntegerField()
    montant_HT_par_JEH = models.FloatField()
    numero = models.IntegerField()
    supprimee = models.BooleanField(default=False)

    def nb_JEH_montant_HT(self):
        assignations = AssignationJEH.objects.filter(phase=self)
        # Calculate total nombre_JEH
        total_nombre_JEH = sum(assignation.nombre_JEH for assignation in assignations)
        # Calculate total amount excluding tax (montant_HT)
        montant_HT = total_nombre_JEH * self.montant_HT_par_JEH
        return total_nombre_JEH, montant_HT

    def __str__(self):
        return f"Phase {self.numero}"

    def calcul_mt_HT(self):
        return self.nb_JEH * self.montant_HT_par_JEH

    def save(self, *args, **kwargs):
        id_etude = kwargs.pop("id_etude", None)
        numero = kwargs.pop("numero", None)
        if id_etude is not None:
            etude = Etude.objects.get(id=id_etude)
            self.etude = etude
        if self.numero is None:
            if numero is not None:
                self.numero = numero
            else:
                self.numero = (
                    max(
                        Phase.objects.filter(etude=self.etude).values_list(
                            "numero", flat=True
                        )
                    )
                    + 1
                )
        super(Phase, self).save(*args, **kwargs)

    def li_eleves(self):
        assignations = AssignationJEH.objects.filter(phase=self)
        eleves = {assignation.eleve for assignation in assignations}
        return eleves

    def retributions(self):
        assignations = AssignationJEH.objects.filter(phase=self)
        nb_JEHs = 0
        retr_totale = 0
        if assignations:
            for assignation in assignations:
                retr_totale += assignation.retribution_brute_totale()
                nb_JEHs += assignation.nombre_JEH
        retr_totale += (self.nb_JEH - nb_JEHs) * self.montant_HT_par_JEH * 0.6
        return retr_totale

    def get_montant_HT(self, eleve):
        res = 0
        assignations_JEH = AssignationJEH.objects.filter(phase=self, eleve=eleve)
        for assignation_JEH in assignations_JEH:
            res += (
                assignation_JEH.nombre_JEH
                * self.montant_HT_par_JEH
                * assignation_JEH.pourcentage_retribution
                / 100
            )
        return res

    def get_nb_JEH_eleve(self, eleve):
        res = 0
        assignations_JEH = AssignationJEH.objects.filter(phase=self, eleve=eleve)
        for assignation_JEH in assignations_JEH:
            res += assignation_JEH.nombre_JEH
        return res

    def get_assignations_JEH(self):
        assignations_JEH = AssignationJEH.objects.filter(phase=self)
        return assignations_JEH

    def bon(self):
        association_bdc = self.associations_bdc
        return (
            association_bdc.first().bon_de_commande
            if association_bdc.first().exists()
            else None
        )


class AssignationJEH(models.Model):
    eleve = models.ForeignKey(Student, on_delete=models.CASCADE)
    pourcentage_retribution = models.FloatField()  # en pourcentage
    nombre_JEH = models.IntegerField()
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE)
    # reference= models.CharField(default="rdm" )

    def __str__(self):
        return (
            self.phase.etude.__str__()
            + "___"
            + self.phase.__str__()
            + "___"
            + self.eleve.__str__()
        )

    def retribution_brute_totale(self):
        return (
            self.phase.montant_HT_par_JEH
            * self.nombre_JEH
            * self.pourcentage_retribution
            / 100
        )

    def mt_totale(self):
        return self.phase.montant_HT_par_JEH * self.nombre_JEH

    def save(self, *args, **kwargs):
        id_etude = kwargs.pop("id_etude", None)
        id_phase = kwargs.pop("id_phase", None)
        if id_etude is not None and id_phase is not None:
            etude = Etude.objects.get(id=id_etude)
            phase = Phase.objects.get(id=id_phase)
            self.phase = phase
        super(AssignationJEH, self).save(*args, **kwargs)


class Candidature(models.Model):
    eleve = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="candidatures"
    )
    etude = models.ForeignKey(
        Etude, on_delete=models.CASCADE, related_name="candidatures"
    )
    motivation = models.TextField(max_length=5000)

    def __str__(self):
        return self.eleve.__str__() + " | " + self.etude.__str__()


class Message(models.Model):
    contenu = models.TextField(max_length=5000)
    date = models.DateTimeField()
    expediteur = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="expediteur"
    )
    destinataire = models.ForeignKey(
        Member, on_delete=models.CASCADE, related_name="destinataire"
    )
    je = models.ForeignKey(JE, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)

    def __str__(self):
        if len(self.contenu) > 50:
            return self.contenu[:50] + "..."
        else:
            return self.contenu

    def createForm(**kwargs):
        return AddMessage(**kwargs)

    def retrieveForm(form, **kwargs):
        if "files" in kwargs.keys():
            return AddMessage(form, kwargs["files"])
        else:
            return AddMessage(form)

    def modifyForm(instance):
        return AddMessage(instance=instance)

    def since(self):
        return timezone.now() - self.date

    def get_display_dict(self):
        return {
            "Expéditeur": self.expediteur,
            "Date": self.date,
            "Contenu": self.contenu,
        }

    def get_title_details(self):
        return "Détails du message"


class Notification(models.Model):
    utilisateur = models.ManyToManyField(
        Member, blank=True, related_name="notifications"
    )
    description = models.CharField(max_length=500)
    date_effet = models.DateField()
    date_echeance = models.DateField()
    href_redirect = models.CharField(blank=True, null=True)

    def active(self):
        return (
            self.date_effet <= timezone.now().date()
            and timezone.now().date() <= self.date_echeance
        )

    def __str__(self):
        return self.description

    def send(self):
        users = self.utilisateur.all()
        for user in users:
            if user.setting:
                email_host = settings.EMAIL_HOST
                email_port = settings.EMAIL_PORT
                email_username = settings.EMAIL_USERNAME
                email_password = settings.EMAIL_PASSWORD
                connection = get_connection(
                    host=email_host,
                    port=email_port,
                    username=email_username,
                    password=email_password,
                    use_tls=True,
                )
                send_mail(
                    "Notification SYLEX",
                    self.description,
                    "titoduc1905@gmail.com",
                    [user.email],
                    fail_silently=False,
                    connection=connection,
                )


class CustomMailTemplate(models.Model):
    je = models.ForeignKey(JE, on_delete=models.CASCADE, related_name="mail_templates")
    message = models.TextField(max_length=20000)
    numero = models.IntegerField()

    def __str__(self):
        return "Template " + str(self.numero)


class CreateMailTemplate(forms.ModelForm):
    class Meta:
        model = CustomMailTemplate
        exclude = ["je"]

    def __str__(self):
        return "Nouveau template"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs["class"] = "form-control"


class AddMessage(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["destinataire", "contenu"]

    def __init__(self, *args, **kwargs):
        je = kwargs.pop("je", None)
        super(AddMessage, self).__init__(*args, **kwargs)
        if je:
            self.fields["destinataire"].queryset = Member.objects.filter(je=je)

    def save(self, commit=True, **kwargs):
        message = super(AddMessage, self).save(commit=False)
        message.expediteur = kwargs["expediteur"]
        message.je = message.expediteur.je
        message.date = timezone.now()
        if commit:
            message.save()
        return message

    def __str__(self):
        return "Nouveau message"


class AjouterRemarqueRepresentant(forms.Form):
    model = Representant
    fields = ["remarque"]


class AddMember(forms.Form):
    TITRE_CHOIX = (("M.", "M."), ("Mme", "Mme"))

    class Poste(models.TextChoices):
        PRESIDENT = "PRESIDENT", "président"
        VICE_PRESIDENT = "VICE_PRESIDENT", "vice-président"
        TRESORIER = "TRESORIER", "Trésorier"
        VICE_TRESORIER = "VICE_TRESORIER", "vice-trésorier"
        SECRETAIRE_GENERALE = "SECRETAIRE_GENERALE", "secrétaire générale"
        CHEF_DE_PROJET = "CHEF_DE_PROJET", "chef de projet"
        DIRECTEUR_COMMERCIALE = "DIRECTEUR_COMMERCIALE", "directeur commerciale"
        DIRECTEUR_PROJET = "DIRECTEUR_PROJET", "directeur projet"
        DSI = "DSI", "DSI"
        RESPONSABLE_QUALITE = "RESPONSABLE_QUALITE", "responsable_qualite"
        DIRECTEUR_COMMUNICATION = "DIRECTEUR_COMMUNICATION", "directeur communication"
        DIRECTEUR_RSE = "DIRECTEUR_RSE", "directeur RSE"

    class Departement(models.TextChoices):
        IMI = "IMI", "IMI"
        SEGF = "SEGF", "SEGF"
        GMM = "GMM", "GMM"
        _1A = "1A", "1A"
        GCC = "GCC", "GCC"
        VET = "VET", "VET"
        AUTRE = "AUTRE", "Autre"

    class Promotion(models.TextChoices):
        P022 = "2022", "2022"
        P023 = "2023", "2023"
        P024 = "2024", "2024"
        P025 = "2025", "2025"
        P026 = "2026", "2026"
        P027 = "2027", "2027"
        DD = "DD", "Double-diplome"
        MS = "MS", "Master Spécialisé"
        AUTRE = "AUTRE", "Autre"

    first_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "First Name"}
        ),
    )
    last_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last Name"}
        ),
    )
    titre = forms.ChoiceField(
        choices=TITRE_CHOIX, widget=forms.Select(attrs={"class": "form-control"})
    )
    mail = forms.EmailField(
        max_length=200,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Email"}
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        )
    )
    password_confirmation = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm Password"}
        )
    )
    phone_number = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Phone Number"}
        ),
    )
    adress = forms.CharField(
        max_length=300,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Address"}
        ),
    )
    country = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Country"}
        ),
    )
    promotion = forms.ChoiceField(
        choices=Promotion.choices,
        required=False,
        widget=forms.Select(attrs={"class": "form-control", "placeholder": "Promo"}),
    )
    poste = forms.ChoiceField(
        choices=Poste.choices,
        required=False,
        widget=forms.Select(attrs={"class": "form-control", "placeholder": "Poste"}),
    )
    identifiant_je = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "JE Identifier"}
        ),
    )

    photo = forms.ImageField(
        required=False, widget=forms.FileInput(attrs={"class": "form-control-file"})
    )

    def __str__(self):
        return "Ajouter un membre"

    def name(self):
        return "AddMember"

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirmation = cleaned_data.get("password_confirmation")

        if password and password_confirmation and password != password_confirmation:
            self.add_error("password", "Passwords do not match.")
            raise forms.ValidationError("Passwords do not match.", code="password")
        identifiant_je = cleaned_data.get("identifiant_je")
        try:
            id = uuid.UUID(identifiant_je)
            JE.objects.get(id=id)
        except JE.DoesNotExist:
            self.add_error("identifiant_je", "This JE identifier does not exist.")
            raise forms.ValidationError("This JE identifier does not exist.", code="JE")
        except ValueError:
            self.add_error("identifiant_je", "Invalid UUID format.")
            raise forms.ValidationError("Invalid UUID format.", code="invalid_uuid")

    def save(self, commit=True, **kwargs):
        je = JE.objects.get(id=uuid.UUID(self.cleaned_data["identifiant_je"]))
        student = Student(
            titre=self.cleaned_data["titre"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            mail=self.cleaned_data["mail"],
            phone_number=self.cleaned_data["phone_number"],
            adress=self.cleaned_data["adress"],
            country=self.cleaned_data["country"],
            promotion=self.cleaned_data["promotion"],
            je=je,
        )
        student.save()
        new_member = Member(
            email=self.cleaned_data["mail"],
            student=student,
            je=je,
            titre=self.cleaned_data["titre"],
        )
        if "photo" in self.cleaned_data:
            new_member.photo = self.cleaned_data["photo"]
        if "poste" in self.cleaned_data:
            new_member.poste = self.cleaned_data["poste"]
        new_member.set_password(self.cleaned_data["password"])
        new_member.save()
        return new_member


class AddStudent(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ["je"]

    titre = forms.ChoiceField(choices=Student.TITRE_CHOIX)

    def __str__(self):
        return "Informations de l'étudiant"

    def name(self):
        return "AddStudent"

    def save(self, commit=True, **kwargs):
        student = super(AddStudent, self).save(commit=False)
        if "expediteur" in kwargs:
            student.je = kwargs["expediteur"].je
        if commit:
            student.save()
        return student

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name == "poste":
                member = self.is_member()
                member.poste = self.fields[field_name]
                member.save()
            field = self.fields[field_name]
            field.widget.attrs["class"] = "form-control"


class AddEtude(forms.ModelForm):
    class Meta:
        model = Etude
        exclude = [
            "numero",
            "je",
            "id_url",
            "remarque",
            "debut",
            "date_fin_recrutement",
            "date_debut_recrutement",
            "raison_contact",
            "contexte",
            "objectifs",
            "methodologie",
            "periode_de_garantie",
            "element_a_fournir",
            "paragraphe_intervenant_devis",
            "periode_de_garantie",
            "cahier_des_charges",
            "suivi_document",
        ]
        widgets = {
            "client": SelectSearch(
                {"data-hrefajax": reverse_lazy("client-suggestions")}
            ),
            "departement": forms.SelectMultiple,
        }

    def __str__(self):
        return "Informations de l'étude"

    def name(self):
        return "AddEtude"

    def clean(self):
        cleaned_data = super().clean()
        ddr = cleaned_data.get("date_debut_recrutement")
        dfr = cleaned_data.get("date_fin_recrutement")

        if ddr and dfr and ddr > dfr:
            self.add_error(
                "date_fin_recrutement", "Start date must be before the end date."
            )
            raise ValidationError("Start date must be before the end date.")

        return cleaned_data

    def save(self, commit=True, **kwargs):
        max_numero = Etude.objects.aggregate(max_numero=Max("numero"))["max_numero"]
        if max_numero is None:
            max_numero = 0

        etude = super(AddEtude, self).save(commit=False)
        if "expediteur" in kwargs:
            etude.je = kwargs["expediteur"].je

        if etude.numero is None:
            etude.numero = max_numero + 1

        if commit:
            etude.save()

        return etude

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs["class"] = "form-control"


class AddClient(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ["je"]

    def __str__(self):
        return "Informations du client"

    def name(self):
        return "AddClient"

    def save(self, commit=True, **kwargs):
        client = super(AddClient, self).save(commit=False)
        if "expediteur" in kwargs:
            client.je = kwargs["expediteur"].je
        if commit:
            client.save()
        return client

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs["class"] = "form-control"


class AddRepresentant(forms.ModelForm):
    class Meta:
        model = Representant
        exclude = [
            "je",
            "contact_rec",
            "contenu_mail",
            "date_mail",
            "date_reponse",
            "contenu_reponse",
            "demarchage",
            "client",
            "contact_recent",
        ]

    def __str__(self):
        return "Informations du représentant"

    def name(self):
        return "AddRepresentant"

    def save(self, commit=True, **kwargs):
        representant = super(AddRepresentant, self).save(commit=False)
        if commit:
            representant.save(**kwargs)
        return representant

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs["class"] = "form-control"


class AddPhase(forms.ModelForm):
    class Meta:
        model = Phase
        exclude = ["etude", "date_debut", "date_fin", "supprimee"]

    def __str__(self):
        return "Information de la Phase"

    def name(self):
        return "AddPhase"

    def save(self, commit=True, **kwargs):
        phase = super(AddPhase, self).save(commit=False)
        if commit:
            phase.save(**kwargs)
        return phase

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs["class"] = "form-control"


class AddFacture(forms.ModelForm):
    class Meta:
        model = Facture
        exclude = [
            "etude",
            "facturé",
            "numero_facture",
            "fac_frais",
            "montant_HT",
            "fichier",
            "date_emission",
            "date_echeance",
            "facture_pdf",
        ]

    def __str__(self):
        return "Information de la Facture"

    def name(self):
        return "AddFacture"

    def save(self, commit=True, **kwargs):
        facture = super(AddFacture, self).save(commit=False)
        if commit:
            facture.save(**kwargs)
        return facture

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs["class"] = "form-control"


class AddIntervenant(forms.ModelForm):
    class Meta:
        model = AssignationJEH
        exclude = ["phase"]

    def __str__(self):
        return "Information de l'AssignationJEH"

    def name(self):
        return "AddIntervenant"

    def save(self, commit=True, **kwargs):
        assignation_jeh = super(AddIntervenant, self).save(commit=False)
        if commit:
            assignation_jeh.save(**kwargs)
        return assignation_jeh

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs["class"] = "form-control"


class SetParametresUtilisateur(forms.ModelForm):
    class Meta:
        model = ParametresUtilisateur
        exclude = ["membre"]

    def statut_etude(self):
        return [
            "param_statut_etude_ec",
            "param_statut_etude_ed",
            "param_statut_etude_t",
        ]

    def col_etude(self):
        return [
            "param_col_etude_numero",
            "param_col_etude_titre",
            "param_col_etude_client",
            "param_col_etude_responsable",
            "param_col_etude_montant_HT",
            "param_col_etude_avancement",
        ]

    def demarchage(self):
        return ["signature"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs["class"] = "custom-control-input"
        self.fields["signature"].widget.attrs["class"] = "form-control"


class Recrutement(forms.Form):
    class Departement(models.TextChoices):
        IMI = "IMI", "IMI"
        SEGF = "SEGF", "SEGF"
        GMM = "GMM", "GMM"
        _1A = "1A", "1A"
        GCC = "GCC", "GCC"
        VET = "VET", "VET"
        AUTRE = "AUTRE", "Autre"

    class Promotion(models.TextChoices):
        P022 = "2022", "2022"
        P023 = "2023", "2023"
        P024 = "2024", "2024"
        P025 = "2025", "2025"
        P026 = "2026", "2026"
        P027 = "2027", "2027"
        DD = "DD", "Double-diplome"
        MS = "MS", "Master Spécialisé"
        AUTRE = "AUTRE", "Autre"

    TITRE_CHOIX = (("M.", "M."), ("Mme", "Mme"))
    titre = forms.ChoiceField(choices=TITRE_CHOIX)
    prenom = forms.CharField(max_length=50)
    nom = forms.CharField(max_length=50)
    email = forms.EmailField(max_length=100)
    promotion = forms.ChoiceField(choices=Promotion.choices, initial=Promotion.P026)
    departement = forms.ChoiceField(
        choices=Departement.choices, initial=Departement.AUTRE
    )
    motivation = forms.CharField(max_length=5000, widget=forms.Textarea)

    def __str__(self):
        return "Formulaire de candidature"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs["class"] = "form-control"
