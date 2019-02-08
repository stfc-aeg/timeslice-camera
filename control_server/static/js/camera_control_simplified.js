// onClick capture button 
$('#capture').click(function() {
    // displays countdown element
    $('#mainSection').html('<div id="countdown">5</div>');

    countdown_timer();

    // $.post('/capture');
});


// 5 second countdown timer; countdown element is dynamically updated
function countdown_timer()
{
    var timeleft = 4;
    var intervalTime = setInterval(function() {
        document.getElementById('countdown').innerHTML = timeleft;
        timeleft -= 1;

        // "GO!" dispalyed when countdown timer reaches 0
        if(timeleft <0){
            clearInterval(intervalTime);
            document.getElementById('countdown').innerHTML = "GO!";
        }
    }, 1000);
}