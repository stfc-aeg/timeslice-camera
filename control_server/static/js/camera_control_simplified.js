poll_camera_state();

// 'renderIndexPage' function called when page is loaded
$(document).ready(renderIndexPage);

function renderIndexPage()
{
    // sets class height to 100%
    $('#mainSection').addClass('h-100');
    // displays systems state element and 'Capture' button
    $('#mainSection').html('<div class="col-md-12 h-50">'+
                           '<h4><span id="system-state" class="badge"></span></h4></div>'+
                           '<div class="col-md-12">'+
                           '<a href="#capture" class="btn btn-primary" id="captureButton">Capture</a></div>');

    // 'renderCountdownPage' function called when 'Capture' button is clicked
    $('#captureButton').click(renderCountdownPage);
}

function renderCountdownPage()
{   
    // removes class height to allow countdown element to be centered
    $('#mainSection').removeClass('h-100')

    // displays the countdown element
    $('#mainSection').html('<div id="countdown">5</div>');

    // 5 second countdown timer; countdown element is dynamically updated
    var timeLeft = 4;
    var intervalTime = setInterval(function() {
        document.getElementById('countdown').innerHTML = timeLeft;
        timeLeft -= 1;

        // 'GO!' dispayed when countdown timer reaches 0
        if(timeLeft <0) {
            clearInterval(intervalTime);
            document.getElementById('countdown').innerHTML = "GO!";

            // 'capture' function called 0.5 secs after 'GO!' is displayed
            setTimeout(capture, 500);
            // 'renderLoadingPage' function called 0.5 secs after 'GO!' is displayed
            setTimeout(renderLoadingPage, 500);
        }
    }, 1000);

    // post request to trigger the capture action
    function capture()
    {
        $.post('/capture');
    }   
} 

function renderLoadingPage()
{
    // displays the loading element once countdown element displays 'GO!'
    if ($('#countdown').html() == "GO!") {
        $('#mainSection').html('<div class="loader"></div>'+
                               '<div id="loader-message"></div>');
    }
}

// polls camera state info
function poll_camera_state()
{
	$.getJSON("/camera_state", function(response) {	     
        
        // dynamically updates the system state element
        if(response.system_state == 0) {
            $('#system-state').removeClass('badge-success').addClass('badge-danger');
            $('#system-state').html('Not ready');
            $('#captureButton').addClass('disabled');
        } else {
            $('#system-state').removeClass('badge-danger').addClass('badge-success');
            $('#system-state').html('Ready');
            $('#captureButton').removeClass('disabled');
        }

        // dynamically updates the loader message element
        $('#loader-message').html(response.capture_status);

        // 'renderRetakeSavePage' function called if rendering completed
        if(response.render_status == 3) {
            renderRetakeSavePage();
        }
    });

    // function called every 0.250 secs
    setTimeout(poll_camera_state, 250);
}

// displays 'Retake' & 'Save' buttons
function renderRetakeSavePage()
{
    $('#mainSection').html('<a href="#capture" class="btn btn-primary" id="retakeButton">Retake</a>'+
                           '<a href="#" class="btn btn-primary" id="saveButton">Save</a>');

    // 'renderIndexPage' function called when 'Retake' button is clicked
    $('#retakeButton').click(renderIndexPage);
}