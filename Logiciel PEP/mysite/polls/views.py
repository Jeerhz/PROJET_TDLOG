from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.template import loader
from django.urls import reverse
from django.apps import apps

from .models import JE, User, Student, Etude, Client, AddStudent, AddClient, AddEtude, UserForm


def index(request):
    template = loader.get_template("polls/index.html")
    context = {'form':UserForm()}
    return HttpResponse(template.render(context, request))


def login(request):
    error_message = ""
    if request.method == 'POST':
        fetchform = UserForm(request.POST)
        if fetchform.is_valid():
            selected_user = User.objects.filter(username=fetchform.cleaned_data["username"])
            if selected_user.exists() and (fetchform.cleaned_data["password"]==selected_user.password):
                request.session["member_id"] = selected_user.id
                request.session['user_authenticated'] = True
                template = loader.get_template("polls/index.html")
                return HttpResponse(template.render({}, request))
            else:
                error_message = "Nom d'utilisateur ou mot de passe incorrect."
                context = {"error_message":error_message, 'form':fetchform}
                template = loader.get_template("polls/login.html")
                return HttpResponse(template.render(context, request))
        else :
            error_message = "Le format des données est invalide."
            context = {"error_message":error_message, 'form':UserForm()}
            template = loader.get_template("polls/login.html")
            return HttpResponse(template.render(context, request))

    template = loader.get_template("polls/login.html")
    context = {'form':UserForm()}
    return HttpResponse(template.render(context, request))
    
def logout(request):
    try:
        del request.session["member_id"]
    except KeyError:
        pass
    return HttpResponse("You're logged out.")

def students(request):
    #if 'user_authenticated' in request.session:
    template = loader.get_template("polls/students.html")
    student_list = Student.objects.all()
    context = {"student_list":student_list}
    #else:
    #    template = loader.get_template("polls/index.html")
    #    context = {'form':UserForm()}
    return HttpResponse(template.render(context, request))

def annuaire(request):
    #if 'user_authenticated' in request.session:
    template = loader.get_template("polls/annuaire.html")
    client_list = Client.objects.all()
    etude_list = Etude.objects.all()
    student_list = Student.objects.all()
    
    context = {"client_list":client_list, "student_list":student_list, "etude_list":etude_list}
    #else:
    #    template = loader.get_template("polls/index.html")
    #    context = {'form':UserForm()}
    return HttpResponse(template.render(context, request))

def details(request, modelName, iD):
    if 'user_authenticated' in request.session:
        template = loader.get_template("polls/page_details.html")
        model = apps.get_model(app_label="polls", model_name=modelName)
        try :
            instance = model.objects.get(id=iD)
            context = {'attribute_list': instance.get_display_dict(), 'title':"Détails de la mission"}
            template = loader.get_template("polls/page_details.html")
        except:
            context = {'error_message': "The selected object does not exist in the database."}
            template = loader.get_template("polls/page_error.html")
    else:
        template = loader.get_template("polls/login.html")
        context = {'form':UserForm()} 
    return HttpResponse(template.render(context, request))

def input(request, modelName):
    if 'user_authenticated' in request.session:
        template = loader.get_template("polls/input.html")
        if(request.method=="GET"):
            model = apps.get_model(app_label="polls", model_name=modelName)
            form = model.createForm()
            context = {'form':form, 'model_name':modelName, 'title':str(form), 'message':""}
        else:
            model = apps.get_model(app_label="polls", model_name=modelName)
            fetchform = model.retrieveForm(request.POST)
            if(fetchform.is_valid()):
                fetchform.save(commit=True)
                context = {'form':fetchform, 'model_name': modelName, 'title':str(fetchform), 'message':"Le formulaire a été envoyé avec succès"}
            else:
                context = {'form':fetchform, 'model_name': modelName, 'title':str(fetchform), 'message':"Entree invalide"}
    else:
        template = loader.get_template("polls/index.html")
        context = {'form':UserForm()} 
    return HttpResponse(template.render(context, request))

