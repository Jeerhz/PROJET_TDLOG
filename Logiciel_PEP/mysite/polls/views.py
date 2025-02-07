import json
import os

#### UTILISATEUR WINDOWS ####
# Installer MSYS2 puis à l'aide du terminal installer GTK puis gobject
# Après installation de gobject, chercher le répertoire des dll et les mettre en variable d'environnement

import openpyxl
import csv
from io import StringIO

from django.template.loader import render_to_string
from weasyprint import HTML
from loguru import logger


import pytz  # pour CA dynamique
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
from jinja2 import Environment
import math
from html2image import Html2Image
import time as time1
from social_django.models import UserSocialAuth
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from asgiref.sync import sync_to_async
from django.db.models import Sum, Max

from django.core.files.uploadedfile import InMemoryUploadedFile


from io import BytesIO
from uuid import UUID
from openpyxl import load_workbook
from django.shortcuts import redirect, get_object_or_404
from django.core.mail import send_mail, get_connection, EmailMessage
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.template import loader
from django.urls import reverse, resolve
from urllib.parse import urlparse
from django.apps import apps
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils import timezone
from django.utils.html import strip_tags
from django.db.models import Sum, Count, Q, Prefetch
import datetime
from datetime import timedelta, date, time
from django.views.decorators.csrf import csrf_exempt
import locale

from django.db.models.functions import ExtractYear
from dateutil.relativedelta import relativedelta

# ADLE: For code optimisation
from asgiref.sync import sync_to_async
from django.http import HttpResponse
from django.template.loader import render_to_string
from polls.tasks import (
    fetch_clients,
    fetch_students,
    fetch_etudes,
    fetch_messages,
    fetch_notifications,
)

from concurrent.futures import ThreadPoolExecutor, as_completed
from django.http import HttpResponse
from django.template import loader
from django.db import connection

locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
from django.http import JsonResponse, FileResponse
from django.conf import settings as conf_settings
from django.core.files.base import ContentFile
from .templatetags.format_duration import (
    format_nombres,
    chiffre_lettres,
    en_lettres,
    assignation,
)
from django.shortcuts import render
from django.template.loader import render_to_string
from django.templatetags.static import static

# from wand.image import Image

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
    CustomMailTemplate,
    CreateMailTemplate,
    StudentCSVUploadForm,
    ClientCSVUploadForm,
    AssociationPhaseBDC,
    BA,
    AssociationFactureBDC,
    BV,
    EtudeImportee,
    AddEtudeImportee,
    EtudeCSVUploadForm,
)


# flemme d'import format durations
def format_nombres(nombre):
    """Formate un nombre en nombre à virgule avec deux chiffres après la virgule"""
    arrondi = round(float(nombre), 2)
    nbre_virg = f"{arrondi:.2f}".replace(".", ",")
    return nbre_virg


def general_context(request):
    """Renvoie un dictionnaire contenant les messages non lus, le nombre de messages non lus, les notifications actives et le nombre de notifications actives"""
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
        "notification_list": notification_list,
        "notification_count": notification_count,
    }
    return context


def confidentialite_donnees(request):
    template = loader.get_template("polls/confidentialite_donnees.html")
    context = {}
    return HttpResponse(template.render(context, request))


##TODO: Refacto this code to be more readable with functions to be reimplemented
def index(request):
    user = request.user
    if not user.is_authenticated:
        return render(request, "polls/login.html")

    user_je = user.je
    mandat_select = request.POST.getlist("mandat-select") or [
        choice[0] for choice in Etude.Mandat.choices
    ]

    # Define helper functions for fetching data
    def fetch_recent_etudes():
        return list(
            Etude.objects.filter(je=user_je, mandat__in=mandat_select)
            .select_related(
                "responsable", "client", "resp_qualite"
            )  # Ensure 'client' is a ForeignKey
            .prefetch_related(
                Prefetch("phases", queryset=Phase.objects.all()),
                Prefetch("responsables", queryset=Member.objects.all()),
            )
            .order_by("numero")
        )

    def fetch_messages():
        return list(
            Message.objects.filter(
                destinataire=user,
                read=False,
                date__range=(
                    timezone.now() - timezone.timedelta(days=20),
                    timezone.now(),
                ),
            ).order_by("date")[:3]
        )

    def fetch_notifications():
        return list(user.notifications.order_by("-date_effet"))

    # Use ThreadPoolExecutor to handle blocking operations
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit tasks to the executor
        future_etudes = executor.submit(fetch_recent_etudes)
        future_messages = executor.submit(fetch_messages)
        future_notifications = executor.submit(fetch_notifications)

        # Collect results as they complete
        results = {}
        for future in as_completed(
            [future_etudes, future_messages, future_notifications]
        ):
            if future == future_etudes:
                results["recent_etudes"] = future.result()
            elif future == future_messages:
                results["liste_messages"] = future.result()
            elif future == future_notifications:
                results["all_notifications"] = future.result()

    # Extract results
    recent_etudes = results.get("recent_etudes", [])
    liste_messages = results.get("liste_messages", [])
    all_notifications = results.get("all_notifications", [])

    # Pre-calculate montant_HT_total and progress_bar for each etude
    for etude in recent_etudes:
        # Calculate montant_phase_HT using pre-fetched phases
        montant_phase_HT = sum(
            phase.montant_HT_par_JEH * phase.nb_JEH
            for phase in etude.phases.all()
            if phase.montant_HT_par_JEH is not None and phase.nb_JEH is not None
        )
        etude.montant_ht_total = etude.frais_dossier + montant_phase_HT

        # Calculate total_duree_semaine
        total_duree_semaine = (
            max(
                (
                    (phase.duree_semaine + phase.debut_relatif)
                    for phase in etude.phases.all()
                    if phase.duree_semaine is not None
                    and phase.debut_relatif is not None
                ),
                default=0,
            )
            * 7
            if recent_etudes
            else 0
        )

        # Calculate progress_bar
        if total_duree_semaine > 0:
            days_passed = (timezone.now().date() - etude.debut).days
            if etude.fin_etude is not None and etude.debut:
                progress = (days_passed / (etude.fin_etude - etude.debut).days) * 100
                etude.progress_bar = int(max(min(100, progress), 0))
        else:
            etude.progress_bar = 0

    # Filter etudes by status
    etudes_terminees = [
        etude for etude in recent_etudes if etude.status == Etude.Status.TERMINEE
    ]
    etudes_en_cours = [
        etude for etude in recent_etudes if etude.status == Etude.Status.EN_COURS
    ]
    etudes_en_negociation = [
        etude for etude in recent_etudes if etude.status == Etude.Status.EN_NEGOCIATION
    ]

    user_parametres = user.parametres

    # Calculate CA (Chiffre d'Affaires)
    def calculate_ca(etudes):
        return sum(
            etude.frais_dossier
            + sum(
                phase.montant_HT_par_JEH * phase.nb_JEH
                for phase in etude.phases.all()
                if phase.montant_HT_par_JEH is not None and phase.nb_JEH is not None
            )
            for etude in etudes
        )

    ca_etudes_ec = calculate_ca(etudes_en_cours)
    ca_etudes_nego = calculate_ca(etudes_en_negociation)
    ca_etudes_term = calculate_ca(etudes_terminees)

    # Prepare the context
    context = {
        "user": user,
        "user_parametres": user_parametres,
        "liste_messages": liste_messages,
        "message_count": len(liste_messages),
        "etudes_terminees": etudes_terminees,
        "etudes_en_cours": etudes_en_cours,
        "etudes_en_negociation": etudes_en_negociation,
        "notification_list": [notif for notif in all_notifications if notif.active()],
        "notification_count": len(all_notifications),
        "mandat_choices": Etude.Mandat.choices,
        "mandat_default": mandat_select,  # Ensure this is a list if used in templates
        "nb_etudes_ec": len(etudes_en_cours),
        "nb_etudes_term": len(etudes_terminees),
        "nb_etudes_nego": len(etudes_en_negociation),
        "ca_etudes_ec": ca_etudes_ec,
        "ca_etudes_term": ca_etudes_term,
        "ca_etudes_nego": ca_etudes_nego,
    }

    return render(request, "polls/index.html", context)


def custom_login(request):
    error_message = ""
    if request.method == "POST":
        user = authenticate(
            request, email=request.POST["email"], password=request.POST["password"]
        )
        if user:
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("index")
        else:
            error_message = "Nom d'utilisateur ou mot de passe incorrect."
            context = {"error_message": error_message}
            template = loader.get_template("polls/login.html")
            return HttpResponse(template.render(context, request))

    template = loader.get_template("polls/login.html")
    context = {}
    return HttpResponse(template.render(context, request))


def google_login(request):
    return redirect("settings")


def custom_logout(request):
    logout(request)
    template = loader.get_template("polls/login.html")
    context = {}
    return HttpResponse(template.render(context, request))


def run_query(func, *args):
    result = func(*args)
    connection.close()
    return result


def annuaire(request):
    """Render the annuaire page with optimized queries using ThreadPoolExecutor."""
    user = request.user
    if not user.is_authenticated:
        template = loader.get_template("polls/login.html")
        return HttpResponse(template.render({}, request))

    user_je = user.je
    user_student = user.student
    user_je_id = user_je.id

    # Define the functions to be executed in parallel
    def fetch_clients_annuaire():
        return list(Client.objects.filter(je=user_je_id).order_by("nom_societe"))

    def fetch_students_annuaire():
        return list(Student.objects.filter(je=user_je_id).order_by("last_name"))

    def fetch_etudes_importees_annuaire():
        return list(EtudeImportee.objects.filter(je=user_je_id).order_by("ref"))

    def fetch_etudes_annuaire():
        return list(
            Etude.objects.filter(je=user_je_id)
            .select_related("responsable__student", "client", "resp_qualite")
            .annotate(annee_creation=ExtractYear("date_creation"))
            .order_by("-annee_creation", "-numero")
        )

    # Use ThreadPoolExecutor to run tasks concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        clients_future = executor.submit(fetch_clients_annuaire)
        students_future = executor.submit(fetch_students_annuaire)
        etudes_future = executor.submit(fetch_etudes_annuaire)
        etudes_importees_future = executor.submit(fetch_etudes_importees_annuaire)
        messages_future = executor.submit(fetch_messages, user)
        notifications_future = executor.submit(fetch_notifications, user)

        # Extract results
        client_list = clients_future.result()
        student_list = students_future.result()
        etude_list = etudes_future.result()
        etude_importe_list = etudes_importees_future.result()

        liste_messages = messages_future.result()
        notification_list = notifications_future.result()

    # Context for rendering the page
    context = {
        "user": user,
        "user_je": user_je,
        "user_student": user_student,
        "user_photo_url": user.photo.url,
        "client_list": client_list,
        "student_list": student_list,
        "etude_list": etude_list,
        "etude_importe_list": etude_importe_list,
        "liste_messages": liste_messages,
        "message_count": len(liste_messages),
        "notification_list": notification_list,
        "notification_count": len(notification_list),
    }

    template = loader.get_template("polls/annuaire.html")
    return HttpResponse(template.render(context, request))


def je_detail(request):
    """Renvoie la page de détail du JE de l'utilisateur connecté"""
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
            "notification_list": notification_list,
            "notification_count": notification_count,
            "je": request.user.je,
        }
        template = loader.get_template("polls/je_detail.html")
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


# TODO: representants n'est jamais utilisé
def demarchage(request):
    """Renvoie la page de démarchage des clients"""
    if request.user.is_authenticated:
        context = general_context(request)
        template = loader.get_template("polls/demarchage.html")
        je = request.user.je
        representants = Representant.objects.filter(client__je=je)
        clients = Client.objects.filter(je=je)
        secteurs = [
            "INDUSTRIE",
            "DISTRIBUTION",
            "SECTEUR_PUBLIC",
            "CONSEIL",
            "TRANSPORT",
            "NUMERIQUE",
            "BTP",
            "AUTRE",
        ]
        mail_templates = je.mail_templates
        mail_templates_ids = list(mail_templates.values_list("id", flat=True))
        mail_template_contents = list(mail_templates.values_list("message", flat=True))
        context["clients"] = clients
        context["secteurs"] = secteurs
        context["mail_template_form"] = CreateMailTemplate()
        context["mail_template_ids"] = mail_templates_ids
        context["mail_template_contents"] = mail_template_contents
        try:
            google_user = request.user.social_auth.get(provider="google-oauth2")
            context["google_user"] = google_user
            context["google_email"] = google_user.extra_data["email"]
            context["connecté"] = True
        except UserSocialAuth.DoesNotExist:
            context["google_user"] = None
            context["alert_message"] = (
                "Vous n'êtes pas connecté à votre compte Google. Vous ne pouvez pas envoyer de mail. (voir paramètres)"
            )
            context["connecté"] = False
        except:
            context["alert_message"] = (
                "L'authentification a fonctionné, mais vous n'avez pas accordé les autorisations Google nécessaires."
            )
            context["connecté"] = False
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def supprimer_demarchage(request, id_representant):
    representant = Representant.objects.filter(id=id_representant).first()

    if request.method == "POST":
        representant.demarchage = "A_CONTACTER"

        nouvelle_remarque = request.POST.get("remarque", "")
        representant.remarque = nouvelle_remarque
        representant.save()
        return redirect("demarchage")

    return redirect("demarchage")


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
        context = {}
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

        context = {
            "attribute_list": Etude.objects.filter(iD=1).get_display_dict(),
            "title": "nptq",
            "iD": 1,
            "liste_messages": liste_messages,
            "message_count": message_count,
        }

        template = loader.get_template("polls/page_detail_etude.html")
        context = {}
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def load_user_messages_and_notifications(user):
    # Load messages
    liste_messages = list(
        Message.objects.filter(
            destinataire=user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).order_by("date")[:3]
    )
    message_count = len(liste_messages)

    # Load notifications
    all_notifications = list(user.notifications.order_by("-date_effet"))
    notification_list = [notif for notif in all_notifications if notif.active()]
    notification_count = len(notification_list)

    return liste_messages, message_count, notification_list, notification_count


def compute_total_retribution(phases):
    total_retribution = 0
    for phase in phases:
        assignations = phase.assignationjeh_set.all()  # Prefetched
        retr_totale = sum(a.retribution_brute_totale() for a in assignations)
        nb_JEHs = sum(a.nombre_JEH for a in assignations)
        # Add remaining JEH retribution
        retr_totale += (phase.nb_JEH - nb_JEHs) * phase.montant_HT_par_JEH * 0.6
        total_retribution += retr_totale
    return total_retribution


def compute_phase_assignations(phases):
    assignations_by_eleve = {}
    assignations_for_each_eleve = {}
    for phase in phases:
        for assignment in phase.assignationjeh_set.all():
            eleve_id = assignment.eleve_id
            if eleve_id not in assignations_by_eleve:
                assignations_by_eleve[eleve_id] = {"JEH_count": 0, "montant_total": 0.0}
                assignations_for_each_eleve[eleve_id] = []
            assignations_by_eleve[eleve_id]["JEH_count"] += assignment.nombre_JEH
            assignations_by_eleve[eleve_id]["montant_total"] += (
                assignment.retribution_brute_totale()
            )
            assignations_for_each_eleve[eleve_id].append(assignment)
    return assignations_by_eleve, assignations_for_each_eleve


def compute_assignations_bon(bon_preloaded_phases):
    dico = {}
    dico_info = {"montant_total_bon": 0, "nb_phases": 0, "nb_JEH": 0}
    for phase in bon_preloaded_phases:
        dico_info["nb_phases"] += 1
        dico_info["nb_JEH"] += phase.nb_JEH
        dico_info["montant_total_bon"] += phase.calcul_mt_HT()
        for assignment in phase.assignationjeh_set.all():
            nb_JEH = assignment.nombre_JEH
            retr = assignment.retribution_brute_totale()
            eleve_id = assignment.eleve_id

            if eleve_id not in dico:
                eleve = assignment.eleve
                dico[eleve_id] = {
                    "nom": eleve.last_name,
                    "prenom": eleve.first_name,
                    "total_nb_JEH": 0,
                    "montant_total": 0,
                    "phases": {
                        phase.id: {
                            "numero": phase.numero,
                            "nb_jeh": nb_JEH,
                            "montant": retr,
                            "pourc": assignment.pourcentage_retribution,
                        }
                    },
                }
            elif phase.id not in dico[eleve_id]["phases"]:
                dico[eleve_id]["phases"][phase.id] = {
                    "numero": phase.numero,
                    "nb_jeh": nb_JEH,
                    "montant": retr,
                    "pourc": assignment.pourcentage_retribution,
                }
            else:
                nb_JEH_ori = dico[eleve_id]["phases"][phase.id]["nb_jeh"]
                pourc_ori = dico[eleve_id]["phases"][phase.id]["pourc"]
                pourc_assi = assignment.pourcentage_retribution
                nv_pourc = (
                    nb_JEH_ori * pourc_ori + nb_JEH * assignment.pourcentage_retribution
                ) / (nb_JEH_ori + nb_JEH)
                dico[eleve_id]["phases"][phase.id]["nb_jeh"] += nb_JEH
                dico[eleve_id]["phases"][phase.id]["montant"] += retr
                dico[eleve_id]["phases"][phase.id]["pourc"] = nv_pourc

            dico[eleve_id]["total_nb_JEH"] += nb_JEH
            dico[eleve_id]["montant_total"] += retr
    return dico, dico_info


def compute_phase_assignations_bdc(bon_preloaded_phases):
    bons_assignations_by_eleve = {}
    bons_assignations_for_each_eleve = {}

    for phase in bon_preloaded_phases:
        for assignment in phase.assignationjeh_set.all():
            eleve_id = assignment.eleve_id
            if eleve_id not in bons_assignations_by_eleve:
                bons_assignations_by_eleve[eleve_id] = {
                    "JEH_count": 0,
                    "montant_total": 0.0,
                }
                bons_assignations_for_each_eleve[eleve_id] = []
            bons_assignations_by_eleve[eleve_id]["JEH_count"] += assignment.nombre_JEH
            bons_assignations_by_eleve[eleve_id]["montant_total"] += (
                assignment.retribution_brute_totale()
            )
            bons_assignations_for_each_eleve[eleve_id].append(assignment)
    return bons_assignations_by_eleve, bons_assignations_for_each_eleve


def compute_jeh_base_and_frais(
    etude, bdc, etude_montant_total_phases, associations_phase
):
    # Compute JEH and frais depending on type_convention
    if etude.type_convention == "Convention cadre":
        bdc_id = bdc.id if bdc else None
        bdc_phases = associations_phase.get(bdc_id, [])
        bdc_montant_total_phases = sum(
            (phase.montant_HT_par_JEH * phase.nb_JEH)
            for phase in bdc_phases
            if phase.montant_HT_par_JEH is not None and phase.nb_JEH is not None
        )
        jeh_base = bdc_montant_total_phases if bdc else 0
        frais_base = bdc.frais_dossier if bdc else 0
    else:
        # Fallback to etude-level data (already in memory from select_related)
        jeh_base = etude_montant_total_phases
        frais_base = etude.frais_dossier
    return jeh_base, frais_base


def etude_ref(etude):
    return etude.ref()


