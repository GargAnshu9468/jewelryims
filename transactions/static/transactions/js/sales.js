// Function to fetch stocks details

function fetchStocksDetails(callback) {

    var url = '/stock/get-stocks/';
    var csrftoken = getCookie('csrftoken');

    $.ajax({
        url: url,
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
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

// Define a callback function to handle the fetched stocks data

function handleStocksData(response) {

    var stocks = response.stocks;
    var select = $('.stock');

    select.empty().append($('<option>', {
        value: '',
        text: '--- Select Stock ---',
        disabled: true,
        selected: true
    }));

    $.each(stocks, function(index, stock) {
        select.append($('<option>', {
            value: stock.id,
            text: stock.name
        }));
    });
}

// Function to calculate price for each row

function calculatePrice() {

    $('#product-details-section .form-group.row').each(function() {
        var pricePerItem = parseFloat($(this).find('.price-per-item').val());
        var weight = parseFloat($(this).find('.weight').val());
        var quantity = parseFloat($(this).find('.quantity').val());

        if (!isNaN(pricePerItem) && !isNaN(weight) && pricePerItem > 0 && weight >= 0) {
            var price = pricePerItem * weight * quantity;
            $(this).find('.price').val(price.toFixed(2));
        } else {
            $(this).find('.price').val('0.00');
        }
    });
}

// Function to fetch sale information based on the active modal

function fetchSaleInformation() {

    var activeModal = $('.modal:visible');

    var saleInfo = {
        'time': $('#add-sale-date').val(),
    };

    if (activeModal.attr('id') === 'popup-add') {

        // Customer Details Section

        saleInfo.customer = {};

        saleInfo.customer.name = $('#customer-name').val();
        saleInfo.customer.phone = $('#customer-phone').val();
        saleInfo.customer.email = $('#customer-email').val();
        saleInfo.customer.gstin = $('#customer-gstin').val();
        saleInfo.customer.address = $('#customer-address').val();

        // Product Details Section

        saleInfo.products = [];

        $('#product-details-section .form-group.row').each(function() {
            var product = {
                id: $(this).find('.stock').val(),
                pricePerItem: parseFloat($(this).find('.price-per-item').val()),
                quantity: parseFloat($(this).find('.quantity').val()),
                totalPrice: parseFloat($(this).find('.price').val()),
                weight: parseFloat($(this).find('.weight').val()),
                stockNote: $(this).find('.stock-note').val()
            };

            saleInfo.products.push(product);
        });

        // Payment Details Section

        saleInfo.paymentDetails = {};

        saleInfo.paymentDetails.paymentMethod = $('#payment-method').val();
        saleInfo.paymentDetails.paymentAmount = $('#payment-amount').val();

        // Discount Details Section

        saleInfo.discountDetails = {};

        saleInfo.discountDetails.discountType = $('#discount-type').val();
        saleInfo.discountDetails.discountValue = $('#discount-value').val();
        saleInfo.discountDetails.discountNote = $('#discount-note').val();

        // Tax Details Section

        saleInfo.taxDetails = {};
        saleInfo.taxDetails.gst = $('#gst').val();

        // Labour/Making Charges Details Section

        saleInfo.chargeDetails = {};

        saleInfo.chargeDetails.labourMakingChargeType = $('#labour-making-charge-type').val();
        saleInfo.chargeDetails.labourMakingChargeValue = $('#labour-making-charge-value').val();
        saleInfo.chargeDetails.labourMakingChargeNote = $('#labour-making-charge-note').val();
    }

    return saleInfo;
}

// Function to set the delete confirmation message

function setDeleteConfirmation(saleID) {
    var confirmationMessage = `Are you sure you want to delete the Sale Bill No: ${saleID}?`;
    $('#delete-sale-bill-confirmation').text(confirmationMessage);
}

// Function to fetch sale details

function fetchSaleDetails(callback) {

    var url = '/transactions/get-sale/';
    var csrftoken = getCookie('csrftoken');

    $.ajax({
        url: url,
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        success: function(response) {
            callback(response);
        },
        error: function(xhr, status, error) {
            swal("Error", "Error fetching sale details: " + error, "error");
            callback([]);
        }
    });
}

// Function to update sale details

function updateSaleDetails(saleInfo) {

    var url = '/transactions/update-sale/';
    var csrftoken = getCookie('csrftoken');

    $.ajax({
        url: url,
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: saleInfo,
        success: function(response) {
            swal("Error", "Sale details updated successfully", "error");
        },
        error: function(xhr, status, error) {
            swal("Error", "Error updating sale details: " + error, "error");
        }
    });
}

// Function to update bill status

function updateBillStatus(grandTotal, paid) {
    let status = 'Unpaid';

    if (paid <= 0) {
        status = 'Unpaid';
    } else if (paid > 0 && paid < grandTotal) {
        status = 'Partially Paid';
    } else {
        status = 'Paid'
    }

    $('#bill-status-view').text(status);
}

$(document).ready(function() {

    // Event handler for opening the add sale popup

    $(document).on('click', '#add-sale', function(event) {
        event.preventDefault();

        fetchStocksDetails(handleStocksData);
        showModal('popup-add');
    });

    // Event listener for change in price per item or weight or quantity

    $(document).on('change', '.price-per-item, .weight, .quantity', function() {
        calculatePrice();
    });

    // Event listener for adding item

    $('#add-more').click(function() {
        var newRow = $('#product-details-section .form-group.row').last().clone();

        newRow.find('input').val('');
        newRow.find('select').val('');

        $('#product-details-section').append(newRow);

        // calculatePrice();
    });

    // Event listener for deleting item

    $(document).on('click', '.delete-item', function() {
        var rowCount = $('#product-details-section .form-group.row').length;

        if (rowCount > 1) {
            $(this).closest('.form-group.row').remove();
            // calculatePrice();
        } else {
            alert("At least one item must be present!");
        }
    });

    // Event handler for calculate button

    $(document).on('click', '#calculate-button-add', function () {
        var saleInfo = fetchSaleInformation();

        // Filter only valid products
        saleInfo.products = saleInfo.products.filter(function (product) {
            return product.quantity > 0 && product.weight > 0 && product.pricePerItem > 0;
        });

        // Step 1: Calculate items_total
        var itemsTotal = 0;
        var totalWeight = 0;

        saleInfo.products.forEach(function (product) {
            itemsTotal += parseFloat(product.totalPrice || 0);
            totalWeight += parseFloat(product.weight || 0);
        });

        // Step 2: Calculate discount
        const discountType = saleInfo.discountDetails.discountType || '';
        const discountValue = parseFloat(saleInfo.discountDetails.discountValue || 0);

        let totalDiscount = 0;

        if (discountType === 'Fixed') {
            totalDiscount = discountValue;
        } else if (discountType === 'Percentage') {
            totalDiscount = (itemsTotal * discountValue) / 100;
        }

        const discountedTotal = itemsTotal - totalDiscount;

        // Step 3: Labour/Making Charge
        const chargeType = saleInfo.chargeDetails.labourMakingChargeType || '';
        const chargeValue = parseFloat(saleInfo.chargeDetails.labourMakingChargeValue || 0);

        let totalLabourCharge = 0;

        if (chargeType === 'Fixed') {
            totalLabourCharge = chargeValue;
        } else if (chargeType === 'Per Gram') {
            totalLabourCharge = chargeValue * totalWeight;
        }

        // Step 4: Final subtotal before GST
        const finalSubtotal = discountedTotal + totalLabourCharge;

        // Step 5: GST
        const gstPercent = parseFloat(saleInfo.taxDetails.gst || 0);
        const gstAmount = (finalSubtotal * gstPercent) / 100;

        // Step 6: Total after discount and labour and GST
        const totalAfterDiscount = finalSubtotal + gstAmount;

        // Step 7: Remaining
        const paymentAmount = parseFloat(saleInfo.paymentDetails.paymentAmount || 0);
        const remainingAmount = totalAfterDiscount - paymentAmount;

        // Step 8: Set values on the frontend
        $('#total-amount-add').val(totalAfterDiscount.toFixed(2));
        $('#remaining-amount-add').val(Math.max(remainingAmount, 0).toFixed(2));
    });

    // Event handler for adding sale

    $(document).on('click', '#add-sale-button', function() {

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var saleInfo = fetchSaleInformation();

        saleInfo.products = saleInfo.products.filter(function(product) {
            return product.quantity > 0 && product.weight > 0 && product.pricePerItem > 0;
        });

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: saleInfo,
            success: function(response) {
                swal("Success", "Sale added successfully", "success").then((value) => {
                    hideModals();
                    location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error adding sale: " + error, "error");
            }
        });
    });

    // Event handler for opening the delete purchase popup

    $(document).on('click', '.delete-sale-bill', function(event) {
        event.preventDefault();

        var row = $(this).closest('tr');
        var saleID = row.find('td:eq(0) p').text().trim();

        $('#delete-sale-bill-id').val(saleID);

        setDeleteConfirmation(saleID);
        showModal('popup-delete');
    });

    // Event handler for opening the view sale popup

    $(document).on('click', '.view-sale-bill', function (event) {
        event.preventDefault();

        const url = $(this).data('url');
        const csrftoken = getCookie('csrftoken');
        const saleID = $(this).closest('tr').find('td:eq(0) p').text().trim();

        $('#view-sale-bill-id').val(saleID);

        $.ajax({
            url,
            type: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            data: { id: saleID },
            success: function (response) {
                const saleData = response.sale;
                const taxData = response.tax_details;
                const previousBalance = parseFloat(response.previous_balance || 0);

                const saleInfo = saleData[0];

                let paymentAmount = parseFloat(saleInfo?.billno__payment_amount || 0);
                const remainingAmount = parseFloat(saleInfo?.billno__remaining_amount || 0);
                const paymentMethod = saleInfo?.billno__payment_method || '';
                const stockNote = saleInfo?.stock_note || '';
                const gst_amount = parseFloat(taxData?.gst_amount || 0);
                const totalDiscount = parseFloat(taxData?.total_discount || 0);
                const totalAfterDiscount = parseFloat(taxData?.total_after_discount || 0);
                const total = parseFloat(taxData?.total || 0);
                const total_labour_making_charge = parseFloat(taxData?.total_labour_making_charge || 0);
                const totalWeight = parseFloat(taxData?.total_weight || 0);
                let totalBalance = total + previousBalance;
                let grandTotalBalance = (totalBalance + total_labour_making_charge) - totalDiscount;
                let remainingBalance = grandTotalBalance - paymentAmount;

                $('#invoice-no').text('INVOICE NO: ' + saleInfo.billno__billno);
                $('#bill-date').text('DATE: ' + formatDate(saleInfo.billno__time));
                $('#customer-name-view').text('Name: ' + saleInfo.billno__customer__name);
                $('#customer-phone-view').text('Phone: ' + saleInfo.billno__customer__phone);
                $('#customer-gstin-view').text('GSTIN: ' + saleInfo.billno__customer__gstin);
                $('#customer-address-view').text('Address: ' + saleInfo.billno__customer__address);

                let productItemsHtml = saleData.map((item, index) => `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${item.stock__name} ${stockNote}</td>
                        <td>${item.quantity}</td>
                        <td>${item.weight}</td>
                        <td>${item.perprice}</td>
                        <td>${item.totalprice}</td>
                    </tr>
                `).join('');

                $('#product-items-view').html(productItemsHtml);
                $('#payment-method-view').text(paymentMethod);

                $('#gst-input').val(gst_amount.toFixed(2));
                $('#view-labour-making-charges').val(total_labour_making_charge.toFixed(2));
                $('#total-price-view').val(totalBalance.toFixed(2));
                $('#total-discount-view').val(totalDiscount.toFixed(2));
                $('#grand-total-view').val(grandTotalBalance.toFixed(2));
                $('#paid-amount-view').val(paymentAmount.toFixed(2));
                $('#previous-balance-view').val(previousBalance.toFixed(2));
                $('#remaining-amount-view').val(remainingBalance.toFixed(2));

                updateBillStatus(grandTotalBalance, paymentAmount);

                $('#paid-amount-view').off('input').on('input', function () {
                    paymentAmount = parseFloat($(this).val()) || 0;

                    const grandTotal = parseFloat($('#grand-total-view').val()) || 0;
                    const remainingBalance = grandTotal - paymentAmount;

                    $('#remaining-amount-view').val(remainingBalance.toFixed(2));
                    updateBillStatus(grandTotal, paymentAmount);
                });

                showModal('popup-view');
            },
            error: function (xhr, status, error) {
                swal("Error", "Error fetching sale details: " + error, "error");
            }
        });
    });

    // Event handler for delete sale button

    $(document).on('click', '#delete-sale-bill-button', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var saleID = $('#delete-sale-bill-id').val();

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: {
                'id': saleID
            },
            success: function(response) {
                swal("Success", "Sale deleted successfully", "success").then((value) => {
                    hideModals();
                    location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error deleting sale: " + error, "error");
            }
        });
    });

    $('#print-button').click(function(event) {
        event.preventDefault();
        window.print();
    });

    $('#save-draft-button-view').click(function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var saleID = $('#view-sale-bill-id').val();

        var payment_amount = $('#paid-amount-view').val();
        var remaining_amount = $('#remaining-amount-view').val();

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: {
                'id': saleID,
                'payment_amount': payment_amount,
                'remaining_amount': remaining_amount,
            },
            success: function(response) {
                swal("Success", "Sale draft saved successfully", "success").then((value) => {
                    hideModals();
                    location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error saving sale draft: " + error, "error");
            }
        });
    });

    // Fetch customer suggestions only for 2+ characters

    $(document).on('input', '#customer-name', function () {
        const query = $(this).val();
        if (query.length < 2) return;

        const url = '/transactions/customer-suggestions/';
        const csrftoken = getCookie('csrftoken');

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: {
                'query': query
            },
            success: function (response) {
                const suggestions = response.map(customer =>
                    `<option data-id="${customer.id}" value="${customer.name}"></option>`
                ).join('');
                $('#customer-suggestions').html(suggestions);
            },
            error: function () {
                swal("Error", "Error fetching customer suggestions.", "error");
            }
        });
    });

    // Auto-fill customer details

    $(document).on('change', '#customer-name', function () {
        const selectedName = $(this).val();

        const selectedOption = $(`#customer-suggestions option[value="${selectedName}"]`);
        const customerId = selectedOption.data('id');

        if (!customerId) return;

        const url = `/transactions/customer-details/`;
        const csrftoken = getCookie('csrftoken');

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: {
                id: customerId
            },
            success: function (response) {
                $('#customer-phone').val(response.phone);
                $('#customer-email').val(response.email);
                $('#customer-address').val(response.address);
                $('#customer-gstin').val(response.gstin);
            },
            error: function () {
                swal("Error", "Error fetching customer details.", "error");
            }
        });
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
            url: '/transactions/search-sale/',
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

                if (response.sales.trim() === '') {
                    $('tbody').empty();
                    swal("No Content", "No content found", "info");
                    $('#pagination-search').hide();
                    $('#pagination-main').hide();
                } else {
                    $('tbody').html(response.sales);
                    $('#pagination-main').hide();
                    $('#pagination-search').show();
                }

            },
            error: function(xhr, status, error) {
                swal("Error", "Error searching sale: " + error, "error");
            }
        });
    });

    // Event handler to delete sale bills

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
            text: "This will permanently delete the matching sale bills.",
            icon: "warning",
            buttons: true,
            dangerMode: true,
        }).then((willDelete) => {
            if (willDelete) {
                $.ajax({
                    url: '/transactions/delete-sale/',
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
                        swal("Error", "Error deleting sale bills: " + error, "error");
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
        var customerID = $(this).data('customer-id');

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
