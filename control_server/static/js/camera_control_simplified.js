var system_state = 0;
var capture_state = 0;
var retrieve_state = 0;
var render_state = 0;

pollCameraState();

function pollCameraState() {
    // Check the state of the cameras
	$.getJSON("/camera_state", function(response) {	     
        // Dynamically update countdown count
        $('#countdown').html(response.capture_countdown_count);

        system_state = response.system_state;
        capture_state = response.capture_state;
        retrieve_state = response.retrieve_state;
        render_state = response.render_state;

        // Dynamically update loader message
        $('#loader-message').html('<h4>'+response.capture_status+'</h4>');

        // Hide loader if capture state is 0
        if(capture_state == 2 || retrieve_state == 2 || render_state == 2) {
            $('#loader1').addClass('d-none');
            $('#error-view').removeClass('d-none');
        }

    });

    setTimeout(pollCameraState, 250);
}

$(document).ready(renderIndexView);

function renderIndexView() {
    $('#error-view').addClass('d-none');
    $('#loading-view').addClass('d-none');
    $('#retake-save-view').addClass('d-none');
    $('#final-view').addClass('d-none');
    $('#index-view').removeClass('d-none');

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
}

function capture() {
    // Trigger capture action and render countdown
    $.post('/capture_countdown');
    renderCountdownView();
}

function renderCountdownView() {
    $('#index-view').addClass('d-none');
    $('#countdown-view').removeClass('d-none');

    awaitCaptureCapturing();
} 

function awaitCaptureCapturing() {
    if (capture_state != 1) {
        setTimeout(awaitCaptureCapturing, 200);
    } else {
        renderLoadingView();
    }

    function renderLoadingView() {
        $('#countdown-view').addClass('d-none');
        $('#loading-view').removeClass('d-none');
        $('#loader1').removeClass('d-none');

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
        $('#loading-view').addClass('d-none');
        $('#retake-save-view').removeClass('d-none');
    }
}

function renderAccessCodeView() {
    $('#retake-save-view').addClass('d-none');
    $('#access-code-view').removeClass('d-none');
}

function renderFinalView() {
    $('#access-code-view').addClass('d-none');
    $('#final-view').removeClass('d-none');
}