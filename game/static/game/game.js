$(document).ready(function(){
    console.log("Starting Poll");
    setTimeout(doPoll, 3000);
});

$("#start-game").on('click', function(){
    $("#start-game").attr('disabled', true);

    if(!confirm("Are you sure you want to restart the game?"))
    {
        return;
    }

    $.ajax({
        headers: {"X-CSRFToken": getCookie('csrftoken')},
        type: 'POST',
        url: '/game/start/' + $("#game-id").html() + '/',
        data: {},
        success: function(resp) {
             $("#player-self").html(resp['self']);

            for(var i = 0; i < resp['players'].length; i++)
            {
                player = resp['players'][i];
                $("#player-"+player[0]).html(player[1]);
            }

            $("#start-game").attr('disabled', false);
        }
    });
});

$(document).on('click', '.card-in-hand', function(){
    card = this.id.substring(2);

    console.log("Card " + card + " clicked");

    $.ajax({
        headers: {"X-CSRFToken": getCookie('csrftoken')},
        type: 'POST',
        url: '/game/update/' + $("#game-id").html() + '/select/',
        data: {"card": card},
        success: function(resp) {
             $("#player-self").html(resp['self']);
        }
    });
});

$(document).on('click', '.selected-card', function(){
    card = this.id.substring(2);

    console.log("Card " + card + " clicked");

    $.ajax({
        headers: {"X-CSRFToken": getCookie('csrftoken')},
        type: 'POST',
        url: '/game/update/' + $("#game-id").html() + '/deselect/',
        data: {"card": card},
        success: function(resp) {
             $("#player-self").html(resp['self']);
        }
    });
});

$(document).on('change', 'input[name=card-face]', function () {
     face = $('input[name=card-face]:checked', '#card-face-form').val();

     $.ajax({
        headers: {"X-CSRFToken": getCookie('csrftoken')},
        type: 'POST',
        url: '/game/update/' + $("#game-id").html() + '/face/',
        data: {"face": face},
        success: function(resp) {
             $("#player-self").html(resp['self']);
        }
    });
});

$(document).on('click', '#submit-action', function(){
     $('#submit-action').attr('disabled', true);

     face = $('input[name=card-face]:checked', '#card-face-form').val();

     $.ajax({
        headers: {"X-CSRFToken": getCookie('csrftoken')},
        type: 'POST',
        url: '/game/update/' + $("#game-id").html() + '/submit/',
        data: {"face": face},
        success: function(resp) {
             $("#player-self").html(resp['self']);

             $('#submit-action').attr('disabled', false);
        }
    });
});

$(document).on('click', '#submit-ready', function(){
     $('#submit-ready').attr('disabled', true);

     $.ajax({
        headers: {"X-CSRFToken": getCookie('csrftoken')},
        type: 'POST',
        url: '/game/update/' + $("#game-id").html() + '/ready/',
        data: {},
        success: function(resp) {
             $("#player-self").html(resp['self']);
             $('#submit-ready').attr('disabled', false);
        }
    });
});



function doPoll(){
    $.ajax({
        headers: {"X-CSRFToken": getCookie('csrftoken')},
        type: 'POST',
        url: '/game/poll/' + $("#game-id").html() + "/",
        data: {},
        success: function(resp) {
            console.log("Polling for new updates...")

             $("#player-self").html(resp['self']);

            for(var i = 0; i < resp['players'].length; i++)
            {
                player = resp['players'][i];
                $("#player-"+player[0]).html(player[1]);
            }

            setTimeout(doPoll, 5000);
        },
        error: function(){
            setTimeout(doPoll, 5000);
        }
    });
}

