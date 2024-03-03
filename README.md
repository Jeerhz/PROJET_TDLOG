# OBJECTIFS

----- TECHNIQUE -----
1) Checkez les liens et les copies-colle
2) La page annuaire, les boutons
3) Le truc à gauche faire ressortuir les bons onglets
4) Modifier la page index (Antony) + enlever les exemples et les illutrations du template
5) Faire en sorte que modifier une instance le modifie vraiment
6) Faire en sorte de supprimer une instance
7) Faire un test de la présentation finale en renseignant par exemple une nouvelle étude comme ils feront eux


-----PRESENTATION-----
1) Bosser le discours sur les fonctionnalités déjà implémentées
2) Tarification et type de license (à vie, annuel, mensuel)
3) Ce qu'on s'engage à proposer comme service ensuite (Suivi, délais, mise à jour)



----- CREATION D'ENTREPRISE -------
1) Attendre la réponse pour le statut d'élève-entrepreneur
2) Trouver un nom
3) Trouver des JE à prospecter (connaissances)
4) Réfléchir au bon statut (SAS SARL...) et checker les démarches à faire (ça peut attendre le 1))



---- TECHNIQUE ------
1) S'assurer d'avoir une version STABLE avant le reste (corriger tous les petits bugs, relire le code)
2) Mise en place d'un REST API pour éviter de recharger inutilement la page
3) Se former sur la mise en ligne de la database et du serveur
4) Rendre fonctionnel le système de notification
5) Améliorer le visuel de la messagerie
6) Constuire les templates des autres documents















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
