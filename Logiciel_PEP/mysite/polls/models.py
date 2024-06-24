import datetime
import uuid
from uuid import UUID
from django import forms
from django.db import models
from django.utils import timezone 
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinLengthValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.files.storage import FileSystemStorage
from django.db.migrations.serializer import BaseSerializer
from django.db.migrations.writer import MigrationWriter
from django.db.models import Sum, Max
from django.core.mail import send_mail, get_connection
from django.conf import settings


IMAGE_STORAGE = FileSystemStorage(location="/static/polls/img")
DOC_STORAGE = "polls/"

    
class JE(models.Model):
    nom = models.CharField(max_length=200)
    raison_sociale = models.CharField(max_length=200)
    rue = models.CharField(max_length=200)
    ville = models.CharField(max_length=100)
    code_postal = models.CharField(max_length=10)
    siret = models.CharField(max_length=14, validators=[RegexValidator(r'^[0-9]+$', _('This field must only contain digits')), MinLengthValidator(14, 'This field must contain exactly 14 characters.')])
    APE = models.CharField(max_length=5, validators=[RegexValidator(r'^[0-9]{4}[A-Za-z]$', _('The expected format is 0000A.'))])
    TVA = models.CharField(max_length=13, validators=[RegexValidator(r'^[A-Za-z]{2}[0-9]{11}$', _('The expected format is 2 letters and 11 digits')), MinLengthValidator(13, 'This field must contain exactly 13 characters.')])
    IBAN = models.CharField(max_length=34, validators=[RegexValidator(r'^[A-Z0-9]+$', _('Special characters are not allowed.'))])
    BIC = models.CharField(max_length=34, validators=[RegexValidator(r'^[A-Z0-9]+$', _('Special characters are not allowed.'))])
    check_order = models.CharField(max_length=50)
    logo = models.ImageField(storage=IMAGE_STORAGE)
    chiffres_affaires = models.FloatField(default=0.0, validators=[MinValueValidator(0)])
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)


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




class JESerializer(BaseSerializer):
    def serialize(self):
        # Customize the serialization logic for the 'JE' model
        return "JE.objects.get(pk={})".format(repr(self.value.pk)), {"from polls.models import JE"}

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
    "id" : "bab6b8bec2744faeb6343c6a40968534" 
}



class Client(models.Model):
    class Type(models.TextChoices):
        GRANDE_ENTREPRISE = 'GRANDE_ENTREPRISE', 'Grande entreprise'
        SECTEUR_PUBLIC = 'SECTEUR_PUBLIC', 'Secteur Public'
        START_UP_ET_TPE = 'START_UP_ET_TPE', 'Start-up et TPE'
        PME = 'PME', 'Petite et moyenne entreprise'
        ETI = 'ETI', 'Entreprise de taille intermédiaire'
        ASSOCIATION = 'ASSOCIATION', 'Association' 
    class Secteur(models.TextChoices):
        INDUSTRIE = 'INDUSTRIE', 'Industrie'
        DISTRIBUTION = 'DISTRIBUTION', 'Distribution'
        SECTEUR_PUBLIC = 'SECTEUR_PUBLIC', 'Secteur Public'
        CONSEIL = 'CONSEIL', 'Conseil'
        TRANSPORT = 'TRANSPORT', 'Transport'
        NUMERIQUE = 'NUMERIQUE', 'Numerique'
        BTP = 'BTP', 'BTP'
        AUTRE = 'AUTRE', 'Autre'

    TITRE_CHOIX = (('M.', 'M.'), ('Mme', 'Mme'))
    nom_societe = models.CharField(max_length = 200)
    raison_sociale = models.CharField(max_length = 150)
    rue = models.CharField(max_length = 300)
    ville = models.CharField(max_length = 100)
    code_postal = models.CharField(max_length = 20)
    country = models.CharField(max_length = 100)
    titre_representant = models.CharField(max_length = 5, choices=TITRE_CHOIX)
    nom_representant = models.CharField(max_length = 100)
    fonction_representant = models.CharField(max_length = 100)
    je = models.ForeignKey(JE, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to=DOC_STORAGE)
    secteur = models.CharField(
        max_length=20,
        choices=Secteur.choices,
        default=Secteur.SECTEUR_PUBLIC,
        help_text="Sélectionnez le secteur d'activité du client."
    )
    _type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.SECTEUR_PUBLIC,
        help_text="Sélectionnez le type d'entreprise."
    )



    def __str__(self):
        return self.nom_societe

    def get_display_dict(self):
        return {'Nom de société':self.nom_societe, 'Raison sociale': self.raison_sociale, 'Adresse': self.rue+'\n'+self.ville+'\n'+self.code_postal,'Pays':self.country, 'Représentant':self.nom_representant, 'Fonction du représentant':self.fonction_representant}

    def get_title_details(self):
        return "Détails du client"
    
    def createForm(**kwargs):
        return AddClient()
    
    def retrieveForm(form):
        return AddClient(form) 

    def modifyForm(instance):
        return AddClient(instance=instance)  
    
