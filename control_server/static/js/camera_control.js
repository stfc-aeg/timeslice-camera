//$('#captureButton').button();

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
