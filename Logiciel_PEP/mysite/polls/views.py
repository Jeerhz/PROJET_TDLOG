import json
import os
import openpyxl
import pytz #pour CA dynamique
from docxtpl import DocxTemplate
from docx.shared import Inches
from jinja2 import Environment
import math


import logging #pour gérer plus facilement les erreurs
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

from io import BytesIO
from uuid import UUID
from openpyxl import load_workbook
from django.shortcuts import redirect, get_object_or_404
from django.core.mail import send_mail, get_connection
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.template import loader
from django.urls import reverse
from django.apps import apps
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta, date, time
from django.views.decorators.csrf import csrf_exempt
import locale
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
from django.http import JsonResponse, FileResponse
from django.conf import settings as conf_settings
from django.core.files.base import ContentFile
from .templatetags.format_duration import format_nombres, chiffre_lettres,en_lettres, assignation
from django.shortcuts import render
from django.template.loader import render_to_string

#from weasyprint import HTML
#from wand.image import Image

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
    Phase,
    AddPhase,
    AddIntervenant,
    Recrutement,
    Facture,
    AddFacture,
    ConventionEtude,
    ConventionCadre,
    Devis,
    SetParametresUtilisateur,
    ParametresUtilisateur,
    AvenantRuptureConventionEtude,
    BonCommande,
    Representant,
    AddRepresentant,
    Candidature,
    RDM,
    Notification,
    AvenantConventionEtude,
    SuppressionPhase,
    ModificationDebutPhase,
    ModificationDureePhase,
    ModificationJEHPhase,
    PV,
    AjouterRemarqueRepresentant,
)

def my_view(request):
    return render(request, 'polls/facpdf.html')

def generate_pdf(request):
    html_content = render_to_string('polls/facpdf.html')
    pdf_file = HTML(string=html_content).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="page.pdf"'
    return response


def index(request):
    if request.user.is_authenticated:
        liste_messages = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).order_by("date")
        message_count = liste_messages.count()
        liste_messages = liste_messages[:3]
        all_notifications = request.user.notifications.order_by("-date_effet")
        notification_list = [notif for notif in all_notifications if notif.active()]
        notification_count = len(notification_list)
        
        user_je = request.user.je
        monthly_sums = calculate_monthly_sums(user_je)
        chiffre_affaire = monthly_sums[-1]
        etudes_recentes = Etude.objects.filter(je=user_je).order_by('-debut')[:5]
        nombre_mission_terminee = Etude.objects.filter(je=user_je, status='TERMINEE').count()
        nombre_mission_en_cours = Etude.objects.filter(je=user_je, status='EN_COURS').count()
        etudes_en_discussion = Etude.objects.filter(je=user_je, status='EN_NEGOCIATION')
        nombre_mission_en_negociation = etudes_en_discussion.count()
        etudes_en_discussion = etudes_en_discussion.order_by('-debut')[:5]
        template = loader.get_template("polls/index.html")
        context = {
            "nombre_mission_en_cours": nombre_mission_en_cours,
            "nombre_mission_terminee": nombre_mission_terminee,
            "nombre_mission_en_negociation": nombre_mission_en_negociation,
            "monthly_sums": monthly_sums,
            "liste_messages": liste_messages,
            "message_count": message_count,
            "notification_list":notification_list,
            "notification_count":notification_count,
            "chiffre_affaire": chiffre_affaire,
            "etudes_recentes":etudes_recentes,
            "etudes_en_discussion":etudes_en_discussion,
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


def annuaire(request):
    if request.user.is_authenticated:
        liste_messages = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).order_by("date")
        message_count = liste_messages.count()
        liste_messages = liste_messages[:3]
        all_notifications = request.user.notifications.order_by("-date_effet")
        notification_list = [notif for notif in all_notifications if notif.active()]
        notification_count = len(notification_list)
        
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
            "notification_list":notification_list,
            "notification_count":notification_count,
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
        ).order_by("date")
        message_count = liste_messages.count()
        liste_messages = liste_messages[:3]
        all_notifications = request.user.notifications.order_by("-date_effet")
        notification_list = [notif for notif in all_notifications if notif.active()]
        notification_count = len(notification_list)
        

        context = {
            "liste_messages": liste_messages,
            "message_count": message_count,
            "notification_list":notification_list,
            "notification_count":notification_count,
            "je":request.user.je
        }
        template = loader.get_template("polls/je_detail.html")
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))

def demarchage(request):
    if request.user.is_authenticated:
        liste_messages = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).order_by("date")
        message_count = liste_messages.count()
        liste_messages = liste_messages[:3]
        all_notifications = request.user.notifications.order_by("-date_effet")
        notification_list = [notif for notif in all_notifications if notif.active()]
        notification_count = len(notification_list)
        

        template = loader.get_template("polls/demarchage.html")
        je = request.user.je
        representants= Representant.objects.filter(client__je=je)
        clients = Client.objects.filter(je=je)
        secteurs =[ 'INDUSTRIE','DISTRIBUTION', 'SECTEUR_PUBLIC', 'CONSEIL',  'TRANSPORT',  'NUMERIQUE', 'BTP','AUTRE']
        context = {
            "liste_messages": liste_messages,
            "message_count": message_count,
            "notification_list":notification_list,
            "notification_count":notification_count,
            'representants': representants,
            'clients':clients,
            'secteurs':secteurs,
        }
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))

def supprimer_demarchage(request, id_representant):
    representant = Representant.objects.filter(id=id_representant).first()

    if request.method == 'POST':
        representant.demarchage = 'A_CONTACTER'
        
        nouvelle_remarque = request.POST.get('remarque', '')
        representant.remarque = nouvelle_remarque
        representant.save()
        return redirect('demarchage')  
    
    return redirect('demarchage')  

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





def details(request, modelName, iD):
    if request.user.is_authenticated:
        liste_messages = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).order_by("date")
        message_count = liste_messages.count()
        liste_messages = liste_messages[:3]
        all_notifications = request.user.notifications.order_by("-date_effet")
        notification_list = [notif for notif in all_notifications if notif.active()]
        notification_count = len(notification_list)

        model = apps.get_model(app_label="polls", model_name=modelName)
        try:
            instance = model.objects.get(id=iD)
            if modelName == "Message":
                instance.read = True
                instance.save()
                
            phases = None
            factures = None
            etude = None  # Initialisez `etude` à None par défaut
            intervenants = None
            client = None
            eleve = None
            if modelName == "Etude":
                etude = instance
                phases = Phase.objects.filter(etude=instance).order_by('date_debut')
                factures=Facture.objects.filter(etude=instance).order_by('numero_facture')
                intervenants = etude.get_li_students()
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
                "notification_list":notification_list,
                "notification_count":notification_count,
            }
            
            # Ajoutez `l'instance` au contexte seulement si elle est définie
            if etude is not None:
                context["etude"] = etude
                context["phases"] = phases
                context["factures"] = factures
                context["intervenants"] = intervenants
                context["phase_form"] = AddPhase()
                context["facture_form"] = AddFacture()
                context["intervenant_form"] = AddIntervenant()

            if client is not None:
                context["client"] = client
                context["representant_form"]= AddRepresentant()
            if eleve is not None:
                context["eleve"] = eleve

            template = loader.get_template("polls/page_details.html")
        except model.DoesNotExist:
            context = {
                "error_message": "The selected object does not exist in the database.",
                "liste_messages": liste_messages,
                "message_count": message_count,
                "notification_list":notification_list,
                "notification_count":notification_count,
            }
            template = loader.get_template("polls/page_error.html")
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))



