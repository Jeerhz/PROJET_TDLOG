# Bienvenue dans ce guide destiné au lancement du serveur !

Une fois le repository cloné, on ouvre un terminal et on se positionne dans le dossier "Logiciel_PEP" fraîchement créé avec une commande "cd", puis on crée un environnement virtuel adapté avec les commandes de terminal :  
py -m venv venv  
On active l'environnement virtuel avec la commande:  
(MacOS :) source venv/bin/activate  
(Windows :) venv\Scripts\activate  

(Si un dossier .venv est déjà présent, pensez à le supprimer avant de créer votre propre environnement.)

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
