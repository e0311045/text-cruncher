$('#emailModal').on('show.bs.modal', function (event) {
  var button = $(event.relatedTarget) // Button that triggered the modal
  var recipient = button.data('whatever') // Extract info from data-* attributes
  // If necessary, you could initiate an AJAX request here (and then do the updating in a callback).
  // Update the modal's content. We'll use jQuery here, but you could use a data binding library or other methods instead.
  var modal = $(this)
  modal.find('.modal-title').text('New message to ' + recipient)
})

$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();
});

function showAlert() {
    var address = document.getElementById('recipient-address').value;
    swal({
          title: "Email Sent!",
          text: "An email has been sent to"+address,
          icon: "success",
          button: "Yay!"
        });
}