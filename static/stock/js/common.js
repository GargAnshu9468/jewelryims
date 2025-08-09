// Function to open a modal by ID

function showModal(modalID) {
    $('#' + modalID).show();
}

// Function to close all modals

function hideModals() {
    $('.modal').hide();
}

function getCookie(name) {
    var cookieValue = null;

    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');

        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}

// Function to format date

function formatDate(dateString) {
    const months = ['Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'Jun.', 'Jul.', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.'];
    const date = new Date(dateString);

    const monthIndex = date.getMonth();
    const day = date.getDate();
    const year = date.getFullYear();

    return months[monthIndex] + ' ' + day + ', ' + year;
}

// Event handler for the close button in all popups

$(document).on('click', '.close', function(event) {
    event.preventDefault();
    hideModals();
});

// Event handler for the cancel buttons in all popups

$(document).on('click', '.btn-danger[data-dismiss="modal"]', function(event) {
    event.preventDefault();
    hideModals();
});
