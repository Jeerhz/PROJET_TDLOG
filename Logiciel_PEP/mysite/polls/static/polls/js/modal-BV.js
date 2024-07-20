document.addEventListener("DOMContentLoaded", () => {
    // Function to make formIntervenant appear
    var formIntervenant = document.getElementById("bv-modal");
    function formForIntervenant(href, formcontent) {
        // formIntervenant.classList.add("show");
        formIntervenant.setAttribute('action', href);
        var modalTable = document.getElementById("bv-modal-table");
        var bvFormContent = document.getElementById(formcontent);
        modalTable.innerHTML = bvFormContent.innerHTML;
    }
    // Add a click event listener to the document
    document.addEventListener("click", (event) => {
        // Check if the clicked element has the class
        if (event.target.classList.contains("bv-trigger")) {
            formForIntervenant(event.target.dataset.href, event.target.dataset.formcontent);
        }
    });
    });