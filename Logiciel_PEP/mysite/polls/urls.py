from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # ex: /polls/5/results/ 

    path("convention_etude/<int:iD>", views.convention_etude, name="convention_etude"),
    
    path("login/", views.custom_login, name="custom_login"),
    path("details/<str:modelName>/<int:iD>", views.details, name="details"),
    path("student/<int:pk>/edit/", views.edit_student, name='edit_student'),
    path("student/<int:pk>/delete/", views.delete_student, name='delete_student'),
    path("client/<int:pk>/edit/", views.edit_client, name='edit_client'),
    path("client/<int:pk>/delete/", views.delete_client, name='delete_client'),
    path("etude/<int:pk>/delete/", views.delete_etude, name='delete_etude'),
    path("input/<str:modelName>/<int:iD>", views.input, name="input"),
    path("logout/", views.custom_logout, name="custom_logout"),
    path("annuaire/", views.annuaire, name="annuaire"),
    path("facture/<int:id_facture>", views.facture, name="facture"),
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
    path("ajouter_assignation_jeh/<int:id_etude>/<int:numero_phase>", views.ajouter_assignation_jeh, name='ajouter_assignation_jeh'),
    path("BV/<int:id_etude>/<int:id_eleve>", views.BV, name='BV'),
    path("ndf/", views.ndf, name="ndf"),
    path("ba/<int:iD>", views.ba, name="ba"),
    path("recrutement/<str:id_url>", views.recrutement, name="recrutement"),
    path('modifier_je/<uuid:id>/', views.modifier_je, name='modifier_je'),
    path('modifier_etude/<int:iD>/', views.modifier_etude, name='modifier_etude'),
    path("modifier_recrutement_etude/<int:iD>", views.modifier_recrutement_etude, name="modifier_recrutement_etude"),
    path("ajouter_facture/<int:id_etude>", views.ajouter_facture, name='ajouter_facture'),
    path("remarque_etude/<int:iD>", views.remarque_etude, name="remarque_etude"),
    path("settings/", views.settings, name="settings"),
    path("editer_convention/<int:iD>", views.editer_convention, name="editer_convention"),
    path("editer_devis/<int:iD>", views.editer_devis, name="editer_devis"),
    path("editer_avenant_ce/<int:iD>", views.editer_avenant_ce, name="editer_avenant_ce"),
    path("editer_bon/<int:iD>", views.editer_bon, name="editer_bon"),
    path("add_intervenant/<int:id_etude>/<int:id_student>", views.add_intervenant, name="add_intervenant"),
    path("search_suggestions_student/<int:id_etude>", views.search_suggestions_student, name='search_suggestions_student'),
    path("demarchage/", views.demarchage, name='demarchage'),
    path("editer_rdm/<int:id_etude>/<int:id_eleve>", views.editer_rdm, name='editer_rdm'),
    path("ajouter_avenant_ce/<int:id_etude>", views.ajouter_avenant_ce, name='ajouter_avenant_ce'),
    path('', views.my_view, name='my_view'),
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
    path('supprimer_demarchage/<int:id_representant>', views.supprimer_demarchage, name='supprimer_demarchage'),
    path("editer_pv/<int:iD>", views.editer_pv, name="editer_pv"),
    path("ajouter_representant/<int:id_client>", views.ajouter_representant, name="ajouter_representant"),
    path("send_mail_demarchage/<int:iD>", views.send_mail_demarchage, name="send_mail_demarchage"),
    path("factures/", views.factures, name="factures"),
    path("BVs/", views.BVs, name="BVs"),
    path("create_mail_template/", views.create_mail_template, name="create_mail_template"),
    path("delete_mail_template/", views.delete_mail_template, name="delete_mail_template"),



    
    
    
    

    #path("ajouter_representant/<int:id_client>", views.ajouter_representant, name='ajouter_representant'),
]