def edit_student(request, pk):
    if request.user.is_authenticated:
        # Fetch messages and notifications
        liste_messages = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).order_by("date")[:3]
        message_count = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).count()
        all_notifications = request.user.notifications.order_by("-date_effet")
        notification_list = [notif for notif in all_notifications if notif.active()]

        # Retrieve the student instance, or return a 404 if not found
        student = get_object_or_404(Student, pk=pk)


        if request.method == 'POST':
            form = AddStudent(request.POST, instance=student)
            if form.is_valid():
                form.save()  # Save changes to the database
                return redirect('details', modelName="Student", iD=student.id)
            else:
                # Debugging: print out form errors if it is not valid
                print(form.errors)
        else:
            form = AddStudent(instance=student)


        context = {
            "eleve": student, 
            "form": form,
            "liste_messages": liste_messages,
            "message_count": message_count,
            "notification_list": notification_list,
            "notification_count": len(notification_list),
            "modelName": "Student",
            "iD": student.id,
        }

        return render(request, "polls/page_details.html", context)
    
    else:
        return redirect('login')
    
def edit_client(request, pk):
    if request.user.is_authenticated:
        # Fetch messages and notifications
        liste_messages = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).order_by("date")[:3]
        message_count = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).count()
        all_notifications = request.user.notifications.order_by("-date_effet")
        notification_list = [notif for notif in all_notifications if notif.active()]

        # Retrieve the client instance, or return a 404 if not found
        client = get_object_or_404(Client, pk=pk)


        if request.method == 'POST':
            form = AddClient(request.POST, instance=client)
            if form.is_valid():
                form.save()  # Save changes to the database
                return redirect('details', modelName="Client", iD=client.id)
            else:
                # Debugging: print out form errors if it is not valid
                print(form.errors)
        else:
            form = AddClient(instance=client)


        context = {
            "client": client,
            "representant_form" : AddRepresentant(),
            "form": form,
            "liste_messages": liste_messages,
            "message_count": message_count,
            "notification_list": notification_list,
            "notification_count": len(notification_list),
            "modelName": "Client",
            "iD": client.id,
        }

        return render(request, "polls/page_details.html", context)
    
    else:
        return redirect('login')

def delete_student(request, pk):
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
        student = get_object_or_404(Student, pk=pk)
        if request.method == 'POST':
            student.delete()
        return redirect('annuaire')
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def delete_client(request, pk):
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
        client = get_object_or_404(Student, pk=pk)
        if request.method == 'POST':
            client.delete()
        return redirect('annuaire')
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
        model = apps.get_model(app_label="polls", model_name=modelName)
        if request.method == "GET":
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
            fetchform = model.retrieveForm(request.POST)
            if fetchform.is_valid():
                if iD == 0:
                    fetchform.save(commit=True, expediteur=request.user)
                else:
                    fetchform.save(commit=True)
                context = {
                    "form": fetchform,
                    "title": str(fetchform),
                    "message": "Le formulaire a été envoyé avec succès",
                    "modelName": modelName,
                    "iD": iD,
                    "liste_messages": liste_messages,
                    "message_count": message_count,
                }
                return redirect('annuaire')
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


def facture(request, id_facture):
    if request.user.is_authenticated:
        try:
            facture = Facture.objects.get(id=id_facture)
            etude = facture.etude
            #etude = {'type_convention': etude.type_convention, }
            client = etude.client
            phases = Phase.objects.filter(etude=etude).order_by('numero')
            res = facture.montant_TTC()
            facture.date_emission = timezone.now().strftime('%d/%m/%Y')
            date_30 = timezone.now() + timedelta(30)
            facture.date_echeance = date_30.strftime('%d/%m/%Y')
            context = {
                "facture": facture,
                "etude": etude,
                "client": client,
                "phases": phases,
                "res": res,
                "date_emission": facture.date_emission,
                "date_echeance": facture.date_echeance
            }
            template = loader.get_template("polls/facpdf.html")

        except Exception as e:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": "Erreur dans l'identification de la facture."}
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def update_facture(request,iD):
    if request.method == 'POST':
        facture_id = request.POST.get('facture_id')
        try:
            instance = Etude.objects.get(id=iD)
            facture = Facture.objects.get(id=facture_id)
            facture.facturé = True
            client = instance.client
            facture.save()
            context = {"etude": instance, "client": client}
            template = loader.get_template("polls/facpdf.html")
        except Facture.DoesNotExist:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": "facture n'existe pas."}
    return HttpResponse(template.render(context, request))

def ndf(request):
    if request.user.is_authenticated:
        try:
            
            template = loader.get_template("polls/ndf.html")
            context={}
        except:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": "Erreur dans l'identification de la mission."}
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))

def ba(request, iD):
    if request.user.is_authenticated:
        try:
            eleve= Student.objects.get(id=iD)
            template = loader.get_template("polls/ba.html")
            context={"eleve":eleve}
        except:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": "Erreur dans l'identification de la mission."}
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))



