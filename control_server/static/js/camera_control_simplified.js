pollCameraState();

$(document).ready(renderIndexPage);

function renderIndexPage() {
    $('#main-section').html('<div class="container-fluid text-center">'+
                            '<div class="row">'+
                            '<div class="col-md-3"></div>'+
                            '<div class="col-md-6">'+
                            '<div class="alert mx-auto" id="system-state" role="alert"></div>'+
                            '</div>'+
                            '<div class="col-md-3"></div>'+
                            '</div>'+
                            '<div class="row">'+
                            '<div class="col-md-12">'+
                            '<button class="btn btn-primary" id="capture-button"><h3>Capture</h3></button>'+
                            '</div>'+
                            '</div>'+
                            '<div class="row">'+
                            '<div class="col-md-1"></div>'+
                            '<div class="col-md-10">'+
                            '<h4>&nbsp;</h4>'+
                            '<div id="index-page-message"></div>'+
                            '</div>'+
                            '<div class="col-md-1"></div>'+
                            '</div>'+
                            '</div>');

    $('#capture-button').click(capture);

    function capture() {
        // Trigger capture action and render countdown
        $.post('/capture');
        renderCountdownPage();
    }
}

function renderCountdownPage() {
    $('#main-section').html('<div class="vertical-center">'+
                            '<div class="container-fluid text-center">'+
                            '<div class="row">'+
                            '<div class="col-md-12">'+
                            '<div id="countdown"></div>'+
                            '</div>'+
                            '</div>'+
                            '</div>'+
                            '</div>') 
} 

function renderLoadingPage() {
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

function pollCameraState() {
    // Check the state of the cameras
	$.getJSON("/camera_state", function(response) {	     
        // Dynamically update the system state element
        if(response.system_state == 0) {
            $('#system-state').removeClass('alert-success').addClass('alert-danger');
            $('#system-state').css({"border":"3px solid darkred"});
            $('#system-state').html('<h3>System not ready</h3>');
            $('#capture-button').prop("disabled", true);
            $('#index-page-message').html('<h4>Please wait until the system is ready to be able to capture a video!</h4>')
        } else {
            $('#system-state').removeClass('alert-danger').addClass('alert-success');
            $('#system-state').css({"border":"3px solid darkgreen"});
            $('#system-state').html('<h3>System ready</h3>');
            $('#capture-button').prop("disabled", false);
            $('#index-page-message').html('<h4>Tap Capture to start capturing a video.</h4>')
        }
        
        // Dynamically update countdown count
        $('#countdown').html(parseInt(response.capture_countdown_count));
        
        if(response.capture_countdown_count == 0) {
            $('#countdown').html('GO!');
        }

        if ($('#countdown').html() == "GO!") {
            renderLoadingPage();
        }

        // Dynamically update loader message
        $('#loader-message').html('<h4>'+response.capture_status+'</h4>');

        // Hide loader if capture state is 0
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
                            '<button class="btn btn-primary" id="retake-button"><h3>Retake</h3></button>'+
                            '<button class="btn btn-primary" id="save-button"><h3>Save</h3></button>'+
                            '</div>'+
                            '</div>'+
                            '<div class="row">'+
                            '<div class="col-md-1"></div>'+
                            '<div class="col-md-10">'+
                            '<h4>&nbsp;</h4>'+
                            '<h4>Tap Save to save this video or tap Retake to start capturing a new video.'+
                            '</div>'+
                            '<div class="col-md-1"></div>'+
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
                            '<h4>&nbsp;</h4>'+
                            '</div>'+
                            '</div>'+
                            '<div class="row">'+
                            '<div class="col-md-1"></div>'+
                            '<div class="col-md-10">'+
                            '<h4>Please write your access code on the card provided to you and follow the instructions on the back of the card to get a copy of your video.</h4>'+
                            '<h4>&nbsp;</h4>'+
                            '</div>'+
                            '<div class="col-md-1"></div>'+
                            '</div>'+
                            '<div class="row">'+
                            '<div class="col-md-12">'+
                            '<button class="btn btn-primary" id="done-button"><h3>Done</h3></button>'+
                            '</div>'+
                            '</div>'+
                            '<div class="row">'+
                            '<div class="col-md-12">'+
                            '<h4>&nbsp;</h4>'+
                            '<h4>Tap Done when you are finished writing your access code.</h4>'+
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
                            '<h4>Your video was successfully uploaded and is ready to be downloaded. Do not forget to take your card with you.</h4>'+
                            '<h4>&nbsp;</h4><h4>&nbsp;</h4>'+
                            '<h4>Thank you! You can now tap Finish.</h4>'+
                            '</div>'+
                            '<div class="col-md-1"></div>'+
                            '</div>'+
                            '<div class="row">'+
                            '<div class="col-md-12">'+
                            '<h4>&nbsp;</h4>'+
                            '</div>'+
                            '</div>'+
                            '<div class="row">'+
                            '<div class="col-md-12">'+
                            '<button class="btn btn-primary" id="finish-button"><h3>Finish</h3></button>'+
                            '</div>'+
                            '</div>'+
                            '</div>'+
                            '</div>') 

    $('#finish-button').click(renderIndexPage);
}