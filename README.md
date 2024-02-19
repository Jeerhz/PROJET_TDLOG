# Welcome to this guide for launching the server!

Once the repository is cloned, open a terminal and navigate to the freshly created "Logiciel_PEP" folder using the "cd" command, then create a suitable virtual environment with the following terminal commands:
py -m venv venv
Activate the virtual environment with the command:
(MacOS :) source venv/bin/activate
(Windows :) venv\Scripts\activate

(If a .venv folder already exists, remember to delete it before creating your own environment.)

Install django and pillow:
pip install django
pip install Pillow (for ImageField management)

Next, navigate to the correct sub-folder containing the "manage.py" file with:
cd "Logiciel PEP/mysite"

Then start the server with:
py manage.py runserver

You can now access the server at http://127.0.0.1:8000/polls/ to begin the adventure.

Since you're not logged in, you'll be redirected to a login page.
Here, you can use my credentials: edgar.duc@eleves.enpc.fr | /Tito1905, or add a new user with the link available on the page (in which case you must provide a JE identifier, you can use bab6b8be-c274-4fae-b634-3c6a40968534).
My credentials grant access to the admin page at http://127.0.0.1:8000/admin/
Once logged in, keep in mind that not all pages have been coded yet, so if you click on a button that has no action, don't be surprised!
The most important functions of the site are found on the "Annuaire" page and then "Etudes" with the generation of invoices and study agreements.