class Student(models.Model):
    class Departement(models.TextChoices):
        IMI = 'IMI', 'IMI'
        SEGF = 'SEGF', 'SEGF'
        GMM = 'GMM', 'GMM'
        _1A = '1A', '1A'
        GCC = 'GCC', 'GCC'
        VET = 'VET', 'VET'
        AUTRE = 'AUTRE', 'Autre'
    first_name = models.CharField(max_length = 200)
    last_name = models.CharField(max_length = 200)
    mail = models.EmailField(max_length = 200)
    phone_number = models.CharField(max_length=200, blank=True, null=True)
    adress = models.CharField(max_length = 300, null=True)
    country = models.CharField(max_length = 100, null=True)
    promotion = models.CharField(max_length = 200, blank=True, null=True)
    departement = models.CharField(max_length=20, choices=Departement.choices, default=Departement.AUTRE)
    je = models.ForeignKey(JE, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.first_name+' '+self.last_name
    
    def get_display_dict(self):
        return {"Prénom":self.first_name, "Nom":self.last_name, "Email":self.mail, "Numéro de téléphone":self.phone_number, "Promotion":self.promotion, "Departement":self.departement}

    def get_title_details(self):
        return "Détails de l'étudiant"
    
    def createForm(**kwargs):
        return AddStudent()
    
    def retrieveForm(form):
        return AddStudent(form)

    def modifyForm(instance):
        return AddStudent(instance=instance)
    
    def nb_candidatures(self):
        return Candidature.objects.filter(eleve=self).count()
    
    def nb_etudes_realisees(self):
        return self.etude_set.count()

    def default():
    # Create a JE instance with the provided default values
        default_je = JE(**default_je_data)
    
        return Student(
            first_name="Edgar",
            last_name="Duc",
            mail="edgar.duc@eleves.enpc.fr",
            phone_number="+33783654605",
            adress="7 Allée des Sorbiers, 77420 Champs-sur-Marne",
            country="France",
            promotion="025",
            je=default_je,
        )


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, je=None, student=None, titre=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if 'is_superuser' not in extra_fields or not extra_fields.get('is_superuser', False):
            if not je:
                raise ValueError('The JE association is required for regular users')
        
        email = self.normalize_email(email)
        user = self.model(email=email, je=je, student=student, titre=titre, **extra_fields)
        
        if password:
            user.set_password(password)
        
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        # Note: 'je' n'est pas nécessaire pour un superutilisateur.
        return self.create_user(email, password, **extra_fields)


class Member(AbstractUser):
    TITRE_CHOIX = (('M.', 'M.'), ('Mme', 'Mme'))
    je = models.ForeignKey('JE', on_delete=models.CASCADE, null=True)
    student = models.OneToOneField('Student', on_delete=models.CASCADE, null=True)
    titre = models.CharField(max_length=5, choices=TITRE_CHOIX)
    email = models.EmailField(max_length=200, primary_key=True)
    photo = models.ImageField(storage=IMAGE_STORAGE, default='/static/polls/img/undraw_profile.svg') #local
    #photo = models.ImageField(upload_to='polls/', null=True, blank=True) #Par defaut S3
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.student.__str__()
    
    def createForm(**kwargs):
        return AddMember()
    
    def retrieveForm(form):
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

# alors en gros dans Etude tu veux 1) L'état de l'étude en négociation / Signé / En cours / Terminée  2) Les étapes d'avancement
# de la mission (les phases) : ceux-ci contiennent différentes dates avec le nom des étapes et le prix de chacune d'elle 3) #
# afficher le planning de l'étude


class Etude(models.Model):
    class Status(models.TextChoices):
        EN_NEGOCIATION = 'EN_NEGOCIATION', 'En négociation'
        EN_COURS = 'EN_COURS', 'En cours'
        TERMINEE = 'TERMINEE', 'Terminée'
    class TypeConvention(models.TextChoices):
        CADRE = "Convention cadre"
        ETUDE = "Convention d'étude"
    titre = models.CharField(max_length = 200)
    numero = models.CharField(max_length = 10)
    description = models.TextField(max_length=500, blank=True)
    debut = models.DateField(blank=True)
    duree_semaine = models.IntegerField()
    resp_qualite = models.ForeignKey(Member, on_delete=models.CASCADE, null=True, blank=True, related_name="qualite_etudes")
    responsable = models.ForeignKey(Member, on_delete=models.CASCADE,null=True, blank=True, related_name="responsable_etudes")
    #liste des étudiants via méthodes get_li_students
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    je = models.ForeignKey(JE, on_delete=models.CASCADE)
    frais_dossier = models.FloatField(default = 0)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.EN_NEGOCIATION)
    type_convention = models.CharField(choices=TypeConvention.choices, blank=True, verbose_name="Type de convention")
    id_url = models.UUIDField(primary_key=False, editable=True, unique=False)
    date_debut_recrutement = models.DateField(blank=True, null=True, verbose_name="Debut du recrutement")
    date_fin_recrutement = models.DateField(blank=True, null=True, verbose_name="Fin du recrutement")
    remarque = models.TextField(blank=True, null=True, default="")
    #nb_factures = models.IntegerField(default = 2)
    
    def __str__(self):
        return self.titre

    def get_display_dict(self):
        intermediary_dict = {'Titre':self.titre, 'Description': self.description, 'Numéro':self.numero, 'Client':self.client.__str__(), 'Début':self.debut, 'Fin':self.fin(), 'Responsable':self.responsable.__str__(), 'Nombre de JEH':self.nb_JEH(), 'Montant HT':self.montant_HT()}
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
    
    def fin(self):
        return self.debut+datetime.timedelta(weeks=self.duree_semaine)
    
    def nb_JEH(self):
        phases = Phase.objects.filter(etude=self)
        total_JEH = sum(phase.nb_JEH for phase in phases)
        return total_JEH
    
    def montant_HT(self):
        phases = Phase.objects.filter(etude=self)
        total_montant_HT = sum(phase.montant_HT_par_JEH * phase.nb_JEH for phase in phases)
        return total_montant_HT
    def montant_HT_totale(self):
        return self.frais_dossier+self. montant_HT()
    def TVA(self):
        return 0.2*self.montant_HT_totale()
    def total_ttc(self):
        return 1.2*self.montant_HT_totale()

    def save(self, *args, **kwargs):
        # Your custom validation logic here before saving
        # For example, you can check if the value matches the regex pattern
        
        if self.id_url is None:
            self.id_url = uuid.uuid4()
        if self.duree_semaine < 0:
            raise ValueError('Begin must be set before end.')
        if self.date_debut_recrutement and self.date_fin_recrutement and self.date_debut_recrutement > self.date_fin_recrutement :
            raise ValueError('Begin must be set before end.')
        if self.numero is None:
            self.numero = Etude.objects.count() + 1
        
        super().save(*args, **kwargs)
    
    def createForm(**kwargs):
        return AddEtude()
    
    def retrieveForm(form):
        return AddEtude(form)

    def modifyForm(instance):
        return AddEtude(instance=instance)

    def numero_AP(self, nom_doc):
        return self.numero+nom_doc
    
    
    def nombre_phases(self):
        phases = Phase.objects.filter(etude=self)
        return len(phases)
    
    def ce_editable(self):
        has_responsable = self.responsable is not None
        has_qualite = self.resp_qualite is not None
        return has_responsable and has_qualite
    
    def convention_edited(self):
        if self.type_convention == "Convention d'étude":     
            return ConventionEtude.objects.filter(etude=self).exists()
        elif self.type_convention == "Convention cadre":
            return ConventionCadre.objects.filter(etude=self).exists()
        else:
            return False
        
    def convention(self):
        if self.type_convention == "Convention d'étude": 
            conventions = ConventionEtude.objects.filter(etude=self)
        elif self.type_convention == "Convention cadre":
            conventions = ConventionCadre.objects.filter(etude=self)
        else:
            return None
        if conventions.exists():
            return conventions[0]
        else:
            return None
        
    def devis_editable(self):
        has_responsable = self.responsable is not None
        has_qualite = self.resp_qualite is not None
        return has_responsable and has_qualite
    
    def devis_edited(self):
        return Devis.objects.filter(etude=self).exists()
    
    def devis(self):
        devis = Devis.objects.filter(etude=self)
        if(devis.exists()):
            return devis[0]
        else:
            None

