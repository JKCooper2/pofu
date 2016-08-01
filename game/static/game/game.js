$(document).ready(function(){
    console.log("Ready!");
})

$("#start-game").on('click', function(){
    console.log("Start Game clicked");

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
})