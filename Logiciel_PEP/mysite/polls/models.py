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

IMAGE_STORAGE = FileSystemStorage(location="/static/polls/img")

    
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
        # You may use self.value to access the 'JE' instance being serialized
        # Return a string representation of the 'JE' instance and any required imports
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
    je = models.ForeignKey(JE, on_delete=models.CASCADE, default = JE(**default_je_data))

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
    first_name = models.CharField(max_length = 200)
    last_name = models.CharField(max_length = 200)
    mail = models.EmailField(max_length = 200)
    phone_number = models.CharField(max_length=200, blank=True)
    adress = models.CharField(max_length = 300)
    country = models.CharField(max_length = 100)
    promotion = models.CharField(max_length = 200, blank=True)
    je = models.ForeignKey(JE, on_delete=models.CASCADE, default = JE(**default_je_data))

    def __str__(self):
        return self.first_name+' '+self.last_name
    
    def get_display_dict(self):
        return {"Prénom":self.first_name, "Nom":self.last_name, "Email":self.mail, "Numéro de téléphone":self.phone_number, "Promotion":self.promotion}

    def get_title_details(self):
        return "Détails de l'étudiant"
    
    def createForm(**kwargs):
        return AddStudent()
    
    def retrieveForm(form):
        return AddStudent(form)

    def modifyForm(instance):
        return AddStudent(instance=instance)

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
    def create_user(self, email, password, je=None, student=None, titre=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not password:
            raise ValueError('The password field must be set.')
        email = self.normalize_email(email)
        user = self.model(email=email, je=je, student=student, titre=titre)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, username, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class Member(AbstractUser):
    TITRE_CHOIX = (('M.', 'M.'), ('Mme', 'Mme'))
    je = models.ForeignKey(JE, on_delete=models.CASCADE, default = JE(**default_je_data))
    student = models.OneToOneField(Student, on_delete=models.CASCADE, default=1)
    titre = models.CharField(max_length = 5, choices=TITRE_CHOIX)
    email = models.EmailField(max_length=200, primary_key=True)
    photo = models.ImageField(storage=IMAGE_STORAGE, default= '/static/polls/img/undraw_profile.svg')
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
    titre = models.CharField(max_length = 200)
    numero = models.CharField(max_length = 10)
    description = models.TextField(max_length=500, blank=True)
    begin = models.DateField()
    end = models.DateField()
    responsable = models.ForeignKey(Member, on_delete=models.CASCADE, default = 1)
    nb_JEH = models.IntegerField()
    montant_HT = models.FloatField()
    students = models.ManyToManyField(Student, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    je = models.ForeignKey(JE, on_delete=models.CASCADE, default = JE(**default_je_data))
    frais_dossier = models.FloatField(default = 0)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.EN_NEGOCIATION)

                              

    def __str__(self):
        return self.titre

    def get_display_dict(self):
        intermediary_dict = {'Titre':self.titre, 'Description': self.description, 'Numéro':self.numero, 'Client':self.client.__str__(), 'Début':self.begin, 'Fin':self.end, 'Responsable':self.responsable.__str__(), 'Nombre de JEH':self.nb_JEH, 'Montant HT':self.montant_HT}
        liste_etudiants = self.students.all()
        for index in range(len(liste_etudiants)) :
            intermediary_dict['Etudiant '+str(index+1)] = liste_etudiants[index].__str__()
        return intermediary_dict

    def get_title_details(self):
        return "Détails de la mission"
    
    def save(self, *args, **kwargs):
        # Your custom validation logic here before saving
        # For example, you can check if the value matches the regex pattern
        if self.begin > self.end:
            raise ValueError('Begin must be set before end.')

        super().save(*args, **kwargs)
    
    def createForm(**kwargs):
        return AddEtude()
    
    def retrieveForm(form):
        return AddEtude(form)

    def modifyForm(instance):
        return AddEtude(instance=instance)

    def numero_AP(self, nom_doc):
        return self.numero+nom_doc
    
    def calcul_montant_total_HT(self):
        phases = Phase.objects.filter(etude=self)
        return sum(phase.montant_HT_par_JEH[1]*phase.nb_JEH[1] for phase in phases)
    
    def nombre_phases(self):
        phases = Phase.objects.filter(etude=self)
        return len(phases)
    

class Phase(models.Model):
    etude = models.ForeignKey(Etude, on_delete=models.CASCADE, related_name='phases')
    date_debut = models.DateField()
    date_fin = models.DateField()
    titre = models.CharField(max_length = 200)
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
    
    def save(self, *args, **kwargs):
        id_etude = kwargs.pop('id_etude')
        etude = Etude.objects.get(id=id_etude)
        self.numero = len(Phase.objects.filter(etude=etude))+1
        self.etude = etude
        super(Phase, self).save(*args, **kwargs)
            

class AssignationJEH(models.Model):
    eleve = models.OneToOneField(Student, on_delete=models.CASCADE)
    pourcentage_retribution = models.FloatField()
    nombre_JEH = models.IntegerField()
    phase = models.ForeignKey(Phase, on_delete=models.CASCADE)

    def __str__(self):
        return self.phase.etude.__str__()+"___"+self.phase.__str__()+"___"+self.eleve.__str__()

    

class Message(models.Model):
    contenu = models.TextField(max_length=5000)
    date = models.DateTimeField()
    expediteur = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="expediteur")
    destinataire = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="destinataire")
    je = models.ForeignKey(JE, on_delete=models.CASCADE, default=JE(**default_je_data))
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
        try:
            id = uuid.UUID(cleaned_data.get('identifiant_je'))
            JE.objects.get(id=id)
        except:
            self.add_error('identifiant_je', "This JE identifier does not exist.")
            raise forms.ValidationError("This JE identifier does not exist.", code="JE")

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
        exclude = ['je', 'students']
    def __str__(self):
        return "Informations de l'étude"
    def name(self):
        return "AddEtude"
    def clean(self):
        cleaned_data = super().clean()
        begin = cleaned_data.get('begin')
        end = cleaned_data.get('end')

        # Vérifiez que la start_date est antérieure à end_date
        if begin and end and begin > end:
            raise ValidationError(_('Start date must be before the end date.'))

        return cleaned_data
    def save(self, commit=True, **kwargs):
        etude = super(AddEtude, self).save(commit=False)
        etude.je = kwargs['expediteur'].je
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
        exclude = ['etude', 'numero']
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
    



    