class Facture(models.Model):
    class Status(models.TextChoices):
        ACOMPTE =  "Facture d'acompte"
        INTERMEDIAIRE = 'Facture intermédiaire'
        SOLDE = 'Facture de solde'
    #class TVA(models.TextChoices):
        #FRANCE = 20
        #ETRANGER = 0
    etude = models.ForeignKey('Etude', on_delete=models.CASCADE, related_name='factures')
    facturé = models.BooleanField(default=False)
    pourcentage_JEH = models.FloatField(default=30)
    pourcentage_frais = models.FloatField(default=30)
    type_facture = models.CharField(max_length=30, choices=Status.choices, default=Status.SOLDE)
    numero_facture = models.IntegerField(default=5) 
    fac_frais=models.FloatField(default=0)
    montant_HT=models.FloatField(default=30)
    fichier = models.FileField(upload_to=DOC_STORAGE, storage=DOC_STORAGE)
    TVA_per =  models.IntegerField(default=20)
    date_emission = models.DateField(null=True)
    date_echeance = models.DateField(null=True)
    def fac_JEH(self):
        return self.etude.montant_HT() * (self.pourcentage_JEH / 100)
    def phases_fac(self):
        return Phase.objects.filter(etude=self.etude).order_by('numero')
    def montant_HT_fac(self,phase):
        return phase.montant_HT_par_JEH*self.pourcentage_JEH*phase.nb_JEH/100
    
    def montant_TVA(self):
        return self.TVA_per*(self.fac_JEH() + self.fac_frais)/100
    def montant_TTC(self):
        return (self.TVA_per+100)*(self.fac_JEH()+self.fac_frais)/100
    def save(self, *args, **kwargs):
        id_etude = kwargs.pop('id_etude')
        etude = Etude.objects.get(id=id_etude)
        self.etude = etude
        self.fac_frais = self.etude.frais_dossier * (self.pourcentage_frais/ 100)
        self.numero_facture = len(Facture.objects.filter(etude=etude))+1
        self.montant_HT=self.etude.montant_HT() * (self.pourcentage_JEH / 100) + self.etude.frais_dossier * (self.pourcentage_frais/ 100)
        super(Facture, self).save(*args, **kwargs)


