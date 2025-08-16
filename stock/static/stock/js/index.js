// Function to fetch stocks details

function fetchStocksDetails(stockID, callback) {

    var url = '/stock/get-stocks/';
    var csrftoken = getCookie('csrftoken');

    $.ajax({
        url: url,
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            'id': stockID
        },
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            swal("Error", "Error fetching stocks details: " + error, "error");
            callback([]);
        }
    });
}

// Function to fetch stock details

function fetchStockDetails(url, csrftoken, stockID, successCallback, errorCallback) {
    $.ajax({
        url: url,
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: {
            'id': stockID
        },
        success: successCallback,
        error: errorCallback
    });
}

// Define a callback function to handle the fetched stocks data

function handleStocksData(response) {

    var stocks = response.stocks;

    $('#edit-stock-id').val(stocks[0].id);
    $('#edit-stock-name').val(stocks[0].name);
    $('#edit-stock-quantity').val(stocks[0].quantity);
    $('#edit-stock-description').val(stocks[0].description);
    $('#edit-stock-weight').val(stocks[0].weight);
    $('#edit-stock-purchase-price').val(stocks[0].purchase_price);
    $('#edit-stock-material').val(stocks[0].material);
    $('#edit-stock-category').val(stocks[0].category);
    $('#edit-stock-karat').val(stocks[0].karat);
    $('#edit-stock-date').val(stocks[0].date);
}