def details(request, modelName, iD):
    user = request.user
    if not user.is_authenticated:
        template = loader.get_template("polls/login.html")
        return HttpResponse(template.render({}, request))

    user_je = user.je
    user_student = user.student

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_messages = executor.submit(load_user_messages_and_notifications, user)

        # Loading model instance
        model = apps.get_model(app_label="polls", model_name=modelName)
        instance = get_object_or_404(model, id=iD)

        liste_messages, message_count, notification_list, notification_count = (
            future_messages.result()
        )
    if modelName == "Message":
        instance.read = True
        instance.save()

    # Une modif

    # Initialize context variables
    etude, phases, factures, intervenants, client, eleve = (
        None,
        None,
        None,
        None,
        None,
        None,
    )

    if modelName == "Etude":
        # Preload all needed relations
        etude = (
            Etude.objects.select_related(
                "resp_qualite",
                "responsable",
                "responsable__student",
                "client",
                "client_interlocuteur",
                "client_representant_legale",
                "je",
            )
            .prefetch_related(
                Prefetch(
                    "phases",
                    queryset=Phase.objects.order_by("numero").prefetch_related(
                        Prefetch(
                            "assignationjeh_set",
                            queryset=AssignationJEH.objects.select_related("eleve"),
                        ),
                        "modif_duree",
                        "modif_debut",
                        "modif_jeh",
                        "suppression",
                    ),
                ),
                Prefetch(
                    "factures",
                    queryset=Facture.objects.order_by("numero_facture").select_related(
                        "etude"
                    ),
                ),
                Prefetch(
                    "conventions_etude",
                    queryset=ConventionEtude.objects.order_by("date_signature"),
                ),
                Prefetch(
                    "conventions_cadre",
                    queryset=ConventionCadre.objects.order_by("date_signature"),
                ),
                "responsable__student",
                "resp_qualite__student",
                "responsables",
                Prefetch("client__representants", queryset=Representant.objects.all()),
            )
            .get(id=iD)
        )

        members = Member.objects.select_related("student").all()
        respo = etude.responsable.student
        phases = etude.phases.all()
        factures = etude.factures.all()
        poste = "Cheffe de Projet" if respo.titre == "Mme" else "Chef de Projet"

        # Intervenants
        intervenants = Student.objects.filter(
            assignationjeh__phase__etude=etude
        ).distinct()

        # Preload AssociationFactureBDC
        associations_facture_bdc = {
            asso.facture: asso.bon_de_commande
            for asso in AssociationFactureBDC.objects.filter(
                facture__in=factures
            ).select_related("bon_de_commande")
        }

        # Preload BDC and associations
        bons = list(
            BonCommande.objects.filter(etude=etude)
            .prefetch_related(
                Prefetch(
                    "associations_phase",
                    queryset=AssociationPhaseBDC.objects.select_related("phase"),
                )
            )
            .order_by("numero")
        )

        associations_bdc_phase = {
            bdc.id: [assoc.phase for assoc in bdc.associations_phase.all()]
            for bdc in bons
        }

        for bon in bons:
            bon.preloaded_phases = associations_bdc_phase.get(bon.id, [])

            bon.preloaded_factures = [
                facture
                for facture, bon_de_commande in associations_facture_bdc.items()
                if bon_de_commande == bon
            ]
        # Compute total retribution
        etude_retributions_totales = compute_total_retribution(phases)

        if etude.client:
            representants_interlocuteurs = [etude.client_interlocuteur]
            representants_legaux = [etude.client_representant_legale]

        else:
            representants_interlocuteurs = []
            representants_legaux = []

        # Compute study end date
        duree = etude.duree_semaine()
        """
        
        duree = max(
            (
                phase.duree_semaine + phase.debut_relatif
                for phase in phases
                if phase.duree_semaine is not None and phase.debut_relatif is not None
            ),
            default=0,
        )
        """

        def etude_fin(etude):
            if etude.fin:
                return etude.fin
            else:
                return (
                    (etude.debut + datetime.timedelta(weeks=duree))
                    if (etude.debut and duree)
                    else None
                )

        etude_fin = etude_fin(etude)

        # Compute total amount of study
        etude_montant_total_phases = sum(
            (phase.montant_HT_par_JEH * phase.nb_JEH)
            for phase in phases
            if phase.montant_HT_par_JEH is not None and phase.nb_JEH is not None
        )

        etude_total_montant_HT = etude_montant_total_phases + etude.frais_dossier

        # Compute total JEH
        etude_nbJEH = sum(phase.nb_JEH for phase in phases if phase.nb_JEH is not None)

        # Compute URSSAF charges
        etude_charge_URSSAF = (
            etude_nbJEH * user_je.base_urssaf * user_je.taux_cotisations / 100.0
            if etude_nbJEH
            else 0
        )

        # Compute marge JE
        etude_marge_JE = (
            etude_total_montant_HT - etude_retributions_totales - etude_charge_URSSAF
        )

        # Find solde facture if any
        etude_facture_solde = next(
            (f for f in factures if f.type_facture == f.Status.SOLDE), None
        )

        # Update factures cached values
        for facture in factures:
            bdc = associations_facture_bdc.get(facture)
            jeh_base, frais_base = compute_jeh_base_and_frais(
                etude, bdc, etude_montant_total_phases, associations_bdc_phase
            )

            fac_JEH = jeh_base * (facture.pourcentage_JEH / 100.0)
            fac_frais = frais_base * (facture.pourcentage_frais / 100.0)

            facture.cached_montant_HT = fac_JEH + fac_frais
            facture.cached_montant_TVA = (
                facture.TVA_per * facture.cached_montant_HT
            ) / 100.0
            facture.cached_montant_TTC = (
                (facture.TVA_per + 100) * facture.cached_montant_HT
            ) / 100.0

        # Compute assignations for each eleve
        type_convention = etude.type_convention
        if type_convention == "Convention d'étude":
            assignations_by_eleve, assignations_for_each_eleve = (
                compute_phase_assignations(phases)
            )

        if type_convention == "Convention d'étude":
            for eleve in intervenants:
                data = assignations_by_eleve.get(
                    eleve.id, {"JEH_count": 0, "montant_total": 0.0}
                )
                eleve.precomputed_JEH_count = data["JEH_count"]
                eleve.precomputed_montant_total = data["montant_total"]

                eleve.assignations_for_etude = assignations_for_each_eleve.get(
                    eleve.id, []
                )

        for bon in bons:
            for facture in bon.preloaded_factures:
                jeh_base, frais_base = compute_jeh_base_and_frais(
                    etude, bon, etude_montant_total_phases, associations_bdc_phase
                )

                facture.fac_frais = frais_base * (facture.pourcentage_frais / 100.0)

            dico_assignations_JEH, dico_info = compute_assignations_bon(
                bon.preloaded_phases
            )
            bon.dico_assignations_JEH = dico_assignations_JEH
            bon.dico_info = dico_info
        client_nom = str(etude.client.nom_societe) if etude.client else "pas de client"

        attribute_list = {
            "Titre": etude.titre,
            "Description": etude.description,
            "Numéro": etude.numero,
            "Client": client_nom,
            "Début": etude.debut,
            "Fin": etude_fin,
            "Responsable": str(respo),
            "Nombre de JEH": etude_nbJEH,
            "Montant HT": etude_total_montant_HT,
        }

    if modelName == "Student":
        eleve = instance
    if modelName == "Client":
        client = instance

    context = {
        "modelName": modelName,
        "iD": iD,
        "user": user,
        "user_student": user_student,
        "user_je": user_je,
        "liste_messages": liste_messages,
        "message_count": message_count,
        "notification_list": notification_list,
        "notification_count": notification_count,
    }

    if etude is not None:
        etude_convention = (
            etude.conventions_etude.first()
            if etude.type_convention == "Convention d'étude"
            else etude.conventions_cadre.first()
        )

        intervenant_form = AddIntervenant(intervenant_queryset=intervenants)
        # à rendre plus efficace ??????
        repartition_budget = {
            "Junior": etude.marge_JE(),
            "Intervenants": etude.retributions_totales(),
            "URSSAF": etude.charges_URSSAF(),
        }
        context.update(
            {
                "attribute_list": attribute_list,
                "title": "Détails de la mission",
                "etude": etude,
                "etude_convention": etude_convention,
                "etude_devis": etude.devis.first(),
                "etude_fac_solde": etude_facture_solde,
                "etude_fin": etude_fin,
                "etude_duree": duree,
                "etude_ref": etude_ref(etude),
                "etude_nbJEH": etude_nbJEH,
                "etude_total_montant_phases": etude_montant_total_phases,
                "etude_total_ht": etude_total_montant_HT,
                "etude_total_ttc": etude_total_montant_HT * (1 + etude.taux_tva / 100),
                "etude_tva": (etude.taux_tva / 100) * etude_total_montant_HT,
                "etude_marge_JE": etude_marge_JE,
                "etude_retributions_totales": etude_retributions_totales,
                "etude_charge_URSSAF": etude_charge_URSSAF,
                "resp_qualite": etude.resp_qualite.student,
                "responsable": respo,
                "phases": phases,
                "factures": factures,
                "intervenants": intervenants,
                "phase_form": AddPhase(),
                "facture_form": AddFacture(),
                "intervenant_form": intervenant_form,
                "etude_form": AddEtude(instance=etude),
                "representants_interlocuteurs": representants_interlocuteurs,
                "representants_legaux": representants_legaux,
                "members": members,
                "poste": poste,
                "bons": bons,
                "repartition_budget": repartition_budget,
                "associations_phase": associations_bdc_phase,
                "type_convention": etude.type_convention,
                "client_interlocuteur": etude.client_interlocuteur,
                "client_representant_legale": etude.client_representant_legale,
            }
        )
        if etude.client:
            context.update({"client": etude.client})

    if client is not None:
        context.update(
            {
                "client": client,
                "representant_form": AddRepresentant(),
            }
        )

    if eleve is not None:
        context["eleve"] = eleve

    template = loader.get_template("polls/page_details.html")
    return HttpResponse(template.render(context, request))


def details_etudes_importees(request, iD):
    if request.user.is_authenticated:
        user_je = request.user.je

        etude = EtudeImportee.objects.get(id=iD, je=user_je)

        template = loader.get_template("polls/page_detail_etude_importee.html")
        context = {"etude": etude}
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def edit_etude(request, pk):
    if request.user.is_authenticated:
        etude = get_object_or_404(Etude, pk=pk)

        if request.method == "POST":
            form = AddEtude(request.POST, instance=etude)
            if form.is_valid():
                form.save(expediteur=request.user)
                return redirect("etude_detail", pk=etude.pk)
        else:
            form = AddEtude(instance=etude)

        return render(request, "etudes/edit_etude.html", {"form": form, "etude": etude})
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

        if request.method == "POST":
            form = AddStudent(request.POST, instance=student)
            if form.is_valid():
                form.save()  # Save changes to the database
                return redirect("details", modelName="Student", iD=student.id)
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
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def edit_pdp(request, pk):
    user = request.user
    if user.is_authenticated:
        # Retrieve the student instance, or return a 404 if not found
        student = get_object_or_404(Student, pk=pk)

        if request.method == "POST":
            # Handle form submission
            member = student.member
            if member and "pdp" in request.FILES:
                uploaded_file = request.FILES["pdp"]
                member.photo = uploaded_file  # Update the photo
                member.save()
                return redirect("details", modelName="Student", iD=student.id)

            else:
                return redirect("details", modelName="Student", iD=student.id)

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def numero_facture(request, iD):
    if request.user.is_authenticated:
        facture = get_object_or_404(Facture, pk=iD)

        if request.method == "POST":
            numero = request.POST["numero_fac"]
            facture.numero_facture = numero
            objet_fac = request.POST["objet_fac"]
            facture.objet = objet_fac
            id_etude = facture.etude.id
            facture.save(id_etude=id_etude)

        return redirect("factures")

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def numero_BV(request, iD):
    if request.user.is_authenticated:
        bv = get_object_or_404(BV, pk=iD)

        if request.method == "POST":
            numero = request.POST["numero_bv"]
            bv.numero_bv = numero
            bv.save()
        return redirect("BVs")

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def modify_etude(request, pk):
    if request.user.is_authenticated:
        print(2)
        # Retrieve the etude instance, or return a 404 if not found
        etude = get_object_or_404(Etude, pk=pk)

        if request.method == "POST":
            form = AddEtude(request.POST, instance=etude)
            if form.is_valid():
                form.save()  # Save changes to the database
            else:
                print(1)
                # Debugging: print out form errors if it is not valid
                print(form.errors)

        return redirect("details", modelName="Etude", iD=pk)

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def object_suppression(request, model_name, object_id):
    if request.user.is_authenticated:
        try:
            model = apps.get_model(app_label="polls", model_name=model_name)
            object = model.objects.get(id=object_id)
            if model_name == "BonCommande":
                etude = object.etude
            # Attention checker la cohérence des JE
            object.delete()
            if model_name == "BonCommande":
                return redirect("details", modelName="Etude", iD=etude.id)
            return JsonResponse({"success": True})
        except:
            return JsonResponse(
                {
                    "success": False,
                    "error_message": "Une erreur a été détectée dans la base de données.",
                }
            )
    else:
        return JsonResponse(
            {
                "success": False,
                "error_message": "Il semblerait que vous ayez été déconnecté.",
            }
        )


def get_client_representants(request):
    if request.user.is_authenticated:
        client_id = request.GET.get("client_id")
        if client_id:
            client = get_object_or_404(Client, id=client_id)
            representants = client.representants()

            interlocuteurs = [
                {"id": r.id, "name": f"{r.first_name} {r.last_name}"}
                for r in representants
            ]

            legaux = [
                {"id": r.id, "name": f"{r.first_name} {r.last_name}"}
                for r in representants
            ]

            return JsonResponse(
                {
                    "interlocuteurs": "".join(
                        [
                            f'<option value="{r["id"]}">{r["name"]}</option>'
                            for r in interlocuteurs
                        ]
                    ),
                    "legaux": "".join(
                        [
                            f'<option value="{r["id"]}">{r["name"]}</option>'
                            for r in legaux
                        ]
                    ),
                }
            )
        return JsonResponse({"error": "Invalid client ID"}, status=400)
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def get_representants(request):
    if request.user.is_authenticated:
        client_id = request.GET.get("client_id")
        if client_id:
            client = get_object_or_404(Client, id=client_id)
            representants = client.representants.distinct()

            results = [
                {"id": r.id, "name": f"{r.first_name} {r.last_name}"}
                for r in representants
            ]

            return JsonResponse({"results": results})
        return JsonResponse({"error": "Invalid client ID"}, status=400)
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


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

        if request.method == "POST":
            # Update the form to include request.FILES to handle file uploads
            form = AddClient(request.POST, request.FILES, instance=client)
            if form.is_valid():
                form.save()  # Save changes to the database, including the new image if uploaded
                return redirect("details", modelName="Client", iD=client.id)
            else:
                # Debugging: print out form errors if it is not valid
                print(form.errors)
        else:
            form = AddClient(instance=client)

        context = {
            "client": client,
            "representant_form": AddRepresentant(),
            "form": form,
            "liste_messages": liste_messages,
            "message_count": message_count,
            "notification_list": notification_list,
            "notification_count": len(notification_list),
            "modelName": "Client",
            "iD": client.id,
            # "user_student" : request.user.student
        }

        return render(request, "polls/page_details.html", context)

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


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
        if request.method == "POST":
            student.delete()
        return redirect("annuaire")
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def delete_etude(request, pk):
    if request.user.is_authenticated:
        etude = get_object_or_404(Etude, pk=pk)
        if request.method == "POST":
            etude.delete()
            return redirect("annuaire")
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def delete_bdc(request, id_etude, id_bon):
    if request.user.is_authenticated:
        bons = BonCommande.objects.filter(etude_id=id_etude)
        bon = bons.get(id=id_bon)
        if not bon:
            return render(
                request,
                "polls/page_error.html",
                {
                    "error_message": "Le bon de commande quje vous souhaitez supprimer n'existe pas.",
                },
            )
        else:
            if request.method == "POST":
                bon.delete()
                return redirect("details", modelName="Etude", iD=id_etude)
            else:
                return render(
                    request,
                    "polls/page_error.html",
                    {
                        "error_message": "La requête pour supprimer le Bon de Commande est invalide.",
                    },
                )

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def edit_phase(request, pk, iD):
    if request.user.is_authenticated:
        # Fetch messages and notifications
        liste_messages = Message.objects.filter(
            destinataire=request.user,
            read=False,
            date__range=(timezone.now() - timezone.timedelta(days=20), timezone.now()),
        ).order_by("date")[:3]
        message_count = liste_messages.count()
        all_notifications = request.user.notifications.order_by("-date_effet")
        notification_list = [notif for notif in all_notifications if notif.active()]

        # Retrieve the phase instance or return a 404 if not found
        phase = Phase.objects.filter(id=pk).first()
        etude = Etude.objects.filter(id=iD).first()

        if request.method == "POST":
            form = AddPhase(request.POST, instance=phase)
            if form.is_valid():
                form.save()  # Save changes to the database
                return redirect("details", modelName="Etude", iD=etude.id)
            else:
                # Debugging: print out form errors if it is not valid
                print(form.errors)
        else:
            form = AddPhase(instance=phase)

        context = {
            "phase": phase,
            "form": form,
            "etude": etude,
            "liste_messages": liste_messages,
            "message_count": message_count,
            "notification_list": notification_list,
            "notification_count": len(notification_list),
            "modelName": "Etude",
            "iD": etude.id,
        }

        return render(request, "polls/page_details.html", context)

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def delete_phase(request, pk, iD):
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

        phase = get_object_or_404(Phase, pk=pk)
        etude = get_object_or_404(Etude, pk=iD)

        context = {
            "etude": etude,
            "liste_messages": liste_messages,
            "message_count": message_count,
            "notification_list": notification_list,
            "notification_count": len(notification_list),
            "modelName": "Etude",
            "iD": etude.id,
        }

        if request.method == "POST":
            phase.delete()
            return redirect("details", modelName="Etude", iD=etude.id)
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def delete_avenant_ce(request, pk, iD):
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

        avenant_ce = get_object_or_404(AvenantConventionEtude, pk=pk)
        etude = get_object_or_404(Etude, pk=iD)

        context = {
            "etude": etude,
            "liste_messages": liste_messages,
            "message_count": message_count,
            "notification_list": notification_list,
            "notification_count": len(notification_list),
            "modelName": "Etude",
            "iD": etude.id,
        }
        print(1)
        if request.method == "POST":
            print(2)
            avenant_ce.delete()
            return redirect("details", modelName="Etude", iD=etude.id)
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def delete_assignation(request, pk, etude_id):
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

        assignation = get_object_or_404(AssignationJEH, pk=pk)
        etude = get_object_or_404(Etude, pk=etude_id)

        context = {
            "etude": etude,
            "liste_messages": liste_messages,
            "message_count": message_count,
            "notification_list": notification_list,
            "notification_count": len(notification_list),
            "modelName": "Etude",
            "iD": etude.id,
        }

        if request.method == "POST":
            assignation.delete()
            return redirect("details", modelName="Etude", iD=etude.id)
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def delete_facture(request, pk, iD):
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

        facture = get_object_or_404(Facture, pk=pk)
        etude = get_object_or_404(Etude, pk=iD)

        context = {
            "etude": etude,
            "liste_messages": liste_messages,
            "message_count": message_count,
            "notification_list": notification_list,
            "notification_count": len(notification_list),
            "modelName": "Etude",
            "iD": etude.id,
        }

        if request.method == "POST":
            facture.delete()
            return redirect("details", modelName="Etude", iD=etude.id)
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def delete_BV(request, pk, iD):
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

        bv = get_object_or_404(BV, pk=pk)
        etude = get_object_or_404(Etude, pk=iD)

        context = {
            "etude": etude,
            "liste_messages": liste_messages,
            "message_count": message_count,
            "notification_list": notification_list,
            "notification_count": len(notification_list),
            "modelName": "Etude",
            "iD": etude.id,
        }

        if request.method == "POST":
            bv.delete()
            return redirect("BVs")
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
        client = get_object_or_404(Client, pk=pk)
        if request.method == "POST":
            client.delete()
        return redirect("annuaire")
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def input(request, modelName, iD):
    if not request.user.is_authenticated:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))

    # Fetch unread messages for the user
    context = general_context(request)

    model = apps.get_model(app_label="polls", model_name=modelName)
    template_name = "polls/page_input.html"

    if request.method == "GET":
        if iD == 0:
            # New instance creation
            form = model.createForm(je=request.user.je)
            # Exclude superusers from any user-related fields
            if "Member" in form.fields:
                form.fields["Member"].queryset = Member.objects.filter(
                    is_superuser=False
                )
            context["form"] = form
            context["title"] = str(form)
            context["message"] = ""
            context["modelName"] = modelName
            context["iD"] = iD
            context["is_message"] = modelName == "Message"
        else:
            # Modify existing instance
            try:
                instance = model.objects.get(id=iD, je=request.user.je)
                form = model.modifyForm(instance)
                # Exclude superusers from any user-related fields
                if "user" in form.fields:
                    form.fields["user"].queryset = User.objects.filter(
                        is_superuser=False
                    )
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
            except model.DoesNotExist:
                # Redirect to error page if instance does not exist
                return render(
                    request,
                    "polls/page_error.html",
                    {
                        "error_message": "L'objet sélectionné n'existe pas dans la base de données.",
                        "liste_messages": liste_messages,
                        "message_count": message_count,
                    },
                )

    else:  # POST request
        fetchform = model.retrieveForm(request.POST, files=request.FILES)
        if fetchform.is_valid():
            # Save the form, handling new and existing instances
            if iD == 0:
                fetchform.save(commit=True, expediteur=request.user)
            else:
                fetchform.save(commit=True)
            # Redirect after successful form submission
            return redirect("annuaire")
        else:
            # Handle form errors
            context = {
                "form": fetchform,
                "title": str(fetchform),
                "message": "Entrée invalide",
                "modelName": modelName,
                "iD": iD,
                "liste_messages": liste_messages,
                "message_count": message_count,
            }

    return HttpResponse(loader.get_template(template_name).render(context, request))


def upload_students(request):
    if request.user.is_authenticated:
        try:
            if request.method == "POST":
                form = StudentCSVUploadForm(request.POST, request.FILES)

                if form.is_valid():
                    csv_file = request.FILES.get("csv_file")

                    # Check if the file is a CSV
                    if not csv_file.name.endswith(".csv"):
                        raise ValueError("Ce n'est pas un csv")

                    try:
                        # Decode the uploaded file and read its content with correct delimiter
                        data = csv_file.read().decode("utf-8")

                        # Use csv.Sniffer to detect the delimiter
                        sniffer = csv.Sniffer()
                        detected_dialect = sniffer.sniff(data)
                        delimiter = detected_dialect.delimiter

                        # Read the file using the detected delimiter
                        reader = csv.reader(StringIO(data), delimiter=delimiter)
                        # Skip the header row if present
                        header = next(reader, None)

                        # Check if header matches the expected columns
                        if len(header) != 12:
                            raise ValueError(
                                "Le fichier csv doit contenir 12 colonnes : titre, prénom, nom, mail, portable, rue, ville, CP, pays, département, promo, numero_ss"
                            )

                        # Iterate through each row in the CSV
                        for row in reader:
                            if len(row) != 12:
                                ValueError(f"problème à la ligne {row}")

                            # Assuming the CSV columns are: titre, first_name, last_name, mail, phone_number, rue, ville, code_postal, pays
                            try:
                                (
                                    titre,
                                    first_name,
                                    last_name,
                                    mail,
                                    phone_number,
                                    rue,
                                    ville,
                                    code_postal,
                                    pays,
                                    depart,
                                    promo,
                                    numero_ss,
                                ) = row
                                je = request.user.je
                                # Create or update the student record
                                Student.objects.get_or_create(
                                    je=je,
                                    first_name=first_name.strip(),
                                    last_name=last_name.strip(),
                                    mail=mail.strip(),
                                    titre=titre.strip(),
                                    phone_number=phone_number.strip(),
                                    adress=rue.strip(),
                                    ville=ville.strip(),
                                    code_postal=code_postal.strip(),
                                    country=pays.strip(),
                                    departement=depart.strip(),
                                    promotion=promo.strip(),
                                    numero_ss=numero_ss.strip(),
                                )

                            except ValueError as ve:
                                template = loader.get_template("polls/page_error.html")
                                context = {"error_message": str(ve)}
                            except Exception as e:
                                template = loader.get_template("polls/page_error.html")
                                context = {
                                    "error_message": f"Un problème a été détecté dans la base de données: {str(e)}"
                                }
                    except ValueError as ve:
                        template = loader.get_template("polls/page_error.html")
                        context = {"error_message": str(ve)}
                    except Exception as e:
                        template = loader.get_template("polls/page_error.html")
                        context = {
                            "error_message": f"Un problème a été détecté dans la base de données: {str(e)}"
                        }

                    return redirect("upload_students")
            else:
                form = StudentCSVUploadForm()

            return redirect("annuaire")
        except ValueError as ve:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": str(ve)}
        except Exception as e:
            template = loader.get_template("polls/page_error.html")
            context = {
                "error_message": f"Un problème a été détecté dans la base de données: {str(e)}"
            }
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))

    # return render(request, 'polls/annuaire.html', {'form': form})


def upload_clients(request):
    if request.user.is_authenticated:
        try:
            if request.method == "POST":
                form = ClientCSVUploadForm(request.POST, request.FILES)

                if form.is_valid():
                    csv_file = request.FILES.get("csv_file_client")

                    # Check if the file is a CSV

                    if not csv_file.name.endswith(".csv"):
                        raise ValueError("Ce n'est pas un csv")

                    try:
                        # Decode the uploaded file and read its content with correct delimiter
                        data = csv_file.read().decode("utf-8")
                        # Use csv.Sniffer to detect the delimiter
                        sniffer = csv.Sniffer()
                        detected_dialect = sniffer.sniff(data)
                        delimiter = detected_dialect.delimiter

                        # Read the file using the detected delimiter
                        reader = csv.reader(StringIO(data), delimiter=delimiter)
                        # Skip the header row if present
                        header = next(reader, None)

                        # Check if header matches the expected columns
                        if len(header) != 6:
                            raise ValueError(
                                "Le fichier csv doit contenir 6 colonnes : nom, raison sociale, rue, ville, code postal, pays"
                            )

                        # Iterate through each row in the CSV
                        for row in reader:
                            if len(row) != 6:
                                raise ValueError(f"La ligne {row} n'a pas 6 cellules")

                            # Assuming the CSV columns are: titre, first_name, last_name, mail, phone_number, rue, ville, code_postal, pays
                            try:
                                (
                                    nom_societe,
                                    raison_sociale,
                                    rue,
                                    ville,
                                    code_postal,
                                    country,
                                ) = row
                                je = request.user.je
                                print("on est lama")
                                # Create or update the student record
                                Client.objects.get_or_create(
                                    je=je,
                                    nom_societe=nom_societe.strip(),
                                    raison_sociale=raison_sociale.strip(),
                                    rue=rue.strip(),
                                    ville=ville.strip(),
                                    code_postal=code_postal.strip(),
                                    country=country.strip(),
                                )

                            except ValueError as ve:
                                template = loader.get_template("polls/page_error.html")
                                context = {"error_message": str(ve)}
                            except Exception as e:
                                template = loader.get_template("polls/page_error.html")
                                context = {
                                    "error_message": f"Un problème a été détecté dans la base de données: {str(e)}"
                                }
                    except ValueError as ve:
                        template = loader.get_template("polls/page_error.html")
                        context = {"error_message": str(ve)}
                    except Exception as e:
                        template = loader.get_template("polls/page_error.html")
                        context = {
                            "error_message": f"Un problème a été détecté dans la base de données: {str(e)}"
                        }

                    return redirect("upload_students")
                else:
                    print("Form errors:", form.errors)
            else:
                form = ClientCSVUploadForm()

            return redirect("annuaire")
        except ValueError as ve:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": str(ve)}
        except Exception as e:
            template = loader.get_template("polls/page_error.html")
            context = {
                "error_message": f"Un problème a été détecté dans la base de données: {str(e)}"
            }
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))
    # return render(request, 'polls/annuaire.html', {'form': form})