def stat_KPI(request):
    if request.user.is_authenticated:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date and end_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
        else:
            now = timezone.now()
            end_date_obj = now.date()
            start_date_obj = (now - timedelta(days=1000)).date()
            start_date = start_date_obj.strftime('%Y-%m-%d')
            end_date = end_date_obj.strftime('%Y-%m-%d')

        # Filtrer les études en fonction des dates
        etudes = Etude.objects.filter(debut__gte=start_date_obj, debut__lte=end_date_obj).order_by('debut')
        print(f"Initial Etudes count: {etudes.count()}")  # Debug print

        # Calculer les montants par mois et les labels
        date_labels = []
        cumulated_CA = []
        current_month = start_date_obj.month
        current_year = start_date_obj.year
        current_sum = 0
        total_sum = 0

        for etude in etudes:
            etude_month = etude.debut.month
            etude_year = etude.debut.year

            if etude_month == current_month and etude_year == current_year:
                current_sum += etude.montant_HT_total()
            else:
                # Ajouter les données pour le mois précédent
                date_labels.append(f"{current_year}-{current_month:02d}")
                total_sum += current_sum
                cumulated_CA.append(total_sum)

                # Réinitialiser pour le nouveau mois
                current_month = etude_month
                current_year = etude_year
                current_sum = etude.montant_HT_total()

        # Ajouter les données pour le dernier mois
        date_labels.append(f"{current_year}-{current_month:02d}")
        total_sum += current_sum
        cumulated_CA.append(total_sum)

        # Calcul des autres métriques
        liste_messages = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).order_by("date")
        message_count = liste_messages.count()
        liste_messages = liste_messages[:3]
        all_notifications = request.user.notifications.order_by("-date_effet")
        notification_list = [notif for notif in all_notifications if notif.active()]
        notification_count = len(notification_list)
        user_je = request.user.je
        chiffres_affaires = request.user.chiffres_affaires()
        chiffre_affaire_total = cumulated_CA[-1]
        chiffre_affaire_par_departement = calculate_chiffre_affaire_par_departement(user_je)
        chiffre_affaire_par_type = calculate_chiffre_affaire_par_type(user_je)
        chiffre_affaire_par_secteur = calculate_chiffre_affaire_par_secteur(user_je)
        nombre_eleve = Student.objects.filter(je=user_je).count()
        nombre_client = Client.objects.filter(je=user_je).count()
        nombre_etude = Etude.objects.filter(je=user_je).count()

        dictionnaire_CA_par_dept = {
            'IMI': chiffre_affaire_par_departement[0],
            'GCC': chiffre_affaire_par_departement[1],
            'GMM': chiffre_affaire_par_departement[2],
            'SEGF': chiffre_affaire_par_departement[3],
            'VET': chiffre_affaire_par_departement[4],
            '1A': chiffre_affaire_par_departement[5],
            'AUTRE': chiffre_affaire_par_departement[6],
        }

        dictionnaire_CA_par_secteur = {
            'INDUSTRIE': chiffre_affaire_par_secteur[0],
            'DISTRIBUTION': chiffre_affaire_par_secteur[1],
            'SECTEUR_PUBLIC': chiffre_affaire_par_secteur[2],
            'CONSEIL': chiffre_affaire_par_secteur[3],
            'TRANSPORT': chiffre_affaire_par_secteur[4],
            'NUMERIQUE': chiffre_affaire_par_secteur[5],
            'BTP': chiffre_affaire_par_secteur[6],
            'AUTRE': chiffre_affaire_par_secteur[7],
        }

        dictionnaire_CA_par_type = {
            'GRANDE_ENTREPRISE': chiffre_affaire_par_type[0],
            'SECTEUR_PUBLIC': chiffre_affaire_par_type[1],
            'START_UP_ET_TPE': chiffre_affaire_par_type[2],
            'PME': chiffre_affaire_par_type[3],
            'ETI': chiffre_affaire_par_type[4],
            'ASSOCIATION': chiffre_affaire_par_type[5],
        }
        
        # Définition des couleurs pour chaque département
        departements_colors = {
            'IMI': '#FF6633',
            'GCC': '#FFB399',
            'GMM': '#FF33FF',
            'SEGF': '#FFFF99',
            'VET': '#00B3E6',
            '1A': '#E6B333',
            'AUTRE': '#3366E6',
        }

        # Définition des couleurs pour chaque secteur
        secteurs_colors = {
            'INDUSTRIE': '#0071C5',
            'DISTRIBUTION': '#FFD700',
            'SECTEUR_PUBLIC': '#DC143C',
            'CONSEIL': '#008B8B',
            'TRANSPORT': '#B8860B',
            'NUMERIQUE': '#4682B4',
            'BTP': '#DAA520',
            'AUTRE': '#808080',
        }

        types_colors = {
            'GRANDE_ENTREPRISE': '#4A90E2',  # Bleu lumineux
            'SECTEUR_PUBLIC': '#D0021B',     # Rouge vif
            'START_UP_ET_TPE': '#7B8D8E',    # Gris ardoise
            'PME': '#F5A623',                # Orange safran
            'ETI': '#8B572A',                # Brun cuir
            'ASSOCIATION': '#50E3C2',        # Turquoise clair
        }

        pourcentage_par_departement = {dept: ca / (chiffre_affaire_total + 1e-12) * 100 for dept, ca in dictionnaire_CA_par_dept.items()}
        pourcentage_par_secteur = {sect: ca / (chiffre_affaire_total + 1e-12) * 100 for sect, ca in dictionnaire_CA_par_secteur.items()}
        pourcentage_par_type = {sect: ca / (chiffre_affaire_total + 1e-12) * 100 for sect, ca in dictionnaire_CA_par_type.items()}

        template = loader.get_template("polls/stat_KPI.html")
        context = {
            "nombre_eleve": nombre_eleve,
            "nombre_client": nombre_client,
            "nombre_etude": nombre_etude,
            "secteurs_colors": secteurs_colors,
            "pourcentage_par_secteur": pourcentage_par_secteur,
            "chiffre_affaire_par_secteur": chiffre_affaire_par_secteur,
            "departements_colors": departements_colors,
            "types_colors": types_colors,
            "pourcentage_par_type": pourcentage_par_type,
            "pourcentage_par_departement": pourcentage_par_departement,
            "chiffre_affaire_total": chiffre_affaire_total,
            "chiffre_affaire_par_departement": chiffre_affaire_par_departement,
            "chiffre_affaire_par_type": chiffre_affaire_par_type,
            "cumulated_CA": cumulated_CA,
            "date_labels": date_labels,
            "liste_messages": liste_messages,
            "message_count": message_count,
            "notification_list":notification_list,
            "notification_count":notification_count,
            "chiffre_affaires": chiffres_affaires,
            "start_date": start_date,
            "end_date": end_date
        }
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def fetch_data(request):
    if request.user.is_authenticated:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date and end_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').replace(tzinfo=pytz.UTC)
        else:
            return JsonResponse({'error': 'Invalid date range'}, status=400)

        # Filtrer les études en fonction des dates
        etudes = Etude.objects.filter(debut__gte=start_date_obj, debut__lte=end_date_obj).order_by('debut')
        print(f"Etudes count: {etudes.count()}")

        # Calculer les montants par mois et les labels
        date_labels = [start_date_obj.strftime('%Y-%m')]
        cumulated_CA = [0]
        current_sum = 0

        for etude in etudes:
            etude_month = etude.debut.month
            etude_year = etude.debut.year
            date_label = f"{etude_year}-{etude_month:02d}"

            if date_labels and date_labels[-1] == date_label:
                # Same month, add to current sum
                current_sum += etude.montant_HT_total()
            else:
                # New month, append previous month data and start new sum
                if date_labels:
                    cumulated_CA[-1] = current_sum  # Update previous month sum
                date_labels.append(date_label)
                current_sum += etude.montant_HT_total()
                cumulated_CA.append(current_sum)  # Initialize new month sum

        # Debug prints
        print(f"date_labels: {date_labels}")
        print(f"cumulated_CA: {cumulated_CA}")

        response_data = {
            'date_labels': date_labels,
            'cumulated_CA': cumulated_CA
        }

        # Ensure response_data is JSON serializable
        try:
            json_response = JsonResponse(response_data)
        except TypeError as e:
            print(f"Serialization error: {e}")
            return JsonResponse({'error': 'Serialization error'}, status=500)

        return json_response

    return JsonResponse({'error': 'Unauthorized'}, status=403)





def messages(request):
    if request.user.is_authenticated:
        liste_messages = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).order_by("date")
        message_count = liste_messages.count()
        all_notifications = request.user.notifications.order_by("-date_effet")
        notification_list = [notif for notif in all_notifications if notif.active()]
        notification_count = len(notification_list)
        

        context = {
            "liste_messages": liste_messages,
            "message_count": message_count,
            "notification_list":notification_list,
            "notification_count":notification_count,
        }
        template = loader.get_template("polls/page_messages.html")
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
                date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
            ).order_by("date")
            message_count = liste_messages.count()
            liste_messages = liste_messages[:3]
            all_notifications = request.user.notifications.order_by("-date_effet")
            notification_list = [notif for notif in all_notifications if notif.active()]
            notification_count = len(notification_list)
            context = {"liste_messages": liste_messages, "message_count": message_count, "notification_list":notification_list, "notification_count":notification_count}
            template = loader.get_template("polls/index.html")
        else:
            context = {"form": fetchform}
            template = loader.get_template("polls/register.html")
    return HttpResponse(template.render(context, request))

