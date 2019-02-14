// 'countdown_timer' function called when capture button is clicked
$('#capture').click(countdown_timer);

// 5 second countdown timer; countdown element is dynamically updated
function countdown_timer()
{   
    // creates a countdown element in mainsection
    $('#mainSection').html('<div id="countdown">5</div>');

    var timeLeft = 4;
    var intervalTime = setInterval(function() {
        document.getElementById('countdown').innerHTML = timeLeft;
        timeLeft -= 1;

        // 'GO!' dispalyed and 'capture' function called when countdown timer reaches 0
        if(timeLeft <0) {
            clearInterval(intervalTime);
            document.getElementById('countdown').innerHTML = "GO!";

            // 'capture' function is called 0.5 secs after 'GO!' is displayed
            setTimeout(capture, 500);
            // 'loader' function called 0.5 secs after 'GO!' is displayed
            setTimeout(loader, 500);
            // 'poll_camera_state' function called when countdown timer reaches 0
            poll_camera_state();
        }
    }, 1000);
}

// post request to trigger the capture action
function capture()
{
    $.post('/capture');
}    

// loading animation displayed
function loader()
{
    if ($('#countdown').html() == "GO!") {
        $('#mainSection').html('<div class="loader"></div>'+
                               '<div id="loader-message"></div>');
    }
}

// polls camera state info and dynamically updates the loader message element
function poll_camera_state()
{
	$.getJSON("/camera_state", function(response) {	        
        $('#loader-message').html(response.capture_status);
    });

    // function called every 0.250 secs
    setTimeout(poll_camera_state, 250);
}