def upload_etudes(request):
    if request.user.is_authenticated:
        # try:
        if request.method == "POST":
            form = EtudeCSVUploadForm(request.POST, request.FILES)
            print("one")

            if form.is_valid():
                csv_file = request.FILES.get("csv_file_etudes")
                print("two")

                # Check if the file is a CSV
                if not csv_file.name.endswith(".csv"):
                    raise ValueError("Ce n'est pas un csv")

                try:
                    # Decode the uploaded file and read its content with correct delimiter
                    data = csv_file.read().decode("utf-8")
                    print("three")
                    # Use csv.Sniffer to detect the delimiter
                    sniffer = csv.Sniffer()
                    detected_dialect = sniffer.sniff(data)
                    delimiter = detected_dialect.delimiter

                    # Read the file using the detected delimiter
                    reader = csv.reader(StringIO(data), delimiter=delimiter)
                    # Skip the header row if present
                    header = next(reader, None)

                    # Check if header matches the expected columns
                    if len(header) != 12:
                        raise ValueError(
                            "Le fichier csv doit contenir 12 colonnes : titre, ref, description, problematique, debut, nb_JEH, montant_HT_phases, frais_dossier, mandat, departement, remarque, fin_etude"
                        )

                    # Iterate through each row in the CSV
                    for row in reader:
                        if len(row) != 12:
                            raise ValueError(f"Un problème à la ligne {row}")

                        # Assuming the CSV columns are: titre, first_name, last_name, mail, phone_number, rue, ville, code_postal, pays

                        try:
                            (
                                titre,
                                ref,
                                description,
                                problematique,
                                debut,
                                nb_JEH,
                                montant_HT_phases,
                                frais_dossier,
                                mandat,
                                departement,
                                remarque,
                                fin_etude,
                            ) = row
                            print("four")
                            print(nb_JEH, montant_HT_phases)
                            je = request.user.je
                            etude, created = EtudeImportee.objects.get_or_create(
                                je=je,
                                ref=ref,
                                titre=titre,
                                description=description,
                                problematique=problematique,
                                remarque=remarque,
                            )
                            print(ref)
                            print(etude.id)
                            etude.montant_HT_phases = montant_HT_phases
                            etude.nb_JEH = nb_JEH

                            if fin_etude:
                                date_end = datetime.strptime(
                                    fin_etude, "%d/%m/%Y"
                                ).date()
                                print(date_end)
                                etude.fin_etude = date_end

                            if debut:
                                date_deb = datetime.strptime(debut, "%d/%m/%Y").date()
                                etude.debut = date_deb
                            etude.save()
                            """
                                if fin_etude:
                                    date_end=None
                                    try:
                                        date_end = datetime.strptime(fin_etude, '%d/%m/%Y').date()
                                    except ValueError:
                                        pass
                                    if date_end:
                                        etude.fin_etude=date_end
                                
                                if debut:
                                    date_deb=None
                                    try:
                                        date_deb = datetime.strptime(debut, '%d/%m/%Y').date()
                                    except ValueError:
                                        pass
                                    if date_deb:
                                        etude.debut=date_deb
                                
                                
                                dico_mandat={"M026":1,"M025":1,"M027":1}
                                if mandat dict(EtudeImportee.Mandat.choices):  
                                    etude.mandat = mandat
                                if departement dict(EtudeImportee.Departement.choices):  
                                    etude.departement = departement
                                
                          
                                try:
                                    nb_JEH = int(nb_JEH)
                                    etude.nb_JEH
                                except ValueError:
                                    pass
                                if isinstance(nb_JEH, int):
                                    etude.nb_JEH =nb_JEH
                                
                                try:
                                    montant_HT_phases = int(montant_HT_phases)
                                    etude.montant_HT_phases
                                except ValueError:
                                    pass
                                if isinstance(montant_HT_phases, int):
                                    etude.montant_HT_phases =montant_HT_phases
                                
                                try:
                                    frais_dossier = int(frais_dossier)
                                    etude.frais_dossier
                                except ValueError:
                                    pass
                                if isinstance(frais_dossier, int):
                                    etude.frais_dossier =frais_dossier
                                
                                etude.save()
                                """

                        except ValueError as ve:
                            template = loader.get_template("polls/page_error.html")
                            context = {"error_message": str(ve)}
                        except Exception as e:
                            template = loader.get_template("polls/page_error.html")
                            context = {
                                "error_message": f"Un problème a été détecté dans la base de données: {str(e)}"
                            }
                except ValueError as ve:
                    template = loader.get_template("polls/page_error.html")
                    context = {"error_message": str(ve)}
                except Exception as e:
                    template = loader.get_template("polls/page_error.html")
                    context = {
                        "error_message": f"Un problème a été détecté dans la base de données: {str(e)}"
                    }

                print("Etudes have been successfully added!")
                return redirect("upload_students")
        else:
            form = ClientCSVUploadForm()

        return redirect("annuaire")
        # except ValueError as ve:
        template = loader.get_template("polls/page_error.html")
        context = {"error_message": str(ve)}
        # except Exception as e:
        template = loader.get_template("polls/page_error.html")
        context = {
            "error_message": f"Un problème a été détecté dans la base de données: {str(e)}"
        }
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))
    # return render(request, 'polls/annuaire.html', {'form': form})


def update_etude(request, id):
    if request.user.is_authenticated:
        etude = Etude.objects.get(id=id)

        if request.method == "POST":
            suivi_document = etude.suivi_document  # Get the existing suivi_document

            if "delete_document_name" in request.POST:
                document_name = request.POST["delete_document_name"]
                # Perform delete logic, e.g., removing document by name
                if document_name in etude.suivi_document:
                    del etude.suivi_document[document_name]
                    etude.suivi_document = suivi_document
                etude.save()
                return redirect("index")

            # Loop through the keys in suivi_document and update both status and date
            for key in suivi_document.keys():
                new_status = request.POST.get(f"suivi_document_{key}_status")
                new_date = request.POST.get(f"suivi_document_{key}_date")
                new_remarque = request.POST.get(f"suivi_document_{key}_remarque")
                if new_status:
                    suivi_document[key]["status"] = new_status
                if new_date:
                    suivi_document[key]["date"] = new_date
                else:
                    suivi_document[key]["date"] = None

                if new_remarque:
                    suivi_document[key]["remarque"] = new_remarque
            etude.suivi_document = suivi_document
            etude.save()
            suivi_document = etude.suivi_document
            # Check if the form is adding a new document (new_document_name is filled)
            new_document_name = request.POST.get("new_document_name")
            new_document_status = request.POST.get("new_document_status")
            new_document_date = request.POST.get("new_document_date")
            new_remarque_name = request.POST.get("new_remarque_name")

            if new_document_name and new_document_status:
                suivi_document[new_document_name] = {
                    "status": new_document_status,
                    "date": new_document_date,
                    "remarque": new_remarque_name,
                }

            etude.suivi_document = (
                suivi_document  # Update the dictionary with new entries
            )
            etude.save()
            # Save the changes

            return redirect("index")  # Redirect after saving

        # Render the template with the existing data (in case you need GET logic)
        return render(request, "index.html")
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def generate_facture_pdf(request, id_facture):
    user = request.user
    if user.is_authenticated:
        try:
            # Fetch the required facture data
            facture = Facture.objects.get(id=id_facture)
            etude = facture.etude
            client = etude.client
            phases = Phase.objects.filter(etude=etude).order_by("numero")

            res = facture.montant_TTC()
            facture.date_emission = timezone.now().strftime("%d/%m/%Y")
            date_30 = timezone.now() + timedelta(30)
            facture.date_echeance = date_30.strftime("%d/%m/%Y")
            logo_url = user.je.logo.url
            nb_JEH = 0
            bdc = facture.bdc()

            if bdc:
                nb_JEH = bdc.nb_JEH()
                montant_HT_totale = bdc.montant_HT_total
            else:
                nb_JEH = etude.nb_JEH()
                montant_HT_totale = etude.montant_HT_total()

            avenante_ref = None

            avenants_signes = AvenantConventionEtude.objects.filter(
                date_signature__isnull=False
            )

            if etude.type_convention == "Convention cadre":
                bdc = facture.bdc()
            else:
                ce = etude.convention()
                if ce:
                    avenants_signes = AvenantConventionEtude.objects.filter(
                        ce=ce, date_signature__isnull=False
                    ).order_by("numero")
                    avenante_ref = avenants_signes.last()
                else:
                    ce = f"{etude.ref()}ce"

            # Context for the invoice
            context = {
                "facture": facture,
                "ref": facture.ref(),
                "etude": etude,
                "client": client,
                "phases": phases,
                "res": res,
                "date_emission": facture.date_emission,
                "date_echeance": facture.date_echeance,
                "logo_url": logo_url,
                "bdc": bdc,
                "avenante_ref": avenante_ref,
                "nb_JEH": nb_JEH,
                "montant_HT_totale": montant_HT_totale,
            }

            # Log context before rendering
            logger.debug("Rendering HTML template")
            html_string = render_to_string("polls/facpdfhtml.html", context)

            # Log HTML generation
            logger.info("HTML template rendered successfully")
            logger.debug(f"HTML content length: {len(html_string)} characters")

            # Generate PDF
            logger.info("Generating PDF")

            pdf_file = HTML(string=html_string).write_pdf()

            # Prepare filename
            date_emission = datetime.datetime.strptime(
                facture.date_emission, "%d/%m/%Y"
            ).year
            refFA = f"FA{date_emission % 100}{facture.numero_facture:03d}"

            logger.info(f"PDF generated. Filename: {refFA}.pdf")

            # Serve the PDF
            response = HttpResponse(pdf_file, content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="{refFA}.pdf"'

            logger.success("PDF generation and download successful")
            return response

        except Exception as e:
            return HttpResponse(f"Le PDF n'a pas pu être généré : {str(e)}", status=500)

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def facture(request, id_facture):
    user = request.user
    if user.is_authenticated:
        try:
            facture = Facture.objects.get(id=id_facture)
            print(f"facture.montant_TVA: {facture.montant_TVA()}")
            etude = facture.etude
            # etude = {'type_convention': etude.type_convention, }
            client = etude.client
            phases = Phase.objects.filter(etude=etude).order_by("numero")
            res = facture.montant_TTC()
            facture.date_emission = timezone.now().date()
            date_emission = timezone.now().date().strftime("%d/%m/%Y")
            date_30 = timezone.now() + timedelta(30)
            facture.date_echeance = date_30.date()
            date_echeance = date_30.date().strftime("%d/%m/%Y")
            nb_JEH = 0
            bdc = facture.bdc()
            montant_HT_totale = etude.montant_HT_total()
            if bdc:
                nb_JEH = bdc.nb_JEH()
                montant_HT_totale = bdc.montant_HT_total
            else:
                nb_JEH = etude.nb_JEH()

            avenante_ref = None

            avenants_signes = AvenantConventionEtude.objects.filter(
                date_signature__isnull=False
            )

            if etude.type_convention == "Convention cadre":
                bdc = facture.bdc()
            else:
                ce = etude.convention()
                if ce:
                    avenants_signes = AvenantConventionEtude.objects.filter(
                        ce=ce, date_signature__isnull=False
                    ).order_by("numero")
                    avenante_ref = avenants_signes.last()
            context = {
                "logo_url": user.je.logo.url,
                "facture": facture,
                "etude": etude,
                "client": client,
                "phases": phases,
                "res": res,
                "date_emission": facture.date_emission,
                "date_echeance": facture.date_echeance,
                "bdc": bdc,
                "avenante_ref": avenante_ref,
                "nb_JEH": nb_JEH,
                "montant_HT_totale": montant_HT_totale,
                "date_emission": date_emission,
                "date_echeance": date_echeance,
            }
            template = loader.get_template("polls/facpdf.html")
            facture.save(id_etude=etude.id)

        except Exception as e:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": "Erreur dans l'identification de la facture."}
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def ndf(request):
    if request.user.is_authenticated:
        try:
            template = loader.get_template("polls/ndf.html")
            context = {}
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
            eleve = Student.objects.get(id=iD)
            template = loader.get_template("polls/ba.html")
            president = {"first_name": "Thomas", "last_name": "Debray"}
            context = {"eleve": eleve, "president": president}
        except:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": "Erreur dans l'identification de la mission."}
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def stat_KPI_2(request):
    if request.user.is_authenticated:
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if start_date and end_date:
            start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d").replace(
                tzinfo=pytz.UTC
            )
            end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").replace(
                tzinfo=pytz.UTC
            )
        else:
            now = timezone.now()
            end_date_obj = (now + timedelta(days=150)).date()
            start_date_obj = (now - timedelta(days=100)).date()
            start_date = start_date_obj.strftime("%Y-%m-%d")
            end_date = end_date_obj.strftime("%Y-%m-%d")

        # Filtrer les études en fonction des dates
        etudes = Etude.objects.filter(
            je=request.user.je, debut__gte=start_date_obj, debut__lte=end_date_obj
        ).order_by("debut")
        # Calculer les montants par mois et les labels
        date_labels = []
        cumulated_CA = []
        current_month = start_date_obj.month
        current_year = start_date_obj.year
        current_sum = 0
        total_sum = 0

        ca_026 = 0  # ca du mandat 026
        ca_026_cutoff = 0
        ca_en_nego = 0
        nb_etudes_ec = {0: 0, 1: 0}
        nb_etude_ed = {0: 0, 1: 0}
        nb_etudes_term_026 = {0: 0, 1: 0}
        dictionaire_dep_eleve = {}
        nb_intervenants_026 = 0

        dico_nb_intervenants_diff_026 = {}
        taux_ouverture = 0
        retributions_etudes026 = 0
        nb_etudes_026_avec_interv = 0
        dico_genre_inter = {"M.": 0, "Mme": 0}
        dico_ca_typeentreprise = {}
        dico_ca_departement = {}
        dico_ca_secteur = {}

        liste_etudes_ec_term = []

        dico_devis_envoye = {}  # key : devis , valeurs : date et si la mission a été signé
        devis_envoye = Devis.objects.filter(
            etude__in=etudes, date_signature__isnull=False
        )

        # TODO : optimise this boucle for
        for devis in devis_envoye:
            dico_devis_envoye[devis.id] = {
                "date": f"{devis.date_signature.month}-{devis.date_signature.year}",
                "mission": 0,
            }
            etude = devis.etude
            if etude.status == "TERMINEE" or etude.status == "EN_COURS":
                dico_devis_envoye[devis.id]["mission"] = 1

        dico_suivi_devis = {}
        date_ajd = datetime.datetime.now()
        derniere_date = date_ajd.strftime("%m-%Y")
        for devis in dico_devis_envoye:
            mois = dico_devis_envoye[devis]["date"]
            if int(mois[3:]) >= int(derniere_date[3:]) and int(mois[0:2]) >= int(
                derniere_date[0:2]
            ):
                derniere_date = mois
            if mois in dico_suivi_devis:
                dico_suivi_devis[mois]["envoyés"] += 1
                dico_suivi_devis[mois]["signées"] += dico_devis_envoye[devis]["mission"]
            else:
                dico_suivi_devis[mois] = {}
                dico_suivi_devis[mois]["envoyés"] = 1
                dico_suivi_devis[mois]["signées"] = dico_devis_envoye[devis]["mission"]
        if derniere_date:
            if derniere_date[0:2] == "12":
                derniere_date = f"01-{int(derniere_date[3:]) + 1}"
            else:
                derniere_date = (
                    f"{(int(derniere_date[0:2]) + 1):02}-{derniere_date[3:]}"
                )
            dico_suivi_devis[derniere_date] = {"envoyés": 0, "signées": 0}

        date_ajd = datetime.datetime.now()
        derniere_date = date_ajd.strftime("%m-%Y")
        dico_avenants_mois_ce = {}  # key : devis , valeurs : date et si la mission a été signé
        avenants_signes = AvenantConventionEtude.objects.filter(
            date_signature__isnull=False, ce__etude__in=etudes
        )
        for avenant in avenants_signes:
            mois = f"{avenant.date_signature.month}-{avenant.date_signature.year}"
            if int(mois[3:]) >= int(derniere_date[3:]) and int(mois[0:2]) >= int(
                derniere_date[0:2]
            ):
                derniere_date = mois
            if mois in dico_avenants_mois_ce:
                dico_avenants_mois_ce[mois]["avenants"] += 1
                if avenant.avenant_delais:
                    dico_avenants_mois_ce[mois]["délais"] += 1
                if avenant.avenant_budget:
                    dico_avenants_mois_ce[mois]["budget"] += 1
            else:
                dico_avenants_mois_ce[mois] = {"avenants": 1, "délais": 0, "budget": 0}
                if avenant.avenant_delais:
                    dico_avenants_mois_ce[mois]["délais"] += 1
                if avenant.avenant_budget:
                    dico_avenants_mois_ce[mois]["budget"] += 1

        if derniere_date:
            if derniere_date[0:2] == "12":
                derniere_date = f"01-{int(derniere_date[3:]) + 1}"
            else:
                derniere_date = (
                    f"{(int(derniere_date[0:2]) + 1):02}-{derniere_date[3:]}"
                )
            dico_avenants_mois_ce[derniere_date] = {
                "avenants": 0,
                "délais": 0,
                "budget": 0,
            }

        for etude in etudes:
            if etude.status == "EN_COURS" or etude.status == "TERMINEE":
                liste_etudes_ec_term.append(etude)
            if (
                etude.status == "EN_COURS" or etude.status == "TERMINEE"
            ) and etude.mandat == "026":
                ca_026 += etude.montant_HT_total()
                if etude.status == "TERMINEE":
                    ca_026_cutoff += etude.montant_HT_total()
                    nb_etudes_term_026[0] += 1
                    nb_etudes_term_026[1] += etude.montant_HT_total()
                else:
                    if etude.fin() is not None and etude.fin() < date(2025, 5, 1):
                        ca_026_cutoff += etude.montant_HT_total()
                    elif etude.duree_semaine():
                        ca_026_cutoff += (
                            etude.montant_HT_total()
                            * ((date(2025, 5, 1) - etude.debut).days / 7)
                            / etude.duree_semaine()
                        )

            elif (
                etude.status == "EN_COURS" or etude.status == "TERMINEE"
            ) and etude.mandat == "025":
                if etude.debut and etude.debut > date(2024, 5, 1):
                    ca_026_cutoff += etude.montant_HT_total()
                elif etude.fin() is not None and etude.fin() > date(2024, 5, 1):
                    ca_026_cutoff += (
                        etude.montant_HT_total()
                        * ((etude.fin() - date(2024, 5, 1)).days / 7)
                        / etude.duree_semaine()
                    )
            if etude.status == "EN_NEGOCIATION":
                ca_en_nego += etude.montant_HT_total()
                nb_etude_ed[0] += 1
                nb_etude_ed[1] += etude.montant_HT_total()
            if etude.status == "EN_COURS":
                nb_etudes_ec[0] += 1
                nb_etudes_ec[1] += etude.montant_HT_total()
            if etude.mandat == "026":
                if etude.status == "EN_COURS" or etude.status == "TERMINEE":
                    if etude.get_li_students():
                        nb_etudes_026_avec_interv += 1
                        for student in etude.get_li_students():
                            dico_genre_inter[student.titre] += 1
                            nb_intervenants_026 += 1
                            dico_nb_intervenants_diff_026[
                                f"{student.first_name}{student.last_name}"
                            ] = 1
                            if student.departement in dictionaire_dep_eleve:
                                dictionaire_dep_eleve[student.departement] += 1
                            else:
                                dictionaire_dep_eleve[student.departement] = 1

                            assignations = list(
                                AssignationJEH.objects.filter(
                                    eleve=student, phase__etude=etude
                                )
                            )
                            remuneration = sum(
                                assignment.retribution_brute_totale()
                                for assignment in assignations
                            )
                            if student.is_member():
                                taux_ouverture += remuneration
                            retributions_etudes026 += remuneration

        dico_CA_mois = {}
        date_ajd = datetime.datetime.now()
        derniere_date_CA = date_ajd.strftime("%m-%Y")

        for etude in liste_etudes_ec_term:
            if etude.type_convention == "Convention d'étude":
                if etude.debut:
                    mois = etude.debut.strftime("%m-%Y")
                else:
                    date_now = datetime.datetime.now()
                    mois = date_now.strftime("%m-%Y")

                if int(mois[3:]) >= int(derniere_date_CA[3:]) and int(mois[0:2]) >= int(
                    derniere_date_CA[0:2]
                ):
                    derniere_date_CA = mois
                print(etude.numero)
                if mois in dico_CA_mois:
                    dico_CA_mois[mois]["CA"] += etude.montant_HT_total()

                else:
                    dico_CA_mois[mois] = {}
                    dico_CA_mois[mois]["CA"] = etude.montant_HT_total()
            else:
                bdcs = etude.get_bon_commandes()
                print(bdcs)
                prems = True
                for bdc in bdcs:
                    if bdc.debut:
                        mois = bdc.debut.strftime("%m-%Y")

                        if int(mois[3:]) >= int(derniere_date_CA[3:]) and int(
                            mois[0:2]
                        ) >= int(derniere_date_CA[0:2]):
                            derniere_date_CA = mois
                        print(etude.numero)
                        if mois not in dico_CA_mois:
                            dico_CA_mois[mois] = {"CA": 0}

                        if prems:
                            dico_CA_mois[mois]["CA"] += (
                                bdc.montant_HT_total() + etude.frais_dossier
                            )
                            prems = False
                        else:
                            dico_CA_mois[mois]["CA"] += bdc.montant_HT_total()

        if derniere_date_CA:
            if derniere_date_CA[0:2] == "12":
                derniere_date_CA = f"01-{int(derniere_date_CA[3:]) + 1}"
            else:
                derniere_date_CA = (
                    f"{(int(derniere_date_CA[0:2]) + 1):02}-{derniere_date_CA[3:]}"
                )
            dico_CA_mois[derniere_date_CA] = {"CA": 0}

        for etude in liste_etudes_ec_term:
            if etude.client:
                secteur = etude.client.get_secteur_display()
                if secteur in dico_ca_secteur:
                    dico_ca_secteur[secteur] += etude.montant_HT_total()
                else:
                    dico_ca_secteur[secteur] = etude.montant_HT_total()

                if etude.client.get_type_display() in dico_ca_typeentreprise:
                    dico_ca_typeentreprise[etude.client.get_type_display()] += (
                        etude.montant_HT_total()
                    )
                else:
                    dico_ca_typeentreprise[etude.client.get_type_display()] = (
                        etude.montant_HT_total()
                    )
                departements = etude.departement
                for depart in departements:
                    if depart in dico_ca_departement:
                        dico_ca_departement[depart] += etude.montant_HT_total()
                    else:
                        dico_ca_departement[depart] = etude.montant_HT_total()

        bar_chart_CA = {}
        for etude in liste_etudes_ec_term:
            if etude.debut:
                etude_month = etude.debut.month
                etude_year = etude.debut.year
                if etude_year in bar_chart_CA:
                    if etude_month in bar_chart_CA[etude_year]:
                        bar_chart_CA[etude_year][etude_month] += (
                            etude.montant_HT_total()
                        )
                    else:
                        bar_chart_CA[etude_year][etude_month] = etude.montant_HT_total()
                else:
                    bar_chart_CA[etude_year] = {etude_month: etude.montant_HT_total()}

        for etude in liste_etudes_ec_term:
            if etude.debut:
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

        nb_intervenants_diff_026 = len(dico_nb_intervenants_diff_026)
        if retributions_etudes026 > 0:
            taux_ouverture = 1 - taux_ouverture / retributions_etudes026
        else:
            taux_ouverture = 0
        if nb_etudes_026_avec_interv > 0:
            retrib_moye_etude = retributions_etudes026 / nb_etudes_026_avec_interv
        else:
            retrib_moye_etude = 0
        if nb_intervenants_026 > 0:
            retrib_moye_etudiant = retributions_etudes026 / nb_intervenants_026
        else:
            retrib_moye_etudiant = 0
        # Ajouter les données pour le dernier mois
        date_labels.append(f"{current_year}-{current_month:02d}")
        total_sum += current_sum

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
        if cumulated_CA:
            chiffre_affaire_total = cumulated_CA[-1]
        else:
            chiffre_affaire_total = 0
        chiffre_affaire_par_departement = calculate_chiffre_affaire_par_departement(
            user_je
        )
        nb_ca_etudes = nb_etudes_ed_ec_term(user_je)
        (
            repartition_CA_etudes,
            repartition_nb_etudes,
            totale_CA_ecterm,
            totale_nb_ecterm,
        ) = repartition_CA_etudes_ec_term(liste_etudes_ec_term)
        chiffre_affaire_par_type = calculate_chiffre_affaire_par_type(user_je)
        chiffre_affaire_par_secteur = calculate_chiffre_affaire_par_secteur(user_je)
        nombre_eleve = Student.objects.filter(je=user_je).count()
        nombre_client = Client.objects.filter(je=user_je).count()
        nombre_etude = Etude.objects.filter(je=user_je).count()

        dictionnaire_CA_par_dept = {
            "IMI": chiffre_affaire_par_departement[0],
            "GCC": chiffre_affaire_par_departement[1],
            "GMM": chiffre_affaire_par_departement[2],
            "SEGF": chiffre_affaire_par_departement[3],
            "VET": chiffre_affaire_par_departement[4],
            "1A": chiffre_affaire_par_departement[5],
            "GI": chiffre_affaire_par_departement[6],
            "AUTRE": chiffre_affaire_par_departement[7],
        }

        dictionnaire_CA_par_secteur = {
            "INDUSTRIE": chiffre_affaire_par_secteur[0],
            "DISTRIBUTION": chiffre_affaire_par_secteur[1],
            "SECTEUR_PUBLIC": chiffre_affaire_par_secteur[2],
            "CONSEIL": chiffre_affaire_par_secteur[3],
            "TRANSPORT": chiffre_affaire_par_secteur[4],
            "NUMERIQUE": chiffre_affaire_par_secteur[5],
            "BTP": chiffre_affaire_par_secteur[6],
            "AUTRE": chiffre_affaire_par_secteur[7],
        }

        dictionnaire_CA_par_type = {
            "GRANDE_ENTREPRISE": chiffre_affaire_par_type[0],
            "SECTEUR_PUBLIC": chiffre_affaire_par_type[1],
            "START_UP_ET_TPE": chiffre_affaire_par_type[2],
            "PME": chiffre_affaire_par_type[3],
            "ETI": chiffre_affaire_par_type[4],
            "ASSOCIATION": chiffre_affaire_par_type[5],
        }

        # Définition des couleurs pour chaque département
        departements_colors = {
            "IMI": "#FF6633",
            "GCC": "#FFB399",
            "GMM": "#FF33FF",
            "SEGF": "#FFFF99",
            "VET": "#00B3E6",
            "1A": "#E6B333",
            "GI": "#4682B4",
            "AUTRE": "#3366E6",
        }

        # Définition des couleurs pour chaque secteur
        secteurs_colors = {
            "INDUSTRIE": "#0071C5",
            "DISTRIBUTION": "#FFD700",
            "SECTEUR_PUBLIC": "#DC143C",
            "CONSEIL": "#008B8B",
            "TRANSPORT": "#B8860B",
            "NUMERIQUE": "#4682B4",
            "BTP": "#DAA520",
            "AUTRE": "#808080",
        }

        types_colors = {
            "GRANDE_ENTREPRISE": "#4A90E2",  # Bleu lumineux
            "SECTEUR_PUBLIC": "#D0021B",  # Rouge vif
            "START_UP_ET_TPE": "#7B8D8E",  # Gris ardoise
            "PME": "#F5A623",  # Orange safran
            "ETI": "#8B572A",  # Brun cuir
            "ASSOCIATION": "#50E3C2",  # Turquoise clair
        }

        pourcentage_par_departement = {
            dept: ca / (chiffre_affaire_total + 1e-12) * 100
            for dept, ca in dictionnaire_CA_par_dept.items()
        }
        pourcentage_par_secteur = {
            sect: ca / (chiffre_affaire_total + 1e-12) * 100
            for sect, ca in dictionnaire_CA_par_secteur.items()
        }
        pourcentage_par_type = {
            sect: ca / (chiffre_affaire_total + 1e-12) * 100
            for sect, ca in dictionnaire_CA_par_type.items()
        }

        if nb_etudes_026_avec_interv > 0:
            moyen_int_etude = nb_intervenants_026 / nb_etudes_026_avec_interv
        else:
            moyen_int_etude = 0

        liste_mois = [mois for mois in dico_CA_mois]
        liste_CA_mois = [dico_CA_mois[mois]["CA"] for mois in liste_mois]
        print("liste_mois", liste_mois, liste_CA_mois)
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
            "notification_list": notification_list,
            "notification_count": notification_count,
            "chiffre_affaires": chiffres_affaires,
            "start_date": start_date,
            "end_date": end_date,
            "nb_ca_etudes": nb_ca_etudes,
            "repartition_CA_etudes": repartition_CA_etudes,
            "repartition_nb_etudes": repartition_nb_etudes,
            "ca_026": ca_026,
            "ca_026_cutoff": ca_026_cutoff,
            "ca_potentiel": ca_en_nego + ca_026_cutoff,
            "nb_etudes_ec": nb_etudes_ec,
            "nb_etude_ed": nb_etude_ed,
            "dictionaire_dep_eleve": dictionaire_dep_eleve,
            "nb_intervenants_diff_026": nb_intervenants_diff_026,
            "nb_intervenants_026": nb_intervenants_026,
            "taux_ouverture": taux_ouverture * 100,
            "retrib_moye_etude": retrib_moye_etude,
            "retrib_moye_etudiant": retrib_moye_etudiant,
            "retributions_etudes026": retributions_etudes026,
            "moyen_int_etude": moyen_int_etude,
            "dico_genre_inter": dico_genre_inter,
            "nb_etudes_term_026": nb_etudes_term_026,
            "totale_nb_ecterm": totale_nb_ecterm,
            "totale_CA_ecterm": totale_CA_ecterm,
            "dico_ca_typeentreprise": dico_ca_typeentreprise,
            "dico_ca_departement": dico_ca_departement,
            "dico_ca_secteur": dico_ca_secteur,
            "bar_chart_CA": bar_chart_CA,
            "dico_suivi_devis": dico_suivi_devis,
            "dico_avenants_mois_ce": dico_avenants_mois_ce,
            "dico_CA_mois": dico_CA_mois,
            "liste_mois": liste_mois,
            "liste_CA_mois": liste_CA_mois,
        }

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def renvoyer_donnees(champs_x, champs_y, donnes_entrees):
    donnees_sorties = {}
    for objet in donnes_entrees:
        if champs_y == "nombre":
            y = 1
        else:
            y = objet[champs_y]
        xs = objet[champs_x]
        if isinstance(xs, str):
            xs = [xs]
        for x in xs:
            if x not in donnees_sorties:
                donnees_sorties[x] = 0
            donnees_sorties[x] += y

    return donnees_sorties


