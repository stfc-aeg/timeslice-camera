pollCameraState();

$(document).ready(renderIndexPage);

function renderIndexPage() {
    $('#main-section').html('<div class="container-fluid text-center">'+
                            '<div class="row">'+
                            '<div class="col-md-12">'+
                            '<span class="badge" id="system-state"></span>'+
                            '</div>'+
                            '</div>'+
                            '<div class="row">'+
                            '<div class="col-md-12">'+
                            '<a class="btn btn-primary" id="capture-button" href="#"><h4>Capture</h4></a>'+
                            '</div>'+
                            '</div>'+
                            '</div>');

    $('#capture-button').click(renderCountdownPage);
}

function renderCountdownPage() {
    $('#main-section').html('<div class="vertical-center">'+
                            '<div class="container-fluid text-center">'+
                            '<div class="row">'+
                            '<div class="col-md-12">'+
                            '<div id="countdown">5</div>'+
                            '</div>'+
                            '</div>'+
                            '</div>'+
                            '</div>')

    // 5 second countdown timer; countdown element is dynamically updated
    var timeLeft = 4;
    var intervalTime = setInterval(function() {
        document.getElementById('countdown').innerHTML = timeLeft;
        timeLeft -= 1;

        if(timeLeft < 0) {
            clearInterval(intervalTime);
            document.getElementById('countdown').innerHTML = "GO!";
            setTimeout(capture, 500);
            setTimeout(renderLoadingPage, 500);
        }
    }, 1000);

    function capture() {
        // Triggers capture action
        $.post('/capture');
    }   
} 

function renderLoadingPage() {
    if ($('#countdown').html() == "GO!") {
        $('#main-section').html('<div class="vertical-center">'+
                                '<div class="container-fluid text-center">'+
                                '<div class="row">'+
                                '<div class="col-md-12">'+
                                '<div id="loader1" class="loader"></div>'+
                                '</div>'+
                                '</div>'+
                                '<div class="row">'+
                                '<div class="col-md-4"></div>'+
                                '<div class="col-md-4">'+
                                '<div id="loader-message"><h4>&nbsp;</h4></div>'+
                                '</div>'+
                                '<div class="col-md-4"></div>'+
                                '</div>'+
                                '</div>'+
                                '</div>');
    }
}

function pollCameraState() {
    // Checks the state of the cameras
	$.getJSON("/camera_state", function(response) {	     
        // Dynamically updates the system state element
        if(response.system_state == 0) {
            $('#system-state').removeClass('badge-success').addClass('badge-danger');
            $('#system-state').html('<h3>Not ready</h3>');
            $('#capture-button').addClass('disabled');
        } else {
            $('#system-state').removeClass('badge-danger').addClass('badge-success');
            $('#system-state').html('<h3>Ready</h3>');
            $('#capture-button').removeClass('disabled');
        }

        $('#loader-message').html('<h4>'+response.capture_status+'</h4>');

        if(response.capture_state == 0) {
            $('#loader1').hide();
        }

        if(response.render_status == 3) {
            renderRetakeSavePage();
        }
    });

    setTimeout(pollCameraState, 250);
}

function renderRetakeSavePage() {
    $('#main-section').html('<div class="vertical-center">'+
                            '<div class="container-fluid text-center">'+
                            '<div class="row">'+
                            '<div class="col-md-12">'+
                            '<a class="btn btn-primary" id="retake-button" href="#"><h4>Retake</h4></a>'+
                            '<a class="btn btn-primary" id="save-button" href="#"><h4>Save</h4></a>'+
                            '</div>'+
                            '</div>'+
                            '</div>'+
                            '</div>');

    $('#retake-button').click(renderIndexPage);

    $('#save-button').click(renderAccessCodePage);
}

function renderAccessCodePage() {
    $('#main-section').html('<div class="vertical-center">'+
                            '<div class="container-fluid text-center">'+
                            '<div class="row">'+
                            '<div class="col-md-3"></div>'+
                            '<div class="col-md-6">'+
                            '<div><h2><b>Your access code is:</b></h2></div>'+
                            '<span class="badge badge-success" id="access-code"><h3>6701</h3></span>'+
                            '</div>'+
                            '<div class="col-md-3"></div>'+
                            '</div>'+
                            '<div class="row">'+
                            '<div class="col-md-12">'+
                            '<h2>&nbsp;</h2>'+
                            '</div>'+
                            '</div>'+
                            '<div class="row">'+
                            '<div class="col-md-1"></div>'+
                            '<div class="col-md-10">'+
                            '<h4>Please write your access code on the card provided to you and follow the instructions on the back of the card to get a copy of your video.</h4>'+
                            '<h4>&nbsp;</h4>'+
                            '<h4>Please click Done when you are finished writing your access code.</h4>'+
                            '</div>'+
                            '<div class="col-md-1"></div>'+
                            '</div>'+
                            '<div class="row">'+
                            '<div class="col-md-12">'+
                            '<h2>&nbsp;</h2>'+
                            '</div>'+
                            '</div>'+
                            '<div class="row">'+
                            '<div class="col-md-12">'+
                            '<a class="btn btn-primary" id="done-button" href="#"><h4>Done</h4></a>'+
                            '</div>'+
                            '</div>'+
                            '</div>'+
                            '</div>')

    $('#done-button').click(renderFinalPage);
}

function renderFinalPage() {
    $('#main-section').html('<div class="vertical-center">'+
                            '<div class="container-fluid text-center">'+
                            '<div class="row">'+
                            '<div class="col-md-1"></div>'+
                            '<div class="col-md-10">'+
                            '<h4>Your video was successfully uploaded and is ready to be downloaded.<br>Please do not forget to take your card with you.</h4>'+
                            '<h4>&nbsp;</h4><h4>&nbsp;</h4><h4>&nbsp;</h4>'+
                            '<h4>Thank you</h4>'+
                            '</div>'+
                            '<div class="col-md-1"></div>'+
                            '</div>'+
                            '<div class="row">'+
                            '<div class="col-md-12">'+
                            '<h2>&nbsp;</h2>'+
                            '</div>'+
                            '</div>'+
                            '<div class="row">'+
                            '<div class="col-md-12">'+
                            '<a class="btn btn-primary" id="finish-button" href="#"><h4>Finish</h4></a>'+
                            '</div>'+
                            '</div>'+
                            '</div>'+
                            '</div>') 

    $('#finish-button').click(renderIndexPage);
}