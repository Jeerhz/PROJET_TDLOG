$(document).ready(function() {
            // Function to handle search
            $('#search-input-student').on('input', function(event) {
                // Prevent the default form submission
                event.preventDefault();
                console.log(url_suggestions);
                // Get the query from the search input
                var query = $('#search-input-student').val().trim();
                if (query.length > 0) {
                    // Make an AJAX request to the Django view
                    $.ajax({
                        type: 'GET',
                        url: url_suggestions_student,
                        data: {
                            'query': query
                        },
                        success: function(data) {
                            // Clear previous results
                            $('#suggestions-results-student').empty();
                            var resultsList = ''
                            var resultsShow = false;
                            // Append new results
                            if (data.suggestions_student.length > 0) {
                                data.suggestions_student.forEach(function(student) {
                                    resultsList += '<div data-href="'+href_form_intervenant+student[2].toString()+'" data-badge="'+student[0] + ' ' + student[1]+'" class="list-group-item list-group-item-action text-dark w-100 justify-content-between student-sg" style="cursor:pointer;" data-toggle="modal" data-target="#formModal"><span>' + student[0] + ' ' + student[1] + '</span><span class="badge badge-primary ml-4">'+ student[3] +'</span><span class="badge badge-success ml-4">'+ student[4] +'</span></div>';
                                });
                                resultsShow = true;
                            }
                            $('#suggestions-results-student').html(resultsList);
                            if(resultsShow){
                                $('#suggestions-results-student').addClass('show');
                            }
                            else{
                                $('#suggestions-results-student').removeClass('show');
                            }
                        }
                    });
                } else {
                    $('#suggestions-results-student').removeClass('show');
                }
            });
            $(document).on('click', function(event) {
        var container = $('#suggestions-results-student');
        // If the clicked element is not inside the container, hide suggestions
        if (!container.is(event.target) && container.has(event.target).length === 0) {
            container.removeClass('show');
        }
    });
        });

document.addEventListener("DOMContentLoaded", () => {
    // Function to make formIntervenant appear
    var formIntervenant = document.getElementById("form-intervenant");
    function formForIntervenant(href, badge) {
        var formBadge = document.getElementById("name-intervenant");
        // formIntervenant.classList.add("show");
        formIntervenant.setAttribute('action', href);
        formBadge.textContent = badge;
    }
    // Add a click event listener to the document
    document.addEventListener("click", (event) => {
        // Check if the clicked element has the class "student-sg"
        if (event.target.classList.contains("student-sg")) {
            formForIntervenant(event.target.dataset.href, event.target.dataset.badge);
        }
        // If click outside formIntervenant, we make it disappear
        /*
        if(!formIntervenant.is(event.target) && container.has(event.target).length === 0){
            formIntervenant.removeClass("show");
        }
        */
    });
    });