def editer_convention(request, iD):
    if request.user.is_authenticated:
        #try:
            instance = Etude.objects.get(id=iD)
            je= instance.je
            client = instance.client
            phases= Phase.objects.filter(etude=instance)
            if instance.type_convention == "Convention d'étude":
                model = ConventionEtude
                template = DocxTemplate("polls/templates/polls/Convention_Etude_026.docx")
            elif instance.type_convention == "Convention cadre":
                model = ConventionCadre
                template = DocxTemplate("polls/templates/polls/Convention_Etude_026.docx")
            else:
                raise ValueError("Type de convention non défini.")
            if instance.convention_edited() :
                ce = instance.convention()
            else :
                ce = model(etude=instance)
                ce.save()

            president = Member.objects.filter(je=je, poste='PRESIDENT').first().student
            duree = instance.duree_semaine()
            nb_phases = instance.nb_phases()
            respo = instance.responsable.student
            qualite = instance.resp_qualite.student
            ref_m = instance.ref()
            representant_client= instance.client_interlocuteur #le gars de la boite qui interagit avec la PEP
            representant_legale_client = instance.client_representant_legale #souvent le patron de l boite qui a le droit de signer les documents
            #souvent le client a un representant a qui on a affaie mais cest le representant legale (champs dans client) qui signe les papiers
            date = timezone.now()
            annee = date.strftime('%Y')





            context = {"etude": instance,"phases":phases,"nb_phases":nb_phases,"president":president, "duree":duree, "client": client, "repr":representant_client,"repr_legale":representant_legale_client, "je":je, "ce":ce, "respo":respo, "quali":qualite,"ref_m":ref_m,"annee":annee}
            # Load the template

            env = Environment()

            env.filters['FormatNombres'] = format_nombres

            

            template.render(context, env)
            output = BytesIO()
            template.save(output)
            output.seek(0)

            # Save the "fichier" field of the CE
            filename = f"Devis_{ref_m}.docx"
            response = FileResponse(output, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        
            
        #except ValueError as ve:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": str(ve)}
        #except :
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": "Un problème a été détecté dans la base de données."}

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))

def editer_pv(request, iD):
    if request.user.is_authenticated:
        #try:
            instance = Etude.objects.get(id=iD)
            je= instance.je
            client = instance.client
            model = PV
            pv = model(etude=instance)
            phases= Phase.objects.filter(etude=instance)
            template = DocxTemplate("polls/templates/polls/PVRI_026.docx")
            

            president = Member.objects.filter(je=je, poste='PRESIDENT').first().student
            duree = instance.duree_semaine()
            nb_phases = instance.nb_phases()
            respo = instance.responsable.student
            qualite = instance.resp_qualite.student
            ref_m = instance.ref()
            representant_client= instance.client_interlocuteur #le gars de la boite qui interagit avec la PEP
            representant_legale_client = instance.client_representant_legale #souvent le patron de l boite qui a le droit de signer les documents
            #souvent le client a un representant a qui on a affaie mais cest le representant legale (champs dans client) qui signe les papiers
            date = datetime.datetime.now()
            annee = date.strftime('%Y')





            context = {"etude": instance,"phases":phases,"nb_phases":nb_phases,"president":president, "duree":duree, "client": client, "repr":representant_client,"repr_legale":representant_legale_client, "je":je,  "respo":respo, "quali":qualite,"ref_m":ref_m,"annee":annee}
            # Load the template

            env = Environment()

            env.filters['FormatNombres'] = format_nombres

            

            template.render(context, env)
            output = BytesIO()
            template.save(output)
            output.seek(0)

            # Save the "fichier" field of the CE
            filename = f"PVRI_{ref_m}.docx"
            response = FileResponse(output, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        
            
        #except ValueError as ve:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": str(ve)}
        #except :
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": "Un problème a été détecté dans la base de données."}

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))



