from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.urls import reverse
from django.apps import apps
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import Sum
from datetime import datetime

from .models import (
    JE,
    Member,
    Student,
    Etude,
    Client,
    AddStudent,
    AddClient,
    AddEtude,
    AddMember,
    Message,
    AddMessage,
)


def index(request):
    if request.user.is_authenticated:
        liste_messages = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).order_by("date")[0:3]
        message_count = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).count()
        user_je = request.user.je
        chiffres_affaires = request.user.chiffres_affaires()
        monthly_sums = calculate_monthly_sums(user_je)
        template = loader.get_template("polls/index.html")
        context = {
            "monthly_sums": monthly_sums,
            "liste_messages": liste_messages,
            "message_count": message_count,
            "chiffre_affaires": chiffres_affaires,
        }
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def custom_login(request):
    error_message = ""
    if request.method == "POST":
        user = authenticate(
            request, email=request.POST["email"], password=request.POST["password"]
        )
        if user:
            login(request, user)
            template = loader.get_template("polls/index.html")
            liste_messages = Message.objects.filter(
                destinataire=request.user,
                read=False,
                date__range=(
                    timezone.now() - timezone.timedelta(days=20),
                    timezone.now(),
                ),
            ).order_by("date")[0:3]
            message_count = Message.objects.filter(
                destinataire=request.user,
                read=False,
                date__range=(
                    timezone.now() - timezone.timedelta(days=20),
                    timezone.now(),
                ),
            ).count()
            return HttpResponse(
                template.render(
                    {"liste_messages": liste_messages, "message_count": message_count},
                    request,
                )
            )
        else:
            error_message = "Nom d'utilisateur ou mot de passe incorrect."
            context = {"error_message": error_message}
            template = loader.get_template("polls/login.html")
            return HttpResponse(template.render(context, request))

    template = loader.get_template("polls/login.html")
    context = {}
    return HttpResponse(template.render(context, request))


def custom_logout(request):
    logout(request)
    template = loader.get_template("polls/login.html")
    context = {}
    return HttpResponse(template.render(context, request))


