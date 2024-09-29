=======
# Réinitialisation de la Base de Données

Bienvenue dans ce guide détaillé pour initialiser votre projet avec une base de données PostgreSQL. Ce document vous guidera à travers l'installation de PostgreSQL, la configuration de Django pour l'utiliser, la création d'instances et la connexion à votre application.

## Modification des Modèles
Les modifications principales incluent la suppression des valeurs par défaut et l'ajustement des exigences pour les associations à des structures (comme les JE). Par exemple, bien que le champ JE reste obligatoire pour la création d'un membre, nous avons retiré certaines restrictions pour faciliter la gestion des superutilisateurs.

## Installation de PostgreSQL

1. **Installer PostgreSQL** :
   - Téléchargez et installez PostgreSQL sur votre machine.
   - Suivez les premières étapes d'installation comme indiqué dans [cette vidéo](https://www.youtube.com/watch?v=unFGJhIvHU4&t=358s) (jusqu'à la minute 4).

2. **Configuration avec pgAdmin4** :
   - Lancez pgAdmin4 et créez une nouvelle base de données :
     - Faites un clic droit sur 'Databases', puis cliquez sur 'Create Database'.
   - La vidéo suggère de créer un utilisateur mais vous pouvez omettre cette étape.

## Configuration de Django

1. **Paramétrage de la base de données** :
   Ajoutez la configuration suivante dans vos `settings` de Django :

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'db_sylex',
           'USER': 'postgres',
           'PASSWORD': 'bensalem',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```
   
## Migration des modèles
- Exécutez `makemigrations` puis `migrate` pour appliquer les changements de modèle à la base de données.

## Création d'une Instance

### Création d'une nouvelle JE
- Accédez au shell Django via `python manage.py shell`.
- Exécutez les commandes suivantes pour créer une nouvelle JE :

```python
from polls.models import JE

def default():
    new_je = JE()
    new_je.nom = "PEP"
    new_je.raison_sociale = "Junior-Entreprise des Ponts"
    new_je.rue = "6-8 Avenue Blaise Pascal"
    new_je.ville = "Champs-sur-Marne"
    new_je.code_postal = "77420"
    new_je.siret = "01234567890123"
    new_je.APE = "0000A"
    new_je.TVA = "AA01234567890"
    new_je.IBAN = "FR000000000000000000000"
    new_je.BIC = "0000000000000000000000"
    new_je.check_order = "ORDRE_CHEQUE"
    new_je.logo = "/static/polls/img/bdc.png"
    new_je.chiffres_affaires = 0.0
    new_je.base_urssaf = 46.6
    new_je.taux_ATMP =0.66
    new_je.aux_cotisations =29.9
    new_je.save()

default()
```

# les paquets google a installer (jai tous mis jsp sils servent tous a qlq chose):
google-auth social-auth-app-django google-auth-oauthlib google-auth-httplib2 google-api-python-client 
+ bien sur Django Pillow docxtpl openpyxl celery django_celery_beat psycopg psycopg2-binary pytz num2words django-crispy_forms html2image python-decouple

# Guide d'utilisation de l'Application

## Connexion à l'Application
### Accès au système

#### Connexion:
Rendez-vous sur [polls/login](url_de_votre_application) et entrez vos informations de connexion.

#### Récupération de l'ID de la JE:
Consultez la table correspondante via pgAdmin4.
Copiez l'identifiant de la JE.
Insérez-le dans le formulaire de connexion, en vous assurant de supprimer les guillemets.

En suivant ces instructions, vous devriez être capable de configurer et d'utiliser votre application. Si vous rencontrez des problèmes, n'hésitez pas à me contacter.
>>>>>>> refs/remotes/origin/main