$(document).ready(function() {

    // Function to set the delete confirmation message

    function setDeleteConfirmation(stockName) {
        var confirmationMessage = 'Are you sure you want to delete the stock item "' + stockName + '"?';
        $('#delete-stock-confirmation').text(confirmationMessage);
    }

    // Function to fetch stock information based on the active modal

    function fetchStockInformation() {

        var activeModal = $('.modal:visible').attr('id');
        var stockInfo = {};

        if (activeModal === 'popup-add') {
            stockInfo.name = $('#add-stock-name').val();
            stockInfo.quantity = $('#add-stock-quantity').val();
            stockInfo.description = $('#add-stock-description').val();
            stockInfo.weight = $('#add-stock-weight').val();
            stockInfo.purchase_price = $('#add-stock-purchase-price').val();
            stockInfo.material = $('#add-stock-material').val();
            stockInfo.category = $('#add-stock-category').val();
            stockInfo.karat = $('#add-stock-karat').val();
            stockInfo.date = $('#add-stock-date').val();
        } else if (activeModal === 'popup-edit') {
            stockInfo.id = $('#edit-stock-id').val();
            stockInfo.name = $('#edit-stock-name').val();
            stockInfo.quantity = $('#edit-stock-quantity').val();
            stockInfo.description = $('#edit-stock-description').val();
            stockInfo.weight = $('#edit-stock-weight').val();
            stockInfo.purchase_price = $('#edit-stock-purchase-price').val();
            stockInfo.material = $('#edit-stock-material').val();
            stockInfo.category = $('#edit-stock-category').val();
            stockInfo.karat = $('#edit-stock-karat').val();
            stockInfo.date = $('#edit-stock-date').val();
        } else if (activeModal === 'popup-delete') {
            stockInfo.id = $('#delete-stock-id').val();
        }

        return stockInfo;
    }

    // Event handler for opening the add stock popup

    $(document).on('click', '#add-stock', function(event) {
        event.preventDefault();
        showModal('popup-add');
    });

    // Event handler for opening the edit stock popup

    $(document).on('click', '.edit-stock', function(event) {
        event.preventDefault();

        var row = $(this).closest('tr');
        var stockID = row.find('td:eq(0) p').text().trim();

        fetchStocksDetails(stockID, handleStocksData);
        showModal('popup-edit');
    });

    // Event handler for opening the delete stock popup

    $(document).on('click', '.delete-stock', function(event) {
        event.preventDefault();

        var row = $(this).closest('tr');
        var stockID = row.find('td:eq(0) p').text().trim();
        var stockName = row.find('td:eq(1) p').text().trim();

        $('#delete-stock-id').val(stockID);

        setDeleteConfirmation(stockName);
        showModal('popup-delete');
    });

    // Event handler for opening the delete stock popup from the edit stock popup

    $(document).on('click', '#delete-button-edit', function(event) {
        event.preventDefault();

        var stockID = $('#edit-stock-id').val();
        var stockName = $('#edit-stock-name').val();

        $('#delete-stock-id').val(stockID);

        setDeleteConfirmation(stockName);
        hideModals();
        showModal('popup-delete');
    });

    // Event handler for add stock button

    $(document).on('click', '#add-stock-button', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var stockInfo = fetchStockInformation();

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: stockInfo,
            success: function(response) {
                swal("Success", "Stock added successfully", "success").then((value) => {
                    hideModals();
                    location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error adding stock: " + error, "error");
            }
        });

    });

    // Event handler for update stock button

    $(document).on('click', '#update-stock-button', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var stockInfo = fetchStockInformation();

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: stockInfo,
            success: function(response) {
                swal("Success", "Stock updated successfully", "success").then((value) => {
                    hideModals();
                    location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error updating stock: " + error, "error");
            }
        });

    });

    // Event handler for delete stock button

    $(document).on('click', '#delete-stock-button', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var stockID = $('#delete-stock-id').val();

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: {
                'id': stockID
            },
            success: function(response) {
                swal("Success", "Stock deleted successfully", "success").then((value) => {
                    hideModals();
                    location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error deleting stock: " + error, "error");
            }
        });
    });

    // Event handler for the reset button in the add stock popup

    $(document).on('click', '#reset-button-add', function(event) {
        event.preventDefault();
        $('#add-stock-form')[0].reset();
    });

    // Event handler for the reset button in the edit stock popup

    $(document).on('click', '#reset-button-edit', function(event) {
        event.preventDefault();
        $('#edit-stock-form')[0].reset();
    });

    // Event handler to fetch and display search results

    // $('#searchButton').click(function(event) {
    //     event.preventDefault();

    //     var csrftoken = getCookie('csrftoken');

    //     var searchText = $('#searchInput').val().trim();
    //     var startDate = $('#searchStartDate').val();
    //     var endDate = $('#searchEndDate').val();

    //     if (!searchText && !startDate && !endDate) {
    //         swal("Error", "Please enter a search term or date range", "error");
    //         return;
    //     }

    //     if (startDate && endDate && new Date(endDate) < new Date(startDate)) {
    //         var temp = startDate;
    //         startDate = endDate;
    //         endDate = temp;
    //     }

    //     $.ajax({
    //         url: '/stock/search-stock/',
    //         type: 'POST',
    //         headers: {
    //             'X-CSRFToken': csrftoken
    //         },
    //         data: {
    //             'search_text': searchText,
    //             'start_date': startDate,
    //             'end_date': endDate
    //         },
    //         success: function(response) {

    //             if (response.stocks.trim() === '') {
    //                 $('tbody').empty();
    //                 swal("No Content", "No content found", "info");
    //                 $('#pagination-search').hide();
    //                 $('#pagination-main').hide();
    //             } else {
    //                 $('tbody').html(response.stocks);
    //                 $('#pagination-main').hide();
    //                 $('#pagination-search').show();
    //             }

    //         },
    //         error: function(xhr, status, error) {
    //             swal("Error", "Error searching stock: " + error, "error");
    //         }
    //     });
    // });

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

        $.ajax({
            url: '/stock/search-stock/',
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: {
                'search_text': searchText,
                'start_date': startDate,
                'end_date': endDate,
                'page': page
            },
            success: function(response) {
                $('tbody').html(response.stocks);
                $('#pagination-main').hide();
                $('#pagination-search').html(response.pagination_html).show();
            },
            error: function(xhr, status, error) {
                swal("Error", "Error searching stocks: " + error, "error");
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
            text: "This will permanently delete the matching Stock records.",
            icon: "warning",
            buttons: true,
            dangerMode: true,
        }).then((willDelete) => {
            if (willDelete) {
                $.ajax({
                    url: '/stock/delete-stock/',
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
                        swal("Error", "Error deleting stocks: " + error, "error");
                    }
                });
            }
        });
    });

    // Event handler for stock details popup

    $(document).on('click', '.stock-name', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var stockID = $(this).data('stock-id');

        fetchStockDetails(url, csrftoken, stockID, function(response) {
            var stock = response.stocks[0];
            var popupContent = '<div class="stock-details">';

            popupContent += '<p class="stock-detail"><span class="stock-label">ID:</span> ' + stock.id + '</p>';
            popupContent += '<p class="stock-detail"><span class="stock-label">Name:</span> ' + stock.name + '</p>';
            popupContent += '<p class="stock-detail"><span class="stock-label">Quantity:</span> ' + stock.quantity + '</p>';
            popupContent += '<p class="stock-detail"><span class="stock-label">Description:</span> ' + stock.description + '</p>';
            popupContent += '<p class="stock-detail"><span class="stock-label">Weight:</span> ' + stock.weight + '</p>';
            popupContent += '<p class="stock-detail"><span class="stock-label">Purchase Price:</span> ' + stock.purchase_price + '</p>';
            popupContent += '<p class="stock-detail"><span class="stock-label">Material:</span> ' + stock.material + '</p>';
            popupContent += '<p class="stock-detail"><span class="stock-label">Category:</span> ' + stock.category + '</p>';
            popupContent += '<p class="stock-detail"><span class="stock-label">Karat:</span> ' + stock.karat + '</p>';
            popupContent += '<p class="stock-detail"><span class="stock-label">Date:</span> ' + stock.date + '</p>';

            popupContent += '</div>';

            $('#stock-details-content').html(popupContent);
            showModal('popup-show');
        }, function(xhr, status, error) {
            swal("Error", "Error fetching stock details: " + error, "error");
        });

    });

});
