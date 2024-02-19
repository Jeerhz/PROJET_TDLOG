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