def stat_KPI(request):
    try:
        if request.user.is_authenticated:
            je_user = request.user.je
            etudes = Etude.objects.filter(je=je_user).order_by("debut")
            etudes_dico = {"ed": [], "ec": [], "term": []}
            liste_infos = [
                "debut",
                "status",
                "mandat",
                "departement",
                "type_convention",
            ]
            dico_id_etude_status = {}
            for etude in etudes:
                id_etude = etude.id
                dico_temp = {}
                for champs in liste_infos:
                    dico_temp[champs] = getattr(etude, champs, None)
                dico_temp["ca"] = etude.montant_HT_total()
                dico_temp["id"] = id_etude
                dico_temp["fin"] = etude.fin()
                if etude.client:
                    client = etude.client
                    type_entreprise = client.get_type_display()
                    secteur = client.get_secteur_display()
                else:
                    client = "pas de client"
                    type_entreprise = "pas de type"
                    secteur = "pas de secteur"
                dico_temp["client"] = client
                dico_temp["type_entreprise"] = type_entreprise
                dico_temp["secteur"] = secteur
                if etude.raison_contact:
                    dico_temp["raison_contact"] = etude.get_raison_contact_display()
                else:
                    dico_temp["raison_contact"] = "pas renseigné"

                if etude.status == "EN_NEGOCIATION":
                    etudes_dico["ed"].append(dico_temp)
                    dico_id_etude_status[id_etude] = [
                        "ed",
                        dico_temp["type_convention"],
                    ]
                elif etude.status == "EN_COURS":
                    etudes_dico["ec"].append(dico_temp)
                    dico_id_etude_status[id_etude] = [
                        "ec",
                        dico_temp["type_convention"],
                    ]
                elif etude.status == "TERMINEE":
                    etudes_dico["term"].append(dico_temp)
                    dico_id_etude_status[id_etude] = [
                        "term",
                        dico_temp["type_convention"],
                    ]

            bdcs = BonCommande.objects.filter(etude__je=je_user)
            liste_infos = ["id", "debut", "fin_bdc", "numero"]
            bdcs_etudes_dico = {}
            for bon in bdcs:
                etude_id = bon.etude.id
                if etude_id not in bdcs_etudes_dico:
                    bdcs_etudes_dico[etude_id] = []
                dico_temp = {
                    "id": bon.id,
                    "debut": bon.debut,
                    "fin": bon.fin_bdc,
                    "ca": bon.montant_HT_total(),
                }
                bdcs_etudes_dico[etude_id].append(dico_temp)

            devis = Devis.objects.filter(etude__je=je_user)
            devis_dico = []
            for devi in devis:
                etude_id = devi.etude.id
                date = devi.date_signature
                devis_dico.append({"etude": etude_id, "date": date})

            avenants_signes = AvenantConventionEtude.objects.filter(
                date_signature__isnull=False, ce__etude__je=je_user
            )
            avenants_ce_dico = {}

            for avenant in avenants_signes:
                date = avenant.date_signature.strftime("%m-%Y")
                if date not in avenants_ce_dico:
                    avenants_ce_dico[date] = {0: 0, 1: 0, 2: 0}
                avenants_ce_dico[date][0] += 1
                if avenant.avenant_delais:
                    avenants_ce_dico[date][1] += 1
                if avenant.avenant_budget:
                    avenants_ce_dico[date][2] += 1

            dates = [datetime.datetime.strptime(m, "%m-%Y") for m in avenants_ce_dico]
            start_date, end_date = (min(dates), max(dates)) if dates else (None, None)
            liste_date_avenants = []
            current_date = start_date

            while current_date <= end_date:
                date_ajou = current_date.strftime("%m-%Y")
                liste_date_avenants.append(date_ajou)
                if date_ajou not in avenants_ce_dico:
                    avenants_ce_dico[date_ajou] = {0: 0, 1: 0, 2: 0}
                current_date += relativedelta(months=1)
            liste_nb_avenants = [
                avenants_ce_dico[mois][0] for mois in liste_date_avenants
            ]
            liste_nb_avenants_del = [
                avenants_ce_dico[mois][1] for mois in liste_date_avenants
            ]
            liste_nb_avenants_bud = [
                avenants_ce_dico[mois][2] for mois in liste_date_avenants
            ]

            assi_JEHs = AssignationJEH.objects.filter(eleve__je=je_user)
            assi_JEHs_dico_temp = {}
            assi_JEHs_dico = []
            for assignation in assi_JEHs:
                eleve = assignation.eleve
                eleve_id = eleve.id
                etude_id = assignation.phase.etude.id
                dico_temp = {
                    "titre": eleve.titre,
                    "departement": eleve.get_departement_display(),
                    "promotion": eleve.get_promotion_display(),
                    "retribution": assignation.retribution_brute_totale(),
                    "pourcentage": assignation.pourcentage_retribution,
                    "status_mission": assignation.phase.etude.get_status_display(),
                    "eleve_id": eleve_id,
                    "membre": eleve.is_member(),
                }
                if dico_id_etude_status[etude_id][1] == "Convention cadre":
                    etude_id = f"{etude_id}_{assignation.phase.bon().id}"
                if etude_id not in assi_JEHs_dico_temp:
                    assi_JEHs_dico_temp[etude_id] = {}
                if eleve_id not in assi_JEHs_dico_temp[etude_id]:
                    assi_JEHs_dico_temp[etude_id][eleve_id] = []
                assi_JEHs_dico_temp[etude_id][eleve_id].append(dico_temp)

            for etude in assi_JEHs_dico_temp:
                for eleve in assi_JEHs_dico_temp[etude]:
                    liste_assi = assi_JEHs_dico_temp[etude][eleve]
                    dico_temp = {
                        "titre": liste_assi[0]["titre"],
                        "departement": liste_assi[0]["departement"],
                        "promotion": liste_assi[0]["promotion"],
                        "retribution": sum(elt["retribution"] for elt in liste_assi),
                        "status_mission": liste_assi[0]["status_mission"],
                        "eleve_id": liste_assi[0]["eleve_id"],
                        "membre": liste_assi[0]["membre"],
                    }
                    assi_JEHs_dico.append(dico_temp)

            graphe_CA_mois = {}
            etudes_ecterm = etudes_dico["ec"] + etudes_dico["term"]
            for etude in etudes_ecterm:
                if etude["type_convention"] == "Convention d'étude":
                    debut_mois = etude["debut"]
                    if debut_mois:
                        debut_m = debut_mois.strftime("%m-%Y")
                        if debut_m not in graphe_CA_mois:
                            graphe_CA_mois[debut_m] = 0
                        graphe_CA_mois[debut_m] += etude["ca"]
                elif etude["type_convention"] == "Convention cadre":
                    id_etude = etude["id"]
                    for bon in bdcs_etudes_dico[id_etude]:
                        print("bon", bon)
                        debut_mois = bon["debut"]
                        if debut_mois:
                            debut_m = debut_mois.strftime("%m-%Y")
                            if debut_m not in graphe_CA_mois:
                                graphe_CA_mois[debut_m] = 0
                            graphe_CA_mois[debut_m] += bon["ca"]

            dates = [datetime.datetime.strptime(m, "%m-%Y") for m in graphe_CA_mois]
            start_date, end_date = min(dates), max(dates)
            liste_mois = []
            current_date = start_date

            while current_date <= end_date:
                date_ajou = current_date.strftime("%m-%Y")
                liste_mois.append(date_ajou)
                if date_ajou not in graphe_CA_mois:
                    graphe_CA_mois[date_ajou] = 0
                current_date += relativedelta(months=1)

            liste_CA_mois = [graphe_CA_mois[mois] for mois in liste_mois]

            dico_ca_departement = renvoyer_donnees("departement", "ca", etudes_ecterm)
            dico_ca_typeentreprise = renvoyer_donnees(
                "type_entreprise", "ca", etudes_ecterm
            )
            dico_ca_secteur = renvoyer_donnees("secteur", "ca", etudes_ecterm)
            dictionaire_dep_eleve = renvoyer_donnees(
                "departement", "nombre", assi_JEHs_dico
            )
            dico_genre_inter = renvoyer_donnees("titre", "nombre", assi_JEHs_dico)
            nb_etudes_ec = {
                0: len(etudes_dico["ec"]),
                1: sum(elt["ca"] for elt in etudes_dico["ec"]),
            }
            nb_etude_ed = {
                0: len(etudes_dico["ed"]),
                1: sum(elt["ca"] for elt in etudes_dico["ed"]),
            }
            nb_etudes_term_026 = {
                0: len(etudes_dico["term"]),
                1: sum(elt["ca"] for elt in etudes_dico["term"]),
            }
            ca_026 = sum(elt["ca"] for elt in etudes_ecterm if elt["mandat"] == "026")
            ca_026_cutoff = 0

            repartition_nb_etudes = {
                "en cours": len(etudes_dico["ec"]),
                "terminées": len(etudes_dico["term"]),
            }
            repartition_CA_etudes = {
                "en cours": nb_etudes_ec[1],
                "terminées": nb_etudes_term_026[1],
            }

            for etude in etudes_ecterm:
                ca_etude = etude["ca"]
                if etude["debut"] and etude["debut"] > datetime.date(2024, 5, 1):
                    if etude["fin"] and etude["fin"] > datetime.date(2025, 5, 1):
                        pourc = 1 - (etude["fin"] - datetime.date(2025, 5, 1)) / (
                            etude["fin"] - etude["debut"]
                        )
                        ca_026_cutoff += ca_etude * pourc
                    else:
                        ca_026_cutoff += ca_etude
                elif etude["debut"] and etude["debut"] < datetime.date(2024, 5, 1):
                    if etude["fin"] and etude["fin"] > datetime.date(2024, 5, 1):
                        pourc = (etude["fin"] - datetime.date(2024, 5, 1)) / (
                            etude["fin"] - etude["debut"]
                        )
                        ca_026_cutoff += ca_etude * pourc
                else:
                    ca_026_cutoff += ca_etude

            ca_en_nego = sum(elt["ca"] for elt in etudes_dico["ed"])

            nb_intervenants = len(assi_JEHs_dico)
            nb_intervenants_diffs = len({elt["eleve_id"]: 1 for elt in assi_JEHs_dico})
            moyenne_inter_mission = nb_intervenants / len(assi_JEHs_dico_temp)
            retributions_totales = sum(elt["retribution"] for elt in assi_JEHs_dico)
            retribution_moyenne_etude = retributions_totales / len(assi_JEHs_dico_temp)
            retribution_moyenne_etudiant = retributions_totales / nb_intervenants
            taux_ouverture = (
                1
                - sum(elt["retribution"] for elt in assi_JEHs_dico if elt["membre"])
                / retributions_totales
                if retributions_totales > 0
                else 1
            )

            start_date = request.GET.get("start_date")
            end_date = request.GET.get("end_date")

            infos_devis_envoyes = {}
            infos_devis_signes = {}
            for devi in devis_dico:
                if devi["date"]:
                    mois = devi["date"].strftime("%m-%Y")
                    if mois not in infos_devis_envoyes:
                        infos_devis_envoyes[mois] = 0
                    infos_devis_envoyes[mois] += 1
                    if (
                        dico_id_etude_status[devi["etude"]][0] == "ec"
                        or dico_id_etude_status[devi["etude"]][0] == "term"
                    ):
                        if mois not in infos_devis_signes:
                            infos_devis_signes[mois] = 0
                        infos_devis_signes[mois] += 1

            dates = [
                datetime.datetime.strptime(m, "%m-%Y") for m in infos_devis_envoyes
            ]
            start_date, end_date = min(dates), max(dates)
            liste_mois_devis = []
            current_date = start_date

            while current_date <= end_date:
                date_ajou = current_date.strftime("%m-%Y")
                liste_mois_devis.append(date_ajou)
                if date_ajou not in infos_devis_envoyes:
                    infos_devis_envoyes[date_ajou] = 0
                if date_ajou not in infos_devis_signes:
                    infos_devis_signes[date_ajou] = 0
                current_date += relativedelta(months=1)

            liste_devis_envo = [infos_devis_envoyes[mois] for mois in liste_mois_devis]
            liste_devis_sign = [infos_devis_signes[mois] for mois in liste_mois_devis]

            # Calcul des autres métriques
            liste_messages = Message.objects.filter(
                destinataire=request.user,
                read=False,
                date__range=(
                    timezone.now() - timezone.timedelta(days=20),
                    timezone.now(),
                ),
            ).order_by("date")
            message_count = liste_messages.count()
            liste_messages = liste_messages[:3]
            all_notifications = request.user.notifications.order_by("-date_effet")
            notification_list = [notif for notif in all_notifications if notif.active()]
            notification_count = len(notification_list)

            template = loader.get_template("polls/stat_KPI.html")
            context = {
                "liste_messages": liste_messages,
                "message_count": message_count,
                "notification_list": notification_list,
                "notification_count": notification_count,
                "start_date": start_date,
                "end_date": end_date,
                "ca_026": ca_026,
                "ca_026_cutoff": ca_026_cutoff,
                "ca_potentiel": ca_en_nego + ca_026_cutoff,
                "nb_etudes_ec": nb_etudes_ec,
                "nb_etude_ed": nb_etude_ed,
                "nb_etudes_term_026": nb_etudes_term_026,
                "dictionaire_dep_eleve": dictionaire_dep_eleve,
                "totale_nb_ecterm": nb_etudes_ec[0] + nb_etudes_term_026[0],
                "repartition_CA_etudes": repartition_CA_etudes,
                "totale_CA_ecterm": repartition_CA_etudes["en cours"]
                + repartition_CA_etudes["terminées"],
                "retributions_etudes026": retributions_totales,
                "dico_genre_inter": dico_genre_inter,
                "dico_ca_typeentreprise": dico_ca_typeentreprise,
                "dico_ca_departement": dico_ca_departement,
                "dico_ca_secteur": dico_ca_secteur,
                "nb_intervenants": nb_intervenants,
                "nb_intervenants_diffs": nb_intervenants_diffs,
                "moyenne_inter_mission": moyenne_inter_mission,
                "liste_mois": liste_mois,
                "liste_CA_mois": liste_CA_mois,
                "liste_mois_devis": liste_mois_devis,
                "liste_devis_sign": liste_devis_sign,
                "liste_devis_envo": liste_devis_envo,
                "retributions_totales": retributions_totales,
                "retribution_moyenne_etude": retribution_moyenne_etude,
                "retribution_moyenne_etudiant": retribution_moyenne_etudiant,
                "taux_ouverture": taux_ouverture * 100,
                "liste_date_avenants": liste_date_avenants,
                "liste_nb_avenants": liste_nb_avenants,
                "liste_nb_avenants_del": liste_nb_avenants_del,
                "liste_nb_avenants_bud": liste_nb_avenants_bud,
                "repartition_nb_etudes": repartition_nb_etudes,
            }

        else:
            template = loader.get_template("polls/login.html")
            context = {}
        return HttpResponse(template.render(context, request))
    except Exception as e:
        template = loader.get_template("polls/page_error.html")
        context = {"error": e}
        return HttpResponse(template.render(context, request))


def fetch_data(request):
    if request.user.is_authenticated:
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        if start_date and end_date:
            start_date_obj = datetime.datetime.strptime(start_date, "%Y-%m-%d").replace(
                tzinfo=pytz.UTC
            )
            end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").replace(
                tzinfo=pytz.UTC
            )
        else:
            return JsonResponse({"error": "Invalid date range"}, status=400)

        # Filtrer les études en fonction des dates
        etudes = Etude.objects.filter(
            debut__gte=start_date_obj, debut__lte=end_date_obj
        ).order_by("debut")

        # Calculer les montants par mois et les labels
        date_labels = [start_date_obj.strftime("%Y-%m")]
        cumulated_CA = [0]
        current_sum = 0

        for etude in etudes:
            if etude.status == "EN_COURS" or etude.status == "TERMINEE":
                if etude.debut:
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

        response_data = {"date_labels": date_labels, "cumulated_CA": cumulated_CA}

        # Ensure response_data is JSON serializable
        try:
            json_response = JsonResponse(response_data)
        except TypeError as e:
            print(f"Serialization error: {e}")
            return JsonResponse({"error": "Serialization error"}, status=500)

        return json_response

    return JsonResponse({"error": "Unauthorized"}, status=403)


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
            "notification_list": notification_list,
            "notification_count": notification_count,
        }
        template = loader.get_template("polls/page_messages.html")
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def register(request):
    if request.method == "GET":
        referer = request.META.get("HTTP_REFERER")
        referer_path = urlparse(referer).path
        try:
            match = resolve(referer_path)
            assert match.view_name == "confidentialite-donnees"
            form = AddMember()
            context = {"form": form}
            template = loader.get_template("polls/register.html")
        except:
            return redirect("confidentialite-donnees")
    else:
        fetchform = AddMember(request.POST, request.FILES)
        if fetchform.is_valid():
            new_member = fetchform.save()
            login(
                request, new_member, backend="django.contrib.auth.backends.ModelBackend"
            )
            return redirect("index")
        else:
            context = {"form": fetchform}
            template = loader.get_template("polls/register.html")

    return HttpResponse(template.render(context, request))


