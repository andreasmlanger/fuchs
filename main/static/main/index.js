function enableTooltips() {
    $('[data-toggle="tooltip"]').tooltip({
        trigger : 'hover'
    })
}

function hideAllTooltips() {
    $(".tooltip").tooltip("hide");
}

function enableDropdowns() {
    $(".dropdown-menu span").click(function(){
        if (!$(this).parents(".dropdown").find('.btn').is("#accountButton")) {  // don't do this for the account button!
            $(this).parents(".dropdown").find('.btn').html($(this).text());
        }
    });
}

function pressEnterToSave(inputElement) {
    if (event.key === 'Enter') {
        var modal = $(inputElement).closest('.modal');
        var okButton = modal.find('.btn-primary');  // OK button within same modal
        okButton.click();
    }
}

function showMessage(message, alert) {
    $("#message").html('<div class="alert alert-' + alert + '">' + message + '</div>')
    window.setTimeout(function() {
        $(".alert").fadeTo(500, 0).slideUp(500, function(){
            $(this).remove();
        });
    }, 2000);
}

const shuffleArray = array => {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    const temp = array[i];
    array[i] = array[j];
    array[j] = temp;
  }
}

document.addEventListener('DOMContentLoaded', function(event) {
    enableTooltips();
    enableDropdowns();
});
