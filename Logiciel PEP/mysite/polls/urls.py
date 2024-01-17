from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # ex: /polls/5/results/
    path("login/", views.login, name="login"),
    path("students/", views.students, name="students"),
    path("details/<str:modelName>/<int:iD>", views.details, name="details"),
    path("input/<str:modelName>", views.input, name="input"),
    path("logout/", views.logout, name="logout"),
    path("annuaire/", views.annuaire, name="annuaire"),
]