def editer_convention(request, iD):
    if request.user.is_authenticated:
        try:
            instance = Etude.objects.get(id=iD)
            je = instance.je
            if not instance.client:
                raise ValueError("Définir un client")

            client = instance.client
            phases = Phase.objects.filter(etude=instance).order_by("numero")
            if instance.type_convention == "Convention d'étude":
                template_path = os.path.join(
                    conf_settings.BASE_DIR,
                    "polls/templates/polls/Convention_Etude_026.docx",
                )

                template = DocxTemplate(template_path)

                model = ConventionEtude
                nom_doc = "Convention_Etude_"

                css_planning = """
                .table_planning {
                    background-color:white;
                    border-collapse: collapse;
                    margin: 0px;
                    padding: 8px;
                    text-align: left;
                    border: 2px solid black;
                    width: 1700px;
                    height: auto;
                }

                .th_planning, .td_planning {
                    padding: 8px;
                    border-top: 1px solid #ddd;
                    position: relative;
                    font-size: 20px;
                }
                .bar_container_plan {
                    position: relative;
                    height: 30px;
                }

                .bar_plan {
                    height: 100%;
                    background-color: rgb(48, 56, 84);
                    position: absolute;
                    left: 0;
                    top: 0;
                }

                .bar_plan .label_plan {
                    position: absolute;
                    left: 50%;
                    top: 50%;
                    font-size: 20px;
                    transform: translate(-50%, -50%);
                    color: white;
                }

                .semaines_plan {
                    display: flex;
                    justify-content: space-between;
                    font-size: 20px;
                    color: #777;
                    margin-bottom: 0px;
                }
                .semaines_plan span {
                    flex: 1; /* Equal width for each span */
                    text-align: right; /* Center text within each span */
                }
                /* FIN PLANNING */
                """
                html_template = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Invoice</title>
                    <style>
                        {css}
                    </style>
                </head>
                <body style="background-color:white;">
                    <table class="table_planning">
                        <thead>
                            <tr>
                                <th class="th_planning" style="font-size: 30px;">{duree_semaine} {semaine_s}</th>
                                <th class="th_planning"></th>
                                <th class="th_planning">
                                    <div class="semaines_plan">
                                        {semaines}
                                    </div>
                                </th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows}
                        </tbody>
                    </table>
                </body>
                </html>
                """

                semaines_html = ""
                for i in range(instance.duree_semaine()):
                    semaines_html += f"<span>{i + 1}</span>"

                rows_html = ""
                for phase in phases:
                    width = (phase.duree_semaine / instance.duree_semaine()) * 100
                    left = (phase.debut_relatif / instance.duree_semaine()) * 100
                    duree_semaine = instance.duree_semaine()
                    semaine_s = "semaine" if duree_semaine == 1 else "semaines"
                    semaine_label = (
                        "semaine" if phase.duree_semaine == 1 else "semaines"
                    )
                    JEH_label = "JEH" if phase.nb_JEH == 1 else "JEHs"
                    row = f"""
                    <tr>
                        <td class='td_planning'> <strong>Phase {phase.numero} :</strong> {phase.duree_semaine} {semaine_label}</td>
                        <td class='td_planning' style='text-align: center;'>{phase.nb_JEH} {JEH_label}</td>
                        <td class='td_planning' style='width: 70%;'>
                            <div class='bar_container_plan'>
                                <div class='bar_plan' style='width: {width}%; left: {left}%;'>
                                    <div class='label_plan'></div>
                                </div>
                            </div>
                        </td>
                    </tr>
                    """
                    rows_html += row

                semaine_s = "semaine" if duree_semaine == 1 else "semaines"
                final_html = html_template.format(
                    debut=instance.debut,
                    fin=instance.fin(),
                    rows=rows_html,
                    css=css_planning,
                    semaines=semaines_html,
                    duree_semaine=duree_semaine,
                    semaine_s=semaine_s,
                )

                output_dir = "polls/static/polls/img"
                os.makedirs(output_dir, exist_ok=True)
                os.chdir(output_dir)
                filename = "tab_planning.png"
                time1.sleep(1)
                hti = Html2Image()
                hti.size = (1720, 60 + 64 * instance.nb_phases())
                hti.screenshot(
                    html_str=final_html, css_str=css_planning, save_as=filename
                )
                image_path = os.path.join(conf_settings.BASE_DIR, "tab_planning.png")
                time1.sleep(1)
                image_path = os.path.join(conf_settings.BASE_DIR, "tab_planning.png")
                with open(image_path, "rb") as img_file:
                    image_data = img_file.read()

                image_stream = BytesIO(image_data)
                image = InlineImage(template, image_stream, width=Mm(173))
                time1.sleep(1)

                """output_dir = os.path.join(conf_settings.BASE_DIR, "polls/static/polls/img")
    
                os.makedirs(output_dir, exist_ok=True)

                filename = f"tab_planning{instance.id}.png"
        
                hti = Html2Image()
                hti.size = (1720, 60 + 64 * instance.nb_phases())  # Adjust the size as needed
                hti.screenshot(html_str=final_html, css_str=css_planning, save_as=filename)

                # Read the generated image
                image_path = os.path.join(conf_settings.BASE_DIR, filename)
                with open(image_path, "rb") as img_file:
                    image_data = img_file.read()

                # Create an in-memory file from the image data
                image_stream = BytesIO(image_data)
                image = InMemoryUploadedFile(image_stream, None, filename, 'image/png', len(image_data), None)

                # Replace the planning_image field with the new image
                instance.planning_image.save(filename, image, save=True)

                # Save the instance to persist the change
                instance.save()

                image = InlineImage(template, instance.planning_image, width=Mm(173))"""

            elif instance.type_convention == "Convention cadre":
                template_path = os.path.join(
                    conf_settings.BASE_DIR,
                    "polls/templates/polls/Convention_Cadre_026.docx",
                )
                template = DocxTemplate(template_path)
                model = ConventionCadre

                nom_doc = "Convention_Cadre_"
            else:
                raise ValueError("Type de convention non défini.")
            if instance.convention():
                ce = instance.convention()
            else:
                ce = model(etude=instance)
                ce.save()

            president = {"titre": "M.", "first_name": "Thomas", "last_name": "Debray"}
            duree = instance.duree_semaine()
            nb_phases = instance.nb_phases()
            respo = instance.responsable.student
            poste = "Chef de Projet"
            if respo.titre == "Mme":
                poste = "Cheffe de Projet"
            qualite = instance.resp_qualite.student
            ref_m = instance.ref()
            if instance.client_interlocuteur is None:
                raise ValueError("Définir un interlocuteur client")

            if instance.client_representant_legale is None:
                raise ValueError("Définir un responsable légale (client)")

            representant_client = instance.client_interlocuteur
            representant_legale_client = instance.client_representant_legale
            date = timezone.now()
            annee = date.strftime("%Y")
            nb_JEH = instance.nb_JEH()
            tot_HT_phase = format_nombres(instance.montant_phase_HT())
            factures = Facture.objects.filter(etude=instance).order_by("numero_facture")

            fac_acom = None
            fac_inter = None
            fac_solde = None
            for facture in factures:
                if facture.type_facture == facture.Status.ACOMPTE:
                    fac_acom = facture
                elif facture.type_facture == facture.Status.SOLDE:
                    fac_solde = facture
                elif facture.type_facture == facture.Status.INTERMEDIAIRE:
                    fac_inter = facture

            ac_inter = []
            if fac_acom or fac_inter:
                if fac_acom:
                    ac_inter.append(
                        {
                            "modal": "A la signature de la Convention d'Étude",
                            "denom": "Acompte",
                            "sht": format_nombres(fac_acom.montant_HT()),
                            "sttc": format_nombres(fac_acom.montant_TTC()),
                        }
                    )
                if fac_inter:
                    ac_inter.append(
                        {
                            "modal": "A la remise du livrable intermédiaire",
                            "denom": "Intermédiaire",
                            "sht": format_nombres(fac_inter.montant_HT()),
                            "sttc": format_nombres(fac_inter.montant_TTC()),
                        }
                    )

            if fac_solde is None:
                raise ValueError("Définir la facturation de solde pour l'échéancier")
            else:
                ac_inter.append(
                    {
                        "modal": "A la remise du livrable final",
                        "denom": "Solde",
                        "sht": format_nombres(fac_solde.montant_HT()),
                        "sttc": format_nombres(fac_solde.montant_TTC()),
                    }
                )

            # acompte_HT= format_nombres(fac_acom.montant_HT())
            # solde_HT= format_nombres(fac_solde.montant_HT())
            logo_client = InlineImage(
                template, client.logo, width=Mm(20)
            )  # width is in millimetres

            context = {
                "planning_pre": image,
                "etude": instance,
                "phases": phases,
                "nb_phases": nb_phases,
                "president": president,
                "duree": duree,
                "client": client,
                "repr": representant_client,
                "repr_legale": representant_legale_client,
                "je": je,
                "ce": ce,
                "respo": respo,
                "quali": qualite,
                "ref_m": ref_m,
                "annee": annee,
                "nb_JEH": nb_JEH,
                "tot_HT_phase": tot_HT_phase,
                "fac_acom": fac_acom,
                "fac_solde": fac_solde,
                "fac_inter": fac_inter,
                "ac_inter": ac_inter,
                "poste": poste,
                "factures": factures,
                "logo_client": logo_client,
            }
            # Load the template

            env = Environment()

            env.filters["FormatNombres"] = format_nombres
            env.filters["ChiffreLettre"] = chiffre_lettres

            template.render(context, env)
            output = BytesIO()
            template.save(output)
            output.seek(0)

            # Save the "fichier" field of the CE
            filename = f"{nom_doc}{ref_m}.docx"
            response = FileResponse(
                output,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            instance.status = "EN_COURS"
            instance.save()
            return response

        except ValueError as ve:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": str(ve)}
        except Exception as e:
            template = loader.get_template("polls/page_error.html")
            context = {
                "error_message": f"Un problème a été détecté dans la base de données: {str(e)}"
            }

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def editer_convention_cadre(request, iD):
    if request.user.is_authenticated:
        try:
            instance = Etude.objects.get(id=iD)
            je = instance.je
            if instance.client is None:
                raise ValueError("Définir un client")
            client = instance.client
            phases = Phase.objects.filter(etude=instance).order_by("numero")

            model = ConventionCadre

            template_path = os.path.join(
                conf_settings.BASE_DIR,
                "polls/templates/polls/Convention_Cadre_026.docx",
            )
            template = DocxTemplate(template_path)

            nom_doc = "Convention_Cadre_"
            if instance.convention:
                ce = instance.convention()
            else:
                ce = model(etude=instance)
                ce.save()

            president = {"titre": "M.", "first_name": "Thomas", "last_name": "Debray"}
            duree = instance.duree_semaine()
            nb_phases = instance.nb_phases()
            respo = instance.responsable.student
            poste = "Chef de Projet"
            if respo.titre == "Mme":
                poste = "Cheffe de Projet"
            qualite = instance.resp_qualite.student
            ref_m = instance.ref()
            if instance.client_interlocuteur is None:
                raise ValueError("Définir un interlocuteur client")
            representant_client = (
                instance.client_interlocuteur
            )  # le gars de la boite qui interagit avec la PEP
            if instance.client_representant_legale is None:
                raise ValueError("Définir un représentant légal")
            representant_legale_client = (
                instance.client_representant_legale
            )  # souvent le patron de l boite qui a le droit de signer les documents
            # souvent le client a un representant a qui on a affaie mais cest le representant legale (champs dans client) qui signe les papiers
            date = timezone.now()
            annee = date.strftime("%Y")

            context = {
                "etude": instance,
                "phases": phases,
                "nb_phases": nb_phases,
                "president": president,
                "duree": duree,
                "client": client,
                "repr": representant_client,
                "repr_legale": representant_legale_client,
                "je": je,
                "ce": ce,
                "respo": respo,
                "quali": qualite,
                "ref_m": ref_m,
                "annee": annee,
                "poste": poste,
            }
            # Load the template

            env = Environment()

            env.filters["FormatNombres"] = format_nombres
            env.filters["ChiffreLettre"] = chiffre_lettres

            template.render(context, env)
            output = BytesIO()
            template.save(output)
            output.seek(0)

            # Save the "fichier" field of the CE
            filename = f"{nom_doc}{ref_m}.docx"
            response = FileResponse(
                output,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            instance.status = "EN_COURS"
            instance.save()
            return response

        except ValueError as ve:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": str(ve)}
        except:
            template = loader.get_template("polls/page_error.html")
            context = {
                "error_message": "Un problème a été détecté dans la base de données."
            }

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def editer_pv(request, iD, type):
    if request.user.is_authenticated:
        try:
            instance = Etude.objects.get(id=iD)

            convention = instance.convention()
            if not convention:
                raise ValueError("pas de convention")

            je = instance.je
            if instance.client is None:
                raise ValueError("Pas de client")
            client = instance.client
            model = PV
            pv = model(etude=instance, type=type)
            if not instance.client_representant_legale:
                raise ValueError("Pas de responsable client")
            client_resp = instance.client_representant_legale

            president = {"titre": "M.", "first_name": "Thomas", "last_name": "Debray"}

            if not instance.responsable:
                raise ValueError("Pas de suiveur")

            respo = instance.responsable.student
            if not instance.resp_qualite:
                raise ValueError("Pas de qualité")
            qualite = instance.resp_qualite.student
            ref_m = instance.ref()

            if instance.type_convention == "Convention d'étude":
                phases = Phase.objects.filter(etude=instance).order_by("numero")

                ce_ref = f"{ref_m}ce"
                duree = instance.duree_semaine()
                nb_phases = instance.nb_phases()
                avenants = AvenantConventionEtude.objects.filter(
                    ce=convention
                ).order_by("numero")
                avenant = None
                num_avenant = None
                if len(avenants) > 0:
                    avenant = avenants[len(avenants) - 1]
                    num_avenant = avenant
                if type == "PVRF":
                    template_path = os.path.join(
                        conf_settings.BASE_DIR, "polls/templates/polls/PVRF_026_CE.docx"
                    )
                    template = DocxTemplate(template_path)

                    filename = f"PVRF_{ref_m}.docx"
                else:
                    template_path = os.path.join(
                        conf_settings.BASE_DIR, "polls/templates/polls/PVRI_026_CE.docx"
                    )
                    template = DocxTemplate(template_path)

                    filename = f"PVRI_{ref_m}.docx"

            else:
                raise ValueError("Pas encore de pv pour les CCs")

            date = datetime.datetime.now()

            date_2 = timezone.now().date()
            mois = [
                "Janvier",
                "Février",
                "Mars",
                "Avril",
                "Mai",
                "Juin",
                "Juillet",
                "Août",
                "Septembre",
                "Octobre",
                "Novembre",
                "Décembre",
            ]

            # Format the date
            general_date_creation = (
                f"{date_2.day} {mois[date_2.month - 1]} {date_2.year}"
            )
            annee = date.strftime("%Y")
            etude_periode_garantie = instance.periode_de_garantie

            logo_client = InlineImage(
                template, client.logo, width=Mm(20)
            )  # width is in millimetres

            context = {
                "etude": instance,
                "phases": phases,
                "nb_phases": nb_phases,
                "president": president,
                "duree": duree,
                "client": client,
                "je": je,
                "respo": respo,
                "quali": qualite,
                "ref_m": ref_m,
                "annee": annee,
                "avenant": avenant,
                "num_avenant": num_avenant,
                "ce": ce_ref,
                "general_date_creation": general_date_creation,
                "pv_ref": pv.ref(),
                "repr_legale": client_resp,
                "logo_client": logo_client,
                "etude_periode_garantie": etude_periode_garantie,
            }
            # Load the template

            env = Environment()

            env.filters["FormatNombres"] = format_nombres
            template.render(context, env)
            output = BytesIO()
            template.save(output)
            output.seek(0)

            # Save the "fichier" field of the CE

            response = FileResponse(
                output,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response

        except ValueError as ve:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": str(ve)}
        except:
            template = loader.get_template("polls/page_error.html")
            context = {
                "error_message": "Un problème a été détecté dans la base de données."
            }

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def editer_rdm(request, id_etude, id_eleve):
    if request.user.is_authenticated:
        try:
            etude = Etude.objects.get(id=id_etude)

            eleve = Student.objects.get(id=id_eleve)
            if not etude.client:
                raise ValueError("Définir un client")

            client = etude.client
            assignations = list(
                AssignationJEH.objects.filter(eleve=eleve, phase__etude=etude).order_by(
                    "phase__numero"
                )
            )
            je = eleve.je
            president = {"titre": "M.", "first_name": "Thomas", "last_name": "Debray"}
            remuneration = sum(
                assignment.retribution_brute_totale() for assignment in assignations
            )
            date_fin = timezone.now().date()
            for assignation in assignations:
                if assignation.phase.date_fin > date_fin:
                    date_fin = assignation.phase.date_fin
            etudiant_nb_JEH = sum(
                assignation.nombre_JEH for assignation in assignations
            )

            template_path = os.path.join(
                conf_settings.BASE_DIR, "polls/templates/polls/RDM_026.docx"
            )
            template = DocxTemplate(template_path)

            model = RDM
            if not RDM.objects.filter(etude=etude, eleve=eleve).first():
                rdm = model(etude=etude, eleve=eleve)
                rdm.save()
            rdm = RDM.objects.get(etude=etude, eleve=eleve)
            ref_m = etude.ref()
            ref_d = rdm
            ce = f"{ref_m}ce"
            date = timezone.now().date()
            annee = date.strftime("%Y")
            context = {
                "etude": etude,
                "client": client,
                "rdm": rdm,
                "ref_d": ref_d,
                "etudiant": eleve,
                "ref_m": ref_m,
                "assignations": assignations,
                "annee": annee,
                "president": president,
                "etudiant_nb_JEH": etudiant_nb_JEH,
                "date_fin": date_fin,
                "remuneration": remuneration,
                "ce": ce,
            }

            env = Environment()
            env.filters["FormatNombres"] = format_nombres
            env.filters["EnLettres"] = en_lettres
            env.filters["ChiffreLettre"] = chiffre_lettres
            template.render(context, env)
            output = BytesIO()
            template.save(output)
            output.seek(0)
            filename = f"{ref_d}.docx"
            response = FileResponse(
                output,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        except ValueError as ve:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": str(ve)}

        except:
            template = loader.get_template("polls/page_error.html")
            context = {
                "error_message": "Un problème a été détecté dans la base de données."
            }

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def editer_avenant_rdm_ce(request, id_etude, id_eleve):
    if request.user.is_authenticated:
        try:
            etude = Etude.objects.get(id=id_etude)
            eleve = Student.objects.get(id=id_eleve)
            num_dernier_avenant = int(request.POST.get("num_dernier_avenant"))
            date_fin = request.POST.get("date_fin")
            causes = request.POST.get("causes_avenants")
            ref_ba = request.POST.get("ref_ba")
            ref_rdm = request.POST.get("ref_rdm")
            dico_mois = {
                1: "janvier",
                2: "février",
                3: "mars",
                4: "avril",
                5: "mai",
                6: "juin",
                7: "juillet",
                8: "août",
                9: "septembre",
                10: "octobre",
                11: "novembre",
                12: "décembre",
            }

            annee_fin, mois_fin, jour_fin = date_fin[0:4], date_fin[5:7], date_fin[8:10]

            date_fin_format = f"{int(jour_fin)} {dico_mois[int(mois_fin)]} {annee_fin}"
            if etude.type_convention == "Convention cadre":
                ref_ce = f"{etude.ref()}cc"
                pass

            if etude.type_convention == "Convention d'étude":
                ref_ce = f"{etude.ref()}ce"
                assignations = list(
                    AssignationJEH.objects.filter(
                        eleve=eleve, phase__etude=etude
                    ).order_by("phase__numero")
                )
                remuneration = sum(
                    assignment.retribution_brute_totale() for assignment in assignations
                )

            # num avenant
            # ref avenant

            nb_JEH = sum(assignment.nombre_JEH for assignment in assignations)
            president = {"titre": "M.", "first_name": "Thomas", "last_name": "Debray"}

            ref_dernier_avenant = None
            if num_dernier_avenant > 0:
                ref_dernier_avenant = f"{etude.ref()}ae{num_dernier_avenant:02d}-{eleve.last_name[0]}{eleve.first_name[0]}"
            num_avenant = num_dernier_avenant + 1
            ref_avenant = f"{etude.ref()}ae{num_avenant:02d}-{eleve.last_name[0]}{eleve.first_name[0]}"

            template_path = os.path.join(
                conf_settings.BASE_DIR, "polls/templates/polls/Avenant_rdm_026.docx"
            )
            template = DocxTemplate(template_path)

            date = timezone.now().date()
            annee = date.strftime("%Y")
            context = {
                "etude": etude,
                "eleve": eleve,
                "date_fin_format": date_fin_format,
                "ref_avenant": ref_avenant,
                "ref_dernier_avenant": ref_dernier_avenant,
                "ref_ba": ref_ba,
                "annee": annee,
                "remuneration": remuneration,
                "assignations": assignations,
                "ref_rdm": ref_rdm,
                "nb_JEH": nb_JEH,
                "president": president,
                "causes": causes,
                "ref_ce": ref_ce,
                "ref_etude": etude.ref(),
            }

            env = Environment()
            env.filters["FormatNombres"] = format_nombres
            env.filters["EnLettres"] = en_lettres
            env.filters["ChiffreLettre"] = chiffre_lettres
            template.render(context, env)
            output = BytesIO()
            template.save(output)
            output.seek(0)
            filename = f"{ref_avenant}.docx"
            response = FileResponse(
                output,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response

        except ValueError as ve:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": str(ve)}

        except:
            template = loader.get_template("polls/page_error.html")
            context = {
                "error_message": "Un problème a été détecté dans la base de données."
            }

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def editer_acf(request, id_etude, id_eleve):
    if request.user.is_authenticated:
        try:
            etude = Etude.objects.get(id=id_etude)
            eleve = Student.objects.get(id=id_eleve)
            if not etude.client:
                raise ValueError("Définir un client")
            else:
                client = etude.client.nom_societe
            president_titre = "M."
            president_prenom = "Thomas"
            president_nom = "Debray"
            num_etude = etude.ref()
            titre = eleve.titre
            nom = eleve.last_name
            prenom = eleve.first_name
            etude_titre = etude.titre
            date = timezone.now().date()
            annee = date.strftime("%Y")

            template_path = os.path.join(
                conf_settings.BASE_DIR, "polls/templates/polls/ACF_etudiant_026.docx"
            )
            template = DocxTemplate(template_path)

            context = {
                "etude": etude,
                "client": client,
                "president_titre": president_titre,
                "president_prenom": president_prenom,
                "president_nom": president_nom,
                "num_etude": num_etude,
                "titre": titre,
                "annee": annee,
                "nom": nom,
                "prenom": prenom,
                "etude_titre": etude_titre,
                "adresse": eleve.adress,
                "code_postal": eleve.code_postal,
                "ville": eleve.ville,
                "portable": eleve.phone_number,
            }

            env = Environment()
            env.filters["FormatNombres"] = format_nombres
            env.filters["EnLettres"] = en_lettres
            env.filters["ChiffreLettre"] = chiffre_lettres
            template.render(context, env)
            output = BytesIO()
            template.save(output)
            output.seek(0)
            filename = f"ACF_{num_etude}{nom}.docx"
            response = FileResponse(
                output,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        except ValueError as ve:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": str(ve)}

        except:
            template = loader.get_template("polls/page_error.html")
            context = {
                "error_message": "Un problème a été détecté dans la base de données."
            }

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def editer_acf_client(request, iD):
    if request.user.is_authenticated:
        try:
            etude = Etude.objects.get(id=iD)
            if not etude.client:
                raise ValueError("Définir un client")

            client = etude.client
            je_president_titre = "M."
            je_president_prenom = "Thomas"
            je_president_nom = "Debray"
            num_etude = etude.ref()
            client_adresse = client.rue
            client_code_postal = client.code_postal
            client_ville = client.ville

            client_pays = client.country
            if etude.client_representant_legale is None:
                raise ValueError("Définir un représentant légal")
            client_titre = etude.client_representant_legale.titre
            client_prenom = etude.client_representant_legale.first_name
            client_nom = etude.client_representant_legale.last_name
            client_fonction = etude.client_representant_legale.fonction

            etude_titre = etude.titre
            date = timezone.now().date()
            mois = [
                "Janvier",
                "Février",
                "Mars",
                "Avril",
                "Mai",
                "Juin",
                "Juillet",
                "Août",
                "Septembre",
                "Octobre",
                "Novembre",
                "Décembre",
            ]

            # Format the date
            general_date_creation = f"{date.day} {mois[date.month - 1]} {date.year}"
            annee = date.strftime("%Y")
            general_date_creation = date.strftime("%d %B %Y")

            template_path = os.path.join(
                conf_settings.BASE_DIR, "polls/templates/polls/ACF_Client_026.docx"
            )
            template = DocxTemplate(template_path)
            logo_client = InlineImage(template, client.logo, width=Mm(20))
            client = client.nom_societe
            context = {
                "etude": etude,
                "client": client,
                "je_president_titre": je_president_titre,
                "je_president_prenom": je_president_prenom,
                "je_president_nom": je_president_nom,
                "num_etude": num_etude,
                "general_date_creation": general_date_creation,
                "annee": annee,
                "client_adresse": client_adresse,
                "client_code_postal": client_code_postal,
                "etude_titre": etude_titre,
                "client_ville": client_ville,
                "client_pays": client_pays,
                "client_titre": client_titre,
                "client_prenom": client_prenom,
                "client_nom": client_nom,
                "client_fonction": client_fonction,
                "logo_client": logo_client,
            }

            env = Environment()
            env.filters["FormatNombres"] = format_nombres
            env.filters["EnLettres"] = en_lettres
            env.filters["ChiffreLettre"] = chiffre_lettres
            template.render(context, env)
            output = BytesIO()
            template.save(output)
            output.seek(0)
            filename = f"ACF_{num_etude}{client}.docx"
            response = FileResponse(
                output,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        except ValueError as ve:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": str(ve)}

        except:
            template = loader.get_template("polls/page_error.html")
            context = {
                "error_message": "Un problème a été détecté dans la base de données."
            }

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def editer_ba(request, id_eleve):
    if request.user.is_authenticated:
        try:
            ba_nombre = request.POST.get("ba_nombre")
            eleve = Student.objects.get(id=id_eleve)
            je_president_nom = "Debray"
            je_president_prenom = "Thomas"
            date = timezone.now()
            general_date_creation = date.strftime("%d %B %Y")
            template_path = os.path.join(
                conf_settings.BASE_DIR, "polls/templates/polls/BA_026.docx"
            )
            template = DocxTemplate(template_path)

            ba_dej_exist = BA.objects.filter(eleve=eleve).first()
            if ba_dej_exist:
                ba_dej_exist.number = ba_nombre
                ba_dej_exist.save()
            else:
                model = BA
                ba = model(eleve=eleve, number=int(ba_nombre))
                ba.save()

            year = datetime.datetime.now().year  # Get the current year
            ref = f"{year}{int(ba_nombre):04d}"
            context = {
                "etudiant": eleve,
                "je_president_nom": je_president_nom,
                "je_president_prenom": je_president_prenom,
                "general_date_creation": general_date_creation,
                "num_conv_etudiant": ref,
            }

            env = Environment()
            template.render(context, env)

            output = BytesIO()
            template.save(output)
            output.seek(0)

            filename = f"{eleve.last_name.upper()}_BA.docx"
            response = FileResponse(
                output,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        except ValueError as ve:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": str(ve)}

        except:
            template = loader.get_template("polls/page_error.html")
            context = {
                "error_message": "Un problème a été détecté dans la base de données."
            }

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def editer_devis(request, iD):
    if request.user.is_authenticated:
        try:
            instance = Etude.objects.get(id=iD)
            if instance.client is None:
                raise ValueError("Définir un client")

            client = instance.client
            template_path = os.path.join(
                conf_settings.BASE_DIR, "polls/templates/polls/Devis_026.docx"
            )
            template = DocxTemplate(template_path)
            model = Devis
            if instance.get_devis():
                devis = instance.get_devis()

            else:
                devis = model(etude=instance)

            responsable = instance.responsable.student
            if responsable is None:
                raise ValueError("Définir un suiveur")

            poste = "Chef de Projet"
            if responsable.titre == "Mme":
                poste = "Cheffe de Projet"

            if instance.resp_qualite is None:
                raise ValueError("Définir un qualité")
            qualite = instance.resp_qualite.student

            ref_m = instance.ref()
            ref_d = ref_m + "pv"
            # !!!! quand je fais ref_d = devis.ref() il reconnait pas devis mais faudra mettre le contexte en fonction de devis
            duree_semaine = instance.duree_semaine()
            date = timezone.now()
            mois = date.strftime("%B")
            annee = date.strftime("%Y")
            date_creation = date.strftime("%d %B %Y")
            president = {"titre": "M.", "first_name": "Thomas", "last_name": "Debray"}
            phases = Phase.objects.filter(etude=instance).order_by("numero")
            nb_JEH = instance.nb_JEH()
            tot_HT_phase = format_nombres(instance.montant_phase_HT())

            factures = Facture.objects.filter(etude=instance).order_by("numero_facture")

            fac_acom = None
            fac_inter = None
            fac_solde = None
            for facture in factures:
                if facture.type_facture == facture.Status.ACOMPTE:
                    fac_acom = facture
                elif facture.type_facture == facture.Status.SOLDE:
                    fac_solde = facture
                elif facture.type_facture == facture.Status.INTERMEDIAIRE:
                    fac_inter = facture

            ac_inter = []
            if fac_acom or fac_inter:
                if fac_acom:
                    ac_inter.append(
                        {
                            "modal": "A la signature de la Convention d'Étude",
                            "denom": "Acompte",
                            "sht": format_nombres(fac_acom.montant_HT()),
                            "sttc": format_nombres(fac_acom.montant_TTC()),
                        }
                    )
                if fac_inter:
                    ac_inter.append(
                        {
                            "modal": "A la remise du livrable intermédiaire",
                            "denom": "Intermédiaire",
                            "sht": format_nombres(fac_inter.montant_HT()),
                            "sttc": format_nombres(fac_inter.montant_TTC()),
                        }
                    )

            if fac_solde is None:
                raise ValueError("Définir la facturation de solde pour l'échéancier")
            else:
                ac_inter.append(
                    {
                        "modal": "A la remise du livrable final",
                        "denom": "Solde",
                        "sht": format_nombres(fac_solde.montant_HT()),
                        "sttc": format_nombres(fac_solde.montant_TTC()),
                    }
                )

            css_planning = """
            .table_planning {
                background-color:white;
                border-collapse: collapse;
                margin: 0px;
                padding: 8px;
                text-align: left;
                border: 2px solid black;
                width: 1700px;
                height: auto;
            }

            .th_planning, .td_planning {
                padding: 8px;
                border-top: 1px solid #ddd;
                position: relative;
                font-size: 20px;
            }
            .bar_container_plan {
                position: relative;
                height: 30px;
            }

            .bar_plan {
                height: 100%;
                background-color: rgb(48, 56, 84);
                position: absolute;
                left: 0;
                top: 0;
            }

            .bar_plan .label_plan {
                position: absolute;
                left: 50%;
                top: 50%;
                font-size: 20px;
                transform: translate(-50%, -50%);
                color: white;
            }

            .semaines_plan {
                display: flex;
                justify-content: space-between;
                font-size: 20px;
                color: #777;
                margin-bottom: 0px;
            }
            .semaines_plan span {
                flex: 1; /* Equal width for each span */
                text-align: right; /* Center text within each span */
            }
            /* FIN PLANNING */
            """
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Invoice</title>
                <style>
                    {css}
                </style>
            </head>
            <body style="background-color:white;">
                <table class="table_planning">
                    <thead>
                        <tr>
                            <th class="th_planning" style="font-size: 30px;">{duree_semaine} {semaine_s}</th>
                            <th class="th_planning"></th>
                            <th class="th_planning">
                                <div class="semaines_plan">
                                    {semaines}
                                </div>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </body>
            </html>
            """

            semaines_html = ""
            for i in range(instance.duree_semaine()):
                semaines_html += f"<span>{i + 1}</span>"

            rows_html = ""
            for phase in phases:
                width = (phase.duree_semaine / instance.duree_semaine()) * 100
                left = (phase.debut_relatif / instance.duree_semaine()) * 100
                duree_semaine = instance.duree_semaine()
                semaine_s = "semaine" if duree_semaine == 1 else "semaines"
                semaine_label = "semaine" if phase.duree_semaine == 1 else "semaines"
                JEH_label = "JEH" if phase.nb_JEH == 1 else "JEHs"
                row = f"""
                <tr>
                    <td class='td_planning'> <strong>Phase {phase.numero} :</strong> {phase.duree_semaine} {semaine_label}</td>
                    <td class='td_planning' style='text-align: center;'>{phase.nb_JEH} {JEH_label}</td>
                    <td class='td_planning' style='width: 70%;'>
                        <div class='bar_container_plan'>
                            <div class='bar_plan' style='width: {width}%; left: {left}%;'>
                                <div class='label_plan'></div>
                            </div>
                        </div>
                    </td>
                </tr>
                """
                rows_html += row

            semaine_s = "semaine" if duree_semaine == 1 else "semaines"
            final_html = html_template.format(
                debut=instance.debut,
                fin=instance.fin(),
                rows=rows_html,
                css=css_planning,
                semaines=semaines_html,
                duree_semaine=duree_semaine,
                semaine_s=semaine_s,
            )

            output_dir = "polls/static/polls/img"
            os.makedirs(output_dir, exist_ok=True)
            os.chdir(output_dir)
            filename = "tab_planning.png"
            time1.sleep(1)
            hti = Html2Image()
            hti.size = (1720, 60 + 64 * instance.nb_phases())
            hti.screenshot(html_str=final_html, css_str=css_planning, save_as=filename)
            image_path = os.path.join(conf_settings.BASE_DIR, "tab_planning.png")
            time1.sleep(1)
            image_path = os.path.join(conf_settings.BASE_DIR, "tab_planning.png")
            with open(image_path, "rb") as img_file:
                image_data = img_file.read()

            image_stream = BytesIO(image_data)
            image = InlineImage(template, image_stream, width=Mm(173))
            time1.sleep(1)

            """output_dir = os.path.join(conf_settings.BASE_DIR, "polls/static/polls/img")
    
            os.makedirs(output_dir, exist_ok=True)

            filename = f"tab_planning{instance.id}.png"

            hti = Html2Image()
            hti.size = (
                1720,
                60 + 64 * instance.nb_phases(),
            )  # Adjust the size as needed
            hti.screenshot(html_str=final_html, css_str=css_planning, save_as=filename)

            # Read the generated image
            image_path = os.path.join(conf_settings.BASE_DIR, filename)
            with open(image_path, "rb") as img_file:
                image_data = img_file.read()

            # Create an in-memory file from the image data
            image_stream = BytesIO(image_data)
            image = InMemoryUploadedFile(
                image_stream, None, filename, "image/png", len(image_data), None
            )

            # Replace the planning_image field with the new image
            instance.planning_image.save(filename, image, save=True)

            # Save the instance to persist the change
            instance.save()

            image = InlineImage(template, instance.planning_image, width=Mm(173))"""

            logo_client = InlineImage(
                template, client.logo, width=Mm(20)
            )  # width is in millimetres
            photo_cdp = InlineImage(template, instance.responsable.photo, width=Mm(20))
            context = {
                "planning_pre": image,
                "president": president,
                "etude": instance,
                "devis": devis,
                "client": client,
                "responsable": responsable,
                "phases": phases,
                "qualite": qualite,
                "mois": mois,
                "annee": annee,
                "date_creation": date_creation,
                "poste": poste,
                "ref_m": ref_m,
                "ref_d": ref_d,
                "nb_JEH": nb_JEH,
                "tot_HT_phase": tot_HT_phase,
                "fac_acom": fac_acom,
                "fac_solde": fac_solde,
                "factures": factures,
                "ac_inter": ac_inter,
                "logo_client": logo_client,
                "photo_cdp": photo_cdp,
                "duree_semaine": duree_semaine,
            }

            env = Environment()

            env.filters["FormatNombres"] = format_nombres
            env.filters["EnLettres"] = en_lettres
            env.filters["ChiffreLettre"] = chiffre_lettres

            # Render the document
            template.render(context, env)
            output = BytesIO()
            template.save(output)
            output.seek(0)

            # Save the "fichier" field of the CE
            filename = f"Devis_{ref_m}.docx"
            response = FileResponse(
                output,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            devis.save()
            return response
        except ValueError as ve:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": str(ve)}
        except Exception as e:
            template = loader.get_template("polls/page_error.html")
            context = {
                "error_message": "Un problème a été détecté dans la base de données."
            }

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def editer_avenant_ce(request, iD):
    if request.user.is_authenticated:
        try:
            instance = AvenantConventionEtude.objects.get(id=iD)
            ce = instance.ce
            avenants = AvenantConventionEtude.objects.filter(ce=ce).order_by("numero")

            dernier_avenant = None
            if len(avenants) > 1:
                dernier_avenant = avenants[len(avenants) - 2]

            avenant_budget = False
            avenant_delais = False
            for avenant in avenants:
                if avenant.avenant_budget:
                    avenant_budget = True
                if avenant.avenant_delais:
                    avenant_delais = True

            objet = instance.objet
            num_del = 1
            num_bud = 2
            if not avenant_delais:
                num_bud = 1

            etude = ce.etude
            if etude.client is None:
                raise ValueError("Définir un client")

            client = etude.client
            if etude.client_representant_legale is None:
                raise ValueError("Définir un représentant légal")
            representant_legale_client = (
                etude.client_representant_legale
            )  # souvent le patron de l boite qui a le droit de signer les documents

            president = {"titre": "M.", "first_name": "Thomas", "last_name": "Debray"}
            ref_m = etude.ref()

            if etude.fin():
                semaine_fin = math.ceil(
                    (etude.fin() - datetime.datetime.today().date()).days / 7
                )
            else:
                semaine_fin = etude.duree_semaine()

            semaine_fin_lettres = en_lettres(semaine_fin)

            nb_JEH = etude.nb_JEH()
            nb_JEH_lettres = en_lettres(nb_JEH)

            phase_montant_HT = format_nombres(etude.montant_phase_HT())
            phase_montant_HT_lettres = chiffre_lettres(etude.montant_phase_HT())
            frais_HT = format_nombres(etude.frais_dossier)
            frais_HT_lettres = chiffre_lettres(etude.frais_dossier)
            total_HT = format_nombres(etude.montant_HT_total())
            total_HT_lettres = chiffre_lettres(etude.montant_HT_total())
            total_TTC = format_nombres(etude.total_ttc())
            total_TTC_lettres = chiffre_lettres(etude.total_ttc())

            template_path = os.path.join(
                conf_settings.BASE_DIR, "polls/templates/polls/avenant_ce_026.docx"
            )

            template = DocxTemplate(template_path)

            logo_client = InlineImage(
                template, client.logo, width=Mm(20)
            )  # width is in millimetres
            context = {
                "avenant": instance,
                "etude": etude,
                "client": client,
                "president": president,
                "ref_m": ref_m,
                "ce": ce,
                "repr_legale": representant_legale_client,
                "semaine_fin": semaine_fin,
                "semaine_fin_lettres": semaine_fin_lettres,
                "nb_JEH": nb_JEH,
                "nb_JEH_lettres": nb_JEH_lettres,
                "phase_montant_HT": phase_montant_HT,
                "phase_montant_HT_lettres": phase_montant_HT_lettres,
                "frais_HT": frais_HT,
                "frais_HT_lettres": frais_HT_lettres,
                "total_HT": total_HT,
                "total_HT_lettres": total_HT_lettres,
                "total_TTC": total_TTC,
                "total_TTC_lettres": total_TTC_lettres,
                "avenant_delais": avenant_delais,
                "avenant_budget": avenant_budget,
                "num_del": num_del,
                "num_bud": num_bud,
                "objet": objet,
                "dernier_avenant": dernier_avenant,
                "logo_client": logo_client,
            }
            print(
                f"avenant_delais : {avenant_delais}, avenant_budget: {avenant_budget}"
            )
            # Load the template

            # Render the document
            template.render(context)

            # Create a temporary in-memory file
            output = BytesIO()
            template.save(output)
            output.seek(0)

            # Save the "fichier" field of the CE
            filename = f"AvenantCE_{instance.__str__()}.docx"
            response = FileResponse(
                output,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        except ValueError as ve:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": str(ve)}

        except:
            template = loader.get_template("polls/page_error.html")
            context = {
                "error_message": "Un problème a été détecté dans la base de données."
            }

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def editer_bon(request, id_bon):
    if request.user.is_authenticated:
        try:
            template_path = os.path.join(
                conf_settings.BASE_DIR, "polls/templates/polls/BDC_026.docx"
            )

            template = DocxTemplate(template_path)

            bon = BonCommande.objects.get(id=id_bon)
            etude = bon.etude
            responsable = etude.responsable
            if not etude.client:
                raise ValueError("Définir un client")
            client = etude.client

            phases = bon.phases()
            if not etude.client_interlocuteur:
                raise ValueError("Définir un interlocuteur client")

            repr = etude.client_interlocuteur
            if not etude.client_representant_legale:
                raise ValueError("Définir un responsable client")
            repr_legale = etude.client_representant_legale
            quali = etude.resp_qualite.student
            respo = etude.responsable.student
            tot_HT_phase = sum(phase.calcul_mt_HT() for phase in phases)
            poste = "Chef de Projet"
            if respo.titre == "Mme":
                poste = "Cheffe de Projet"
            president = {"titre": "M.", "first_name": "Thomas", "last_name": "Debray"}
            logo_client = InlineImage(template, client.logo, width=Mm(20))
            context = {
                "etude": etude,
                "client": client,
                "responsable": responsable,
                "bon": bon,
                "repr": repr,
                "repr_legale": repr_legale,
                "quali": quali,
                "respo": respo,
                "president": president,
                "phases": phases,
                "poste": poste,
                "nombre_phases": bon.nb_phases(),
                "logo_client": logo_client,
            }
            # Load the template
            env = Environment()
            env.filters["FormatNombres"] = format_nombres
            env.filters["EnLettres"] = en_lettres
            env.filters["ChiffreLettre"] = chiffre_lettres
            # Render the document
            template.render(context, env)
            # Create a temporary in-memory file
            output = BytesIO()
            template.save(output)
            output.seek(0)

            # Save the "fichier" field of the CE
            filename = f"{bon.ref()}.docx"
            response = FileResponse(
                output,
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        except ValueError as ve:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": str(ve)}

        except:
            template = loader.get_template("polls/page_error.html")
            context = {
                "error_message": "Un problème a été détecté dans la base de données."
            }

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def get_object_info(request, model_name, object_id):
    if request.user.is_authenticated:
        try:
            model = apps.get_model(app_label="polls", model_name=model_name)
            object = model.objects.get(id=object_id)
            fields = {}
            for field in object._meta.fields:
                field_name = field.name
                field_value = getattr(object, field_name)
                if field.is_relation and field.many_to_one:
                    # For ForeignKey, return the related object's primary key or other attribute
                    related_obj = getattr(object, field_name)
                    fields[field_name] = related_obj.pk if related_obj else None
                else:
                    fields[field_name] = field_value

            fields["success"] = True
            return JsonResponse(fields)
        except:
            return JsonResponse(
                {
                    "success": False,
                    "error_message": "Un problème a été détecté dans la base de données.",
                }
            )

    else:
        return JsonResponse(
            {
                "success": False,
                "error_message": "You have been identified as not logged in.",
            }
        )


def modifier_bon_commande(request, id_etude, id_bon):
    if request.user.is_authenticated:
        try:
            etude = Etude.objects.get(id=id_etude)
            print("on est la")
            if id_bon == 0:
                print("on est la")
                bon = BonCommande(
                    etude=etude,
                    numero=request.POST["numero_bdc"],
                    periode_de_garantie=request.POST["periode_de_garantie_bdc"],
                    acompte_pourcentage=request.POST["acompte_pourcentage_bdc"],
                )
                bon.save()
                objectifs = request.POST["objectifs_bdc"]
                if objectifs:
                    bon.objectifs = objectifs

                frais_dossier = request.POST["frais_dossier"]
                if frais_dossier:
                    bon.frais_dossier = frais_dossier

                remarque = request.POST["remarque_bdc"]
                if remarque:
                    bon.remarque = remarque
                if request.POST["debut"]:
                    bon.debut = request.POST["debut"]
                if request.POST["fin"]:
                    bon.fin_bdc = request.POST["fin"]

                keys = request.POST.getlist("keys_bdc[]")

                values = request.POST.getlist("values_bdc[]")
                if keys:
                    cahier_des_charges = {
                        key: value for key, value in zip(keys, values) if key
                    }
                    bon.cahier_des_charges = cahier_des_charges
                bon.save()
            else:
                bon = BonCommande.objects.get(id=id_bon)
                bon.remarque = request.POST["remarque_bdc"]
                bon.numero = request.POST["numero_bdc"]
                if request.POST["acompte_pourcentage_bdc"]:
                    bon.acompte_pourcentage = request.POST["acompte_pourcentage_bdc"]
                if request.POST["periode_de_garantie_bdc"]:
                    bon.periode_de_garantie = request.POST["periode_de_garantie_bdc"]
                if request.POST["frais_dossier"]:
                    bon.frais_dossier = request.POST["frais_dossier"]

                if request.POST["objectifs_bdc"]:
                    bon.objectifs = request.POST["objectifs_bdc"]

                if request.POST["debut"]:
                    bon.debut = request.POST["debut"]
                if request.POST["fin"]:
                    bon.fin_bdc = request.POST["fin"]

                keys = request.POST.getlist("keys_bdc[]")
                values = request.POST.getlist("values_bdc[]")
                if keys:
                    cahier_des_charges = {
                        key: value for key, value in zip(keys, values) if key
                    }
                    bon.cahier_des_charges = cahier_des_charges

                bon.etude = etude
                bon.save()

            return redirect("details", modelName="Etude", iD=id_etude)
        except:
            context = {general_context(request)}
            template = loader.get_template("polls/page_error.html")
            context["error_message"] = (
                "Un problème a été détecté dans la base de données."
            )

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


# ---- FONCTIONS POUR STATISTIQUES ------------


def calculate_monthly_sums(user_je):
    september = 9
    monthly_sums = []
    month_ca = 0
    res = []

    for month in range(12):
        current_month = (month + september) % 12
        etudes = Etude.objects.filter(
            je=user_je,
            debut__month=current_month,
            status__in=[Etude.Status.EN_COURS, Etude.Status.TERMINEE],
        )
        total_montant_HT = sum(etude.montant_HT_total() for etude in etudes)
        monthly_sums.append(total_montant_HT)

    for k in range(12):
        month_ca += monthly_sums[k]
        res.append(month_ca)
    return res


def calculate_chiffre_affaire_par_departement(user_je):
    revenues = [0] * 8
    department_index = {
        "IMI": 0,
        "GCC": 1,
        "GMM": 2,
        "SEGF": 3,
        "VET": 4,
        "1A": 5,
        "GI": 6,
        "AUTRE": 7,
    }
    studies = Etude.objects.filter(je=user_je)

    for study in studies:
        if study.montant_HT_total() > 0:
            phases = Phase.objects.filter(etude=study)
            students = study.get_li_students()

            for student in students:
                for phase in phases:
                    if student.departement:
                        revenues[department_index[student.departement]] += (
                            phase.get_montant_HT(student)
                        )

    return revenues


def repartition_CA_etudes_ec_term(etudes):
    dictionaire_CA = {
        "025 en cours": 0,
        "026 en cours": 0,
        "025 terminées 026": 0,
        "026 terminées 026": 0,
    }
    dictionaire_nb = {
        "025 en cours": 0,
        "026 en cours": 0,
        "025 terminées 026": 0,
        "026 terminées 026": 0,
    }
    totale_CA = 0
    totale_nb = 0
    for etude in etudes:
        if etude.mandat == "025":
            if etude.status == "EN_COURS":
                dictionaire_CA["025 en cours"] += etude.montant_HT_total()
                dictionaire_nb["025 en cours"] += 1
                totale_CA += etude.montant_HT_total()
                totale_nb += 1
            elif etude.status == "TERMINEE":
                if etude.fin() is not None and etude.fin() > datetime(2024, 5, 1):
                    dictionaire_CA["025 terminées 026"] += etude.montant_HT_total()
                    dictionaire_nb["025 terminées 026"] += 1
                    totale_CA += etude.montant_HT_total()
                    totale_nb += 1
        elif etude.mandat == "026":
            if etude.status == "EN_COURS":
                dictionaire_CA["026 en cours"] += etude.montant_HT_total()
                dictionaire_nb["026 en cours"] += 1
                totale_CA += etude.montant_HT_total()
                totale_nb += 1
            elif etude.status == "TERMINEE":
                dictionaire_CA["026 terminées 026"] += etude.montant_HT_total()
                dictionaire_nb["026 terminées 026"] += 1
                totale_CA += etude.montant_HT_total()
                totale_nb += 1
    return dictionaire_CA, dictionaire_nb, totale_CA, totale_nb


def nb_etudes_ed_ec_term(user_je):
    etudes = Etude.objects.filter(je=user_je)
    dictionaire = {
        "EN_NEGOCIATION": {0: 0, 1: 0},
        "EN_COURS": {0: 0, 1: 0},
        "TERMINEE": {0: 0, 1: 0},
    }
    for etude in etudes:
        dictionaire[etude.status][0] += 1
        dictionaire[etude.status][1] += etude.montant_HT_total()
    return dictionaire


def calculate_chiffre_affaire_par_type(user_je):
    revenues = [0] * 6
    type_index = {
        "GRANDE_ENTREPRISE": 0,
        "SECTEUR_PUBLIC": 1,
        "START_UP_ET_TPE": 2,
        "PME": 3,
        "ETI": 4,
        "ASSOCIATION": 5,
    }
    studies = Etude.objects.filter(je=user_je)
    for study in studies:
        if study.client:
            montant_HT_total = study.montant_HT_total()
            if montant_HT_total > 0:
                revenues[type_index[study.client.type]] += montant_HT_total
    return revenues


def calculate_chiffre_affaire_par_secteur(user_je):
    revenues = [0] * 8
    secteur_index = {
        "INDUSTRIE": 0,
        "DISTRIBUTION": 1,
        "SECTEUR_PUBLIC": 2,
        "CONSEIL": 3,
        "TRANSPORT": 4,
        "NUMERIQUE": 5,
        "BTP": 6,
        "AUTRE": 7,
    }
    studies = Etude.objects.filter(je=user_je)
    for study in studies:
        if study.client:
            montant_HT_total = study.montant_HT_total()
            if montant_HT_total > 0:
                revenues[secteur_index[study.client.secteur]] += montant_HT_total
    return revenues


# -----------------------


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
    query = request.GET.get("query", "")
    if query:
        print(f"query: {query}")
        keywords = query.split()
        suggestions_etude = Etude.objects.filter(je=request.user.je)
        suggestions_client = Client.objects.filter(je=request.user.je)
        suggestions_student = Student.objects.filter(je=request.user.je)
        for keyword in keywords:
            suggestions_etude = suggestions_etude.filter(
                Q(titre__icontains=keyword)
                | Q(numero__icontains=keyword)
                | Q(responsable__student__first_name__icontains=keyword)
                | Q(responsable__student__last_name__icontains=keyword)
                | Q(client__nom_societe__icontains=keyword)
                | Q(resp_qualite__student__first_name__icontains=keyword)
                | Q(resp_qualite__student__last_name__icontains=keyword)
            )
            suggestions_client = suggestions_client.filter(
                Q(nom_societe__icontains=keyword) | Q(raison_sociale__icontains=keyword)
            )
            suggestions_student = suggestions_student.filter(
                Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword)
            )
        count_client = suggestions_client.count()

        print("count_client: ", count_client)

        count_student = suggestions_student.count()

        print("count_student: ", count_student)
        # We set this variable in the case there is no studies in the suggestions to not count 1 for an empty set ?
        suppression_etude_c = max(1, count_client)

        print(f" Suppression_etude_c:{suppression_etude_c}")

        suppression_etude_s = max(1, count_student)

        print(f" Suppression_etude_s:{suppression_etude_s}")

        suggestions_etude = suggestions_etude.order_by("-debut")[
            : 5 - suppression_etude_c - suppression_etude_s
        ]

        print(f"suggestions etude: {suggestions_etude}")
        nombre_etude = suggestions_etude.count()
        suggestions_client = suggestions_client[
            : 5 - nombre_etude - suppression_etude_s
        ]

        print(f"suggestions client: {suggestions_client}")
        nombre_client = suggestions_client.count()
        suggestions_student = suggestions_student[: 5 - nombre_etude - nombre_client]

        print(f"suggestions student: {suggestions_student}")
        return JsonResponse(
            {
                "suggestions_etude": list(suggestions_etude.values_list("titre", "id")),
                "suggestions_client": list(
                    suggestions_client.values_list("nom_societe", "id")
                ),
                "suggestions_student": list(
                    suggestions_student.values_list("first_name", "last_name", "id")
                ),
            }
        )
    else:
        return JsonResponse(
            {
                "suggestions_etude": [],
                "suggestions_client": [],
                "suggestions_student": [],
            }
        )


def search_suggestions_student(request, id_etude):
    query = request.GET.get("query", "")
    if query:
        keywords = query.split()
        suggestions_student = Student.objects.filter(je=request.user.je)
        for keyword in keywords:
            suggestions_student = suggestions_student.filter(
                Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword)
            )
        suggestions_student = suggestions_student[:5]
        etude = Etude.objects.get(id=id_etude)
        return JsonResponse(
            {
                "suggestions_student": [
                    [
                        student.first_name,
                        student.last_name,
                        student.id,
                        student.phases_etude(etude).count(),
                        student.nb_etudes_realisees(),
                    ]
                    for student in suggestions_student.all()
                ]
            }
        )
    else:
        return JsonResponse({"suggestions_student": []})


def client_suggestions(request):
    if request.user.is_authenticated:
        query = request.GET.get("q", "")
        if query:
            results = Client.objects.filter(nom_societe__icontains=query)
            results_list = [{"id": obj.id, "name": obj.__str__()} for obj in results]
        else:
            results_list = []

        return JsonResponse({"results": results_list})
    else:
        return JsonResponse({"results": []})


def search(request):
    print("search atteint")
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
    query = request.GET.get("search-input", "")
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
            liste_res_etude.append(
                resultats_etude.filter(
                    Q(titre__icontains=keyword)
                    | Q(numero__icontains=keyword)
                    | Q(responsable__student__first_name__icontains=keyword)
                    | Q(responsable__student__last_name__icontains=keyword)
                    | Q(client__nom_societe__icontains=keyword)
                    | Q(resp_qualite__student__first_name__icontains=keyword)
                    | Q(resp_qualite__student__last_name__icontains=keyword)
                )
            )
            liste_res_client.append(
                resultats_client.filter(
                    Q(nom_societe__icontains=keyword)
                    | Q(raison_sociale__icontains=keyword)
                )
            )
            liste_res_student.append(
                resultats_student.filter(
                    Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword)
                )
            )
        for i in range(len(liste_res_etude)):
            combined_res_etude |= liste_res_etude[i]
            combined_res_client |= liste_res_client[i]
            combined_res_student |= liste_res_student[i]
        combined_res_etude = combined_res_etude.annotate(
            appearances_count=Count("id", distinct=True)
        ).order_by("-appearances_count")
        combined_res_client = combined_res_client.annotate(
            appearances_count=Count("id", distinct=True)
        ).order_by("-appearances_count")
        combined_res_student = combined_res_student.annotate(
            appearances_count=Count("id", distinct=True)
        ).order_by("-appearances_count")
        final_res_etude = combined_res_etude.all()
        final_res_client = combined_res_client.all()
        final_res_student = combined_res_student.all()
        context = {
            "query": query,
            "res_etude": final_res_etude,
            "res_client": final_res_client,
            "res_student": final_res_student,
            "liste_messages": liste_messages,
            "message_count": message_count,
            "notification_list": notification_list,
            "notification_count": notification_count,
        }
        template = loader.get_template("polls/search_results.html")
        return HttpResponse(template.render(context, request))
    else:
        context = {
            "query": query,
            "liste_messages": liste_messages,
            "message_count": message_count,
            "notification_list": notification_list,
            "notification_count": notification_count,
        }
        template = loader.get_template("polls/search_results.html")
        return HttpResponse(template.render(context, request))


