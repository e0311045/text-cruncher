function validator()
{
    var queries = document.getElementById('input').value;
    var commas_query = queries.match(/,/g);
    var commas = 0
    if ( commas_query != null ) {
        commas = commas_query.length
    }
    if (queries == "") {
        swal({
          title: "Input is Empty!",
          text: "Please check the missing field!!",
          icon: "warning",
          button: "Alright"
        });
    }
    else if (commas > 4) {
          swal({
              title: "Input has too many queries",
              text: "Sorry but we are unable to process too many queries at once",
              icon: "info",
              button: "Aww Okay..."
            });
    }
    else {
        function load() {
            // disable button
            $("#btnFetch").prop("disabled", true);
            // add spinner to button
            $("#btnFetch").html(
            '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...'
            );
            document.getElementById("getUserInput").submit(); //Submits form
        }
        load();
        swal({
              title: "Processing Queries",
              text: "As this process involves multiple processes, it will take a few minutes. Therefore, we seek your patience and understanding",
              icon: "success",
              button: "I understand"
            });
    }
}



