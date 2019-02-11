// onClick capture button 
$('#capture').click(countdown_timer);
    loader();

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
        if(timeLeft <0){
            clearInterval(intervalTime);
            document.getElementById('countdown').innerHTML = "GO!";

            // 'capture' function is called 0.5 secs after 'GO!' is displayed
            setTimeout(capture, 500);
        }
    }, 1000);
}

// post request to trigger the capture action
function capture()
{
    $.post('/capture');
}    