def ajouter_phase(request, id_etude):
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                fetchform = AddPhase(request.POST)
                if fetchform.is_valid():
                    etude = Etude.objects.get(id=id_etude)
                    numero_bdc = request.POST.get("numero_bdc", None)
                    if etude.type_convention == "Convention cadre":
                        if not numero_bdc:
                            raise ValueError(
                                "Veuillez préciser le bon de commande de la phase."
                            )
                        else:
                            bdcs = BonCommande.objects.filter(
                                etude=etude, numero=numero_bdc
                            )
                            if not bdcs.exists():
                                raise ValueError(
                                    "Le numéro de bon de commande indiqué ne correspond à aucun bon de commande existant."
                                )
                    count_phase = Phase.objects.filter(etude=etude).count()
                    new_phase = fetchform.save(
                        commit=True, id_etude=id_etude, numero=count_phase + 1
                    )
                    if etude.type_convention == "Convention cadre" and numero_bdc:
                        bdcs = BonCommande.objects.filter(
                            etude=etude, numero=numero_bdc
                        )
                        bdc = None
                        if bdcs.exists():
                            bdc = bdcs[0]
                        else:
                            gen_context = general_context(request)
                            gen_context["error_message"] = (
                                "Le numéro de bon de commande indiqué ne correspond à aucun bon de commande existant."
                            )
                            template = loader.get_template("polls/page_error.html")
                            return HttpResponse(template.render(gen_context, request))
                        new_ass_phase_bdc = AssociationPhaseBDC(
                            phase=new_phase, bon_de_commande=bdc
                        )
                        new_ass_phase_bdc.save()
                else:
                    gen_context = general_context(request)
                    gen_context["error_message"] = (
                        "Le formulaire envoyé comporte une erreur."
                    )
                    template = loader.get_template("polls/page_error.html")
                    return HttpResponse(template.render(gen_context, request))
            except ValueError as ve:
                # Handle any ValueError, including the case when `numero_bdc` is None
                template = loader.get_template("polls/page_error.html")
                context = {"error_message": str(ve)}
                return HttpResponse(template.render(context, request))

        return redirect("details", modelName="Etude", iD=id_etude)
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))