def students(request):
    if request.user.is_authenticated:
        template = loader.get_template("polls/students.html")
        student_list = Student.objects.all()
        context = {"student_list": student_list}
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def annuaire(request):
    if request.user.is_authenticated:
        liste_messages = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).order_by("date")[0:3]
        message_count = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).count()
        template = loader.get_template("polls/annuaire.html")
        client_list = Client.objects.filter(je=request.user.je)
        etude_list = Etude.objects.filter(je=request.user.je)
        student_list = Student.objects.filter(je=request.user.je)

        context = {
            "client_list": client_list,
            "student_list": student_list,
            "etude_list": etude_list,
            "liste_messages": liste_messages,
            "message_count": message_count,
        }
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def details(request, modelName, iD):
    if request.user.is_authenticated:
        liste_messages = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).order_by("date")[0:3]
        message_count = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).count()
        template = loader.get_template("polls/page_details.html")
        model = apps.get_model(app_label="polls", model_name=modelName)
        try:
            instance = model.objects.get(id=iD, je=request.user.je)
            if modelName == "Message":
                instance.read = True
                instance.save()
            context = {
                "attribute_list": instance.get_display_dict(),
                "title": instance.get_title_details(),
                "is_etude": (modelName == "Etude"),
                "is_message": (modelName == "Message"),
                "modelName": modelName,
                "iD": iD,
                "liste_messages": liste_messages,
                "message_count": message_count,
            }
            template = loader.get_template("polls/page_details.html")
        except:
            context = {
                "error_message": "The selected object does not exist in the database.",
                "liste_messages": liste_messages,
                "message_count": message_count,
            }
            template = loader.get_template("polls/page_error.html")
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def input(request, modelName, iD):
    if request.user.is_authenticated:
        liste_messages = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).order_by("date")[0:3]
        message_count = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).count()
        template = loader.get_template("polls/page_input.html")
        if request.method == "GET":
            model = apps.get_model(app_label="polls", model_name=modelName)
            if iD == 0:
                form = model.createForm(je=request.user.je)
                context = {
                    "form": form,
                    "title": str(form),
                    "message": "",
                    "modelName": modelName,
                    "iD": iD,
                    "liste_messages": liste_messages,
                    "message_count": message_count,
                }
            else:
                try:
                    instance = model.objects.get(id=iD, je=request.user.je)
                    form = model.modifyForm(instance)
                    context = {
                        "form": form,
                        "title": str(form),
                        "message": "",
                        "modelName": modelName,
                        "iD": iD,
                        "liste_messages": liste_messages,
                        "message_count": message_count,
                    }
                except:
                    context = {
                        "error_message": "The selected object does not exist in the database.",
                        "liste_messages": liste_messages,
                        "message_count": message_count,
                    }
                    template = loader.get_template("polls/page_error.html")
        else:
            model = apps.get_model(app_label="polls", model_name=modelName)
            fetchform = model.retrieveForm(request.POST)
            if fetchform.is_valid():
                fetchform.save(commit=True, expediteur=request.user)
                context = {
                    "form": fetchform,
                    "title": str(fetchform),
                    "message": "Le formulaire a été envoyé avec succès",
                    "modelName": modelName,
                    "iD": iD,
                    "liste_messages": liste_messages,
                    "message_count": message_count,
                }
            else:
                context = {
                    "form": fetchform,
                    "title": str(fetchform),
                    "message": "Entree invalide",
                    "modelName": modelName,
                    "iD": iD,
                    "liste_messages": liste_messages,
                    "message_count": message_count,
                }
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def facture(request, iD):
    if request.user.is_authenticated:
        try:
            instance = Etude.objects.get(id=iD)

            client = instance.client
            context = {"etude": instance, "client": client}
            template = loader.get_template("polls/facpdf.html")
        except:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": "Erreur dans l'identification de la mission."}
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def messages(request):
    if request.user.is_authenticated:
        liste_messages = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).order_by("date")[0:3]
        message_count = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).count()
        message_list = Message.objects.filter(destinataire=request.user).order_by(
            "date"
        )
        template = loader.get_template("polls/page_messages.html")

        context = {
            "message_list": message_list,
            "liste_messages": liste_messages,
            "message_count": message_count,
        }
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def register(request):
    if request.method == "GET":
        form = AddMember()
        context = {"form": form}
        template = loader.get_template("polls/register.html")
    else:
        fetchform = AddMember(request.POST)
        if fetchform.is_valid():
            new_member = fetchform.save()
            login(request, new_member)
            liste_messages = Message.objects.filter(
                destinataire=request.user,
                read=False,
                date__range=(
                    timezone.now() - timezone.timedelta(days=20),
                    timezone.now(),
                ),
            ).order_by("date")[0:3]
            message_count = Message.objects.filter(
                destinataire=request.user,
                read=False,
                date__range=(
                    timezone.now() - timezone.timedelta(days=20),
                    timezone.now(),
                ),
            ).count()
            context = {"liste_messages": liste_messages, "message_count": message_count}
            template = loader.get_template("polls/index.html")
        else:
            context = {"form": fetchform}
            template = loader.get_template("polls/register.html")
    return HttpResponse(template.render(context, request))


def convention_etude(request, iD):
    if request.user.is_authenticated:
        try:
            instance = Etude.objects.get(id=iD)

            client = instance.client
            context = {"etude": instance, "client": client}
            template = loader.get_template("polls/ce.html")
        except:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": "Erreur dans l'identification de la mission."}
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def calculate_monthly_sums(user_je):
    september = 9
    monthly_sums = []
    month_ca = 0
    res = []

    for month in range(12):
        current_month = (month + september) % 12
        month_sum = (
            Etude.objects.filter(je=user_je, begin__month=current_month).aggregate(
                Sum("montant_HT")
            )["montant_HT__sum"]
            or 0.0
        )
        monthly_sums.append(month_sum)

    for k in range(12):
        month_ca += monthly_sums[k]
        res.append(month_ca)

    return res


def charts(request):
    if request.user.is_authenticated:
        user_je = request.user.je
        monthly_sums = calculate_monthly_sums(user_je)

        template = loader.get_template("polls/charts.html")
        context = {
            "monthly_sums": monthly_sums,
            "liste_messages": Message.objects.filter(
                destinataire=request.user,
                read=False,
                date__range=(
                    timezone.now() - timezone.timedelta(days=20),
                    timezone.now(),
                ),
            ).order_by("date")[0:3],
            "message_count": Message.objects.filter(
                destinataire=request.user,
                read=False,
                date__range=(
                    timezone.now() - timezone.timedelta(days=20),
                    timezone.now(),
                ),
            ).count(),
            "chiffre_affaires": request.user.chiffres_affaires(),
        }

        return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))