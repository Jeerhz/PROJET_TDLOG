from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.template import loader
from django.urls import reverse
from django.apps import apps
from django.contrib.auth import authenticate, login, logout

from .models import JE, Member, Student, Etude, Client, AddStudent, AddClient, AddEtude, AddMember


def index(request):
    if request.user.is_authenticated :
        template = loader.get_template("polls/index.html")
        context = {}
    else :
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def custom_login(request):
    error_message = ""
    if request.method == 'POST':
        user = authenticate(request, email=request.POST['email'], password=request.POST['password'])
        if user :
            login(request, user)
            template = loader.get_template("polls/index.html")
            return HttpResponse(template.render({}, request))
        else:
            error_message = "Nom d'utilisateur ou mot de passe incorrect."
            context = {"error_message":error_message}
            template = loader.get_template("polls/login.html")
            return HttpResponse(template.render(context, request))

    template = loader.get_template("polls/login.html")
    context = {}
    return HttpResponse(template.render(context, request))
    
def custom_logout(request):
    logout(request)
    return HttpResponse("You're logged out.")

def students(request):
    if request.user.is_authenticated:
        template = loader.get_template("polls/students.html")
        student_list = Student.objects.all()
        context = {"student_list":student_list}
    else :
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))

def annuaire(request):
    if request.user.is_authenticated:
        template = loader.get_template("polls/annuaire.html")
        client_list = Client.objects.all()
        etude_list = Etude.objects.all()
        student_list = Student.objects.all()
    
        context = {"client_list":client_list, "student_list":student_list, "etude_list":etude_list}
    else :
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))

def details(request, modelName, iD):
    if request.user.is_authenticated:
        template = loader.get_template("polls/page_details.html")
        model = apps.get_model(app_label="polls", model_name=modelName)
        try :
            instance = model.objects.get(id=iD)
            context = {'attribute_list': instance.get_display_dict(), 'title':instance.get_title_details(), 'is_etude':(modelName=="Etude"), 'modelName':modelName, 'iD':iD}
            template = loader.get_template("polls/page_details.html")
        except:
            context = {'error_message': "The selected object does not exist in the database."}
            template = loader.get_template("polls/page_error.html")
    else :
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))

def input(request, modelName, iD):
    if request.user.is_authenticated:
        template = loader.get_template("polls/page_input.html")
        if(request.method=="GET"):
            model = apps.get_model(app_label="polls", model_name=modelName)
            if(iD==0):
                form = model.createForm()
                context = {'form':form, 'model_name':modelName, 'title':str(form), 'message':"", 'modelName':modelName, 'iD':iD}
            else:
                try:
                    instance = model.objects.get(id=iD)
                    form = model.modifyForm(instance)
                    context = {'form':form, 'model_name':modelName, 'title':str(form), 'message':"", 'modelName':modelName, 'iD':iD}
                except:
                    context = {'error_message': "The selected object does not exist in the database."}
                    template = loader.get_template("polls/page_error.html")
        else:
            model = apps.get_model(app_label="polls", model_name=modelName)
            fetchform = model.retrieveForm(request.POST)
            if(fetchform.is_valid()):
                fetchform.save(commit=True)
                context = {'form':fetchform, 'model_name': modelName, 'title':str(fetchform), 'message':"Le formulaire a été envoyé avec succès", 'modelName':modelName, 'iD':iD}
            else:
                context = {'form':fetchform, 'model_name': modelName, 'title':str(fetchform), 'message':"Entree invalide", 'modelName':modelName, 'iD':iD}
    else :
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))

def facture(request, iD):
    if request.user.is_authenticated:
        try:
            instance = Etude.objects.get(id=iD)

            client = instance.client
            context = {'etude':instance, 'client':client}
            template = loader.get_template("polls/bdc.html")
        except:
            template = loader.get_template("polls/page_error.html")
            context = {'error_message':"Erreur dans l'identification de la mission."}
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))

