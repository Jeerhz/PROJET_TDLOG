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
]