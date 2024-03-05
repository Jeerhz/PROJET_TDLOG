function ajouterEtudiant(){
    if(res_student_js.length > compteurEtudiant){
        // Récupérer le conteneur
        var container = document.getElementById("liste-etudiant");
        var wholecontent = container.innerHTML;
        // Ajouter les éléments à partir de la liste récupérée depuis Django
        res_student_js.slice(compteurEtudiant, Math.min(compteurEtudiant+5, res_student_js.length)).forEach(function(eleve) {
            wholecontent += '<a href="'+eleve['url']+'" class="list-group-item list-group-item-action d-flex justify-content-between">'
            wholecontent += '<i class="fa fa-user"></i>'
            wholecontent += '<span class="col-3">' + eleve['first_name'] +'</span>'
            wholecontent += '<span class="col-3">'+eleve['last_name']+'</span>'
            wholecontent += '<span class="col-3 text-end">'+eleve['promotion']+'</span>'                                     
            wholecontent += '</li>'
        });
        container.innerHTML = wholecontent;
        compteurEtudiant += 5;
    }
}

function ajouterEtude() {
    if(res_etude_js.length > compteurEtude){
        // Récupérer le conteneur
        var container = document.getElementById("liste-etude");
        var wholecontent = container.innerHTML;
        console.log(compteurEtude);
        console.log(Math.min(compteurEtude+5, res_etude_js.length));
        // Ajouter les éléments à partir de la liste récupérée depuis Django
        res_etude_js.slice(compteurEtude, Math.min(compteurEtude+5, res_etude_js.length)).forEach(function(etude) {
            wholecontent += '<a href="'+etude['url']+'" class="list-group-item list-group-item-action d-flex justify-content-between">'
            wholecontent += '<i class="fa fa-file-contract"></i>'
            wholecontent += '<span class="col-3">' + etude['titre'] +'</span>'
            wholecontent += '<span class="col-3">'+etude['responsable']+'</span>'
            wholecontent += '<span class="col-3 text-end">'+etude['statut']+'</span>'                                     
            wholecontent += '</li>'
        });
        container.innerHTML = wholecontent;
        compteurEtude += 5;
    }
}

function ajouterClient() {
    if(res_client_js.length > compteurClient){
        // Récupérer le conteneur
        var container = document.getElementById("liste-client");
        var wholecontent = container.innerHTML;
        // Ajouter les éléments à partir de la liste récupérée depuis Django
        res_client_js.slice(compteurClient, Math.min(compteurClient+5, res_client_js.length)).forEach(function(client) {
            wholecontent += '<a href="'+client['url']+'" class="list-group-item list-group-item-action d-flex justify-content-between">'
            wholecontent += '<i class="fa fa-user-tag"></i>'
            wholecontent += '<span class="col-3">' + client['nom_societe'] +'</span>'
            wholecontent += '<span class="col-3">'+client['nom_representant']+'</span>'                                   
            wholecontent += '</a>'
        });
        container.innerHTML = wholecontent;
        compteurClient += 5;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById("bouton-etudiant").addEventListener("click", ajouterEtudiant());
    document.getElementById("bouton-etude").addEventListener("click", ajouterEtude());
    document.getElementById("bouton-client").addEventListener("click", ajouterClient());
    ajouterEtudiant();
    ajouterEtude();
    ajouterClient();
});