def ajouter_facture(request, id_etude):
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                fetchform = AddFacture(request.POST)
                if fetchform.is_valid():
                    etude = Etude.objects.get(id=id_etude)
                    numero_bdc = request.POST.get("numero_bdc_fac", None)

                    # Check if `numero_bdc` is None and raise an error if necessary
                    if etude.type_convention == "Convention cadre":
                        if not numero_bdc:
                            raise ValueError(
                                "Veuillez préciser le bon de commande de la facture."
                            )
                        else:
                            bdcs = BonCommande.objects.filter(
                                etude=etude, numero=numero_bdc
                            )
                            if not bdcs.exists():
                                raise ValueError(
                                    "Le numéro de bon de commande indiqué ne correspond à aucun bon de commande existant."
                                )

                    # Proceed to save the new facture if numero_bdc is not None
                    new_facture = fetchform.save(commit=True, id_etude=id_etude)

                    # Handle the BDC association
                    if numero_bdc:
                        bdcs = BonCommande.objects.filter(
                            etude=etude, numero=numero_bdc
                        )
                        bdc = None
                        if bdcs.exists():
                            bdc = bdcs[0]
                        else:
                            gen_context = general_context(request)
                            gen_context["error_message"] = (
                                "Le numéro de bon de commande indiqué ne correspond à aucun bon de commande existant."
                            )
                            template = loader.get_template("polls/page_error.html")
                            return HttpResponse(template.render(gen_context, request))

                        # Associate facture with BDC
                        new_ass_fac_bdc = AssociationFactureBDC(
                            facture=new_facture, bon_de_commande=bdc
                        )
                        new_ass_fac_bdc.save()
                    return redirect("details", modelName="Etude", iD=id_etude)

                else:
                    # Handle form errors
                    gen_context = general_context(request)
                    gen_context["error_message"] = (
                        "Le formulaire envoyé comporte une erreur."
                    )
                    template = loader.get_template("polls/page_error.html")
                    return HttpResponse(template.render(gen_context, request))

            except ValueError as ve:
                # Handle any ValueError, including the case when `numero_bdc` is None
                template = loader.get_template("polls/page_error.html")
                context = {"error_message": str(ve)}
                return HttpResponse(template.render(context, request))

        # Redirect to details page if everything went smoothly
        return redirect("details", modelName="Etude", iD=id_etude)

    else:
        # Redirect to login if not authenticated
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))


def nouveau_BV(request, id_etude, id_eleve):
    if request.user.is_authenticated:
        try:
            etude = Etude.objects.get(id=id_etude)
            eleve = Student.objects.get(id=id_eleve)
            je = eleve.je
            nb_JEH = 0
            montant_HT = 0.0
            if request.method == "POST":
                for phase in etude.phases.all():
                    my_checkbox_value = request.POST.get(f"checkInputPhase{phase.id}")

                    if my_checkbox_value is not None:
                        nb_JEH += phase.get_nb_JEH_eleve(eleve)
                        montant_HT += phase.get_montant_HT(eleve)
            nouveau_BV = BV(
                etude=etude,
                eleve=eleve,
                date_emission=timezone.now().date(),
                nb_JEH=nb_JEH,
                retr_brute=montant_HT,
            )
            nouveau_BV.save()

            return redirect("BVs")

        except:
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
            template = loader.get_template("polls/page_error.html")
            context = {
                "error_message": "Erreur dans le téléversement du BV.",
                "liste_messages": liste_messages,
                "message_count": message_count,
            }
            return HttpResponse(template.render(context, request))
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))


def generer_BV(request, id_bv):
    if request.user.is_authenticated:
        try:
            bv = BV.objects.get(id=id_bv)
            eleve = bv.eleve
            je = eleve.je
            etude = bv.etude

            chemin_absolu = os.path.join("polls/static/polls/template_bv_sylog.xlsx")

            classeur = openpyxl.load_workbook(chemin_absolu)

            # Sélectionner la feuille de calcul
            feuille = classeur.active

            # Modifier la cellule G4
            feuille["H2"] = f"N° {bv}"
            feuille["I13"] = bv.retr_brute
            feuille["I14"] = bv.nb_JEH
            feuille["G4"] = eleve.first_name + " " + eleve.last_name
            feuille["G6"] = eleve.adress
            feuille["G8"] = eleve.code_postal + " " + eleve.country
            feuille["I3"] = datetime.datetime.now().strftime("%d %B %Y")
            feuille["C13"] = etude.ref()

            feuille["C14"] = (
                f"{etude.ref()}rdm-{eleve.last_name[0] + eleve.first_name[0]}"
            )

            # assignation_jeh = AssignationJEH.objects.get(etude=etude, student=eleve)
            # feuille['C13']= assignation_jeh.reference
            feuille["H10"] = eleve.numero_ss

            # info JE
            feuille["I15"] = je.base_urssaf
            feuille["F23"] = je.taux_ATMP
            # Sauvegarder les modifications dans le fichier Excel
            output = BytesIO()
            classeur.save(output)
            output.seek(0)

            # Specify a new name for the downloaded file
            download_filename = f"BV_{bv}_{eleve.last_name.upper()}_{etude.ref()}.xlsx"

            # Return the file with the new filename
            response = FileResponse(
                output, as_attachment=True, filename=download_filename
            )

            return response

        except ValueError as ve:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": str(ve)}

        except:
            template = loader.get_template("polls/page_error.html")
            context = {
                "error_message": "Un problème a été détecté dans la base de données."
            }

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def csv_import_etudiants(request):
    if request.user.is_authenticated:
        # try:

        chemin_absolu = os.path.join("polls/static/polls/import_etudiants.csv")

        with open(chemin_absolu, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=";")

            # Create an in-memory file object to write the CSV content
            output = BytesIO()

            # Write the CSV content to the in-memory file object
            writer = csv.writer(output)
            for row in reader:
                writer.writerow(row)

            # Reset the pointer to the beginning of the file for download
            output.seek(0)

            # Specify the filename for the download
            download_filename = "import_etudiants.csv"

            # Return the file with the correct content type and as an attachment
            response = HttpResponse(output, content_type="text/csv")
            response["Content-Disposition"] = (
                f"attachment; filename={download_filename}"
            )

            return response

        # except ValueError as ve:
        template = loader.get_template("polls/page_error.html")
        context = {"error_message": str(ve)}

        # except:
        template = loader.get_template("polls/page_error.html")
        context = {
            "error_message": "Un problème a été détecté dans la base de données."
        }

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def ajouter_assignation_jeh(request, id_etude, id_phase):
    if request.user.is_authenticated:
        if request.method == "POST":
            fetchform = AddIntervenant(request.POST)
            if fetchform.is_valid():
                try:
                    etude = Etude.objects.get(id=id_etude)
                    phase = Phase.objects.get(id=id_phase)
                    eleve = fetchform.cleaned_data["eleve"]
                    ass_jeh = AssignationJEH.objects.filter(phase=phase, eleve=eleve)
                    if ass_jeh.exists():
                        only_ass_jeh = ass_jeh[0]
                        only_ass_jeh.nombre_JEH = fetchform.cleaned_data["nombre_JEH"]
                        only_ass_jeh.pourcentage_retribution = fetchform.cleaned_data[
                            "pourcentage_retribution"
                        ]
                        only_ass_jeh.save()
                    else:
                        fetchform.save(
                            commit=True, id_etude=id_etude, id_phase=id_phase
                        )
                except:
                    pass
        return redirect("details", modelName="Etude", iD=id_etude)
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))


def recrutement(request, id_url):  # Controler les dates
    if request.method == "GET":
        try:
            uuid_url = UUID(id_url)
            etude = Etude.objects.get(id_url=uuid_url)
            if (
                etude.date_fin_recrutement is None
                or etude.date_debut_recrutement is None
                or timezone.now().date() < etude.date_debut_recrutement
                or timezone.now().date() > etude.date_fin_recrutement
            ):
                raise ValueError("")
            context = {"etude": etude, "form": Recrutement()}
            template = loader.get_template("polls/recrutement.html")
        except:
            context = {
                "error_message": "Cette page n'est associée à aucune mission, ou vous tentez d'y accéder hors période de recrutement."
            }
            template = loader.get_template("polls/recrutement_fail.html")
    else:
        try:
            uuid_url = UUID(id_url)
            etude = Etude.objects.get(id_url=uuid_url)
            recrutement = Recrutement(request.POST)
            if recrutement.is_valid():
                existing_students = Student.objects.filter(
                    mail=recrutement.cleaned_data["email"],
                    first_name__iexact=recrutement.cleaned_data["prenom"],
                    last_name__iexact=recrutement.cleaned_data["nom"],
                )
                student = None
                detail_message = None
                if existing_students.exists():
                    student = existing_students[0]
                    detail_message = (
                        "Votre profil a été reconnu dans la base de données."
                    )
                else:
                    student = Student(
                        je=request.user.je,
                        titre=recrutement.cleaned_data["titre"],
                        first_name=recrutement.cleaned_data["prenom"],
                        last_name=recrutement.cleaned_data["nom"],
                        mail=recrutement.cleaned_data["email"],
                        promotion=recrutement.cleaned_data["promotion"],
                        departement=recrutement.cleaned_data["departement"],
                    )
                    student.save()
                    detail_message = (
                        "D'après nos données, il s'agit de votre première candidature."
                    )
                candidature = Candidature(
                    eleve=student,
                    motivation=recrutement.cleaned_data["motivation"],
                    etude=etude,
                )
                candidature.save()

                notif = Notification(
                    description=student.__str__()
                    + " a soumis sa candidature pour la mission "
                    + etude.ref(),
                    date_effet=timezone.now().date(),
                    date_echeance=(timezone.now() + timedelta(weeks=2)).date(),
                    href_redirect=reverse(
                        "details", kwargs={"modelName": "Etude", "iD": etude.id}
                    ),
                )
                notif.save()
                all_responsables = [etude.responsable]
                for representant in all_responsables:
                    notif.utilisateur.add(representant)

                context = {"detail_message": detail_message}
                template = loader.get_template("polls/recrutement_succes.html")
            else:
                context = {
                    "error_message": "Votre candidature semble contenir des données corrompues."
                }
                template = loader.get_template("polls/recrutement_fail.html")
        except:
            context = {"error_message": "Votre candidature n'a pas pu aboutir."}
            template = loader.get_template("polls/recrutement_fail.html")
    return HttpResponse(template.render(context, request))


def modifier_je(request, id):
    if request.user.is_authenticated:
        je = get_object_or_404(JE, id=id)

        if request.method == "POST":
            # Met à jour les champs avec les données du formulaire
            je.nom = request.POST.get("nom")
            je.raison_sociale = request.POST.get("raison_sociale")
            je.rue = request.POST.get("rue")
            je.ville = request.POST.get("ville")
            je.code_postal = request.POST.get("code_postal")
            je.siret = request.POST.get("siret")
            je.APE = request.POST.get("APE")
            je.TVA = request.POST.get("TVA")
            je.IBAN = request.POST.get("IBAN")
            je.BIC = request.POST.get("BIC")
            je.chiffres_affaires = request.POST.get("chiffres_affaires")
            je.base_urssaf = request.POST.get("base_urssaf")
            je.save()

            # Redirection vers la page je_detail après la sauvegarde
            return HttpResponseRedirect(reverse("je_detail"))

        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=400
        )
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))


def modifier_recrutement_etude(request, iD):
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                etude = Etude.objects.get(id=iD)
                if request.POST["debut"]:
                    etude.date_debut_recrutement = request.POST["debut"]
                if request.POST["fin"]:
                    etude.date_fin_recrutement = request.POST["fin"]
                etude.save()
                return JsonResponse(
                    {
                        "success": True,
                        "debut": etude.date_debut_recrutement,
                        "fin": etude.date_fin_recrutement,
                    }
                )
            except:
                return JsonResponse({"success": False})
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))