class Devis(models.Model):
    etude = models.ForeignKey('Etude', on_delete=models.CASCADE, related_name="devis")
    fichier = models.FileField(upload_to=DOC_STORAGE, storage=DOC_STORAGE)
    numero = models.IntegerField()

    def save(self, *args, **kwargs):
        if (self.numero is None):
            self.numero = len(self.etude.devis.all())+1
        super(Devis, self).save(*args, **kwargs)

    def __str__(self):
        current_year = timezone.now().year
        current_year_last_two_digits = current_year % 100
        return f"{current_year_last_two_digits}e{self.etude.numero}D"

class ConventionEtude(models.Model):
    etude = models.ForeignKey('Etude', on_delete=models.CASCADE, related_name="conventions_etude")
    fichier = models.FileField(upload_to=DOC_STORAGE, storage=DOC_STORAGE)

    def __str__(self):
        current_year = timezone.now().year
        current_year_last_two_digits = current_year % 100
        return f"{current_year_last_two_digits}e{self.etude.numero}CE"

class ConventionCadre(models.Model):
    etude = models.ForeignKey('Etude', on_delete=models.CASCADE, related_name="conventions_cadre")
    fichier = models.FileField(upload_to=DOC_STORAGE, storage=DOC_STORAGE)

    def __str__(self):
        current_year = timezone.now().year
        current_year_last_two_digits = current_year % 100
        return f"{current_year_last_two_digits}e{self.etude.numero}CC"

