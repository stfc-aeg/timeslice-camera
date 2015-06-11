//$('#captureButton').button();

// Set up monitor enable checkbox and sync state with server
$("[name='monitor-enable-checkbox']").bootstrapSwitch();
$.get('/monitor', function(data) {
    monitor_state = parseInt(data)
    console.log(monitor_state)
    $("[name='monitor-enable-checkbox']").bootstrapSwitch('state', monitor_state, true);
});

$('input[name="monitor-enable-checkbox"]').on('switchChange.bootstrapSwitch', function(event, state) {
    $.post('/monitor?enable=' + (state == true ? 1 : 0))
});

$('#captureButton').click(function() {

    $(this).button('loading');
    $('#capture-state span').html('')

    $.get('/capture', function(data) {
        //alert(data);
        $('#capture-state span').html(data)
        $('#captureButton').button('reset');
    });

    //setTimeout(function() { $('#captureButton').button('reset');}, 2000);
});

$('#connectButton').click(function() {

    $(this).button('loading');
    $('#connect-state span').html('Connecting...')

    $.get('/connect', function(data) {
        $('#connect-state span').html(data);
        $('#connectButton').button('reset');
    });
});
