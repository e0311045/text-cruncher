$(document).ready(function() {
    $("#btnFetch").click(function() {
        var user_input = $("#input").val();
        var commas_finder = user_input.match(,);
        var commas_count = commas_finder.length;
        if(commas_count>4){
            #btnFetch.button('reset');
            swal({
              title: "Apologies...",
              text: "There are Too Many Queries to be Handled",
              icon: "Awww... Okay",
            });
        }
        else if(user_input=='') {
            #btnFetch.button('reset');
            swal({
              title: "Reminder",
              text: "Please Input Something D:",
              icon: "Oops... Alright!",
            });
        }
        else{
            // disable button
            $(this).prop("disabled", true);
            // add spinner to button
            $(this).html(
            '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...'
            );
            document.getElementById("getUserInput").submit(); //Submits form
            swal({
              title: "Please be Patient",
              text: "This takes about a minute or so; you will be redirected to a download page upon completion",
              icon: "I Understand!",
            });
        }
    });
});

$(document).ready(function() {
    $("#btnFetch").click(function() {
        // disable button
        $(this).prop("disabled", true);
        // add spinner to button
        $(this).html(
        '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...'
        );
        document.getElementById("getUserInput").submit(); //Submits form
    });
});


$(document).ready(function() {
    $("#btnFetch").click(function() {
        // disable button
        $(this).prop("disabled", true);
        // add spinner to button
        $(this).html(
        '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...'
        );
    });
    var user_input = $("#input").val();
    var commas_finder = user_input.match(,);
    var commas_count = commas_finder.length;
    if(commas_count>4){
        #btnFetch.button('reset');
        swal({
          title: "Apologies...",
          text: "There are Too Many Queries to be Handled",
          icon: "Awww... Okay",
        });
    }
});


$("#btnFetch").click(function() {
    var user_input = $("#input").val();
    var commas_finder = user_input.match(,);
    var commas_count = commas_finder.length;
    if(commas_count>4){
        swal({
          title: "Apologies...",
          text: "There are Too Many Queries to be Handled",
          icon: "Awww... Okay",
        });
    }
    else if(user_input==''){
        swal({
              title: "Reminder",
              text: "Please Input Something D:",
              icon: "Oops... Alright!",
            });
    }
    else{
        document.getElementById("getUserInput").submit(); //Submits form
    }
});
