from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # ex: /polls/5/results/
    path("login/", views.custom_login, name="custom_login"),
    path("students/", views.students, name="students"),
    path("details/<str:modelName>/<int:iD>", views.details, name="details"),
    path("input/<str:modelName>/<int:iD>", views.input, name="input"),
    path("logout/", views.custom_logout, name="custom_logout"),
    path("annuaire/", views.annuaire, name="annuaire"),
    path("facture/<int:iD>", views.facture, name="facture"),
    path("messages/", views.messages, name="messages"),
    path("register/", views.register, name="register"),
    path("convention_etude/<int:iD>", views.convention_etude, name="convention_etude"),
    path("charts/", views.charts, name="charts"),
    path("blank_page/", views.blank_page, name="charts"),
    path("je_detail/", views.je_detail, name='je_detail'),
    path("search_suggestions/", views.search_suggestions, name='search_suggestions'),
    path("search/", views.search, name='search'),
    path("stat_KPI/", views.stat_KPI, name='stat_KPI'),
    path("messagerie/", views.messages, name='messagerie'),
    path("ajouter_phase/<int:id_etude>", views.ajouter_phase, name='ajouter_phase'),
    path("ajouter_assignation_jeh/<int:id_etude>/<int:numero_phase>", views.ajouter_assignation_jeh, name='ajouter_assignation_jeh'),
    path("BV/<int:id_etude>", views.BV, name='BV'),
    path("ndf/", views.ndf, name="ndf"),
    path("recrutement/<str:id_url>", views.recrutement, name="recrutement"),
    path("modifier_recrutement_etude/<int:iD>", views.modifier_recrutement_etude, name="modifier_recrutement_etude"),
    
]
