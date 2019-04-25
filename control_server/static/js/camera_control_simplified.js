var system_state = 0;
var capture_state = 0;
var retrieve_state = 0;
var render_state = 0;
var process_status = null;

pollCameraState();

function pollCameraState() {
    // Checks the state of the cameras.
	$.getJSON("/camera_state", function(response) {	     
        // Dynamically updates countdown count.
        $('#countdown').html(response.capture_countdown_count);

        system_state = response.system_state;
        capture_state = response.capture_state;
        retrieve_state = response.retrieve_state;
        render_state = response.render_state;
        process_status = response.process_status;

        // Dynamically updates loader message.
        $('#loader-message').html('<h4>'+response.process_status+'</h4>');

        // Hides loader and displays Error view if capture, retrieve or render state equal 0.
        if(capture_state == 2 || retrieve_state == 2 || render_state == 2) {
            $('#loader').addClass('d-none');
            $('#error-view').removeClass('d-none');
        }

    });

    setTimeout(pollCameraState, 250);
}
// Calls the 'renderIndexView' function once the page is fully loaded
$(document).ready(renderIndexView);

function capture() {
    // Sends a post request to the '/capture_countdown' URL and calls the 'renderCountdownView' function.

    $.post('/capture_countdown');
    renderCountdownView();
}

function resetStates() {
    // Sends a post request to the '/reset_states' URL and calls the 'renderIndexView' function.

    $.post('/reset_states');
    renderIndexView();
}

$('#capture-button').click(capture);
$('#start-again-button').click(resetStates);
$('#retake-button').click(resetStates);
$('#save-button').click(renderAccessCodeView);
$('#done-button').click(renderFinalView);
$('#finish-button').click(renderIndexView);

function renderIndexView() {
    // Displays the Index view and checks the value of 'system_state' to decide which function to call.

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
        /*
            Calls the 'renderSystemNotReadyView' and 'awaitSystemReady' functions if the value of 
            'system_state' is 0 (not ready), otherwise it calls itself again in 0.1 seconds.
        */

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
        /*  
            Calls the 'renderSystemReadyView' and 'awaitSystemNotReady' functions if the value 
            of 'system_state' is 1 (ready), otherwise it calls itself again in 0.1 seconds.
        */

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

function renderCountdownView() {
    // Displays the Countdown view and calls the 'awaitCaptureCapturing' function.

    $('#index-view').addClass('d-none');
    $('#countdown-view').removeClass('d-none');

    awaitCaptureCapturing();
} 

function awaitCaptureCapturing() {
    /* 
        Calls the 'renderLoadingView' function if the value of 'capture_state' is 
        not equal to 1, otherwise it calls itself again in 0.1 seconds.
    */

    if (capture_state != 1) {
        setTimeout(awaitCaptureCapturing, 200);
    } else {
        renderLoadingView();
    }

    function renderLoadingView() {
        // Displays the Loading view and calls the 'awaitRenderCompleted' function.

        $('#countdown-view').addClass('d-none');
        $('#loading-view').removeClass('d-none');
        $('#loader').removeClass('d-none');

        awaitRenderCompleted();
    }
}

function awaitRenderCompleted() {
    /* 
        Calls the 'renderRetakeSaveView' function if the value of 'render_state' 
        is 3, otherwise it calls itself again in 0.1 seconds.
    */

    if (render_state != 3) {
        setTimeout(awaitRenderCompleted, 200);
    } else {
        renderRetakeSaveView();
    }

    function renderRetakeSaveView() {
        // Displays the Retake & Save view.
        $('#loading-view').addClass('d-none');
        $('#retake-save-view').removeClass('d-none');
    }
}

function renderAccessCodeView() {
    // Displays the Access Code view
    $('#retake-save-view').addClass('d-none');
    $('#access-code-view').removeClass('d-none');
}

function renderFinalView() {
    // Displays the Final view
    $('#access-code-view').addClass('d-none');
    $('#final-view').removeClass('d-none');
}