// Function to fetch supplier details

function fetchSupplierDetails(url, csrftoken, supplierID, successCallback, errorCallback) {
    $.ajax({
        url: url,
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            'id': supplierID
        },
        success: successCallback,
        error: errorCallback
    });
}

$(document).ready(function() {

    // Function to set the delete confirmation message

    function setDeleteConfirmation(supplierName) {
        var confirmationMessage = 'Are you sure you want to delete the supplier "' + supplierName + '"?';
        $('#delete-supplier-confirmation').text(confirmationMessage);
    }

    // Function to fetch supplier information based on the active modal

    function fetchSupplierInformation() {

        var activeModal = $('.modal:visible').attr('id');
        var supplierInfo = {};

        if (activeModal === 'popup-add') {
            supplierInfo.name = $('#add-supplier-name').val();
            supplierInfo.phone = $('#add-supplier-phone').val();
            supplierInfo.address = $('#add-supplier-address').val();
            supplierInfo.email = $('#add-supplier-email').val();
            supplierInfo.gstin = $('#add-supplier-gstin').val();
            supplierInfo.date = $('#add-supplier-date').val();
        } else if (activeModal === 'popup-edit') {
            supplierInfo.id = $('#edit-supplier-id').val();
            supplierInfo.name = $('#edit-supplier-name').val();
            supplierInfo.phone = $('#edit-supplier-phone').val();
            supplierInfo.address = $('#edit-supplier-address').val();
            supplierInfo.email = $('#edit-supplier-email').val();
            supplierInfo.gstin = $('#edit-supplier-gstin').val();
            supplierInfo.date = $('#edit-supplier-date').val();
        } else if (activeModal === 'popup-delete') {
            supplierInfo.id = $('#delete-supplier-id').val();
        }

        return supplierInfo;
    }

    // Event handler for opening the add supplier popup

    $(document).on('click', '#add-supplier', function(event) {
        event.preventDefault();
        showModal('popup-add');
    });

    // Event handler for opening the edit supplier popup

    $(document).on('click', '.edit-supplier', function(event) {
        event.preventDefault();

        var row = $(this).closest('tr');
        var supplierID = row.find('td:eq(0) p').text().trim();
        // var supplierName = row.find('td:eq(1) p').text().trim();
        // var supplierPhone = row.find('td:eq(2) p').text().trim();
        // var supplierGSTIN = row.find('td:eq(3) p').text().trim();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');

        fetchSupplierDetails(url, csrftoken, supplierID, function(response) {
            var supplierAddress = response.address;
            var supplierEmail = response.email;
            var supplierName = response.name;
            var supplierPhone = response.phone;
            var supplierGSTIN = response.gstin;
            var supplierDate = response.date;

            $('#edit-supplier-email').val(supplierEmail);
            $('#edit-supplier-address').val(supplierAddress);
            $('#edit-supplier-name').val(supplierName);
            $('#edit-supplier-phone').val(supplierPhone);
            $('#edit-supplier-gstin').val(supplierGSTIN);
            $('#edit-supplier-date').val(supplierDate);
        }, function(xhr, status, error) {
            swal("Error", "Error updating supplier info: " + error, "error");
        });

        $('#edit-supplier-id').val(supplierID);
        // $('#edit-supplier-name').val(supplierName);
        // $('#edit-supplier-phone').val(supplierPhone);
        // $('#edit-supplier-gstin').val(supplierGSTIN);

        showModal('popup-edit');
    });

    // Event handler for opening the delete supplier popup

    $(document).on('click', '.delete-supplier', function(event) {
        event.preventDefault();

        var row = $(this).closest('tr');
        var supplierID = row.find('td:eq(0) p').text().trim();
        var supplierName = row.find('td:eq(1) p').text().trim();

        $('#delete-supplier-id').val(supplierID);

        setDeleteConfirmation(supplierName);
        showModal('popup-delete');
    });

    // Event handler for opening the delete supplier popup from the edit supplier popup

    $(document).on('click', '#delete-button-edit', function(event) {
        event.preventDefault();

        var supplierID = $('#edit-supplier-id').val();
        var supplierName = $('#edit-supplier-name').val();

        $('#delete-supplier-id').val(supplierID);

        setDeleteConfirmation(supplierName);
        hideModals();
        showModal('popup-delete');
    });

    // Event handler for add supplier button

    $(document).on('click', '#add-supplier-button', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var supplierInfo = fetchSupplierInformation();

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: supplierInfo,
            success: function(response) {
                swal("Success", "Supplier added successfully", "success").then((value) => {
                    hideModals();
                    location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error adding supplier: " + error, "error");
            }
        });

    });

    // Event handler for update supplier button

    $(document).on('click', '#update-supplier-button', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var supplierInfo = fetchSupplierInformation();

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: supplierInfo,
            success: function(response) {
                swal("Success", "Supplier updated successfully", "success").then((value) => {
                    hideModals();
                    location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error updating supplier: " + error, "error");
            }
        });

    });

    // Event handler for delete supplier button

    $(document).on('click', '#delete-supplier-button', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var supplierID = $('#delete-supplier-id').val();

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: {
                'id': supplierID
            },
            success: function(response) {
                swal("Success", "Supplier deleted successfully", "success").then((value) => {
                    hideModals();
                    location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error deleting supplier: " + error, "error");
            }
        });
    });

    // Event handler for the reset button in the add supplier popup

    $(document).on('click', '#reset-button-add', function(event) {
        event.preventDefault();
        $('#add-supplier-form')[0].reset();
    });

    // Event handler for the reset button in the edit supplier popup

    $(document).on('click', '#reset-button-edit', function(event) {
        event.preventDefault();
        $('#edit-supplier-form')[0].reset();
    });

    // Event handler to fetch and display search results

    $('#searchButton').click(function(event) {
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

        $.ajax({
            url: '/transactions/search-supplier/',
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

                if (response.suppliers.trim() === '') {
                    swal("No Content", "No content found", "info");
                } else {
                    $('tbody').html(response.suppliers);
                    $('#pagination-main').hide();
                    $('#pagination-search').show();
                }

            },
            error: function(xhr, status, error) {
                swal("Error", "Error searching supplier: " + error, "error");
            }
        });
    });

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

        $.ajax({
            url: '/transactions/delete-supplier/',
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
                swal("Success", "Suppliers deleted successfully", "success").then((value) => {
                    location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error deleting suppliers: " + error, "error");
            }
        });
    });

    // Event handler for supplier details popup

    $(document).on('click', '.supplier-name', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var supplierID = $(this).closest('tr').find('td:eq(0) p').text().trim();

        fetchSupplierDetails(url, csrftoken, supplierID, function(response) {
            var popupContent = '<div class="supplier-details">';

            popupContent += '<p class="supplier-detail"><span class="supplier-label">ID:</span> ' + response.id + '</p>';
            popupContent += '<p class="supplier-detail"><span class="supplier-label">Name:</span> ' + response.name + '</p>';
            popupContent += '<p class="supplier-detail"><span class="supplier-label">Phone:</span> ' + response.phone + '</p>';
            popupContent += '<p class="supplier-detail"><span class="supplier-label">Address:</span> ' + response.address + '</p>';
            popupContent += '<p class="supplier-detail"><span class="supplier-label">Email:</span> ' + response.email + '</p>';
            popupContent += '<p class="supplier-detail"><span class="supplier-label">GSTIN No:</span> ' + response.gstin + '</p>';
            popupContent += '<p class="supplier-detail"><span class="supplier-label">Date:</span> ' + response.date + '</p>';

            popupContent += '</div>';

            $('#supplier-details-content').html(popupContent);
            showModal('popup-show');
        }, function(xhr, status, error) {
            swal("Error", "Error fetching supplier details: " + error, "error");
        });

    });

});
