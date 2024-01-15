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


def connexion(request):
    try:
        fetchform = UserForm(request.POST)
        if fetchform.is_valid():
            selected_user = User.objects.get(username=fetchform.cleaned_data["username"])
            if(fetchform.cleaned_data["password"]!=selected_user.password):
                raise User.DoesNotExist
        else:
            raise KeyError
    except (KeyError, User.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/index.html",
            {
                "error_message": "Incorrect username or password.",
                "form":fetchform
            },
        )
    else:
        request.session["member_id"] = selected_user.id
        request.session['user_authenticated'] = True
        template = loader.get_template("polls/results.html")
        return HttpResponse(template.render({}, request))
    
def logout(request):
    try:
        del request.session["member_id"]
    except KeyError:
        pass
    return HttpResponse("You're logged out.")
    
def results(request):
    if 'user_authenticated' in request.session:
        user = User.objects.get(id=request.session["member_id"])
        context = {"user":user}
        template = loader.get_template("polls/results.html")
    else:
        template = loader.get_template("polls/index.html")
        context = {'form':UserForm()}
    return HttpResponse(template.render(context, request))

def students(request):
    if 'user_authenticated' in request.session:
        template = loader.get_template("polls/students.html")
        student_list = Student.objects.all()
        context = {"student_list":student_list}
    else:
        template = loader.get_template("polls/index.html")
        context = {'form':UserForm()}
    return HttpResponse(template.render(context, request))

def etudes(request):
    if 'user_authenticated' in request.session:
        template = loader.get_template("polls/etudes.html")
        etudes_list = Etude.objects.all()
        context = {"etudes_list":etudes_list}
    else:
        template = loader.get_template("polls/index.html")
        context = {'form':UserForm()}   
    return HttpResponse(template.render(context, request))

def clients(request):
    if 'user_authenticated' in request.session:
        template = loader.get_template("polls/clients.html")
        client_list = Client.objects.all()
        context = {"client_list":client_list}
    else:
        template = loader.get_template("polls/index.html")
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


def annuaire(request):
    etudiants = Student.objects.all()  
    context = {'etudiants': etudiants}
    return render(request, 'annuaire.html', context)

