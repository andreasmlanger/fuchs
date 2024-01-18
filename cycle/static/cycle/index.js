function removeElement(x) {
  x.remove();
  hideAllTooltips();
  enableTooltips();
}

function addAttributeToElementsOfClass(x, attribute) {
   var elements = document.querySelectorAll(x)
   for (var i = 0; i < elements.length; i++) {
     elements[i].classList.add(attribute);
   }
}

function removeAttributeFromElementsOfClass(x, attribute) {
  var elements = document.querySelectorAll(x)
  for (var i = 0; i < elements.length; i++) {
    elements[i].classList.remove(attribute);
  }
}

function highlightCategory(x) {
  var elements = document.querySelectorAll('.category');
  for (var i = 0; i < elements.length; i++) {
    elements[i].style.color = 'gray';
  }
  x.style.color = 'black';
}

function openModal() {
  document.getElementById("modal").style.display = "block";
}

function closeModal() {
  $('#modal-body').html('');
  document.getElementById("modal").style.display = "none";
  document.body.style.overflow = 'auto';
}

function getPages(nrOfRoutes, routesPerPage) {
  return Math.floor((nrOfRoutes - 1) / routesPerPage) + 1;
}

function getPrompt(task) {
  if (task == 'mark_as_done') {
    return 'Do you want to mark this tour as done?'
  } else if (task == 'mark_as_undone') {
    return 'Do you want to mark this tour as undone?'
  } else if (task == 'delete') {
    return 'Do you really want to delete this tour?'
  }
}