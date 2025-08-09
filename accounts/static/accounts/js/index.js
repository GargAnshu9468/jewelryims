// Function to open a modal by ID

function showModal(modalID) {
    $('#' + modalID).show();
}

// Function to close all modals

function hideModals() {
    $('.modal').hide();
}

// Event handler for the close button

$(document).on('click', '.close', function(event) {
    event.preventDefault();
    hideModals();
});

// Event handler for the ok buttons

$(document).on('click', '.btn-danger[data-dismiss="modal"]', function(event) {
    event.preventDefault();
    hideModals();
});

// Function to check if the email verification popup should be shown

function showEmailVerificationPopup() {
    const params = new URLSearchParams(window.location.search);
    const message = params.get('message');

    if (message === "Email Verification Pending") {
        showModal('email-verification-popup');
    }
}

// Call the function when the document is ready

$(document).ready(function() {
    showEmailVerificationPopup();
});
