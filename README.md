<<<<<<< HEAD
# OBJECTIFS PRESENTATION EMANUELE

-Priorité à la question de l'hébergement de la base de données et la gestion du réseau

-Relire les modèles
-Déterminer les bonnes pratiques pour l'authentification et les requetes de la base de données
-Comment implémenter les "trois tiers" avec Django
-Identity server pour héberger les comptes locaux et du protocole OIDC ou SAML 2.0 pour l'enrollement des clients. 
-Quel langage utiliser (Postgre, NoSQL), MINIO ou Ceph Storage pour l'hébergement des fichiers ?
-firewall périmétriques.
-chiffrement des communications entre les différents composants au travers du protocole TLS version 1.2
-Question de la sous-traitance
-Question de notre accès à la base de données


-Quels sont les solutions pour lancer l'application en locale.
-Chiffrement du code source ? Comment faire en sorte que les utilisateurs puissent se connecter et communiquer ?














# Welcome to this guide for launching the server!

Once the repository is cloned, open a terminal and navigate to the freshly created "Logiciel_PEP" folder using the "cd" command, then create a suitable virtual environment with the following terminal commands:
py -m venv venv
Activate the virtual environment with the command:
(MacOS :) source venv/bin/activate
(Windows :) venv\Scripts\activate

(If a .venv folder already exists, remember to delete it before creating your own environment.)

On installe django et pillow :  
pip install django  
pip install Pillow (gestion des champs ImageField)  
  
Ensuite, on se place dans le bon sous-dossier contenant le fichier "manage.py" avec:  
cd "Logiciel PEP/mysite"  
  
Puis on lance le serveur avec :  
py manage.py runserver  
  
On peut alors se rendre à l'adresse http://127.0.0.1:8000/polls/ pour débuter l'aventure.  
  
Puisque vous n'êtes pas connecté, vous allez être redirigé vers une page de login.  
Là, vous pouvez saisir mes identifiants : edgar.duc@eleves.enpc.fr  |  /Tito1905  , ou ajouter un nouvel utilisateur avec le lien disponible sur la page (auquel cas vous devez renseigner un identifiant de JE, vous utiliserez alors bab6b8be-c274-4fae-b634-3c6a40968534).  
Mes identifiants permettent d'accéder à la page d'administrateur http://127.0.0.1:8000/admin/  
Une fois connecté, il faut garder à l'esprit que toutes les pages n'ont pas encore été codées, donc si vous appuyez sur un bouton qui n'a aucune action ne soyez pas décontenancés !  
Les fonctions les plus importantes du site se trouvent sur la page "Annuaire" puis "Etudes" avec la génération de facture et de convention d'étude.  
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
    new_je.save()

default()
```

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
