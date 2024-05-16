import json
import os
from docxtpl import DocxTemplate

from io import BytesIO
from uuid import UUID
from openpyxl import load_workbook
from django.shortcuts import redirect
from django.core.mail import send_mail, get_connection
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.urls import reverse
from django.apps import apps
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import datetime
from django.http import JsonResponse, FileResponse
from django.conf import settings
from django.core.files.base import ContentFile

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
        chiffres_affaires = request.user.chiffres_affaires
        monthly_sums = calculate_monthly_sums(user_je)
        etudes_recentes = Etude.objects.filter(je=user_je).order_by('-debut')[:5]
        template = loader.get_template("polls/index.html")
        context = {
            "monthly_sums": monthly_sums,
            "liste_messages": liste_messages,
            "message_count": message_count,
            "chiffre_affaires": chiffres_affaires,
            "etudes_recentes":etudes_recentes,
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
            factures = None
            etude = None  # Initialisez `etude` à None par défaut
            client = None
            eleve = None
            if modelName == "Etude":
                phases = Phase.objects.filter(etude=instance).order_by('date_debut')
                factures=Facture.objects.filter(etude=instance).order_by('numero_facture')
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
                context["factures"] = factures
                context["phase_form"] = AddPhase()
                context["facture_form"] = AddFacture()
                context["intervenant_form"] = AddIntervenant()

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
            facture = Facture.objects.get(id=iD)
            etude= facture.etude
            client = etude.client
            context = {"facture": facture,"etude": etude, "client": client}
            template = loader.get_template("polls/facpdf.html")
        except:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": "Erreur dans l'identification de la mission."}
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





def stat_KPI(request):
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
        template = loader.get_template("polls/stat_KPI.html")
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


def editer_convention(request, iD):
    if request.user.is_authenticated:
        try:
            instance = Etude.objects.get(id=iD)
            if not instance.ce_editable():
                raise ValueError("Informations manquantes pour l'édition de la CE.")
            client = instance.client
            if instance.type_convention == "Convention d'étude":
                model = ConventionEtude
                template = DocxTemplate("polls\\templates\\polls\\Convention_Etude.docx")
            elif instance.type_convention == "Convention cadre":
                model = ConventionCadre
                template = DocxTemplate("polls\\templates\\polls\\Convention_Cadre.docx")
            else:
                raise ValueError("Type de convention non défini.")
            ce = model(etude=instance)
            ce.save()
            responsable = instance.responsable.all()[0]
            context = {"etude": instance, "client": client, "ce":ce, "responsable":responsable}
            # Load the template

            # Render the document
            template.render(context)


            # Create a temporary in-memory file
            output = BytesIO()
            template.save(output)
            output.seek(0)

            # Save the "fichier" field of the CE
            filename = f"Convention_Etude_{ce.__str__()}.docx"
            ce.fichier.save(filename, ContentFile(output.read()))
            ce.save()

            # Return the filled document as a FileResponse

            return JsonResponse({"message":"The document has been created and saved successfully."})
        except ValueError as ve:
            return JsonResponse({"message":str(ve)})
        except :
            return JsonResponse({"message":"Un problème a été détecté dans la base de données."})

    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))
    
def editer_devis(request, iD):
    if request.user.is_authenticated:
        try:
            instance = Etude.objects.get(id=iD)
            if not instance.devis_editable():
                raise ValueError("Informations manquantes pour l'édition de la CE.")
            client = instance.client
            devis = Devis(etude=instance)
            devis.save()
            template = DocxTemplate("polls\\templates\\polls\\Devis_V2.docx")
            responsable = instance.responsable.all()[0]
            context = {"etude": instance, "client": client, "devis":devis, "responsable":responsable}
            # Load the template

            # Render the document
            template.render(context)


            # Create a temporary in-memory file
            output = BytesIO()
            template.save(output)
            output.seek(0)

            # Save the "fichier" field of the CE
            filename = f"Devis_{devis.__str__()}.docx"
            devis.fichier.save(filename, ContentFile(output.read()))
            devis.save()

            # Return the filled document as a FileResponse

            return JsonResponse({"message":"The document has been created and saved successfully."})
        except ValueError as ve:
            return JsonResponse({"message":str(ve)})
        except :
            return JsonResponse({"message":"Un problème a été détecté dans la base de données."})

    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))
    