class BonCommande(models.Model):
    convention_cadre = models.ForeignKey('ConventionCadre', on_delete=models.CASCADE, related_name="bons_commande")
    numero = models.IntegerField()
    fichier = fichier = models.FileField(upload_to=DOC_STORAGE, storage=DOC_STORAGE)

    def save(self, *args, **kwargs):
        if (self.numero is None):
            self.numero = len(self.convention_cadre.bons_commande.all())+1
        super(BonCommande, self).save(*args, **kwargs)


class Phase(models.Model):
    etude = models.ForeignKey(Etude, on_delete=models.CASCADE, related_name='phases')
    date_debut = models.DateField()
    date_fin = models.DateField()
    titre = models.CharField(max_length = 200)
    description = models.TextField(max_length = 5000, blank=True)
    nb_JEH = models.IntegerField()
    montant_HT_par_JEH = models.FloatField()
    numero = models.IntegerField()

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
        id_etude = kwargs.pop('id_etude')
        etude = Etude.objects.get(id=id_etude)
        #etude=self.etude()
        self.etude = etude

        super(Phase, self).save(*args, **kwargs)
        
    def li_eleves(self):
        assignations = AssignationJEH.objects.filter(phase=self)
        eleves = {assignation.eleve for assignation in assignations}
        return eleves
    
    def get_montant_HT(self, eleve):
        res=0
        assignations_JEH = AssignationJEH.objects.filter(phase=self, eleve=eleve)
        for assignation_JEH in assignations_JEH:
            res += assignation_JEH.nombre_JEH * self.montant_HT_par_JEH
        return res
    
    def get_assignations_JEH(self):
        assignations_JEH = AssignationJEH.objects.filter(phase=self)
        return assignations_JEH
    

class AssignationJEH(models.Model):
    eleve = models.ForeignKey(Student, on_delete=models.CASCADE)
    pourcentage_retribution = models.FloatField()  #en pourcentage
    nombre_JEH = models.IntegerField()
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE)

    def __str__(self):
        return self.phase.etude.__str__()+"___"+self.phase.__str__()+"___"+self.eleve.__str__()
    
    def retribution_brute_totale(self):
        return self.phase.montant_HT_par_JEH * self.nombre_JEH * self.pourcentage_retribution/100
    
    def save(self, *args, **kwargs):
        id_etude = kwargs.pop('id_etude')
        numero_phase = kwargs.pop('numero_phase')
        etude = Etude.objects.get(id=id_etude)
        phase = Phase.objects.get(etude=etude, numero=numero_phase)
        self.phase = phase
        super(AssignationJEH, self).save(*args, **kwargs)

class Candidature(models.Model):
    eleve = models.ForeignKey(Student, on_delete=models.CASCADE)
    etude = models.ForeignKey(Etude, on_delete=models.CASCADE, related_name="candidatures")
    motivation = models.TextField(max_length=5000)
    def __str__(self):
        return self.eleve.__str__()+" | "+self.etude.__str__()
    
    

