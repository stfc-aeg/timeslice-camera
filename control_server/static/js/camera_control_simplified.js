var system_state = 0;
var capture_state = 0;
var retrieve_state = 0;
var render_state = 0;

pollCameraState();

function pollCameraState() {
    // Check the state of the cameras
	$.getJSON("/camera_state", function(response) {	     
        
        // Dynamically update countdown count
        $('#countdown').html(parseInt(response.capture_countdown_count));
        
        system_state = response.system_state;
        capture_state = response.capture_state;
        retrieve_state = response.retrieve_state;
        render_state = response.render_state;

        // Dynamically update loader message
        $('#loader-message').html('<h4>'+response.capture_status+'</h4>');

        // Hide loader if capture state is 0
        if(capture_state == 2 || retrieve_state == 2 || render_state == 2) {
            $('#loader1').addClass('d-none');
            $('#start-again-button').removeClass('d-none');
        }

    });

    setTimeout(pollCameraState, 250);
}

$(document).ready(renderIndexView);

function renderIndexView() {
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
                            '<div id="index-view-message"></div>'+
                            '</div>'+
                            '<div class="col-md-1"></div>'+
                            '</div>'+
                            '</div>');
    
    if(system_state == 0) {
        awaitSystemNotReady();
    } else {
        awaitSystemReady();
    }

    function awaitSystemNotReady() {
        if(system_state == 0) {
            renderSystemNotReadyView();
            awaitSystemReady();
        } else {
            setTimeout(awaitSystemNotReady, 200);
        }
    
        function renderSystemNotReadyView() {
            $('#system-state').removeClass('alert-success').addClass('alert-danger');
            $('#system-state').css({"border":"3px solid darkred"});
            $('#system-state').html('<h3>System not ready</h3>');
            $('#capture-button').prop("disabled", true);
            $('#index-view-message').html('<h4>Please wait until the system is ready to be able to capture a video!</h4>');
        }
    }
    
    function awaitSystemReady() {
        if(system_state == 1) {
            renderSystemReadyView();
            awaitSystemNotReady();
        } else {
            setTimeout(awaitSystemReady, 200);
        }
    
        function renderSystemReadyView() {
            $('#system-state').removeClass('alert-danger').addClass('alert-success');
            $('#system-state').css({"border":"3px solid darkgreen"});
            $('#system-state').html('<h3>System ready</h3>');
            $('#capture-button').prop("disabled", false);
            $('#index-view-message').html('<h4>Tap Capture to start capturing a video.</h4>');
        }
    }

    $('#capture-button').click(capture);

    function capture() {
        // Trigger capture action and render countdown
        $.post('/capture_countdown');
        renderCountdownView();
    }
}

function renderCountdownView() {
    $('#main-section').html('<div class="vertical-center">'+
                            '<div class="container-fluid text-center">'+
                            '<div class="row">'+
                            '<div class="col-md-12">'+
                            '<div id="countdown"></div>'+
                            '</div>'+
                            '</div>'+
                            '</div>'+
                            '</div>'); 
    awaitCaptureCapturing();
} 

function awaitCaptureCapturing() {
    if (capture_state != 1) {
        setTimeout(awaitCaptureCapturing, 200);
    } else {
        renderLoadingView();
    }

    function renderLoadingView() {
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
                                '<div class="row">'+
                                '<div class="col-md-12">'+
                                '<h4>&nbsp;</h4>'+
                                '<button class="btn btn-primary d-none" id="start-again-button"><h3>Start Again</h3></button>'+
                                '</div>'+
                                '</div>'+
                                '</div>'+
                                '</div>');

        $('#start-again-button').click(resetStates);

        awaitRenderCompleted();          
    }
}

function resetStates() {
    $.post('/reset_states');
    renderIndexView();
}

function awaitRenderCompleted() {
    if (render_state != 3) {
        setTimeout(awaitRenderCompleted, 200);
    } else {
        renderRetakeSaveView();
    }

    function renderRetakeSaveView() {
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

    $('#retake-button').click(resetStates);

    $('#save-button').click(renderAccessCodeView);
    }
}

function renderAccessCodeView() {
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
                            '</div>');

    $('#done-button').click(renderFinalView);
}

function renderFinalView() {
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
                            '</div>');

    $('#finish-button').click(renderIndexView);
}