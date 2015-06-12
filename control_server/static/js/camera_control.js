//$('#captureButton').button();

// Set up monitor enable checkbox and sync state with server
$("[name='monitor-enable-checkbox']").bootstrapSwitch();
$.get('/monitor', function(data) {
    monitor_state = parseInt(data)
    //console.log(monitor_state)
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

var max_cameras = 48
var cameras_per_group = 8;
var max_groups = max_cameras / cameras_per_group;
var icam = 0;

for ( var group = 0; group < max_groups; group++)
{
    var offset = group * cameras_per_group;
    $('<div class="btn-group" role="group">'+
      '<button id="camera-state-'+(++offset)+'" type="button" class="btn btn-danger btn-fixed-width" '+
          'data-toggle="button" aria-pressed="false">'+(offset)+'</button>'+
      '<button id="camera-state-'+(++offset)+'" type="button" class="btn btn-danger btn-fixed-width" '+
          'data-toggle="button" aria-pressed="false">'+(offset)+'</button>'+
      '<button id="camera-state-'+(++offset)+'" type="button" class="btn btn-danger btn-fixed-width" '+
          'data-toggle="button" aria-pressed="false">'+(offset)+'</button>'+
      '<button id="camera-state-'+(++offset)+'" type="button" class="btn btn-danger btn-fixed-width" '+
          'data-toggle="button" aria-pressed="false">'+(offset)+'</button>'+
      '<button id="camera-state-'+(++offset)+'" type="button" class="btn btn-danger btn-fixed-width" '+
          'data-toggle="button" aria-pressed="false">'+(offset)+'</button>'+
      '<button id="camera-state-'+(++offset)+'" type="button" class="btn btn-danger btn-fixed-width" '+
          'data-toggle="button" aria-pressed="false">'+(offset)+'</button>'+
      '<button id="camera-state-'+(++offset)+'" type="button" class="btn btn-danger btn-fixed-width" '+
          'data-toggle="button" aria-pressed="false">'+(offset)+'</button>'+
      '<button id="camera-state-'+(++offset)+'" type="button" class="btn btn-danger btn-fixed-width" '+
          'data-toggle="button" aria-pressed="false">'+(offset)+'</button>'+
      '</div><br>').appendTo('#camera-state');
}
$('</div>').appendTo('#camera-state');

$('#camera-enable-all').click(function() {
    for (var icam = 1; icam <= max_cameras; icam++)
    {
        $('#camera-state-'+icam).addClass('active');
    }
});

$('#camera-enable-none').click(function() {
    for (var icam = 1; icam <= max_cameras; icam++)
    {
        $('#camera-state-'+icam).removeClass('active');
    }
});

poll_camera_state();

function poll_camera_state()
{
    $.getJSON("/camera_state", function(response) {
        //console.log("Camera state: " + response.camera_state)
        //console.log("Camera state length: " + response.camera_state.length)
        var loop_len = (response.camera_state.length > max_cameras) ? max_cameras : response.camera_state.length;
        for (var icam = 0; icam < loop_len; icam++)
        {
            //$('#camera-state-'+(icam+1)).html(response.camera_state[icam]);
            var btn_id = '#camera-state-'+(icam+1);
            if (response.camera_state[icam] == 1) {
                $(btn_id).removeClass('btn-danger').addClass('btn-success');
            } else {
                $(btn_id).removeClass('btn-success').addClass('btn-danger');
            }
            if (response.camera_enable[icam] == 1) {
                $(btn_id).addClass('active');
            } else {
                $(btn_id).removeClass('active');
            }

        }
    });
    setTimeout(poll_camera_state, 1000);
}
