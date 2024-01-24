import datetime
from django import forms
from django.db import models
from django.utils import timezone 
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, BaseUserManager


class JE(models.Model):
    nom = models.CharField(max_length = 200)
    raison_sociale = models.CharField(max_length = 200)
    adress = models.CharField(max_length = 200)
    siret = models.CharField(max_length = 14, validators=[RegexValidator(r'^[0-9]+$', _('This field must only contain digits')), MinLengthValidator(14, 'This field must contain exactly 14 caracters.')])
    APE = models.CharField(max_length=5, validators=[RegexValidator(r'^[0-9]{4}[A-Za-z]$', _('The expected format is 0000A.'))])
    TVA = models.CharField(max_length=13, validators=[RegexValidator(r'^[A-Za-z]{2}[0-9]{11}$', _('The expected format is 2 letters and 11 digits')), MinLengthValidator(13, 'This field must contain exactly 13 caracters.')])
    IBAN = models.CharField(max_length=34, validators=[RegexValidator(r'^[A-Z0-9]+$', _('Special caracters are not allowed.'))])
    BIC = models.CharField(max_length=34, validators=[RegexValidator(r'^[A-Z0-9]+$', _('Special caracters are not allowed.'))])
    check_order = models.CharField(max_length=50)

    def __str__(self):
        return self.nom

    def default():
        new_je = JE()
        new_je.nom = "PEP"
        new_je.raison_sociale = "Junio-Entreprise des Ponts"
        new_je.adress = "6-8 Avenue Blaise Pascal, 77420 Champs-sur-Marne"
        new_je.siret = "01234567890123"
        new_je.APE = "0000A"
        new_je.TVA = "AA01234567890"
        new_je.IBAN = "FR000000000000000000000"
        new_je.BIC = "0000000000000000000000"
        new_je.check_order = ""
        return new_je

    def get_title_details(self):
        return "Détails de la Junior-Entreprise"
    

class Client(models.Model):
    name = models.CharField(max_length = 200)
    raison_sociale = models.CharField(max_length = 150)
    rue = models.CharField(max_length = 300)
    ville = models.CharField(max_length = 100)
    code_postal = models.CharField(max_length = 20)
    representant = models.CharField(max_length = 100)
    country = models.CharField(max_length = 100)
    siret = models.CharField(max_length = 15, default='12345678901234', validators=[RegexValidator(r'^[0-9]+$'), MinLengthValidator(14, 'This field must contain exactly 14 caracters.')])
    je = models.ForeignKey(JE, on_delete=models.CASCADE, default = 1)

    def __str__(self):
        return self.name

    def get_display_dict(self):
        return {'Nom':self.name, 'Pays':self.country, 'Représentant':representant}

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
    je = models.ForeignKey(JE, on_delete=models.CASCADE, default = 1)

    def __str__(self):
        return self.first_name+' '+self.last_name
    
    def get_display_dict(self):
        return {"Prénom":self.first_name, "Nom":self.last_name, "Promotion":self.promotion}

    def get_title_details(self):
        return "Détails de l'étudiant"
    
    def createForm(**kwargs):
        return AddStudent()
    
    def retrieveForm(form):
        return AddStudent(form)

    def modifyForm(instance):
        return AddStudent(instance=instance)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, je=None, student=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not password:
            raise ValueError('The password field must be set.')
        email = self.normalize_email(email)
        user = self.model(email=email, je=je, student=student)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, username, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class Member(AbstractUser):
    je = models.ForeignKey(JE, on_delete=models.CASCADE, default = 1)
    student = models.OneToOneField(Student, on_delete=models.CASCADE, default=1)
    email = models.EmailField(max_length=200, primary_key=True)
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
        return student.get_display_dict()

    def get_title_details(self):
        return student.get_title_details()

    def save(self, *args, **kwargs):
        self.username = self.email  # Set username to email
        super().save(*args, **kwargs)

class Etude(models.Model):
    description = models.CharField(max_length=200)
    begin = models.DateField()
    end = models.DateField()
    responsable = models.ForeignKey(Member, on_delete=models.CASCADE, default = 1)
    nb_JEH = models.IntegerField()
    montant_HT = models.FloatField()
    students = models.ManyToManyField(Student, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    je = models.ForeignKey(JE, on_delete=models.CASCADE, default = 1)
    
    def __str__(self):
        return self.description

    def get_display_dict(self):
        return {'Description':self.description, 'Client':self.client.__str__(), 'Début':self.begin, 'Fin':self.end, 'Responsable':self.responsable.__str__()}

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

class Message(models.Model):
    contenu = models.CharField(max_length=5000)
    date = models.DateTimeField()
    expediteur = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="expediteur")
    destinataire = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="destinataire")
    je = models.ForeignKey(JE, on_delete=models.CASCADE, default=1)
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
        return {'Expéditeur':self.expediteur, 'Contenu':self.contenu}

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


class AddMember(forms.ModelForm):
    class Meta:
        model = Member
        fields='__all__'
    def __str__(self):
        return "Ajouter un membre"
    def name(self):
        return "AddMember"

    
class AddStudent(forms.ModelForm):
    class Meta:
        model = Student
        fields='__all__'
    def __str__(self):
        return "Informations de l'étudiant"
    def name(self):
        return "AddStudent"
    
class AddEtude(forms.ModelForm):
    error_message = ""
    class Meta:
        model = Etude
        fields='__all__'
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
    
class AddClient(forms.ModelForm):
    class Meta:
        model = Client
        fields='__all__'
    def __str__(self):
        return "Informations du client"
    def name(self):
        return "AddClient"
    



    

