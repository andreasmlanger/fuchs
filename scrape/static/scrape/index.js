function showMessage(message, alert) {
    $("#message").html('<div class="alert alert-' + alert + '">' + message + '</div>')
    window.setTimeout(function() {
        $(".alert").fadeTo(500, 0).slideUp(500, function(){
            $(this).remove();
        });
    }, 2000);
}

function displayNotification(x) {
    if (x == 0) {
        showMessage('No new events found!', 'warning')
    } else {
        showMessage(x + ' new event' + (x > 1 ? 's' : '') + ' found!', 'success')
    }
}