class Message(models.Model):
    contenu = models.TextField(max_length=5000)
    date = models.DateTimeField()
    expediteur = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="expediteur")
    destinataire = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="destinataire")
    je = models.ForeignKey(JE, on_delete=models.CASCADE)
    read = models.BooleanField(default = False)

    def __str__(self):
        if len(self.contenu)>50:
            return self.contenu[:50]+"..."
        else:
            return self.contenu

    def createForm(**kwargs):
        return AddMessage(**kwargs)
    
    def retrieveForm(form):
        return AddMessage(form)

    def modifyForm(instance):
        return AddMessage(instance=instance)

    def since(self):
        return timezone.now() - self.date

    def get_display_dict(self):
        return {'Expéditeur':self.expediteur, 'Date': self.date, 'Contenu':self.contenu}

    def get_title_details(self):
        return "Détails du message"

class Notification(models.Model):
    utilisateur = models.ManyToManyField(Member, blank=True)
    description = models.CharField(max_length=500)
    date_effet = models.DateField()
    date_echeance = models.DateField()
    def active(self):
        return (self.date_effet <= timezone.now() and timezone.now() <= self.date_echeance)
    def __str__(self):
        return self.description
    def send(self):
        users = self.utilisateur.all()
        for user in users:
            if user.setting :
                email_host = settings.EMAIL_HOST
                email_port = settings.EMAIL_PORT
                email_username = settings.EMAIL_USERNAME
                email_password = settings.EMAIL_PASSWORD
                connection = get_connection(host=email_host, port=email_port, username=email_username,
                    password=email_password,
                    use_tls=True,)
                send_mail("Notification SYLEX", self.description, "titoduc1905@gmail.com", [user.email], 
                        fail_silently=False, 
                        connection=connection)