def editer_rdm(request, id_etude, id_eleve):
    if request.user.is_authenticated:
        #try :
            etude = Etude.objects.get(id=id_etude)
            eleve = Student.objects.get(id=id_eleve)
            #phases= Phase.objects.filter(etude=etude)
            client= etude.client
            assignations  = list(AssignationJEH.objects.filter(eleve=eleve, phase__etude=etude))
            je= eleve.je
            president = Member.objects.filter(je=je,  poste='PRESIDENT').first().student
            remuneration = sum(assignment.retribution_brute_totale() for assignment in assignations)
            date_fin= timezone.now().date()
            for assignation in assignations:
                if assignation.phase.date_fin > date_fin:
                    date_fin = assignation.phase.date_fin
            etudiant_nb_JEH = sum(assignation.nombre_JEH for assignation in assignations )
            template = DocxTemplate("polls/templates/polls/RDM_026.docx")
            model = RDM
            if etude.rdm_edited() :
                #a modifier
                rdm = model(etude=etude, eleve=eleve)
            else :
                rdm = model(etude=etude, eleve=eleve)
                rdm.save()
            
            
            ref_m = etude.ref()
            ref_d = rdm
            ce = etude.convention()
            date = timezone.now().date()
            annee = date.strftime('%Y')
            # !!!! quand je fais ref_d = devis.ref() il reconnait pas devis mais faudra mettre le contexte en fonction de devis
            
            


            context = {"etude": etude,"client": client, "rdm": rdm, "ref_d":ref_d, "etudiant": eleve, "ref_m":ref_m, "assignations":assignations,"annee":annee,"president" :president,"etudiant_nb_JEH":etudiant_nb_JEH,"date_fin":date_fin,
                       "remuneration":remuneration,"ce":ce}
            # Load the template

            env = Environment()

            env.filters['FormatNombres'] = format_nombres
            env.filters['EnLettres'] = en_lettres
            env.filters['ChiffreLettre'] = chiffre_lettres
        
            

            template.render(context, env)

            # Create a temporary in-memory file
            output = BytesIO()
            template.save(output)
            output.seek(0)

            # Save the "fichier" field of the CE
            filename = f"RDM_{ref_m}.docx"
            response = FileResponse(output, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        #except :
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": "Un problème a été détecté dans la base de données."}

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def editer_devis(request, iD):
    if request.user.is_authenticated:
        #try:
            instance = Etude.objects.get(id=iD)
            client = instance.client
            template = DocxTemplate("polls/templates/polls/Devis_026.docx")
            model = Devis
            if instance.devis_edited() :
                devis = instance.devis
            else :
                devis = model(etude=instance)
                devis.save()
            
            responsable = instance.responsable.student
            qualite = instance.resp_qualite.student
            ref_m = instance.ref()
            ref_d = ref_m + "pv"
            # !!!! quand je fais ref_d = devis.ref() il reconnait pas devis mais faudra mettre le contexte en fonction de devis
            
            date = timezone.now()
            mois = date.strftime('%B')
            annee = date.strftime('%Y')
            date_creation= date.strftime('%d %B %Y')


            context = {"etude": instance, "devis": devis, "client": client, "responsable":responsable, "qualite":qualite, "mois":mois, "annee":annee, "date_creation":date_creation,"ref_m":ref_m,"ref_d":ref_d}
            # Load the template

            # Render the document
            template.render(context)


            # Create a temporary in-memory file
            output = BytesIO()
            template.save(output)
            output.seek(0)

            # Save the "fichier" field of the CE
            filename = f"Devis_{ref_m}.docx"
            response = FileResponse(output, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        #except :
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": "Un problème a été détecté dans la base de données."}

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def editer_avenant_ce(request, iD):
    if request.user.is_authenticated:
        try:
            instance = AvenantConventionEtude.objects.get(id=iD)
            ce= instance.ce
            etude = ce.etude
            client = etude.client
            representant_legale_client = etude.client_representant_legale #souvent le patron de l boite qui a le droit de signer les documents

            president = Member.objects.filter(je=etude.je,  poste='PRESIDENT').first().student
            ref_m = etude.ref()

            if etude.fin():
                semaine_fin = math.ceil( (datetime.combine(etude.fin(),time(12, 0))  -datetime.today() ).days /7 )
            else:
                semaine_fin= etude.duree_semaine()

            semaine_fin_lettres= en_lettres(semaine_fin)

            nb_JEH= etude.nb_JEH()
            nb_JEH_lettres = en_lettres(nb_JEH)

            phase_montant_HT=etude.montant_phase_HT()
            phase_montant_HT_lettres = chiffre_lettres(phase_montant_HT)
            frais_HT =etude.frais_dossier
            frais_HT_lettres=chiffre_lettres(frais_HT)
            total_HT= etude.montant_HT_total()
            total_HT_lettres = chiffre_lettres(total_HT)
            total_TTC= etude.total_ttc()
            total_TTC_lettres= chiffre_lettres(total_TTC)
            template = DocxTemplate("polls/templates/polls/avenant_ce_026.docx")
            context = {"avenant": instance, "etude": etude, "client": client, "president":president, "ref_m":ref_m,"ce":ce,"repr_legale": representant_legale_client, "semaine_fin":semaine_fin,
                       "semaine_fin":semaine_fin,"semaine_fin_lettres":semaine_fin_lettres,"nb_JEH":nb_JEH,"nb_JEH_lettres":nb_JEH_lettres,
                       "phase_montant_HT":phase_montant_HT,"phase_montant_HT_lettres":phase_montant_HT_lettres,"frais_HT":frais_HT, "frais_HT_lettres":frais_HT_lettres,
                       "total_HT":total_HT,"total_HT_lettres":total_HT_lettres,"total_TTC":total_TTC,"total_TTC_lettres":total_TTC_lettres
                       }
            # Load the template

            # Render the document
            template.render(context)


            # Create a temporary in-memory file
            output = BytesIO()
            template.save(output)
            output.seek(0)

            # Save the "fichier" field of the CE
            filename = f"AvenantCE_{instance.__str__()}.docx"
            response = FileResponse(output, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except :
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": "Un problème a été détecté dans la base de données."}

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))

def editer_bon(request, iD):
    if request.user.is_authenticated:
        try:
            instance = Etude.objects.get(id=iD)
            client = instance.client
            template = DocxTemplate("polls\\templates\\polls\\Bon_de_Commande.docx")
            bon = BonCommande(cc=instance.convention())
            bon.save()
            responsable = instance.responsable
            context = {"etude": instance, "client": client, "responsable":responsable}
            # Load the template

            # Render the document
            template.render(context)


            # Create a temporary in-memory file
            output = BytesIO()
            template.save(output)
            output.seek(0)

            # Save the "fichier" field of the CE
            filename = f"Devis_{bon.__str__()}.docx"
            response = FileResponse(output, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except :
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": "Un problème a été détecté dans la base de données."}

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


#---- FONCTIONS POUR STATISTIQUES ------------

def calculate_monthly_sums(user_je):
    september = 9
    monthly_sums = []
    month_ca = 0
    res = []

    for month in range(12):
        current_month = (month + september) % 12
        etudes = Etude.objects.filter(je=user_je, debut__month=current_month)

        total_montant_HT = sum(etude.montant_HT_total() for etude in etudes)
        monthly_sums.append(total_montant_HT)

    for k in range(12):
        month_ca += monthly_sums[k]
        res.append(month_ca)
    return res



def calculate_chiffre_affaire_par_departement(user_je):
    revenues = [0]*7
    department_index = {"IMI":0, "GCC":1, "GMM":2, "SEGF":3, "VET":4, "1A":5, "AUTRE":6}
    studies = Etude.objects.filter(je=user_je)
    
    for study in studies:
        if study.montant_HT_total() > 0:
            phases = Phase.objects.filter(etude=study)
            students = study.get_li_students()
            
            for student in students:
                for phase in phases:
                    revenues[department_index[student.departement]] += phase.get_montant_HT(student)

    return revenues

def calculate_chiffre_affaire_par_type(user_je):
    revenues = [0]*6
    type_index = {"GRANDE_ENTREPRISE":0, "SECTEUR_PUBLIC":1, "START_UP_ET_TPE":2, "PME":3, "ETI":4, "ASSOCIATION":5}
    studies = Etude.objects.filter(je=user_je)
    for study in studies:
        montant_HT_total = study.montant_HT_total()
        if montant_HT_total > 0: 
            revenues[type_index[study.client.type]] += montant_HT_total
    return revenues


def calculate_chiffre_affaire_par_secteur(user_je):
    revenues = [0]*8
    secteur_index = {'INDUSTRIE':0, 'DISTRIBUTION':1, 'SECTEUR_PUBLIC':2, 'CONSEIL':3, 'TRANSPORT':4, 'NUMERIQUE':5, 'BTP':6, 'AUTRE':7}
    studies = Etude.objects.filter(je=user_je)
    for study in studies:
        montant_HT_total = study.montant_HT_total()
        if montant_HT_total > 0:
            revenues[secteur_index[study.client.secteur]] += montant_HT_total
    return revenues





#-----------------------

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
            suggestions_client = suggestions_client.filter(Q(nom_societe__icontains=keyword) | Q(nom_representant_legale__icontains=keyword))
            suggestions_student = suggestions_student.filter(Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword))
        count_client = suggestions_client.count()
        count_student = suggestions_student.count()
        suppression_etude_c=max(1, count_client)
        suppression_etude_s=max(1, count_student)
        suggestions_etude=suggestions_etude.order_by('-debut')[:5-suppression_etude_c-suppression_etude_s]
        nombre_etude = suggestions_etude.count()
        suggestions_client = suggestions_client[:5-nombre_etude-suppression_etude_s]
        nombre_client = suggestions_client.count()
        suggestions_student = suggestions_student[:5-nombre_etude-nombre_client]
        return JsonResponse({'suggestions_etude': list(suggestions_etude.values_list('titre', 'id')), 'suggestions_client': list(suggestions_client.values_list('nom_societe', 'id')), 'suggestions_student': list(suggestions_student.values_list('first_name', 'last_name', 'id'))})
    else :
        return JsonResponse({'suggestions_etude': [], 'suggestions_client': [], 'suggestions_student': []})
    
def search_suggestions_student(request, id_etude):
    query = request.GET.get('query', '')
    if query:
        keywords = query.split()
        suggestions_student = Student.objects.filter(je=request.user.je)
        for keyword in keywords:
            suggestions_student = suggestions_student.filter(Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword))
        suggestions_student = suggestions_student[:5]
        etude = Etude.objects.get(id=id_etude)
        return JsonResponse({'suggestions_student': [[student.first_name, student.last_name, student.id, student.phases_etude(etude).count(), student.nb_etudes_realisees()] for student in suggestions_student.all()]})
    else :
        return JsonResponse({'suggestions_student': []})


