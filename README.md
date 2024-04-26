# REINITIALISATION DE LA BASE DE DONNES

Bienvenue dans ce guide pour initialiser le projet avec une base de données PostgreSQL. Les principales modifications résident dans la réparation dans models: j'ai enlevé les valeurs par défauts pour student par exemple. J'ai aussi enlevé la nécessité d'être lié à une je pour être un Member parce que Member comprend les superusers (nous). En fait il est nécessaire de spécifier une JE pour créer un Member tout de même parce que le champ est obligatoire lorsqu'on remplit le form.

1) PostgreSQL

   --> Installer PostgreSQL sur sa machine
   --> Vous pouvez suivre les 4 premières minutes de cette video : https://www.youtube.com/watch?v=unFGJhIvHU4&t=358s
   --> Dans la vidéo il installe donc PostgreSQL sur sa machine puis importe le package psycho jsp quoi dans l'environnement virtuel
   --> Ensuite il ouvre pgAdmin4 qui est le browser pour accéder aux différentes database. Il suffit alors de créer une nouvelle database via click droit sur 'Databases' puis click gauche sur 'Create Database'
   --> Lui prend le temps de créer un User mais vous pouvez sauter cette étape

 2) Django
    --> Toujours dans la même video, il vous montre quoi ajouter dans settings: i.e un truc comme ça:
    
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'db_sylex',
        'USER': 'postgres',
        'PASSWORD': 'bensalem',
        'HOST': 'localhost',  
        'PORT': '5433',
    }
}

  --> A cette étape, vous devriez être en mesure de faire un makemigrations puis un migrate, faites le

3) Création d'instance

  --> Maintenant comme si on avait un nouveau client, il faut créer une instance pour cette JE pour permettre aux membres de s'inscrire et de travailler
  --> Pour se faire on accède au shell via python manage.py shell et on entre les commandes suivantes
  --> from polls.models import JE
  -->
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
--> On peut vérifier que notre JE est bien crée en tapant : JE.objects.all()

4) Connexion
   --> Finalement, il ne vous reste qu'à vous connecter
   --> Allez dans polls/login et entrez vos informations*
   --> Pour trouver l'id de la JE vous devez allez dans pgAdmin4 et consulter directement la table je. Copier l'identifiant, collez le dans le form et supprimez les guillemets

Voilà vous devriez être sur la page et prêt à travailler
Si soucis vous pouvez toujours m'appeler même si je viens de tester la manip et que cela marche de mon côté.
 
