document.addEventListener("DOMContentLoaded", () => {
    var modal_suppression_form = document.getElementById("suppression-modal-form");
    var modal_suppression_body = document.getElementById("suppression-modal-body");
    var modal_suppression_button = document.getElementById("suppression-modal-button");
    $('#suppressionModal').on('show.bs.modal', function (e) {
        update_href_modal_suppression_form(e.relatedTarget.dataset.href, e.relatedTarget.dataset.objectname)
    })
    function update_href_modal_suppression_form(href, objectname) {
        modal_suppression_form.setAttribute("action", href);
        modal_suppression_body.innerHTML = "<p>Êtes-vous sûr de vouloir supprimer <strong>"+objectname+"</strong> ?</p>";
    }
    // Add a click event listener to the document
    /*
    document.addEventListener("click", (event) => {
        // Handle the click on every suppression button on the page
        if (event.target.classList.contains("bouton-suppression")) {
            update_href_modal_suppression_form(event.target.dataset.href, event.target.dataset.objectname);
        }
    });
    */
    modal_suppression_button.addEventListener('click', function(event) {
        // Send POST request using Fetch API
        $.get(modal_suppression_form.action, function(data) {
            // Handle JSON response
            if (data.success) {
                // Show success message or perform any action
                location.reload();
            } else {
                // Show error message or perform any action
                console.log("First error"+data.error_message);
                showAlert(data.error_message);
            }
        })
        .catch(error => {
            // Handle any errors
            console.log("Second error");
            showAlert('La connexion au serveur a échoué.');
        });
    });
});

// A utiliser en créant des boutons de suppression du type <button class="btn btn-danger" data-objectname="Phase n°{{phase.numero}}" data-href="{% url 'object_suppression' model_name='Phase' object_id=phase.id %}">Supprimer</button>