def search(request):
    liste_messages = Message.objects.filter(
        destinataire=request.user,
        read=False,
        date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
    ).order_by("date")
    message_count = liste_messages.count()
    liste_messages = liste_messages[:3]
    all_notifications = request.user.notifications.order_by("-date_effet")
    notification_list = [notif for notif in all_notifications if notif.active()]
    notification_count = len(notification_list)
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
            liste_res_client.append(resultats_client.filter(Q(nom_societe__icontains=keyword) | Q(nom_representant_legale__icontains=keyword)))
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
        context = {"query":query, "res_etude":final_res_etude, "res_client":final_res_client, "res_student":final_res_student, "liste_messages":liste_messages, "message_count":message_count, "notification_list":notification_list, "notification_count":notification_count}
        template = loader.get_template("polls/search_results.html")
        return HttpResponse(template.render(context, request))
    else:
        context = {"query":query, "liste_messages":liste_messages, "message_count":message_count, "notification_list":notification_list, "notification_count":notification_count}
        template = loader.get_template("polls/search_results.html")
        return HttpResponse(template.render(context, request))
    
def ajouter_phase(request, id_etude):
    if request.user.is_authenticated:
        if request.method == 'POST':
            fetchform = AddPhase(request.POST)
            if fetchform.is_valid():
                etude = Etude.objects.get(id=id_etude)
                count_phase = Phase.objects.filter(etude=etude).count()
                fetchform.save(commit=True, id_etude=id_etude, numero=count_phase+1)
        return redirect('details', modelName='Etude', iD=id_etude)
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))
'''
def ajouter_representant(request, id_client):
    if request.user.is_authenticated:
        if request.method == 'POST':
            fetchform = AddRepresentant(request.POST)
            if fetchform.is_valid():
                fetchform.save(commit=True, id_client=id_client)
        return redirect('details', modelName='Client', iD=id_client)
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))
'''
def ajouter_facture(request, id_etude):
    if request.user.is_authenticated:
        if request.method == 'POST':
            fetchform = AddFacture(request.POST)
            if fetchform.is_valid():
                fetchform.save(commit=True, id_etude=id_etude)
        return redirect('details', modelName='Etude', iD=id_etude)
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))
    
def BV(request, id_etude, id_eleve):
    if request.user.is_authenticated:
        #try :
            etude = Etude.objects.get(id=id_etude)
            eleve = Student.objects.get(id=id_eleve)
            je= eleve.je
            nb_JEH = 0
            montant_HT = 0.
            if request.method == 'POST':
                for phase in etude.phases.all():
                    my_checkbox_value = request.POST.get(f'checkInputPhase{phase.id}')
                    print(f'checkInputPhase{phase.id}')
                    print(my_checkbox_value)
                    print(request.POST)
                    if (my_checkbox_value is not None):
                        nb_JEH += phase.get_nb_JEH_eleve(eleve)
                        montant_HT += phase.get_montant_HT(eleve)


            chemin_absolu = os.path.join("polls/static/polls/template_bv_sylog.xlsx")
            
            classeur = openpyxl.load_workbook(chemin_absolu)

            # Sélectionner la feuille de calcul
            feuille = classeur.active

            # Modifier la cellule G4
            feuille['H2'] = "N° 24001"
            feuille['I13'] = montant_HT
            feuille['I14'] = nb_JEH
            feuille['G4'] = eleve.first_name +" " + eleve.last_name
            feuille['G6'] = eleve.adress
            feuille['G8'] = eleve.code_postal + " " + eleve.country
            feuille['I3'] = datetime.now().strftime('%d %B %Y')
            feuille['C13']= etude.ref()

            #assignation_jeh = AssignationJEH.objects.get(etude=etude, student=eleve)
            #feuille['C13']= assignation_jeh.reference
            feuille['H10'] = eleve.numero_ss
            
            #info JE
            feuille['I15'] = je.base_urssaf
            feuille['F23'] = je.taux_ATMP
            # Sauvegarder les modifications dans le fichier Excel
            classeur.save(chemin_absolu)
            return FileResponse(open(chemin_absolu, 'rb'), as_attachment=True)
        #except :
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
            template = loader.get_template("polls/page_error.html")
            context = {"error_message":"Erreur dans le téléversement du BV.", "liste_messages":liste_messages, "message_count":message_count}
            return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))


def ajouter_assignation_jeh(request, id_etude, numero_phase):
    if request.user.is_authenticated:
        if request.method == 'POST':
            fetchform = AddIntervenant(request.POST)
            if fetchform.is_valid():
                #try :
                    etude = Etude.objects.get(id=id_etude)
                    phase = Phase.objects.get(etude=etude, numero=numero_phase)
                    eleve = fetchform.cleaned_data['eleve']
                    ass_jeh = AssignationJEH.objects.filter(phase=phase, eleve=eleve)
                    if (ass_jeh.exists()):
                        only_ass_jeh = ass_jeh[0]
                        only_ass_jeh.nombre_JEH = fetchform.cleaned_data['nombre_JEH']
                        only_ass_jeh.pourcentage_retribution = fetchform.cleaned_data['pourcentage_retribution']
                        only_ass_jeh.save()
                    else :
                        fetchform.save(commit=True, id_etude=id_etude, numero_phase=numero_phase)
                #except:
                    pass
        return redirect('details', modelName='Etude', iD=id_etude)
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))
    
