$(document).ready(function(){
    console.log("Ready!");
});

$("#start-game").on('click', function(){
    console.log("Start Game clicked");

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

$(document).on('click', '#submit-action', function(){
     face = $('input[name=card-face]:checked', '#card-face-form').val();

     $.ajax({
        headers: {"X-CSRFToken": getCookie('csrftoken')},
        type: 'POST',
        url: '/game/update/' + $("#game-id").html() + '/submit/',
        data: {"face": face},
        success: function(resp) {
             $("#player-self").html(resp['self']);
        }
    });
});