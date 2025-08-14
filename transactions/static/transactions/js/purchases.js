// Function to fetch suppliers details

function fetchSuppliersDetails(callback) {

    var url = '/transactions/get-suppliers/';
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
            swal("Error", "Error fetching suppliers details: " + error, "error");
            callback([]);
        }
    });
}

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

// Define a callback function to handle the fetched suppliers data

function handleSuppliersData(response) {

    var suppliers = response.suppliers;
    var select = $('#supplier');

    select.empty().append($('<option>', {
        value: '',
        text: '--- Select Supplier ---',
        disabled: true,
        selected: true
    }));

    $.each(suppliers, function(index, supplier) {
        select.append($('<option>', {
            value: supplier.id,
            text: supplier.name
        }));
    });

    select.change(function() {
        var selectedSupplierId = $(this).val();

        var selectedSupplier = suppliers.find(function(supplier) {
            return supplier.id == selectedSupplierId;
        });

        $('#supplier-phone').val(selectedSupplier.phone);
        $('#supplier-gstin').val(selectedSupplier.gstin);
        $('#supplier-address').val(selectedSupplier.address);
        $('#supplier-email').val(selectedSupplier.email);
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

// Function to fetch purchase information based on the active modal

function fetchPurchaseInformation() {

    var activeModal = $('.modal:visible');

    var purchaseInfo = {
        'time': $('#add-purchase-date').val(),
    };

    if (activeModal.attr('id') === 'popup-add') {

        // Supplier Details Section

        purchaseInfo.supplier = {};

        purchaseInfo.supplier.id = $('#supplier').val();
        purchaseInfo.supplier.phone = $('#supplier-phone').val();
        purchaseInfo.supplier.gstin = $('#supplier-gstin').val();
        purchaseInfo.supplier.email = $('#supplier-email').val();
        purchaseInfo.supplier.address = $('#supplier-address').val();

        // Product Details Section

        purchaseInfo.products = [];

        $('#product-details-section .form-group.row').each(function() {
            var product = {
                id: $(this).find('.stock').val(),
                pricePerItem: parseFloat($(this).find('.price-per-item').val()),
                quantity: parseFloat($(this).find('.quantity').val()),
                totalPrice: parseFloat($(this).find('.price').val()),
                weight: parseFloat($(this).find('.weight').val()),
                stockNote: $(this).find('.stock-note').val()
            };

            purchaseInfo.products.push(product);
        });

        // Payment Details Section

        purchaseInfo.paymentDetails = {};

        purchaseInfo.paymentDetails.paymentMethod = $('#payment-method').val();
        purchaseInfo.paymentDetails.paymentAmount = $('#payment-amount').val();

        // Discount Details Section

        purchaseInfo.discountDetails = {};

        purchaseInfo.discountDetails.discountType = $('#discount-type').val();
        purchaseInfo.discountDetails.discountValue = $('#discount-value').val();
        purchaseInfo.discountDetails.discountNote = $('#discount-note').val();

        // Tax Details Section

        purchaseInfo.taxDetails = {};
        purchaseInfo.taxDetails.gst = $('#gst').val();

        // Labour/Making Charges Details Section

        purchaseInfo.chargeDetails = {};

        purchaseInfo.chargeDetails.labourMakingChargeType = $('#labour-making-charge-type').val();
        purchaseInfo.chargeDetails.labourMakingChargeValue = $('#labour-making-charge-value').val();
        purchaseInfo.chargeDetails.labourMakingChargeNote = $('#labour-making-charge-note').val();
    }

    return purchaseInfo;
}

// Function to set the delete confirmation message

function setDeleteConfirmation(purchaseID) {
    var confirmationMessage = `Are you sure you want to delete the Purchase Bill No: ${purchaseID}?`;
    $('#delete-purchase-bill-confirmation').text(confirmationMessage);
}

// Function to update purchase details

function updatePurchaseDetails(purchaseInfo) {

    var url = '/transactions/update-purchase/';
    var csrftoken = getCookie('csrftoken');

    $.ajax({
        url: url,
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: purchaseInfo,
        success: function(response) {
            swal("Error", "Purchase details updated successfully", "error");
        },
        error: function(xhr, status, error) {
            swal("Error", "Error updating purchase details: " + error, "error");
        }
    });
}

// Function to update bill status

function updateBillStatus(remaining, total) {
    let status = 'Unpaid';

    if (remaining <= 0) {
        status = 'Paid';
    } else if (remaining > 0 && remaining < total) {
        status = 'Partially Paid';
    } else {
        status = 'Unpaid'
    }

    $('#bill-status-view').text(status);
}

$(document).ready(function() {

    // Event handler for opening the add purchase popup

    $(document).on('click', '#add-purchase', function(event) {
        event.preventDefault();

        fetchSuppliersDetails(handleSuppliersData);
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
        var purchaseInfo = fetchPurchaseInformation();

        // Filter only valid products
        purchaseInfo.products = purchaseInfo.products.filter(function (product) {
            return product.quantity > 0 && product.weight > 0 && product.pricePerItem > 0;
        });

        // Step 1: Calculate items_total
        var itemsTotal = 0;
        var totalWeight = 0;

        purchaseInfo.products.forEach(function (product) {
            itemsTotal += parseFloat(product.totalPrice || 0);
            totalWeight += parseFloat(product.weight || 0);
        });

        // Step 2: Calculate discount
        const discountType = purchaseInfo.discountDetails.discountType || '';
        const discountValue = parseFloat(purchaseInfo.discountDetails.discountValue || 0);

        let totalDiscount = 0;

        if (discountType === 'Fixed') {
            totalDiscount = discountValue;
        } else if (discountType === 'Percentage') {
            totalDiscount = (itemsTotal * discountValue) / 100;
        }

        const discountedTotal = itemsTotal - totalDiscount;

        // Step 3: Labour/Making Charge
        const chargeType = purchaseInfo.chargeDetails.labourMakingChargeType || '';
        const chargeValue = parseFloat(purchaseInfo.chargeDetails.labourMakingChargeValue || 0);

        let totalLabourCharge = 0;

        if (chargeType === 'Fixed') {
            totalLabourCharge = chargeValue;
        } else if (chargeType === 'Per Gram') {
            totalLabourCharge = chargeValue * totalWeight;
        }

        // Step 4: Final subtotal before GST
        const finalSubtotal = discountedTotal + totalLabourCharge;

        // Step 5: GST
        const gstPercent = parseFloat(purchaseInfo.taxDetails.gst || 0);
        const gstAmount = (finalSubtotal * gstPercent) / 100;

        // Step 6: Total after discount and labour and GST
        const totalAfterDiscount = finalSubtotal + gstAmount;

        // Step 7: Remaining
        const paymentAmount = parseFloat(purchaseInfo.paymentDetails.paymentAmount || 0);
        const remainingAmount = totalAfterDiscount - paymentAmount;

        // Step 8: Set values on the frontend
        $('#total-amount-add').val(totalAfterDiscount.toFixed(2));
        $('#remaining-amount-add').val(Math.max(remainingAmount, 0).toFixed(2));
    });

    // Event handler for adding purchase

    $(document).on('click', '#add-purchase-button', function() {

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var purchaseInfo = fetchPurchaseInformation();

        purchaseInfo.products = purchaseInfo.products.filter(function(product) {
            return product.quantity > 0 && product.weight > 0 && product.pricePerItem > 0;
        });

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: purchaseInfo,
            success: function(response) {
                swal("Success", "Purchase added successfully", "success").then((value) => {
                    hideModals();
                    location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error adding purchase: " + error, "error");
            }
        });
    });

    // Event handler for opening the delete purchase popup

    $(document).on('click', '.delete-purchase-bill', function(event) {
        event.preventDefault();

        var row = $(this).closest('tr');
        var purchaseID = row.find('td:eq(0) p').text().trim();

        $('#delete-purchase-bill-id').val(purchaseID);

        setDeleteConfirmation(purchaseID);
        showModal('popup-delete');
    });

    // Event handler for opening the view purchase popup

    $(document).on('click', '.view-purchase-bill', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var row = $(this).closest('tr');
        var csrftoken = getCookie('csrftoken');
        var purchaseID = row.find('td:eq(0) p').text().trim();

        $('#view-purchase-bill-id').val(purchaseID);

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: {
                'id': purchaseID
            },
            success: function(response) {
                var purchaseData = response.purchase;
                var taxData = response.tax_details;

                const purchaseInfo = purchaseData[0];

                const paymentAmount = parseFloat(purchaseInfo?.billno__payment_amount || 0);
                const remainingAmount = parseFloat(purchaseInfo?.billno__remaining_amount || 0);
                const paymentMethod = purchaseInfo?.billno__payment_method || '';
                const stockNote = purchaseInfo?.stock_note || '';
                const gst_amount = parseFloat(taxData?.gst_amount || 0);
                const totalDiscount = parseFloat(taxData?.total_discount || 0);
                const totalAfterDiscount = parseFloat(taxData?.total_after_discount || 0);
                const total = parseFloat(taxData?.total || 0);
                const total_labour_making_charge = parseFloat(taxData?.total_labour_making_charge || 0);
                const total_weight = parseFloat(taxData?.total_weight || 0);

                $('#invoice-no').text('INVOICE NO: ' + purchaseInfo.billno__billno);
                $('#bill-date').text('DATE: ' + formatDate(purchaseInfo.billno__time));
                $('#supplier-name-view').text('Name: ' + purchaseInfo.billno__supplier__name);
                $('#supplier-phone-view').text('Phone: ' + purchaseInfo.billno__supplier__phone);
                $('#supplier-gstin-view').text('GSTIN: ' + purchaseInfo.billno__supplier__gstin);
                $('#supplier-address-view').text('Address: ' + purchaseInfo.billno__supplier__address);

                let productItemsHtml = purchaseData.map((item, index) => `
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
                $('#total-price-view').val(total.toFixed(2));
                $('#total-discount-view').val(totalDiscount.toFixed(2));
                $('#grand-total-view').val(totalAfterDiscount.toFixed(2));
                $('#paid-amount-view').val(paymentAmount.toFixed(2));
                $('#remaining-amount-view').val(remainingAmount.toFixed(2));

                updateBillStatus(remainingAmount, totalAfterDiscount);

                $('#total-discount-view').off('input').on('input', function () {
                    const discount = parseFloat($(this).val()) || 0;
                    const totalPrice = parseFloat($('#total-price-view').val()) || 0;
                    const paid = parseFloat($('#paid-amount-view').val()) || 0;

                    const newGrandTotal = totalPrice - discount;
                    const newRemaining = newGrandTotal - paid;

                    $('#grand-total-view').val(newGrandTotal.toFixed(2));
                    $('#remaining-amount-view').val(newRemaining.toFixed(2));

                    updateBillStatus(newRemaining, newGrandTotal);
                });

                $('#paid-amount-view').off('input').on('input', function () {
                    const paid = parseFloat($(this).val()) || 0;
                    const grandTotal = parseFloat($('#grand-total-view').val()) || 0;

                    const newRemaining = grandTotal - paid;
                    $('#remaining-amount-view').val(newRemaining.toFixed(2));

                    updateBillStatus(newRemaining, grandTotal);
                });

                showModal('popup-view');
            },
            error: function(xhr, status, error) {
                swal("Error", "Error fetching purchase details: " + error, "error");
            }
        });
    });

    // Event handler for delete purchase button

    $(document).on('click', '#delete-purchase-bill-button', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var purchaseID = $('#delete-purchase-bill-id').val();

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: {
                'id': purchaseID
            },
            success: function(response) {
                swal("Success", "Purchase deleted successfully", "success").then((value) => {
                    hideModals();
                    location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error deleting purchase: " + error, "error");
            }
        });
    });

    // Event handler for supplier details popup

    $(document).on('click', '.supplier-name', function(event) {
        event.preventDefault();

        var url = $(this).data('url');
        var csrftoken = getCookie('csrftoken');
        var supplierID = $(this).data('supplier-id');

        fetchSupplierDetails(url, csrftoken, supplierID, function(response) {
            var popupContent = '<div class="supplier-details">';

            popupContent += '<p class="supplier-detail"><span class="supplier-label">ID:</span> ' + response.id + '</p>';
            popupContent += '<p class="supplier-detail"><span class="supplier-label">Name:</span> ' + response.name + '</p>';
            popupContent += '<p class="supplier-detail"><span class="supplier-label">Phone:</span> ' + response.phone + '</p>';
            popupContent += '<p class="supplier-detail"><span class="supplier-label">Address:</span> ' + response.address + '</p>';
            popupContent += '<p class="supplier-detail"><span class="supplier-label">Email:</span> ' + response.email + '</p>';
            popupContent += '<p class="supplier-detail"><span class="supplier-label">GSTIN No:</span> ' + response.gstin + '</p>';
            popupContent += '<p class="supplier-detail"><span class="supplier-label">Date:</span> ' + formatDate(response.date) + '</p>';

            popupContent += '</div>';

            $('#supplier-details-content').html(popupContent);
            showModal('popup-show');
        }, function(xhr, status, error) {
            swal("Error", "Error fetching supplier details: " + error, "error");
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
        var purchaseID = $('#view-purchase-bill-id').val();

        var payment_amount = $('#paid-amount-view').val();
        var remaining_amount = $('#remaining-amount-view').val();

        $.ajax({
            url: url,
            type: 'POST',
            headers: {
                'X-CSRFToken': csrftoken
            },
            data: {
                'id': purchaseID,
                'payment_amount': payment_amount,
                'remaining_amount': remaining_amount,
            },
            success: function(response) {
                swal("Success", "Purchase draft saved successfully", "success").then((value) => {
                    hideModals();
                    location.reload();
                });
            },
            error: function(xhr, status, error) {
                swal("Error", "Error saving purchase draft: " + error, "error");
            }
        });
    });

    // Event handler to fetch and display search results

    $('#searchButton').click(function(event) {
        event.preventDefault();

        var csrftoken = getCookie('csrftoken');
        var searchText = $('#searchInput').val().trim();

        if (searchText) {

            $.ajax({
                url: '/transactions/search-purchase/',
                type: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken
                },
                data: {
                    'search_text': searchText
                },
                success: function(response) {

                    if (response.purchases.trim() === '') {
                        swal("No Content", "No content found", "info");
                    } else {
                        $('tbody').html(response.purchases);
                        $('#pagination-main').hide();
                        $('#pagination-search').show();
                    }

                },
                error: function(xhr, status, error) {
                    swal("Error", "Error searching purchase: " + error, "error");
                }
            });

        } else {
            swal("Error", "Please enter a search term", "error");
        }
    });

});
