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
            console.log(resp);
        }
    });
})