class AddMessage(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['destinataire', 'contenu']

    def __init__(self, *args, **kwargs):
        je = kwargs.pop('je', None)
        super(AddMessage, self).__init__(*args, **kwargs) 
        if je:
            self.fields['destinataire'].queryset = Member.objects.filter(je=je)

    def save(self, commit=True, **kwargs):
        message = super(AddMessage, self).save(commit=False)
        message.expediteur = kwargs['expediteur']
        message.je = message.expediteur.je
        message.date = timezone.now()
        if commit:
            message.save()
        return message

    def __str__(self):
        return "Nouveau message"


class AddMember(forms.Form):
    TITRE_CHOIX = (('M.', 'M.'), ('Mme', 'Mme'))
    first_name = forms.CharField(max_length=200)
    last_name = forms.CharField(max_length=200)
    titre = forms.ChoiceField(choices=TITRE_CHOIX)
    mail = forms.EmailField(max_length=200)
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirmation = forms.CharField(widget=forms.PasswordInput) 
    phone_number = forms.CharField(max_length=200)
    adress = forms.CharField(max_length=300)
    country = forms.CharField(max_length=100)
    promotion = forms.CharField(max_length=200, required=False)
    identifiant_je = forms.CharField(max_length = 50)
    photo = forms.ImageField(required=False)
    def __str__(self):
        return "Ajouter un membre"
    def name(self):
        return "AddMember"

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        if password and password_confirmation and password != password_confirmation:
            self.add_error('password', "Passwords do not match.")
            raise forms.ValidationError("Passwords do not match.", code="password")
        identifiant_je = cleaned_data.get('identifiant_je')
        try:
            id = uuid.UUID(identifiant_je)
            JE.objects.get(id=id)
        except JE.DoesNotExist:
            self.add_error('identifiant_je', "This JE identifier does not exist.")
            raise ValidationError("This JE identifier does not exist.", code="JE")
        except ValueError:
            self.add_error('identifiant_je', "Invalid UUID format.")
            raise ValidationError("Invalid UUID format.", code="invalid_uuid")

    def save(self, commit=True, **kwargs):
        # Create and save a new Student object using the form data
        je = JE.objects.get(id=uuid.UUID(self.cleaned_data['identifiant_je']))
        student = Student(
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            mail=self.cleaned_data['mail'],
            phone_number=self.cleaned_data['phone_number'],
            adress=self.cleaned_data['adress'],
            country=self.cleaned_data['country'],
            promotion=self.cleaned_data['promotion'],
            je=je
        )
        student.save()
        new_member = Member(email=self.cleaned_data['mail'], student=student, je=je, titre=self.cleaned_data['titre'])
        if 'photo' in self.cleaned_data and self.cleaned_data['photo']:
            new_member.photo = self.cleaned_data['photo']
        new_member.set_password(self.cleaned_data['password'])
        new_member.save()
        return new_member


    
class AddStudent(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['je']
    def __str__(self):
        return "Informations de l'étudiant"
    def name(self):
        return "AddStudent"
    def save(self, commit=True, **kwargs):
        student = super(AddStudent, self).save(commit=False)
        student.je = kwargs['expediteur'].je
        if commit:
            student.save()
        return student
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs['class'] = 'form-control'
    
class AddEtude(forms.ModelForm):
    error_message = ""
    class Meta:
        model = Etude
        exclude = ['numero','je', 'students', 'id_url', 'remarque']
    def __str__(self):
        return "Informations de l'étude"
    def name(self):
        return "AddEtude"
    def clean(self):
        cleaned_data = super().clean()
        duree = cleaned_data.get('duree_semaine')
        ddr = cleaned_data.get('date_debut_recrutement')
        dfr = cleaned_data.get('date_fin_recrutement')

        # Vérifiez que la start_date est antérieure à end_date
        if duree<0:
            self.add_error('duree_semaine', 'La durée doit être un entier positif.')
            raise ValidationError(_('La durée doit être un entier positif.'))
        
        if ddr and dfr and ddr > dfr:
            self.add_error('date_fin_recrutement', 'Start date must be before the end date.')
            raise ValidationError(_('Start date must be before the end date.'))

        return cleaned_data
    def save(self, commit=True, **kwargs):
        max_numero = Etude.objects.aggregate(max_numero=Max('numero'))['max_numero']
        if max_numero is None:
            max_numero=0
        etude = super(AddEtude, self).save(commit=False)
        etude.je = kwargs['expediteur'].je
        if etude.numero is None :
            etude.numero = max_numero+1
        if commit:
            etude.save()
        return etude
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['responsable'].widget = forms.TextInput(attrs={'class': 'form-control'})
        #self.fields['client'].widget = forms.TextInput(attrs={'class': 'form-control'})
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs['class'] = 'form-control'
    
class AddClient(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ['je']
    def __str__(self):
        return "Informations du client"
    def name(self):
        return "AddClient"
    def save(self, commit=True, **kwargs):
        client = super(AddClient, self).save(commit=False)
        client.je = kwargs['expediteur'].je
        if commit:
            client.save()
        return client
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs['class'] = 'form-control'
    
    
class AddPhase(forms.ModelForm):
    class Meta:
        model = Phase
        exclude = ['etude','montant_HT','begin','end']
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
            field.widget.attrs['class'] = 'form-control'

class AddFacture(forms.ModelForm):
    class Meta:
        model = Facture
        exclude = ['etude','facturé','numero_facture','fac_frais', 'montant_HT', 'fichier','date_emission','date_echeance']
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
            field.widget.attrs['class'] = 'form-control'

class AddIntervenant(forms.ModelForm):
    class Meta:
        model = AssignationJEH
        exclude = ['phase']
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
            field.widget.attrs['class'] = 'form-control'

class Recrutement(forms.Form):
    prenom = forms.CharField(max_length = 50)
    nom = forms.CharField(max_length = 50)
    email = forms.EmailField(max_length = 100)
    motivation = forms.CharField(max_length = 5000, widget=forms.Textarea)
    def __str__(self):
        return "Formulaire de candidature"
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs['class'] = 'form-control'
    def save(self, commit=True, **kwargs):
        etude = kwargs['etude']
        try :
            student = Student.objects.get(first_name=self.prenom,
                          last_name=self.nom,
                          mail=self.email)
            etude.students.add(student)
            candidature = Candidature(eleve=student, etude=etude, motivation=self.motivation)
            candidature.save()
        except:
            student = Student(first_name=self.prenom,
                            last_name=self.nom,
                            mail=self.email,
                            je=etude.je)
            student.save()
            etude.students.add(student)
            candidature = Candidature(eleve=student, etude=etude, motivation=self.motivation)
            candidature.save()


    

