from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    # ex: /polls/5/results/
    path("connexion/", views.connexion, name="connexion"),
    path("results/<int:user_id>", views.results, name="results"),
    path("students/", views.students, name="students"),
    path("etudes/", views.etudes, name="etudes"),
    path("clients/", views.clients, name="clients"),
    path("input/<str:modelName>", views.input, name="input"),
    path("logout/", views.logout, name="logout"),
    path('annuaire/', views.annuaire, name='annuaire'),
]