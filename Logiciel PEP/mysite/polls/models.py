import datetime
from django import forms
from django.db import models
from django.utils import timezone 
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils.translation import gettext_lazy as _


class JE(models.Model):
    raison_sociale = models.CharField(max_length = 200)
    adress = models.CharField(max_length = 200)
    siret = models.CharField(max_length = 14, validators=[RegexValidator(r'^[0-9]+$', _('This field must only contain digits')), MinLengthValidator(14, 'This field must contain exactly 14 caracters.')])
    APE = models.CharField(max_length=5, validators=[RegexValidator(r'^[0-9]{4}[A-Za-z]$', _('The expected format is 0000A.'))])
    TVA = models.CharField(max_length=13, validators=[RegexValidator(r'^[A-Za-z]{2}[0-9]{11}$', _('The expected format is 2 letters and 11 digits')), MinLengthValidator(13, 'This field must contain exactly 13 caracters.')])
    IBAN = models.CharField(max_length=34, validators=[RegexValidator(r'^[A-Z0-9]+$', _('Special caracters are not allowed.'))])
    BIC = models.CharField(max_length=34, validators=[RegexValidator(r'^[A-Z0-9]+$', _('Special caracters are not allowed.'))])
    check_order = models.CharField(max_length=50)

    def default():
        new_je = JE()
        new_je.raison_sociale = "Junio-Entreprise des Ponts"
        new_je.adress = "6-8 Avenue Blaise Pascal, 77420 Champs-sur-Marne"
        new_je.siret = "01234567890123"
        new_je.APE = "0000A"
        new_je.TVA = "AA01234567890"
        new_je.IBAN = "FR000000000000000000000"
        new_je.BIC = "0000000000000000000000"
        new_je.check_order = ""
        return new_je
    

class Client(models.Model):
    name = models.CharField(max_length = 300)
    adress = models.CharField(max_length = 300)
    country = models.CharField(max_length = 100)
    siret = models.CharField(max_length = 15, default='12345678901234', validators=[RegexValidator(r'^[0-9]+$'), MinLengthValidator(14, 'This field must contain exactly 14 caracters.')])
    je = models.ForeignKey(JE, on_delete=models.CASCADE, default = 1)

    def __str__(self):
        return self.name
    
    def createForm():
        return AddClient()
    
    def retrieveForm(form):
        return AddClient(form)   
    
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
    
    def createForm():
        return AddStudent()
    
    def retrieveForm(form):
        return AddStudent(form)

class Member(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True)

class Etude(models.Model):
    description = models.CharField(max_length=200)
    begin = models.DateField()
    end = models.DateField()
    responsable = models.ForeignKey(Member, on_delete=models.CASCADE, default = 1)
    students = models.ManyToManyField(Student, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    je = models.ForeignKey(JE, on_delete=models.CASCADE, default = 1)
    
    def __str__(self):
        return self.description
    
    def save(self, *args, **kwargs):
        # Your custom validation logic here before saving
        # For example, you can check if the value matches the regex pattern
        if self.begin > self.end:
            raise ValueError('Begin must be set before end.')

        super().save(*args, **kwargs)
    
    def createForm():
        return AddEtude()
    
    def retrieveForm(form):
        return AddEtude(form)
    

    
class User(models.Model):
    je = models.ForeignKey(JE, on_delete=models.CASCADE, default = 1)
    username = models.CharField(max_length = 200)
    password = models.CharField(max_length=100)
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    def __str__(self):
        return self.student.__str__()
    
    def createForm():
        return AddUser()
    
    def retrieveForm(form):
        return AddUser(form)
    
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
        'password': forms.PasswordInput(),
    }

class AddUser(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
    
class AddStudent(forms.ModelForm):
    class Meta:
        model = Student
        fields='__all__'
    def __str__(self):
        return "Ajouter un étudiant"
    def name(self):
        return "AddStudent"
    
class AddEtude(forms.ModelForm):
    error_message = ""
    class Meta:
        model = Etude
        fields='__all__'
    def __str__(self):
        return "Ajouter une étude"
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
        return "Ajouter un client"
    def name(self):
        return "AddClient"
    



    

