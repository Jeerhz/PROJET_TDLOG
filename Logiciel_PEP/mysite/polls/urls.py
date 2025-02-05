from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # ex: /polls/5/results/ 

    path("convention_etude/<int:iD>", views.convention_etude, name="convention_etude"),
    
    path("login/", views.custom_login, name="custom_login"),
    path("details/<str:modelName>/<int:iD>", views.details, name="details"),
    path("details_etudes_importees/<int:iD>", views.details_etudes_importees, name="details_etudes_importees"),

    
    path("student/<int:pk>/edit/", views.edit_student, name='edit_student'),
    path("edit_pdp/<int:pk>/edit/", views.edit_pdp, name='edit_pdp'),

    path("student/<int:pk>/delete/", views.delete_student, name='delete_student'),
    path("client/<int:pk>/edit/", views.edit_client, name='edit_client'),
    path("client/<int:pk>/delete/", views.delete_client, name='delete_client'),
    path("etude/<int:pk>/delete/", views.delete_etude, name='delete_etude'),
    path("etude/<int:id_etude>/<int:id_bon>/delete_bdc/", views.delete_bdc, name='delete_bdc'),
    path("etude/<int:pk>/<int:iD>/delete_phase/", views.delete_phase, name='delete_phase'),
    path("etude/<int:pk>/<int:iD>/delete_avenant_ce/", views.delete_avenant_ce, name='delete_avenant_ce'),


    path("etude/<int:pk>/<int:iD>/edit_phase/", views.edit_phase, name='edit_phase'),
    path("phase/<int:pk>/<int:etude_id>/delete_assignation/", views.delete_assignation, name='delete_assignation'),
    path("etude/<int:pk>/<int:iD>/delete_facture/", views.delete_facture, name='delete_facture'),
    path("etude/<int:pk>/<int:iD>/delete_BV/", views.delete_BV, name='delete_BV'),

    
    path("input/<str:modelName>/<int:iD>", views.input, name="input"),
    path("logout/", views.custom_logout, name="custom_logout"),
    path("annuaire/", views.annuaire, name="annuaire"),
    
    path("facture/<int:id_facture>", views.facture, name="facture"), 
    path("generer_BV/<int:id_bv>", views.generer_BV, name="generer_BV"), 

    
    path("messages/", views.messages, name="messages"),
    path("register/", views.register, name="register"),
    path("charts/", views.charts, name="charts"),
    path("je_detail/", views.je_detail, name='je_detail'),
    path('search_suggestions_student/<int:id_etude>/', views.search_suggestions_student, name='search_suggestions_student'),
    path("search_suggestions/", views.search_suggestions, name='search_suggestions'),
    path("search/", views.search, name='search'),
    path("stat_KPI/", views.stat_KPI, name='stat_KPI'),
    path('fetch_data/', views.fetch_data, name='fetch_data'),
    path("messagerie/", views.messages, name='messagerie'),
    path("ajouter_phase/<int:id_etude>", views.ajouter_phase, name='ajouter_phase'),
    path("ajouter_assignation_jeh/<int:id_etude>/<int:id_phase>", views.ajouter_assignation_jeh, name='ajouter_assignation_jeh'),
    path("nouveau_BV/<int:id_etude>/<int:id_eleve>", views.nouveau_BV, name='nouveau_BV'),
    path("ndf/", views.ndf, name="ndf"),
    path("ba/<int:iD>", views.ba, name="ba"),
    path("recrutement/<str:id_url>", views.recrutement, name="recrutement"),
    path('modifier_je/<uuid:id>/', views.modifier_je, name='modifier_je'),
    path('etude/modify/<int:pk>/', views.modify_etude, name='modify_etude'),
    path('get_client_representants/', views.get_client_representants, name='get_client_representants'),
    path('modifier_etude/<int:iD>/', views.modifier_etude, name='modifier_etude'),
    path('modifier_etude_form/<int:iD>/', views.modifier_etude_form, name='modifier_etude_form'),

    path("modifier_recrutement_etude/<int:iD>", views.modifier_recrutement_etude, name="modifier_recrutement_etude"),
    path("ajouter_facture/<int:id_etude>", views.ajouter_facture, name='ajouter_facture'),
    path("remarque_etude/<int:iD>", views.remarque_etude, name="remarque_etude"),
    path("settings/", views.settings, name="settings"),
    path("editer_convention/<int:iD>", views.editer_convention, name="editer_convention"),
    path("editer_devis/<int:iD>", views.editer_devis, name="editer_devis"),
    path("editer_avenant_ce/<int:iD>", views.editer_avenant_ce, name="editer_avenant_ce"),
    path("editer_bon/<int:id_bon>", views.editer_bon, name="editer_bon"),
    path("add_intervenant/<int:id_etude>/<int:id_student>", views.add_intervenant, name="add_intervenant"),
    path("search_suggestions_student/<int:id_etude>", views.search_suggestions_student, name='search_suggestions_student'),
    path("demarchage/", views.demarchage, name='demarchage'),
    path("editer_rdm/<int:id_etude>/<int:id_eleve>", views.editer_rdm, name='editer_rdm'),
    path("editer_avenant_rdm_ce/<int:id_etude>/<int:id_eleve>", views.editer_avenant_rdm_ce, name='editer_avenant_rdm_ce'),
    path("ajouter_avenant_ce/<int:id_etude>", views.ajouter_avenant_ce, name='ajouter_avenant_ce'),
    path('supprimer_demarchage/<int:id_representant>', views.supprimer_demarchage, name='supprimer_demarchage'),
    path("editer_pv/<int:iD>/<str:type>", views.editer_pv, name="editer_pv"),
    path("ajouter_representant/<int:id_client>", views.ajouter_representant, name="ajouter_representant"),
    path("send_mail_demarchage/<int:iD>", views.send_mail_demarchage, name="send_mail_demarchage"),
    path('ajouter_representant/<int:id_client>/', views.ajouter_representant, name='ajouter_representant'),
    path('supprimer_representant/<int:id_representant>/', views.supprimer_representant, name='supprimer_representant'),
    path("send_mail_demarchage", views.send_mail_demarchage, name="send_mail_demarchage"),
    
    path("facture_redirect/<int:fac_id>", views.facture_redirect, name="facture_redirect"),
    path("factures/", views.factures, name="factures"),
    path("BVs/", views.BVs, name="BVs"),
    path("create_mail_template/", views.create_mail_template, name="create_mail_template"),
    path("delete_mail_template/", views.delete_mail_template, name="delete_mail_template"),
    path('upload_students/', views.upload_students, name='upload_students'),
    path('verifier_etude/<int:iD>/', views.verifier_etude, name='verifier_etude'),
    path("editer_ba/<int:id_eleve>", views.editer_ba, name="editer_ba"),
    path('upload_clients/', views.upload_clients, name='upload_clients'),
    path('upload_etudes/', views.upload_etudes, name='upload_etudes'),


    path('object_suppression/<str:model_name>/<int:object_id>', views.object_suppression, name="object_suppression"),
    path("modifier_bon_commande/<int:id_etude>/<int:id_bon>", views.modifier_bon_commande, name="modifier_bon_commande"),
    path("get_object_info/<str:model_name>/<int:object_id>", views.get_object_info, name="get_object_info"),
    path("google-login", views.google_login, name="google-login"),
    path("confidentialite-donnees", views.confidentialite_donnees, name="confidentialite-donnees"),
    path("client-suggestions", views.client_suggestions, name="client-suggestions"),
    path('get_representants/', views.get_representants, name='get_representants'),
    path("facture/<int:id_facture>/generate-pdf/", views.generate_facture_pdf, name='generate_facture_pdf'),
    path("signature_document/<str:model>/<int:iD>", views.signature_document, name="signature_document"),
    path("signature_devis/<int:iD>", views.signature_devis, name="signature_devis"),
    
    path("update_etude/<int:id>", views.update_etude, name="update_etude"),

    
    path("editer_acf/<int:id_etude>/<int:id_eleve>", views.editer_acf, name='editer_acf'),
    path("editer_convention_cadre/<int:iD>", views.editer_convention_cadre, name="editer_convention_cadre"),
    path("editer_acf_client/<int:iD>", views.editer_acf_client, name='editer_acf_client'),
    path("numero_facture/<int:iD>/edit/", views.numero_facture, name='numero_facture'),
    path("numero_BV/<int:iD>/edit/", views.numero_BV, name='numero_BV'),
    path("csv_import_etudiants/", views.csv_import_etudiants, name="csv_import_etudiants"),





    
    








    
    
    
    

    #path("ajouter_representant/<int:id_client>", views.ajouter_representant, name='ajouter_representant'),
]
