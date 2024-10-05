
$(document).ready(function(){
    // Listen to input in the search bar
    $('.select-search').on('keyup', function() {
        let query = $(this).val();
        let id_select = $(this).data('idselect');
        let select_input = $('#'+id_select);
        let href_ajax = select_input.data('hrefajax');
        // Send AJAX request if there's a query
        if (query.length > 2) {
            $.ajax({
                url: href_ajax,  // Django URL that will handle the search
                data: {
                    'q': query
                },
                dataType: 'json',
                success: function (data) {
                    // Clear current options
                    select_input.empty();  // id_name is Django's default ID for the 'name' field
                    select_input.append('<option value="">Select an option</option>');

                    // Populate select with new options from AJAX response
                    data.results.forEach(function(item) {
                        select_input.append('<option value="' + item.id + '">' + item.name + '</option>');
                    });
                }
            });
        }
    });
});