$(document).ready(function() {
            // Function to handle search
            $('#search-input').on('input', function(event) {
                // Prevent the default form submission
                event.preventDefault();
                console.log(url_suggestions);
                // Get the query from the search input
                var query = $('#search-input').val().trim();
                if (query.length > 0) {
                    // Make an AJAX request to the Django view
                    $.ajax({
                        type: 'GET',
                        url: url_suggestions,
                        data: {
                            'query': query
                        },
                        success: function(data) {
                            // Clear previous results
                            $('#suggestions-results').empty();
                            var resultsList = ''
                            var resultsShow = false;
                            // Append new results
                            if (data.suggestions_etude.length > 0) {
                                data.suggestions_etude.forEach(function(etude) {
                                    resultsList += '<a href="'+href_etude+etude[1].toString()+'" class="list-group-item list-group-item-action text-primary">' + etude[0] + '</a>';
                                });
                                resultsShow = true;
                            } 
                            if (data.suggestions_client.length > 0) {
                                data.suggestions_client.forEach(function(client) {
                                    resultsList += '<a href="'+href_client+client[1].toString()+'" class="list-group-item list-group-item-action text-success">' + client[0] + '</a>';
                                });
                                resultsShow = true;
                            }
                            if (data.suggestions_student.length > 0) {
                                data.suggestions_student.forEach(function(student) {
                                    resultsList += '<a href="'+href_student+student[2].toString()+'" class="list-group-item list-group-item-action text-dark">' + student[0] + ' ' + student[1] + '</a>';
                                });
                                resultsShow = true;
                            }
                            $('#suggestions-results').html(resultsList);
                            if(resultsShow){
                                $('#suggestions-results').addClass('show');
                            }
                            else{
                                $('#suggestions-results').removeClass('show');
                            }
                        }
                    });
                } else {
                    $('#suggestions-results').removeClass('show');
                }
            });
            $(document).on('click', function(event) {
        var container = $('#suggestions-results');
        // If the clicked element is not inside the container, hide suggestions
        if (!container.is(event.target) && container.has(event.target).length === 0) {
            container.removeClass('show');
        }
    });
        });