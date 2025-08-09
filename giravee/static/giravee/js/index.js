// Function to fetch giravees details

function fetchGiraveesDetails(giraveeID, callback) {

    var url = '/giravee/get-giravees/';
    var csrftoken = getCookie('csrftoken');

    $.ajax({
        url: url,
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            'id': giraveeID
        },
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            swal("Error", "Error fetching giravees details: " + error, "error");
            callback([]);
        }
    });
}

// Function to fetch giravee details

function fetchGiraveeDetails(url, csrftoken, giraveeID, successCallback, errorCallback) {
    $.ajax({
        url: url,
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            'id': giraveeID
        },
        success: successCallback,
        error: errorCallback
    });
}

// Define a callback function to handle the fetched giravees data

function handleGiraveesData(response) {

    var giravees = response.giravees;
    var transactions = response.transactions || [];

    $('#edit-giravee-id').val(giravees[0].id);
    $('#edit-giravee-name').val(giravees[0].name);
    $('#edit-giravee-amount').val(giravees[0].amount);
    $('#edit-giravee-description').val(giravees[0].description);
    $('#edit-giravee-weight').val(giravees[0].weight);
    $('#edit-giravee-interest-rate').val(giravees[0].interest_rate);
    $('#edit-giravee-paid-amount').val(giravees[0].paid_amount);
    $('#edit-giravee-interest-amount').val(giravees[0].interest_amount);
    $('#edit-giravee-due-amount').val(giravees[0].due_amount);
    $('#edit-giravee-due-amount-without-interest').val(giravees[0].due_amount_without_interest);
    $('#edit-giravee-locker-number').val(giravees[0].locker_number);

    var tbody = $('#transaction-history-body');
    tbody.empty();

    if (transactions.length === 0) {
        tbody.append('<tr><td colspan="4" class="text-center"><p class="text-xs font-weight-bold mb-0">No transactions found</p></td></tr>');
    } else {
        transactions.forEach(function(txn) {
            var row = `
                <tr>
                    <td><p class="text-xs font-weight-bold mb-0">${txn.id}</p></td>
                    <td><p class="text-xs font-weight-bold mb-0">${txn.date}</p></td>
                    <td><p class="text-xs font-weight-bold mb-0">${txn.amount}</p></td>
                    <td><p class="text-xs font-weight-bold mb-0">${txn.note || ''}</p></td>
                </tr>
            `;

            tbody.append(row);
        });
    }
}