def recrutement(request, id_url): # Controler les dates
    if (request.method=='GET'):
        try :
            uuid_url = UUID(id_url)
            etude = Etude.objects.get(id_url=uuid_url)
            if (etude.date_fin_recrutement is None or etude.date_debut_recrutement is None or timezone.now().date()<etude.date_debut_recrutement or timezone.now().date()>etude.date_fin_recrutement):
                raise ValueError('')
            context = {'etude':etude, 'form':Recrutement()}
            template = loader.get_template("polls/recrutement.html")
        except :
            context = {'error_message': "Cette page n'est associée à aucune mission, ou vous tentez d'y accéder hors période de recrutement."}
            template = loader.get_template("polls/recrutement_fail.html")
    else:
        try :
            uuid_url = UUID(id_url)
            etude = Etude.objects.get(id_url=uuid_url)
            recrutement = Recrutement(request.POST)
            if(recrutement.is_valid()):
                existing_students = Student.objects.filter(mail=recrutement.cleaned_data['email'], first_name__iexact=recrutement.cleaned_data['prenom'], last_name__iexact=recrutement.cleaned_data['nom'])
                student = None
                detail_message = None
                if(existing_students.exists()):
                    student = existing_students[0]
                    detail_message = "Votre profil a été reconnu dans la base de données."
                else:
                    student = Student(je=request.user.je, titre=recrutement.cleaned_data['titre'], first_name=recrutement.cleaned_data['prenom'], last_name=recrutement.cleaned_data['nom'], mail=recrutement.cleaned_data['email'], promotion=recrutement.cleaned_data['promotion'], departement=recrutement.cleaned_data['departement'])
                    student.save()
                    detail_message = "D'après nos données, il s'agit de votre première candidature."
                candidature = Candidature(eleve=student, motivation=recrutement.cleaned_data['motivation'], etude=etude)
                candidature.save()

                notif = Notification(description=student.__str__()+" a soumis sa candidature pour la mission "+etude.ref(), date_effet=timezone.now().date(), date_echeance=(timezone.now()+timedelta(weeks=2)).date(), href_redirect=reverse('details', kwargs={"modelName":"Etude", "iD":etude.id}))
                notif.save()
                all_responsables = [etude.responsable]
                for representant in all_responsables:
                    notif.utilisateur.add(representant)

                context = {"detail_message" : detail_message}
                template = loader.get_template("polls/recrutement_succes.html")
            else:
                context = {'error_message': "Votre candidature semble contenir des données corrompues."}
                template = loader.get_template("polls/recrutement_fail.html")
        except :
            context = {'error_message': "Votre candidature n'a pas pu aboutir."}
            template = loader.get_template("polls/recrutement_fail.html")
    return HttpResponse(template.render(context, request))


@csrf_exempt
def modifier_je(request, id):
    je = get_object_or_404(JE, id=id)

    if request.method == 'POST':
        # Update the fields with data from the form
        je.nom = request.POST.get('nom')
        je.raison_sociale = request.POST.get('raison_sociale')
        je.rue = request.POST.get('rue')
        je.ville = request.POST.get('ville')
        je.code_postal = request.POST.get('code_postal')
        je.siret = request.POST.get('siret')
        je.APE = request.POST.get('APE')
        je.TVA = request.POST.get('TVA')
        je.IBAN = request.POST.get('IBAN')
        je.BIC = request.POST.get('BIC')
        je.chiffres_affaires = request.POST.get('chiffres_affaires')
        je.save()

        # Return JSON response
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)


def modifier_recrutement_etude(request, iD):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                etude = Etude.objects.get(id=iD)
                etude.date_debut_recrutement = request.POST['debut']
                etude.date_fin_recrutement = request.POST['fin']
                etude.save()
                return JsonResponse({'success':True, 'debut':etude.date_debut_recrutement, 'fin':etude.date_fin_recrutement})
            except:
                return JsonResponse({'success':False})
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))
    
@csrf_exempt
def modifier_etude(request, iD):
    # Fetch the Etude instance using the provided iD
    etude = get_object_or_404(Etude, id=iD)

    if request.method == 'POST':
        # Get the form data from the request
        debut = request.POST.get('debut')
        fin = request.POST.get('fin')
        nb_JEH = request.POST.get('nb_JEH')
        montant_phase_HT = request.POST.get('montant_phase_HT')
        frais_dossier = request.POST.get('frais_dossier')

        # Update the Etude instance with the new data
        etude.debut = debut
        etude.fin = fin
        etude.nb_JEH = nb_JEH
        etude.montant_phase_HT = montant_phase_HT
        etude.frais_dossier = frais_dossier
        etude.save()  # Save changes to the database

        # Prepare JSON response
        response_data = {
            'success': True,
            'debut': etude.debut,
            'fin': etude.fin,
            'nb_JEH': etude.nb_JEH,
            'montant_phase_HT': etude.montant_phase_HT,
            'frais_dossier': etude.frais_dossier,
        }
        return JsonResponse(response_data)
    else:
        # If not POST, return an error response
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)
    
def remarque_etude(request, iD):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                raw_data = request.body
                data = json.loads(raw_data.decode('utf-8'))  # Decode bytes to string
                content = data.get('content', '')
                etude = Etude.objects.get(id=iD)
                etude.remarque = content
                print("Texte de la remarque : ",etude.remarque)
                etude.save()
                return JsonResponse({'success':True})
            except:
                return JsonResponse({'success':False})
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))


def send_mail_demarchage(request):
    if request.user.is_authenticated:
        liste_messages = Message.objects.filter(
                destinataire=request.user,
                read=False,
                date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
            ).order_by("date")
        message_count = liste_messages.count()
        liste_messages = liste_messages[:3]
        all_notifications = request.user.notifications.order_by("-date_effet")
        notification_list = [notif for notif in all_notifications if notif.active()]
        notification_count = len(notification_list)
        context = {
        "liste_messages": liste_messages,
        "message_count": message_count,
        "notification_list":notification_list,
        "notification_count":notification_count,
        }
        if request.method == 'POST':
            try :
                host = None
                port = None
                username = None
                email_host = host if host else conf_settings.EMAIL_HOST
                email_port = port if port else conf_settings.EMAIL_PORT
                username = None
                username = username if username else conf_settings.EMAIL_USERNAME
                password = None
                password = password if password else conf_settings.EMAIL_PASSWORD
                connection = get_connection(host=email_host, port=email_port, username=username,
                    password=password,
                    use_tls=True,)
                subject = request.POST['subject']
                message = request.POST['message']+"\n"+"\n"+request.POST['name']+"\n"+request.POST['signature']
                from_email = conf_settings.EMAIL_USERNAME
                recipient_list = [request.POST['destinataire']]
                send_mail(subject, message, from_email, recipient_list, 
                        fail_silently=False, 
                        connection=connection)
                return redirect('demarchage')
            except:
                context['error_message'] = "Vous n'avez pas de connexion ou votre serveur d'envoi de mail n'est pas fonctionnel."
                template = loader.get_template("polls/page_error.html")
        else :
            template = loader.get_template("polls/page_error.html")
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))



def settings(request):
    if request.user.is_authenticated:
        liste_messages = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).order_by("date")
        message_count = liste_messages.count()
        liste_messages = liste_messages[:3]
        all_notifications = request.user.notifications.order_by("-date_effet")
        notification_list = [notif for notif in all_notifications if notif.active()]
        notification_count = len(notification_list)
        
        template = loader.get_template("polls/settings.html")
        if request.method == 'GET':
            context = {
                "liste_messages": liste_messages,
                "message_count": message_count,
                "notification_list":notification_list,
                "notification_count":notification_count,
                "user": request.user,
                "form_param": SetParametresUtilisateur(instance=request.user.parametres)
            }
        else :
            try:
                fetchform = request.POST
                param = SetParametresUtilisateur(fetchform, instance=request.user.parametres)
                param.save()
                context = {
                    "liste_messages": liste_messages,
                    "message_count": message_count,
                    "notification_list":notification_list,
                    "notification_count":notification_count,
                    "user": request.user,
                    "form_param": SetParametresUtilisateur(instance=request.user.parametres),
                    "alert_message":"Modifications enregistrées!"
                }
            except:
                context = {
                    "liste_messages": liste_messages,
                    "message_count": message_count,
                    "notification_list":notification_list,
                    "notification_count":notification_count,
                    "user": request.user,
                    "form_param": SetParametresUtilisateur(instance=request.user.parametres),
                    "alert_message":"La modification n'a pas aboutie!"
                }
        return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template("polls/login.html")
        context = {}
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