def modifier_etude(request, iD):
    if request.user.is_authenticated:
        etude = get_object_or_404(Etude, id=iD)
        numero_ori = etude.numero
        annee_encours = datetime.datetime.now().year
        numero_list = list(
            Etude.objects.filter(
                je=request.user.je, date_creation__year=annee_encours
            ).values_list("numero", flat=True)
        )
        numero_list.remove(numero_ori)
        if request.method == "POST":
            debut = request.POST.get("debut")
            fin_etude = request.POST.get("fin")
            frais_dossier = request.POST.get("frais_dossier")
            remarque = request.POST.get("remarque")
            numero = int(request.POST.get("numero"))

            # Allow 'debut' to be null, and only update if it's provided
            if debut:
                etude.debut = debut
            if fin_etude:
                etude.fin_etude = fin_etude

            if not numero:
                return JsonResponse(
                    {"success": False, "message": "Le numéro est obligatoire."},
                    status=400,
                )

            if numero:
                if numero not in numero_list:
                    etude.numero = numero

                else:
                    etude_deja_exist = Etude.objects.filter(numero=numero).first()
                    return JsonResponse(
                        {
                            "success": False,
                            "message": f"l'étude '{etude_deja_exist.ref()} - {etude_deja_exist.titre}' à déjà ce numéro",
                        },
                        status=400,
                    )

            etude.frais_dossier = frais_dossier
            etude.remarque = remarque
            etude.save()

            # Redirect to the details page with the correct modelName
            return JsonResponse(
                {
                    "success": True,
                    "message": "Étude modifiée avec succès.",
                    "redirect": reverse("details", args=["Etude", iD]),
                }
            )

    else:
        return JsonResponse(
            {
                "success": False,
                "message": "Vous devez être connecté pour modifier l'étude.",
            },
            status=401,
        )

    return JsonResponse(
        {"success": False, "message": "Invalid request method"}, status=400
    )


def modifier_etude_form(request, iD):
    if request.user.is_authenticated:
        etude = get_object_or_404(Etude, id=iD)
        annee_etude = etude.date_creation.year
        print(annee_etude)
        numero_ori = etude.numero
        numero_list = list(
            Etude.objects.filter(
                je=request.user.je, date_creation__year=annee_etude
            ).values_list("numero", flat=True)
        )
        print(numero_list, numero_ori)
        numero_list.remove(numero_ori)
        if request.method == "POST":
            debut = request.POST.get("debut")
            fin_etude = request.POST.get("fin")
            frais_dossier = request.POST.get("frais_dossier")
            if frais_dossier:
                etude.frais_dossier = frais_dossier
            remarque = request.POST.get("remarque")
            numero = int(request.POST.get("numero"))

            # Allow 'debut' to be null, and only update if it's provided
            if debut:
                etude.debut = debut
            if fin_etude:
                etude.fin_etude = fin_etude

            if not numero:
                return JsonResponse(
                    {"success": False, "message": "Le numéro est obligatoire."},
                    status=400,
                )

            if numero:
                if numero not in numero_list:
                    etude.numero = numero

                else:
                    etude_deja_exist = Etude.objects.filter(numero=numero).first()
                    return JsonResponse(
                        {
                            "success": False,
                            "message": f"l'étude '{etude_deja_exist.ref()} - {etude_deja_exist.titre}' à déjà ce numéro",
                        },
                        status=400,
                    )

            etude.remarque = remarque
            etude.save()
            modelName = "Etude"
            return HttpResponseRedirect(reverse("details", args=[modelName, iD]))

        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=400
        )
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))


def verifier_etude(request, iD):
    if request.user.is_authenticated:
        # Fetch the Etude instance using the provided iD
        etude = get_object_or_404(Etude, id=iD)

        if request.method == "POST":
            # Get the form data from the request
            debut = request.POST.get("debut")
            if debut:
                etude.debut = debut

            frais_dossier = request.POST.get("frais_dossier")
            if frais_dossier:
                etude.frais_dossier = frais_dossier

            remarque = request.POST.get("remarque")
            if remarque:
                etude.remarque = remarque

            client_description = request.POST.get("client_description")
            if etude.client and client_description:
                client = etude.client
                client.description = client_description
                client.save()

            etude_contexte = request.POST.get("etude_contexte")
            if etude_contexte:
                etude.contexte = etude_contexte

            paragraphe_intervenant_devis = request.POST.get(
                "paragraphe_intervenant_devis"
            )
            if paragraphe_intervenant_devis:
                etude.paragraphe_intervenant_devis = paragraphe_intervenant_devis

            cdp_mail = request.POST.get("chefdep")
            cdp = Member.objects.filter(email=cdp_mail).first()
            if cdp:
                etude.responsable = cdp

            quali_mail = request.POST.get("qualite")
            quali = Member.objects.filter(email=quali_mail).first()
            if quali:
                etude.resp_qualite = quali

            garantie = request.POST.get("per_gara")
            if garantie:
                etude.periode_de_garantie = garantie
            objectifs = request.POST.get("objectifs")
            if objectifs:
                etude.objectifs = objectifs
            methodologie = request.POST.get("methodologie")
            if methodologie:
                etude.methodologie = methodologie

            element_a_fournir = request.POST.get("element_a_fournir")
            if element_a_fournir:
                etude.element_a_fournir = element_a_fournir

            keys = request.POST.getlist("keys[]")
            values = request.POST.getlist("values[]")

            if keys and values:
                cahier_des_charges = {
                    key: value for key, value in zip(keys, values) if key
                }
                etude.cahier_des_charges = cahier_des_charges

            etude.save()

            # Redirect to the details page with the correct modelName
            modelName = "Etude"
            return HttpResponseRedirect(reverse("details", args=[modelName, iD]))

        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=400
        )
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))


def remarque_etude(request, iD):
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                raw_data = request.body
                data = json.loads(raw_data.decode("utf-8"))  # Decode bytes to string
                content = data.get("content", "")
                etude = Etude.objects.get(id=iD)
                etude.remarque = content
                etude.save()
                return JsonResponse({"success": True})
            except:
                return JsonResponse({"success": False})
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))


def signature_document(request, model, iD):
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                new_date = request.POST.get("new_date")

                if model == "CE":
                    convention = ConventionEtude.objects.get(id=iD)
                    etude = convention.etude
                    if new_date:
                        convention.date_signature = new_date
                        etude = convention.etude
                        etude.debut = new_date
                        etude.save()
                    convention.save()

                elif model == "Devis":
                    devis = Devis.objects.get(id=iD)
                    etude = devis.etude
                    if new_date:
                        devis.date_signature = new_date

                        devis.save()
                elif model == "AvCE":
                    avenant = AvenantConventionEtude.objects.get(id=iD)
                    etude = avenant.ce.etude
                    if new_date:
                        avenant.date_signature = new_date

                        avenant.save()

                elif model == "CC":
                    connvention = ConventionCadre.objects.get(id=iD)
                    etude = connvention.etude
                    if new_date:
                        connvention.date_signature = new_date
                        etude.debut = new_date
                        etude.save()
                        connvention.save()

                elif model == "BDC":
                    bdc = BonCommande.objects.get(id=iD)
                    etude = bdc.etude
                    if new_date:
                        bdc.debut = new_date

                        bdc.save()

                return redirect("details", modelName="Etude", iD=etude.id)
            except Exception as e:
                return JsonResponse({"success": False, "error": str(e)})
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))


def signature_devis(request, iD):
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                raw_data = request.body
                data = json.loads(raw_data.decode("utf-8"))  # Decode bytes to string
                content = data.get("content", "")

                devis = Devis.objects.get(id=iD)
                if not content:
                    devis.date = None
                else:
                    try:
                        date_signature = datetime.datetime.strptime(
                            content, "%d/%m/%Y"
                        ).date()
                    except ValueError:
                        # Return a message if the date format is invalid
                        return JsonResponse(
                            {
                                "success": False,
                                "message": "mettre la date au format JJ/MM/AAAA",
                            }
                        )

                    devis.date = date_signature

                    devis.save()
                return JsonResponse({"success": True})
            except Exception as e:
                return JsonResponse({"success": False, "error": str(e)})
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))


def send_mail_demarchage(request, iD):
    if request.user.is_authenticated:
        context = general_context(request)
        if request.method == "POST":
            try:
                google_user = request.user.social_auth.get(provider="google-oauth2")
                context["google_user"] = google_user
                # Extract OAuth2 tokens
                credentials = Credentials(
                    token=google_user.extra_data["access_token"],
                    refresh_token=google_user.extra_data["refresh_token"],
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=conf_settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                    client_secret=conf_settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
                )

                # Build Gmail API service
                service = build("gmail", "v1", credentials=credentials)

                # Create the email message
                html_message = loader.render_to_string(
                    "polls/mail_template.html",
                    {
                        "message": request.POST["message"],
                        "name": request.POST["name"],
                        "signature": request.POST["signature"],
                    },
                )
                message = MIMEText(html_message, "html")
                message["to"] = request.POST["destinataire"]
                message["subject"] = request.POST["subject"]
                raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
                content = {"raw": raw}

                # Send the email using the Gmail API
                send_message = (
                    service.users().messages().send(userId="me", body=content).execute()
                )

                # representant = Representant.objects.get(id=iD)
                # representant.contenu_mail=request.POST['message']
                # representant.demarchage="ATTENTE_REPONSE"
                # representant.save()
                return redirect("demarchage")
            except UserSocialAuth.DoesNotExist:
                context = general_context(request)
                context["error_message"] = (
                    "Vous n'êtes pas connecté avec votre compte Google. (voir paramètres)"
                )
                template = loader.get_template("polls/page_error.html")
            except:
                context = general_context(request)
                context["error_message"] = (
                    "Vous n'avez pas de connexion ou votre serveur d'envoi de mail n'est pas fonctionnel."
                )
                template = loader.get_template("polls/page_error.html")
        else:
            context = general_context(request)
            context["error_message"] = (
                "Vous tentez d'utiliser une fonctionnalité de manière inattendue."
            )
            template = loader.get_template("polls/page_error.html")
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def settings(request):
    if request.user.is_authenticated:
        context = general_context(request)
        try:
            google_user = request.user.social_auth.get(provider="google-oauth2")
            context["google_user"] = google_user
            print(google_user.extra_data)
            context["google_email"] = google_user.extra_data["email"]
        except UserSocialAuth.DoesNotExist:
            context["google_user"] = None
            context["alert_message"] = "L'authentification Google a échoué!"
        except:
            context["alert_message"] = (
                "L'authentification Google a fonctionné, mais vous n'avez pas accordé les autorisations."
            )
        template = loader.get_template("polls/settings.html")
        if request.method == "GET":
            context["form_param"] = SetParametresUtilisateur(
                instance=request.user.parametres
            )
        else:
            try:
                fetchform = request.POST
                param = SetParametresUtilisateur(
                    fetchform, instance=request.user.parametres
                )
                if param.is_valid():
                    param.save()
                    context["form_param"] = SetParametresUtilisateur(
                        instance=request.user.parametres
                    )
                    context["alert_message"] = "Modifications enregistrées!"
                else:
                    context["form_param"] = SetParametresUtilisateur(
                        instance=request.user.parametres
                    )
                    context["alert_message"] = "La modification n'a pas aboutie!"
            except:
                context["form_param"] = SetParametresUtilisateur(
                    instance=request.user.parametres
                )
                context["alert_message"] = "La modification n'a pas aboutie!"
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
            print("on est la")
            etude = Etude.objects.get(id=id_etude)
            eleve = Student.objects.get(id=id_student)

            for phase in etude.phases.all():
                if (
                    request.POST[("nb_jeh_phase" + str(phase.id))]
                    and request.POST[("pourcentage_retribution_phase" + str(phase.id))]
                ):
                    print("on est lala")
                    nb_jeh = request.POST[("nb_jeh_phase" + str(phase.id))]
                    pourcentage_retribution = request.POST[
                        ("pourcentage_retribution_phase" + str(phase.id))
                    ]
                    if nb_jeh is not None and pourcentage_retribution is not None:
                        existing_ass_jeh = AssignationJEH.objects.filter(
                            phase=phase, eleve=eleve
                        )
                        if existing_ass_jeh.exists():
                            retrieve_ass_jeh = existing_ass_jeh[0]
                            retrieve_ass_jeh.nombre_JEH = nb_jeh
                            retrieve_ass_jeh.pourcentage_retribution = (
                                pourcentage_retribution
                            )
                            retrieve_ass_jeh.save()
                        else:
                            new_ass_jeh = AssignationJEH(
                                phase=phase,
                                eleve=eleve,
                                nombre_JEH=nb_jeh,
                                pourcentage_retribution=pourcentage_retribution,
                            )
                            new_ass_jeh.save()
            return redirect("details", modelName="Etude", iD=id_etude)

        except:
            context = general_context(request)
            template = loader.get_template("polls/page_error.html")
            context["error_message"] = "Erreur dans l'identification de la mission."
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
        if request.method == "POST":
            try:
                etude = Etude.objects.get(id=id_etude)
                signature = None
                modif_budget = False
                modif_delais = False
                for phase in etude.phases.all():
                    suppression_key = f"suppression{phase.id}"
                    if suppression_key in request.POST:
                        modif_budget = True
                    if float(request.POST["nb_jeh" + str(phase.id)]) != float(
                        phase.nb_JEH
                    ):
                        modif_budget = True
                    if float(request.POST["debut" + str(phase.id)]) + float(
                        request.POST["duree" + str(phase.id)]
                    ) != float(phase.duree_semaine) + float(phase.debut_relatif):
                        print("ouiii !!!!")
                        print(request.POST["debut" + str(phase.id)])
                        print(request.POST["duree" + str(phase.id)])
                        print(
                            float(request.POST["debut" + str(phase.id)])
                            + float(request.POST["duree" + str(phase.id)])
                        )
                        print(float(phase.duree_semaine) + float(phase.debut_relatif))
                        modif_delais = True

                nouveau_frais_dossier = request.POST["frais_dossier"]
                if float(nouveau_frais_dossier) != etude.frais_dossier:
                    modif_budget = True
                new_avenant = AvenantConventionEtude(
                    ce=etude.convention(),
                    numero=request.POST["numero"],
                    date_signature=signature,
                    objet=request.POST["objet"],
                    avenant_budget=modif_budget,
                    avenant_delais=modif_delais,
                )
                if (
                    nouveau_frais_dossier is not None
                    and etude.frais_dossier != nouveau_frais_dossier
                ):
                    new_avenant.nouveau_frais_dossier = nouveau_frais_dossier
                    new_avenant.ancien_frais_dossier = etude.frais_dossier
                    etude.frais_dossier = nouveau_frais_dossier
                new_avenant.save()
                for phase in etude.phases.all():
                    suppression_key = f"suppression{phase.id}"
                    if suppression_key in request.POST:
                        print(f"supprimer phase {phase.id}")
                        supp_phase = SuppressionPhase(
                            avenant_ce=new_avenant, phase=phase
                        )
                        supp_phase.save()
                        phase.supprimee = True
                    if request.POST["debut" + str(phase.id)] != phase.debut_relatif:
                        n_debut = request.POST["debut" + str(phase.id)]
                        deb_phase = ModificationDebutPhase(
                            avenant_ce=new_avenant,
                            phase=phase,
                            nouveau_debut=n_debut,
                            ancien_debut=phase.debut_relatif,
                        )
                        deb_phase.save()
                        phase.debut_relatif = n_debut
                    if request.POST["duree" + str(phase.id)] != phase.duree_semaine:
                        n_duree = request.POST["duree" + str(phase.id)]
                        dur_phase = ModificationDureePhase(
                            avenant_ce=new_avenant,
                            phase=phase,
                            nouvelle_duree=n_duree,
                            ancienne_duree=phase.duree_semaine,
                        )
                        dur_phase.save()
                        phase.duree_semaine = n_duree
                    if request.POST["nb_jeh" + str(phase.id)] != phase.nb_JEH:
                        n_jeh = request.POST["nb_jeh" + str(phase.id)]
                        jeh_phase = ModificationJEHPhase(
                            avenant_ce=new_avenant,
                            phase=phase,
                            nouveau_nombre_JEH=n_jeh,
                            ancien_nombre_JEH=phase.nb_JEH,
                        )
                        jeh_phase.save()
                        phase.nb_JEH = n_jeh
                    phase.save(
                        update_fields=[
                            "supprimee",
                            "debut_relatif",
                            "duree_semaine",
                            "nb_JEH",
                        ]
                    )
                    etude.save()
                return redirect("details", modelName="Etude", iD=id_etude)
            except:
                template = loader.get_template("polls/page_error.html")
                context = {
                    "liste_messages": liste_messages,
                    "message_count": message_count,
                    "error_message": "Le formulaire envoyé est incohérent : certaines données sont manquantes, certaines données sont inattendues.",
                    "notification_list": notification_list,
                    "notification_count": notification_count,
                }
        else:
            template = loader.get_template("polls/page_error.html")
            context = {
                "liste_messages": liste_messages,
                "message_count": message_count,
                "error_message": "Erreur de requête.",
                "notification_list": notification_list,
                "notification_count": notification_count,
            }
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
        if request.method == "POST":
            try:
                client = Client.objects.get(id=id_client)
                fetchform = AddRepresentant(request.POST)
                if fetchform.is_valid():
                    new_representant = fetchform.save(commit=False)
                    new_representant.client = client
                    new_representant.save()
                    return redirect("details", modelName="Client", iD=id_client)
                else:
                    raise ValueError("Formulaire corrompu")
            except:
                template = loader.get_template("polls/page_error.html")
                context = {
                    "liste_messages": liste_messages,
                    "message_count": message_count,
                    "error_message": "Le formulaire envoyé est incohérent : certaines données sont manquantes, certaines données sont inattendues.",
                    "notification_list": notification_list,
                    "notification_count": notification_count,
                }
        else:
            template = loader.get_template("polls/page_error.html")
            context = {
                "liste_messages": liste_messages,
                "message_count": message_count,
                "error_message": "Erreur de requête.",
                "notification_list": notification_list,
                "notification_count": notification_count,
            }
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def supprimer_representant(request, id_representant):
    if request.user.is_authenticated:
        representant = get_object_or_404(Representant, id=id_representant)
        id_client = representant.client.id
        representant.delete()
        return redirect("details", modelName="Client", iD=id_client)
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def facture_redirect(request, fac_id):
    if request.user.is_authenticated:
        print("redirect fonc")
        user_je = request.user.je
        facture = Facture.objects.get(id=fac_id)
        facture.date_emission = date.today()
        etude = facture.etude
        ref_conv = f"{etude.type_convention} concernant l'étude {etude.ref()} en référence à la "
        if etude.type_convention == "Convention d'étude":
            ref_conv += f"convention d'étude {etude.ref()}ce "
        else:
            bdc = facture.bdc()
            if bdc:
                bdc_ref = bdc.ref()
            ref_conv += (
                f"convention cadre {etude.ref()}cc et au bon de commande {bdc_ref} "
            )
        # plus tard avenant
        facture.objet = ref_conv
        if not facture.numero_facture:
            current_year = date.today().year
            je_act = facture.etude.je
            max_numero = Facture.objects.filter(
                date_emission__year=current_year,
                etude__je=je_act,
                date_emission__isnull=False,
            ).aggregate(Max("numero_facture"))["numero_facture__max"]
            if max_numero:
                facture.numero_facture = max_numero + 1
            else:
                facture.numero_facture = 1

        facture.save(id_etude=facture.etude.id)

        factures = (
            Facture.objects.all()
            .annotate(annee_creation=ExtractYear("date_emission"))
            .order_by("-annee_creation", "-numero_facture")
        )
        # pas optimale mais faudrait potentiellement crééer un champs je
        filtered_factures = [facture for facture in factures if facture.je() == user_je]
        template = loader.get_template("polls/factures.html")
        context = {"factures": filtered_factures}
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def factures(request):
    if request.user.is_authenticated:
        context = general_context(request)
        user_je = request.user.je

        factures = Facture.objects.all().order_by("-numero_facture")
        # pas optimale mais faudrait potentiellement crééer un champs je
        filtered_factures = [facture for facture in factures if facture.je() == user_je]
        template = loader.get_template("polls/factures.html")
        context["factures"] = filtered_factures
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def BVs(request):
    if request.user.is_authenticated:
        user_je = request.user.je
        BVs = (
            BV.objects.all()
            .annotate(annee_creation=ExtractYear("date_emission"))
            .order_by("-annee_creation", "-numero_bv")
        )
        # pas optimale mais faudrait potentiellement crééer un champs je
        BVs = [bv for bv in BVs if bv.je() == user_je and bv.date_emission]
        template = loader.get_template("polls/BVs.html")
        context = {"BVs": BVs}
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def create_mail_template(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                message = request.POST["message"]
                je = request.user.je
                numero = request.POST.get("numero", None)
                numero = (
                    numero
                    if numero
                    else (max(je.mail_templates.values_list("numero", flat=True)) + 1)
                )
                new_mail_template = CustomMailTemplate(
                    je=je, message=message, numero=numero
                )
                new_mail_template.save()
                return redirect("demarchage")
            except:
                liste_messages = Message.objects.filter(
                    destinataire=request.user,
                    read=False,
                    date__range=(
                        timezone.now() - timezone.timedelta(days=20),
                        timezone.now(),
                    ),
                ).order_by("date")
                message_count = liste_messages.count()
                liste_messages = liste_messages[:3]
                all_notifications = request.user.notifications.order_by("-date_effet")
                notification_list = [
                    notif for notif in all_notifications if notif.active()
                ]
                notification_count = len(notification_list)
                template = loader.get_template("polls/page_error.html")
                context = {
                    "liste_messages": liste_messages,
                    "message_count": message_count,
                    "error_message": "La création du template a échoué.",
                    "notification_list": notification_list,
                    "notification_count": notification_count,
                }
        else:
            liste_messages = Message.objects.filter(
                destinataire=request.user,
                read=False,
                date__range=(
                    timezone.now() - timezone.timedelta(days=20),
                    timezone.now(),
                ),
            ).order_by("date")
            message_count = liste_messages.count()
            liste_messages = liste_messages[:3]
            all_notifications = request.user.notifications.order_by("-date_effet")
            notification_list = [notif for notif in all_notifications if notif.active()]
            notification_count = len(notification_list)
            template = loader.get_template("polls/page_error.html")
            context = {
                "liste_messages": liste_messages,
                "message_count": message_count,
                "error_message": "Vous tentez d'utiliser une fonctionnalité de manière inattendue.",
                "notification_list": notification_list,
                "notification_count": notification_count,
            }
    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))


def delete_mail_template(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            try:
                template_id = request.POST["id_template"]
                template = CustomMailTemplate.objects.get(id=template_id)
                if template.je != request.user.je:
                    raise ValueError("Le template sélectionné n'a pas été trouvé.")
                template.delete()
                return redirect("demarchage")
            except:
                liste_messages = Message.objects.filter(
                    destinataire=request.user,
                    read=False,
                    date__range=(
                        timezone.now() - timezone.timedelta(days=20),
                        timezone.now(),
                    ),
                ).order_by("date")
                message_count = liste_messages.count()
                liste_messages = liste_messages[:3]
                all_notifications = request.user.notifications.order_by("-date_effet")
                notification_list = [
                    notif for notif in all_notifications if notif.active()
                ]
                notification_count = len(notification_list)
                template = loader.get_template("polls/page_error.html")
                context = {
                    "liste_messages": liste_messages,
                    "message_count": message_count,
                    "error_message": "Le template sélectionné n'a pas été trouvé.",
                    "notification_list": notification_list,
                    "notification_count": notification_count,
                }
                return HttpResponse(template.render(context, request))
        else:
            liste_messages = Message.objects.filter(
                destinataire=request.user,
                read=False,
                date__range=(
                    timezone.now() - timezone.timedelta(days=20),
                    timezone.now(),
                ),
            ).order_by("date")
            message_count = liste_messages.count()
            liste_messages = liste_messages[:3]
            all_notifications = request.user.notifications.order_by("-date_effet")
            notification_list = [notif for notif in all_notifications if notif.active()]
            notification_count = len(notification_list)
            template = loader.get_template("polls/page_error.html")
            context = {
                "liste_messages": liste_messages,
                "message_count": message_count,
                "error_message": "Vous tentez d'utiliser une fonctionnalité de manière inattendue.",
                "notification_list": notification_list,
                "notification_count": notification_count,
            }
            return HttpResponse(template.render(context, request))

    else:
        return redirect("login")  # Adjust as needed
