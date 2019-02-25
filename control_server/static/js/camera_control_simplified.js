poll_camera_state();

// 'renderIndexPage' function called when page is loaded
$(document).ready(renderIndexPage);

function renderIndexPage()
{
    // sets class height to 100%
    $('#mainSection').addClass('h-100');
    // displays systems state element and 'Capture' button
    $('#mainSection').html('<div class="col-md-12 h-50">'+
                           '<span id="system-state" class="badge"></span></div>'+
                           '<div class="col-md-12">'+
                           '<a href="#capture" class="btn btn-primary" id="captureButton"><h4>Capture</h4></a></div>');

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
            $('#system-state').html('<h3>Not ready</h3>');
            $('#captureButton').addClass('disabled');
        } else {
            $('#system-state').removeClass('badge-danger').addClass('badge-success');
            $('#system-state').html('<h3>Ready</h3>');
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
    $('#mainSection').html('<a href="#capture" class="btn btn-primary" id="retakeButton"><h4>Retake</h4></a>'+
                           '<a href="#" class="btn btn-primary" id="saveButton"><h4>Save</h4></a>');

    // 'renderIndexPage' function called when 'Retake' button is clicked
    $('#retakeButton').click(renderIndexPage);

    // 'renderAccessCodePage' function called when 'Save' button is clicked
    $('#saveButton').click(renderAccessCodePage);
}

function renderAccessCodePage()
{
    // sets class height to 100%
    $('#mainSection').addClass('h-100');
    // displays systems state element and 'Capture' button
    $('#mainSection').html('<div class="container-fluid h-100">'+
                           '<div class="row text-center">'+
                           '<div class="col-md-12"><h2>&nbsp;</h2><h2>&nbsp;</h2></div>'+
                           '</div>'+
                           '<div class="row text-center">'+
                           '<div class="col-md-4"></div>'+
                           '<div class="col-md-4">'+
                           '<div><h2><b>Your access code is:</b></h2></div>'+
                           '<span id="access-code" class="badge badge-success"><h3>6701</h3></span>'+
                           '</div>'+
                           '<div class="col-md-4">'+
                           '</div>'+
                           '</div>'+
                           '<div class="row text-center">'+
                           '<div class="col-md-12"><h2>&nbsp;</h2><h2>&nbsp;</h2></div>'+
                           '</div>'+
                           '<div class="row text-center">'+
                           '<div class="col-md-3"></div>'+
                           '<div class="col-md-6">'+
                           '<h4>Please write your access code on the card provided to you and follow the instructions on the back of the card to get a copy of your video.</h4>'+
                           '<h4>&nbsp;</h4>'+
                           '<h4>Please click Done when you are finished writing your access code.</h4>'+
                           '</div>'+
                           '<div class="col-md-3"></div>'+
                           '</div>'+
                           '<div class="row text-center">'+
                           '<div class="col-md-12">'+
                           '<h2>&nbsp;</h2>'+
                           '<h2>&nbsp;</h2>'+
                           '</div>'+
                           '</div>'+
                           '<div class="row text-center">'+
                           '<div class="col-md-12">'+
                           '<a href="" class="btn btn-primary" id="done-Button"><h4>Done</h4></a>'+
                           '</div>'+
                           '</div>'+
                           '<div class="row text-center">'+
                           '<div class="col-md-12">'+
                           '<h2>&nbsp;</h2>'+
                           '<h2>&nbsp;</h2>'+
                           '</div>'+
                           '</div>'+
                           '</div>')
}