def telecharger_document(request, modelName, iD):
    if request.user.is_authenticated:
        try:
            model = apps.get_model(app_label="polls", model_name=modelName)
            document = model.objects.get(id=iD)

            # Save the "fichier" field of the CE
            filename = f"{document.__str__()}.docx"

            # Return the filled document as a FileResponse
            response = FileResponse(document.fichier, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except:
            template = loader.get_template("polls/page_error.html")
            context = {"error_message": "Le document n'a pas pu être transmis."}

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
        etudes = Etude.objects.filter(je=user_je, debut__month=current_month)

        # Calculate the sum of montant_HT for these objects using Python
        total_montant_HT = sum(etude.montant_HT() for etude in etudes)
        monthly_sums.append(total_montant_HT)

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
            suggestions_etude = suggestions_etude.filter(Q(titre__icontains=keyword) | Q(numero__icontains=keyword) | Q(responsable__membre__student__first_name__icontains=keyword) | Q(responsable__membre__student__last_name__icontains=keyword) | Q(client__nom_societe__icontains=keyword))
            suggestions_client = suggestions_client.filter(Q(nom_societe__icontains=keyword) | Q(nom_representant__icontains=keyword))
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
            liste_res_etude.append(resultats_etude.filter(Q(titre__icontains=keyword) | Q(numero__icontains=keyword) | Q(responsable__membre__student__first_name__icontains=keyword) | Q(responsable__membre__student__last_name__icontains=keyword) | Q(client__nom_societe__icontains=keyword)))
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
    
def ajouter_phase(request, id_etude):
    if request.user.is_authenticated:
        if request.method == 'POST':
            fetchform = AddPhase(request.POST)
            if fetchform.is_valid():
                fetchform.save(commit=True, id_etude=id_etude)
        return redirect('details', modelName='Etude', iD=id_etude)
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))



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
    
def BV(request, id_etude):
    if request.user.is_authenticated:
        chemin_absolu = os.path.join("polls\\static\\polls\\BV_test.xlsx")
        classeur = openpyxl.load_workbook(chemin_absolu)

        # Sélectionner la feuille de calcul
        # feuille = classeur.active

        # Modifier la cellule G4
        # feuille['C13'] = "23e42"

        # Sauvegarder les modifications dans le fichier Excel
        # classeur.save(chemin_absolu)
        return FileResponse(open(chemin_absolu, 'rb'), as_attachment=True)
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))
    
def ajouter_assignation_jeh(request, id_etude, numero_phase):
    if request.user.is_authenticated:
        if request.method == 'POST':
            fetchform = AddIntervenant(request.POST)
            if fetchform.is_valid():
                fetchform.save(commit=True, id_etude=id_etude, numero_phase=numero_phase)
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
            if (etude.date_fin_recrutement.is_blank() or etude.date_debut_recrutement.is_blank() or timezone.now()<etude.date_debut_recrutement or timezone.now()>etude.date_fin_recrutement()):
                raise ValueError('')
            context = {'etude':etude, 'form':Recrutement()}
            template = loader.get_template("polls/recrutement.html")
        except :
            context = {'error_message': "Cette page n'est associée à aucune mission, ou vous tentez d'y accéder hors période de recrutement."}
            template = loader.get_template("polls/recrutement_fail.html")
        return HttpResponse(template.render(context, request))
    else:
        try :
            uuid_url = UUID(id_url)
            etude = Etude.objects.get(id_url=uuid_url)
            recrutement = Recrutement(request.POST)
            recrutement.save(etude=etude)
            context = {}
            template = loader.get_template("polls/recrutement_succes.html")
        except :
            context = {'error_message': "Votre candidature n'a pas pu aboutir."}
            template = loader.get_template("polls/recrutement_fail.html")
        return HttpResponse(template.render(context, request))

def modifier_recrutement_etude(request, iD):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                etude = Etude.objects.get(id=iD)
                etude.date_debut_recrutement = datetime.strptime(request.POST['debut'], '%d/%m/%Y').date()
                etude.date_fin_recrutement = datetime.strptime(request.POST['fin'], '%d/%m/%Y').date()
                etude.save()
                return JsonResponse({'success':True, 'debut':etude.date_debut_recrutement, 'fin':etude.date_fin_recrutement})
            except:
                return JsonResponse({'success':False})
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))
    
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


def word_template(request):
    if request.user.is_authenticated:
        send_custom_email("Test mail Django", "Ce mail a été envoyé à partir d'une vue Django", "titoduc1905@gmail.com", "titoduc1905@gmail.com", "qrorvjgmtunxthpg", ["edgar.duc@eleves.enpc.fr"], host="smtp.gmail.com", port=587)
        # Load the template
        template = DocxTemplate("polls\\templates\\polls\\23e05_Convention_Etude.docx")

        # Prepare context
        context = {'name': "Edgar Duc"}

        # Render the document
        template.render(context)

        # Create a temporary in-memory file
        output = BytesIO()
        template.save(output)
        output.seek(0)

        # Return the filled document as a FileResponse
        filename = "filled_template.docx"
        response = FileResponse(output, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        template = loader.get_template("polls/login.html")
        context = {}
        return HttpResponse(template.render(context, request))


def send_custom_email(subject, message, from_email, username, password, recipient_list, host=None, port=None):
    # Override default email settings if provided
    email_host = host if host else settings.EMAIL_HOST
    email_port = port if port else settings.EMAIL_PORT
    connection = get_connection(host=email_host, port=email_port, username=username,
        password=password,
        use_tls=True,)
    send_mail(subject, message, from_email, recipient_list, 
              fail_silently=False, 
              connection=connection)

def settings(request):
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
        
        template = loader.get_template("polls/settings.html")
        context = {
            "liste_messages": liste_messages,
            "message_count": message_count,
            "user": request.user,
        }

    else:
        template = loader.get_template("polls/login.html")
        context = {}
    return HttpResponse(template.render(context, request))
