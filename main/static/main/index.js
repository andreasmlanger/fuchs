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
        $(this).parents(".dropdown").find('.btn').html($(this).text());
    });
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