def add_intervenant(request, id_etude, id_student):
    if request.user.is_authenticated:
        try:
            etude = Etude.objects.get(id=id_etude)
            eleve = Student.objects.get(id=id_student)
            for phase in etude.phases.all() :
                nb_jeh = request.POST[("nb_jeh_phase"+str(phase.numero))]
                pourcentage_retribution = request.POST[("pourcentage_retribution_phase"+str(phase.numero))]
                if(nb_jeh is not None and pourcentage_retribution is not None):
                    existing_ass_jeh = AssignationJEH.objects.filter(phase=phase, eleve=eleve)
                    if(existing_ass_jeh.exists()):
                        retrieve_ass_jeh = existing_ass_jeh[0]
                        retrieve_ass_jeh.nombre_JEH = nb_jeh
                        retrieve_ass_jeh.pourcentage_retribution = pourcentage_retribution
                        retrieve_ass_jeh.save()
                    else :
                        new_ass_jeh = AssignationJEH(phase=phase, eleve=eleve, nombre_JEH=nb_jeh, pourcentage_retribution=pourcentage_retribution)
                        new_ass_jeh.save()
            return redirect('details', modelName="Etude", iD=id_etude)
            
        except:
            liste_messages = Message.objects.filter(
                destinataire=request.user,
                read=False,
                date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
            ).order_by("date")
            message_count = liste_messages.count()
            liste_messages = liste_messages[:3]
            all_notifications = request.user.notifications.order_by("-date_effet")
            notification_list = [notif for notif in all_notifications if notif.active()]
            notification_count = len(notification_list)
            template = loader.get_template("polls/page_error.html")
            context = {"liste_messages":liste_messages,"message_count":message_count, "error_message": "Erreur dans l'identification de la mission.", "notification_list":notification_list, "notification_count":notification_count}
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def ajouter_avenant_ce(request, id_etude):
    if request.user.is_authenticated:
        liste_messages = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).order_by("date")
        message_count = liste_messages.count()
        liste_messages = liste_messages[:3]
        all_notifications = request.user.notifications.order_by("-date_effet")
        notification_list = [notif for notif in all_notifications if notif.active()]
        notification_count = len(notification_list)
        if request.method == 'POST':
            try:
                etude = Etude.objects.get(id=id_etude)
                signature = None
                if request.POST['date_signature'] != '':
                    signature = request.POST['date_signature']
                nouveau_frais_dossier = request.POST['frais_dossier']              
                new_avenant = AvenantConventionEtude(ce = etude.convention(), numero = request.POST['numero'], date_signature=signature, remarque=request.POST['remarque'])
                if nouveau_frais_dossier is not None and etude.frais_dossier != nouveau_frais_dossier:
                    new_avenant.nouveau_frais_dossier = nouveau_frais_dossier
                    new_avenant.ancien_frais_dossier = etude.frais_dossier
                    etude.frais_dossier = nouveau_frais_dossier
                new_avenant.save()
                for phase in etude.phases.all():
                    if( 'suppression'+str(phase.id) in request.POST and request.POST['suppression'+str(phase.id)] == "on" and not phase.supprimee):
                        supp_phase = SuppressionPhase(avenant_ce=new_avenant, phase=phase)
                        supp_phase.save()
                        phase.supprimee=True
                    if(request.POST['debut'+str(phase.id)] != phase.debut_relatif):
                        n_debut = request.POST['debut'+str(phase.id)]
                        deb_phase = ModificationDebutPhase(avenant_ce=new_avenant, phase=phase, nouveau_debut=n_debut, ancien_debut=phase.debut_relatif)
                        deb_phase.save()
                        phase.debut_relatif = n_debut
                    if(request.POST['duree'+str(phase.id)] != phase.duree_semaine):
                        n_duree = request.POST['duree'+str(phase.id)]
                        dur_phase = ModificationDureePhase(avenant_ce=new_avenant, phase=phase, nouvelle_duree=n_duree, ancienne_duree=phase.duree_semaine)
                        dur_phase.save()
                        phase.duree_semaine = n_duree
                    if(request.POST['nb_jeh'+str(phase.id)] != phase.duree_semaine):
                        n_jeh = request.POST['nb_jeh'+str(phase.id)]
                        jeh_phase = ModificationJEHPhase(avenant_ce=new_avenant, phase=phase, nouveau_nombre_JEH=n_jeh, ancien_nombre_JEH=phase.nb_JEH)
                        jeh_phase.save()
                        phase.nb_JEH = n_jeh
                    phase.save(update_fields=['supprimee', 'debut_relatif', 'duree_semaine', 'nb_JEH'])
                return redirect('details', modelName="Etude", iD=id_etude)
            except:
                template = loader.get_template("polls/page_error.html")
                context = {"liste_messages":liste_messages,"message_count":message_count, "error_message": "Le formulaire envoyé est incohérent : certaines données sont manquantes, certaines données sont inattendues.", "notification_list":notification_list, "notification_count":notification_count}
        else :
            template = loader.get_template("polls/page_error.html")
            context = {"liste_messages":liste_messages,"message_count":message_count, "error_message": "Erreur de requête.", "notification_list":notification_list, "notification_count":notification_count}
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))

def ajouter_representant(request, id_client):
    if request.user.is_authenticated:
        liste_messages = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).order_by("date")
        message_count = liste_messages.count()
        liste_messages = liste_messages[:3]
        all_notifications = request.user.notifications.order_by("-date_effet")
        notification_list = [notif for notif in all_notifications if notif.active()]
        notification_count = len(notification_list)
        if request.method == 'POST':
            #try:
                client = Client.objects.get(id=id_client)
                fetchform = AddRepresentant(request.POST)
                #if fetchform.is_valid():
                new_representant = fetchform.save(commit=False)
                new_representant.client = client
                new_representant.save()
                return redirect('details', modelName="Client", iD=id_client)
                #else :
                    #raise ValueError("Formulaire corrompu")
            #except:
                template = loader.get_template("polls/page_error.html")
                context = {"liste_messages":liste_messages,"message_count":message_count, "error_message": "Le formulaire envoyé est incohérent : certaines données sont manquantes, certaines données sont inattendues.", "notification_list":notification_list, "notification_count":notification_count}
        else :
            template = loader.get_template("polls/page_error.html")
            context = {"liste_messages":liste_messages,"message_count":message_count, "error_message": "Erreur de requête.", "notification_list":notification_list, "notification_count":notification_count}
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))



def factures(request):
    if request.user.is_authenticated:
        user_je = request.user.je
        factures = Facture.objects.all().order_by('numero_facture')
        #pas optimale mais faudrait potentiellement crééer un champs je
        filtered_factures = [facture for facture in factures if facture.je() == user_je]
        template = loader.get_template("polls/factures.html")
        context = { "factures": filtered_factures}
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def BVs(request):
    if request.user.is_authenticated:
        user_je = request.user.je
        factures = Facture.objects.all().order_by('numero_facture')
        #pas optimale mais faudrait potentiellement crééer un champs je
        filtered_factures = [facture for facture in factures if facture.je() == user_je]
        template = loader.get_template("polls/factures.html")
        context = { "factures": filtered_factures}
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


