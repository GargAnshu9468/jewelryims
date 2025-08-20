// Function to fetch customer details

function fetchCustomerDetails(url, csrftoken, customerID, successCallback, errorCallback) {
    $.ajax({
        url: url,
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            'id': customerID
        },
        success: successCallback,
        error: errorCallback
    });
}

$(document).ready(function() {

    // Function to set the delete confirmation message

    function setDeleteConfirmation(customerName) {
        var confirmationMessage = 'Are you sure you want to delete the customer "' + customerName + '"?';
        $('#delete-customer-confirmation').text(confirmationMessage);
    }

    // Function to fetch customer information based on the active modal

    function fetchCustomerInformation() {

        var activeModal = $('.modal:visible').attr('id');
        var customerInfo = {};

        if (activeModal === 'popup-add') {
            customerInfo.name = $('#customer-name').val();
            customerInfo.phone = $('#customer-phone').val();
            customerInfo.address = $('#customer-address').val();
            customerInfo.email = $('#customer-email').val();
            customerInfo.gstin = $('#customer-gstin').val();
            customerInfo.date = $('#add-customer-date').val();
        } else if (activeModal === 'popup-edit') {
            customerInfo.id = $('#edit-customer-id').val();
            customerInfo.name = $('#edit-customer-name').val();
            customerInfo.phone = $('#edit-customer-phone').val();
            customerInfo.address = $('#edit-customer-address').val();
            customerInfo.email = $('#edit-customer-email').val();
            customerInfo.gstin = $('#edit-customer-gstin').val();
            customerInfo.date = $('#edit-customer-date').val();
        } else if (activeModal === 'popup-delete') {
            customerInfo.id = $('#delete-customer-id').val();
        }

        return customerInfo;
    }

    // Event handler for opening the add customer popup

    $(document).on('click', '#add-customer', function(event) {
        event.preventDefault();
        showModal('popup-add');
    });

    // Event handler for opening the edit customer popup

    $(document).on('click', '.edit-customer', function(event) {
        event.preventDefault();

        var row = $(this).closest('tr');
        var customerID = row.find('td:eq(0) p').text().trim();
        // var customerName = row.find('td:eq(1) p').text().trim();
        // var customerPhone = row.find('td:eq(2) p').text().trim();
        // var customerGSTIN = row.find('td:eq(3) p').text().trim();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');

        fetchCustomerDetails(url, csrftoken, customerID, function(response) {
            var customerAddress = response.address;
            var customerEmail = response.email;
            var customerName = response.name;
            var customerPhone = response.phone;
            var customerGSTIN = response.gstin;
            var customerDate = response.date;

            $('#edit-customer-email').val(customerEmail);
            $('#edit-customer-address').val(customerAddress);
            $('#edit-customer-name').val(customerName);
            $('#edit-customer-phone').val(customerPhone);
            $('#edit-customer-gstin').val(customerGSTIN);
            $('#edit-customer-date').val(customerDate);
        }, function(xhr, status, error) {
            swal("Error", "Error updating customer info: " + error, "error");
        });

        $('#edit-customer-id').val(customerID);
        // $('#edit-customer-name').val(customerName);
        // $('#edit-customer-phone').val(customerPhone);
        // $('#edit-customer-gstin').val(customerGSTIN);

        showModal('popup-edit');
    });

    // Event handler for opening the delete customer popup

    $(document).on('click', '.delete-customer', function(event) {
        event.preventDefault();

        var row = $(this).closest('tr');
        var customerID = row.find('td:eq(0) p').text().trim();
        var customerName = row.find('td:eq(1) p').text().trim();

        $('#delete-customer-id').val(customerID);

        setDeleteConfirmation(customerName);
        showModal('popup-delete');
    });

    // Event handler for opening the delete customer popup from the edit customer popup

    $(document).on('click', '#delete-button-edit', function(event) {
        event.preventDefault();

        var customerID = $('#edit-customer-id').val();
        var customerName = $('#edit-customer-name').val();

        $('#delete-customer-id').val(customerID);

        setDeleteConfirmation(customerName);
        hideModals();
        showModal('popup-delete');
    });

    // Event handler for add customer button

    $(document).on('click', '#add-customer-button', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var customerInfo = fetchCustomerInformation();

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: customerInfo,
            success: function(response) {
                swal("Success", "Customer added successfully", "success").then((value) => {
                    hideModals();
                    location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error adding customer: " + error, "error");
            }
        });

    });

    // Event handler for update customer button

    $(document).on('click', '#update-customer-button', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var customerInfo = fetchCustomerInformation();

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: customerInfo,
            success: function(response) {
                swal("Success", "Customer updated successfully", "success").then((value) => {
                    hideModals();
                    // location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error updating customer: " + error, "error");
            }
        });

    });

    // Event handler for delete customer button

    $(document).on('click', '#delete-customer-button', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var customerID = $('#delete-customer-id').val();

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: {
                'id': customerID
            },
            success: function(response) {
                swal("Success", "Customer deleted successfully", "success").then((value) => {
                    hideModals();
                    location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error deleting customer: " + error, "error");
            }
        });
    });

    // Event handler for the reset button in the add customer popup

    $(document).on('click', '#reset-button-add', function(event) {
        event.preventDefault();
        $('#add-customer-form')[0].reset();
    });

    // Event handler for the reset button in the edit customer popup

    $(document).on('click', '#reset-button-edit', function(event) {
        event.preventDefault();
        $('#edit-customer-form')[0].reset();
    });

    // Search button click

    $('#searchButton').click(function(event) {
        event.preventDefault();
        performSearch(1);
    });

    // Handle pagination clicks for search

    $(document).on('click', '.search-page', function(e) {
        e.preventDefault();
        var page = $(this).data('page');
        performSearch(page);
    });

    function performSearch(page) {
        var csrftoken = getCookie('csrftoken');

        var searchText = $('#searchInput').val().trim();
        var startDate = $('#searchStartDate').val();
        var endDate = $('#searchEndDate').val();

        // if (!searchText && !startDate && !endDate) {
        //     swal("Error", "Please enter a search term or date range", "error");
        //     return;
        // }

        if (startDate && endDate && new Date(endDate) < new Date(startDate)) {
            var temp = startDate;
            startDate = endDate;
            endDate = temp;
        }

        $.ajax({
            url: '/transactions/search-customer/',
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                'search_text': searchText,
                'start_date': startDate,
                'end_date': endDate,
                'page': page
            },
            success: function(response) {
                if (response.customers.trim() === '') {
                    $('tbody').empty();
                    swal("No Content", "No content found", "info");
                    $('#pagination-search').hide();
                    $('#pagination-main').hide();
                } else {
                    $('tbody').html(response.customers);
                    $('#pagination-main').hide();
                    $('#pagination-search').html(response.pagination_html).show();
                }
            },
            error: function(xhr, status, error) {
                swal("Error", "Error searching customers: " + error, "error");
            }
        });
    }

    // Event handler to delete search results

    $('#deleteButton').click(function(event) {
        event.preventDefault();

        var csrftoken = getCookie('csrftoken');

        var searchText = $('#searchInput').val().trim();
        var startDate = $('#searchStartDate').val();
        var endDate = $('#searchEndDate').val();

        if (!searchText && !startDate && !endDate) {
            swal("Error", "Please enter a search term or date range", "error");
            return;
        }

        if (startDate && endDate && new Date(endDate) < new Date(startDate)) {
            var temp = startDate;
            startDate = endDate;
            endDate = temp;
        }

        swal({
            title: "Are you sure?",
            text: "This will permanently delete the matching customers.",
            icon: "warning",
            buttons: true,
            dangerMode: true,
        }).then((willDelete) => {
            if (willDelete) {
                $.ajax({
                    url: '/transactions/delete-customer/',
                    type: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    data: {
                        'search_text': searchText,
                        'start_date': startDate,
                        'end_date': endDate
                    },
                    success: function(response) {
                        if (response.status === 'info') {
                            swal("No Content", response.message, "info");
                        } else {
                            swal("Success", response.message, "success").then(() => {
                                location.reload();
                            });
                        }
                    },
                    error: function(xhr, status, error) {
                        swal("Error", "Error deleting customers: " + error, "error");
                    }
                });
            }
        });
    });

    // Event handler for customer details popup

    $(document).on('click', '.customer-name', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var customerID = $(this).closest('tr').find('td:eq(0) p').text().trim();

        fetchCustomerDetails(url, csrftoken, customerID, function(response) {
            var popupContent = '<div class="customer-details">';

            popupContent += '<p class="customer-detail"><span class="customer-label">ID:</span> ' + response.id + '</p>';
            popupContent += '<p class="customer-detail"><span class="customer-label">Name:</span> ' + response.name + '</p>';
            popupContent += '<p class="customer-detail"><span class="customer-label">Phone:</span> ' + response.phone + '</p>';
            popupContent += '<p class="customer-detail"><span class="customer-label">Address:</span> ' + response.address + '</p>';
            popupContent += '<p class="customer-detail"><span class="customer-label">Email:</span> ' + response.email + '</p>';
            popupContent += '<p class="customer-detail"><span class="customer-label">GSTIN No:</span> ' + response.gstin + '</p>';
            popupContent += '<p class="customer-detail"><span class="customer-label">Date:</span> ' + formatDate(response.date) + '</p>';

            popupContent += '</div>';

            $('#customer-details-content').html(popupContent);
            showModal('popup-show');
        }, function(xhr, status, error) {
            swal("Error", "Error fetching customer details: " + error, "error");
        });

    });

});