$(document).ready(function() {

    // Function to set the delete confirmation message

    function setDeleteConfirmation(giraveeName) {
        var confirmationMessage = 'Are you sure you want to delete the giravee item "' + giraveeName + '"?';
        $('#delete-giravee-confirmation').text(confirmationMessage);
    }

    // Function to fetch giravee information based on the active modal

    function fetchGiraveeInformation() {

        var activeModal = $('.modal:visible').attr('id');
        var giraveeInfo = {};

        if (activeModal === 'popup-add') {
            giraveeInfo.name = $('#add-giravee-name').val();
            giraveeInfo.amount = $('#add-giravee-amount').val();
            giraveeInfo.description = $('#add-giravee-description').val();
            giraveeInfo.weight = $('#add-giravee-weight').val();
            giraveeInfo.interest_rate = $('#add-giravee-interest-rate').val();
            giraveeInfo.locker_number = $('#add-giravee-locker-number').val();
        } else if (activeModal === 'popup-edit') {
            giraveeInfo.id = $('#edit-giravee-id').val();
            giraveeInfo.name = $('#edit-giravee-name').val();
            giraveeInfo.amount = $('#edit-giravee-amount').val();
            giraveeInfo.description = $('#edit-giravee-description').val();
            giraveeInfo.weight = $('#edit-giravee-weight').val();
            giraveeInfo.interest_rate = $('#edit-giravee-interest-rate').val();
            giraveeInfo.locker_number = $('#edit-giravee-locker-number').val();
            giraveeInfo.add_amount = $('#edit-giravee-add-amount').val();
            giraveeInfo.add_note = $('#edit-giravee-add-note').val();
        } else if (activeModal === 'popup-delete') {
            giraveeInfo.id = $('#delete-giravee-id').val();
        }

        return giraveeInfo;
    }

    // Event handler for opening the add giravee popup

    $(document).on('click', '#add-giravee', function(event) {
        event.preventDefault();
        showModal('popup-add');
    });

    // Event handler for opening the edit giravee popup

    $(document).on('click', '.edit-giravee', function(event) {
        event.preventDefault();

        var row = $(this).closest('tr');
        var giraveeID = row.find('td:eq(0) p').text().trim();

        fetchGiraveesDetails(giraveeID, handleGiraveesData);
        showModal('popup-edit');
    });

    // Event handler for opening the delete giravee popup

    $(document).on('click', '.delete-giravee', function(event) {
        event.preventDefault();

        var row = $(this).closest('tr');
        var giraveeID = row.find('td:eq(0) p').text().trim();
        var giraveeName = row.find('td:eq(1) p').text().trim();

        $('#delete-giravee-id').val(giraveeID);

        setDeleteConfirmation(giraveeName);
        showModal('popup-delete');
    });

    // Event handler for opening the delete giravee popup from the edit giravee popup

    $(document).on('click', '#delete-button-edit', function(event) {
        event.preventDefault();

        var giraveeID = $('#edit-giravee-id').val();
        var giraveeName = $('#edit-giravee-name').val();

        $('#delete-giravee-id').val(giraveeID);

        setDeleteConfirmation(giraveeName);
        hideModals();
        showModal('popup-delete');
    });

    // Event handler for add giravee button

    $(document).on('click', '#add-giravee-button', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var giraveeInfo = fetchGiraveeInformation();

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: giraveeInfo,
            success: function(response) {
                swal("Success", "Giravee added successfully", "success").then((value) => {
                    hideModals();
                    location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error adding giravee: " + error, "error");
            }
        });

    });

    // Event handler for update giravee button

    $(document).on('click', '#update-giravee-button', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var giraveeInfo = fetchGiraveeInformation();

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: giraveeInfo,
            success: function(response) {
                swal("Success", "Giravee updated successfully", "success").then((value) => {
                    hideModals();
                    location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error updating giravee: " + error, "error");
            }
        });

    });

    // Event handler for refresh giravee button

    $(document).on('click', '#refresh-giravee-button', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');

        var giraveeInfo = {};
        giraveeInfo.id = $('#edit-giravee-id').val();

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: giraveeInfo,
            success: function(response) {
                swal("Success", "Giravee refreshed successfully", "success").then((value) => {
                    hideModals();
                    location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error refreshing giravee: " + error, "error");
            }
        });

    });

    // Event handler for delete giravee button

    $(document).on('click', '#delete-giravee-button', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var giraveeID = $('#delete-giravee-id').val();

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: {
                'id': giraveeID
            },
            success: function(response) {
                swal("Success", "Giravee deleted successfully", "success").then((value) => {
                    hideModals();
                    location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error deleting giravee: " + error, "error");
            }
        });
    });

    // Event handler for the reset button in the add giravee popup

    $(document).on('click', '#reset-button-add', function(event) {
        event.preventDefault();
        $('#add-giravee-form')[0].reset();
    });

    // Event handler for the reset button in the edit giravee popup

    $(document).on('click', '#reset-button-edit', function(event) {
        event.preventDefault();
        $('#edit-giravee-form')[0].reset();
    });

    // Event handler to fetch and display search results

    $('#searchButton').click(function(event) {
        event.preventDefault();

        var csrftoken = getCookie('csrftoken');
        var searchText = $('#searchInput').val().trim();

        if (searchText) {

            $.ajax({
                url: '/giravee/search-giravee/',
                type: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    'search_text': searchText
                },
                success: function(response) {

                    if (response.giravees.trim() === '') {
                        swal("No Content", "No content found", "info");
                    } else {
                        $('tbody').html(response.giravees);
                        $('#pagination-main').hide();
                        $('#pagination-search').show();
                    }

                },
                error: function(xhr, status, error) {
                    swal("Error", "Error searching giravee: " + error, "error");
                }
            });

        } else {
            swal("Error", "Please enter a search term", "error");
        }

    });

    // Event handler for giravee details popup

    $(document).on('click', '.giravee-name', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var giraveeID = $(this).data('giravee-id');

        fetchGiraveeDetails(url, csrftoken, giraveeID, function(response) {
            var giravee = response.giravees[0];
            var popupContent = '<div class="giravee-details">';

            popupContent += '<p class="giravee-detail"><span class="giravee-label">ID:</span> ' + giravee.id + '</p>';
            popupContent += '<p class="giravee-detail"><span class="giravee-label">Name:</span> ' + giravee.name + '</p>';
            popupContent += '<p class="giravee-detail"><span class="giravee-label">Amount:</span> ' + giravee.amount + '</p>';
            popupContent += '<p class="giravee-detail"><span class="giravee-label">Description:</span> ' + giravee.description + '</p>';
            popupContent += '<p class="giravee-detail"><span class="giravee-label">Weight:</span> ' + giravee.weight + '</p>';
            popupContent += '<p class="giravee-detail"><span class="giravee-label">Interest Rate:</span> ' + giravee.interest_rate + '</p>';
            popupContent += '<p class="giravee-detail"><span class="giravee-label">Locker Number:</span> ' + giravee.locker_number + '</p>';
            popupContent += '<p class="giravee-detail"><span class="giravee-label">Date:</span> ' + formatDate(giravee.created_at) + '</p>';

            popupContent += '</div>';

            $('#giravee-details-content').html(popupContent);
            showModal('popup-show');
        }, function(xhr, status, error) {
            swal("Error", "Error fetching giravee details: " + error, "error");
        });

    });

});
