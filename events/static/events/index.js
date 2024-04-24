function displayNotification(x) {
    if (x == 0) {
        showMessage('No new events found!', 'warning')
    } else {
        showMessage(x + ' new event' + (x > 1 ? 's' : '') + ' found!', 'success')
    }
}
