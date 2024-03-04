import json
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.urls import reverse
from django.apps import apps
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import datetime
from django.http import JsonResponse

from .models import (
    JE,
    Phase,
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
    AssignationJEH,
    Phase
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
            return redirect('index')
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


def je_detail(request):
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
        template = loader.get_template("polls/je_detail.html")
        je = request.user.je
        context = {
            'je': je,
        }
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def blank_page(request):
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
        template = loader.get_template("polls/blank_page.html")
        context = {
        }
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def page_detail_etude(request):
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

        context ={"attribute_list": Etude.objects.filter(iD=1).get_display_dict(),
                "title": 'nptq',
                "iD": 1,
                "liste_messages": liste_messages,
                "message_count": message_count,}

        template = loader.get_template("polls/page_detail_etude.html")
        context = {
        }
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def organigramme(request):
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
        template = loader.get_template("polls/blank.html")
        context = {
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

        model = apps.get_model(app_label="polls", model_name=modelName)
        try:
            instance = model.objects.get(id=iD, je=request.user.je)
            if modelName == "Message":
                instance.read = True
                instance.save()
                
            phases = None
            etude = None  # Initialisez `etude` à None par défaut
            client = None
            eleve = None
            if modelName == "Etude":
                phases = Phase.objects.filter(etude=instance)
                etude = instance
            if modelName == "Student":
                eleve = instance
            if modelName == "Client":
                client = instance

            context = {
                "attribute_list": instance.get_display_dict(),
                "title": instance.get_title_details(),
                "modelName": modelName,
                "iD": iD,
                "liste_messages": liste_messages,
                "message_count": message_count,
            }
            
            # Ajoutez `l'instance` au contexte seulement si elle est définie
            if etude is not None:
                context["etude"] = etude
                context["phases"] = phases
            if client is not None:
                context["client"] = client
            if eleve is not None:
                context["eleve"] = eleve

            template = loader.get_template("polls/page_details.html")
        except model.DoesNotExist:
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
                    "is_message": (modelName == "Message"),
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
                        "is_message": (modelName == "Message"),
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

def stat_KPI(request):
    if request.user.is_authenticated:
        try:
            
            template = loader.get_template("polls/stat_KPI.html")
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
    
def search_suggestions(request):
    query = request.GET.get('query', '')
    if query:
        keywords = query.split()
        suggestions_etude = Etude.objects.filter(je=request.user.je)
        suggestions_client = Client.objects.filter(je=request.user.je)
        suggestions_student = Student.objects.filter(je=request.user.je)
        for keyword in keywords:
            suggestions_etude = suggestions_etude.filter(Q(titre__icontains=keyword) | Q(numero__icontains=keyword) | Q(responsable__student__first_name__icontains=keyword) | Q(responsable__student__last_name__icontains=keyword) | Q(client__nom_societe__icontains=keyword))
            suggestions_client = suggestions_client.filter(Q(nom_societe__icontains=keyword) | Q(nom_representant__icontains=keyword))
            suggestions_student = suggestions_student.filter(Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword))
        count_client = suggestions_client.count()
        count_student = suggestions_student.count()
        suppression_etude_c=max(1, count_client)
        suppression_etude_s=max(1, count_student)
        suggestions_etude=suggestions_etude.order_by('-begin')[:5-suppression_etude_c-suppression_etude_s]
        nombre_etude = suggestions_etude.count()
        suggestions_client = suggestions_client[:5-nombre_etude-suppression_etude_s]
        nombre_client = suggestions_client.count()
        suggestions_student = suggestions_student[:5-nombre_etude-nombre_client]
        return JsonResponse({'suggestions_etude': list(suggestions_etude.values_list('titre', 'id')), 'suggestions_client': list(suggestions_client.values_list('nom_societe', 'id')), 'suggestions_student': list(suggestions_student.values_list('first_name', 'last_name', 'id'))})
    else :
        return JsonResponse({'suggestions_etude': [], 'suggestions_client': [], 'suggestions_student': []})


def search(request):
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
    query = request.GET.get('search-input', '')
    if query:
        keywords = query.split()
        resultats_etude = Etude.objects.filter(je=request.user.je)
        resultats_client = Client.objects.filter(je=request.user.je)
        resultats_student = Student.objects.filter(je=request.user.je)
        liste_res_etude = []
        liste_res_client = []
        liste_res_student = []
        combined_res_etude = Etude.objects.none()
        combined_res_client = Client.objects.none()
        combined_res_student = Student.objects.none()
        for keyword in keywords:
            liste_res_etude.append(resultats_etude.filter(Q(titre__icontains=keyword) | Q(numero__icontains=keyword) | Q(responsable__student__first_name__icontains=keyword) | Q(responsable__student__last_name__icontains=keyword) | Q(client__nom_societe__icontains=keyword)))
            liste_res_client.append(resultats_client.filter(Q(nom_societe__icontains=keyword) | Q(nom_representant__icontains=keyword)))
            liste_res_student.append(resultats_student.filter(Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword)))
        for i in range(len(liste_res_etude)):
            combined_res_etude |= liste_res_etude[i]
            combined_res_client |= liste_res_client[i]
            combined_res_student |= liste_res_student[i]
        combined_res_etude = combined_res_etude.annotate(appearances_count=Count('id', distinct=True)).order_by('-appearances_count')
        combined_res_client = combined_res_client.annotate(appearances_count=Count('id', distinct=True)).order_by('-appearances_count')
        combined_res_student = combined_res_student.annotate(appearances_count=Count('id', distinct=True)).order_by('-appearances_count')
        final_res_etude = combined_res_etude.all()
        final_res_client = combined_res_client.all()
        final_res_student = combined_res_student.all()
        context = {"query":query, "res_etude":final_res_etude, "res_client":final_res_client, "res_student":final_res_student, "liste_messages":liste_messages, "message_count":message_count}
        template = loader.get_template("polls/search_results.html")
        return HttpResponse(template.render(context, request))
    else:
        context = {"query":query, "liste_messages":liste_messages, "message_count":message_count}
        template = loader.get_template("polls/search_results.html")
        return HttpResponse(template.render(context, request))