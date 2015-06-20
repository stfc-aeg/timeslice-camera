//$('#captureButton').button();

var max_cameras = 48
var cameras_per_group = 8;
var max_groups = max_cameras / cameras_per_group;
var icam = 0;
var preview_enable = false;
var preview_camera_select = 1;
var preview_update_time = 1;

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

$("[name='preview-enable-checkbox']").bootstrapSwitch();
$("[name='preview-enable-checkbox']").bootstrapSwitch('state', preview_enable, true);

for (var icam = 1; icam <= max_cameras; icam++)
{
    $('<option>'+icam+'</option>').appendTo('#preview-camera-select');
}

$('input[name="preview-enable-checkbox"]').on('switchChange.bootstrapSwitch', function(event,state) {
    post_preview_change();
});

$('#preview-camera-select').change(function() {
    post_preview_change();
});

$('#preview-update-rate').change(function() {
    post_preview_change();
});

function post_preview_change()
{
    preview_enable = $("[name='preview-enable-checkbox']").bootstrapSwitch('state');
    preview_camera_select = $('#preview-camera-select').val();
    preview_update_time = parseInt($('#preview-update-rate').val());
    $.post("/preview?enable=" + (preview_enable == true ? 1 : 0) + "&camera=" + preview_camera_select + "&update=" + preview_update_time);
}

poll_preview_image();

function poll_preview_image()
{
    if (preview_enable) {
        d = new Date();
        $("#preview-image").attr("src", $('#preview-image').attr('data-src') + '?' + d.getTime());

    }
    setTimeout(poll_preview_image, preview_update_time * 1000);
}

$('#captureButton').click(function() {

    $(this).button('loading');
    //$('#capture-state span').html('')

    $.post('/capture', function(data) {
        //alert(data);
        //$('#capture-state span').html(data)
        $('#captureButton').button('reset');
    });

    //setTimeout(function() { $('#captureButton').button('reset');}, 2000);

});

for ( var group = 0; group < max_groups; group++)
{
    var offset = group * cameras_per_group;
    $('<div class="btn-group" role="group">'+
      '<button id="camera-state-'+(++offset)+'" type="button" class="btn btn-danger btn-fixed-width">'+(offset)+'</button>'+
      '<button id="camera-state-'+(++offset)+'" type="button" class="btn btn-danger btn-fixed-width">'+(offset)+'</button>'+
      '<button id="camera-state-'+(++offset)+'" type="button" class="btn btn-danger btn-fixed-width">'+(offset)+'</button>'+
      '<button id="camera-state-'+(++offset)+'" type="button" class="btn btn-danger btn-fixed-width">'+(offset)+'</button>'+
      '<button id="camera-state-'+(++offset)+'" type="button" class="btn btn-danger btn-fixed-width">'+(offset)+'</button>'+
      '<button id="camera-state-'+(++offset)+'" type="button" class="btn btn-danger btn-fixed-width">'+(offset)+'</button>'+
      '<button id="camera-state-'+(++offset)+'" type="button" class="btn btn-danger btn-fixed-width">'+(offset)+'</button>'+
      '<button id="camera-state-'+(++offset)+'" type="button" class="btn btn-danger btn-fixed-width">'+(offset)+'</button>'+
      '</div><br>').appendTo('#camera-state');
}
$('</div>').appendTo('#camera-state');

var camera_enable = [];

for (var icam = 1; icam <= max_cameras; icam++)
{
    $('#camera-state-'+(icam)).click(function() {
        //console.log($(this).html());
        var camera_id = parseInt($(this).html())
        camera_enable[camera_id-1] = 1 - camera_enable[camera_id-1];
        $(this).toggleClass('active');
        post_camera_enable();
    });
}

function post_camera_enable()
{
    var enable_var = { 'camera_enable' : camera_enable};
    $.ajax({
        type: 'POST',
        url: '/camera_enable',
        data: JSON.stringify(enable_var),
        contentType: 'application/json; charset=utf-8',
        dataType: 'json',
        processData: true,
     });

}

$('#camera-enable-all').click(function() {
    for (var icam = 1; icam <= max_cameras; icam++)
    {
        camera_enable[icam-1] = 1;
        $('#camera-state-'+icam).addClass('active');
    }
    post_camera_enable();
});

$('#camera-enable-none').click(function() {
    for (var icam = 1; icam <= max_cameras; icam++)
    {
        camera_enable[icam-1] = 0
        $('#camera-state-'+icam).removeClass('active');
    }
    post_camera_enable();
});

poll_camera_state();

function poll_camera_state()
{
    $.getJSON("/camera_state", function(response) {
        var loop_len = (response.camera_state.length > max_cameras) ? max_cameras : response.camera_state.length;
        for (var icam = 0; icam < loop_len; icam++)
        {
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
        camera_enable = response.camera_enable;
        $('#system-state').html(response.system_status);
        if (response.system_state == 0) {
            $('#system-state').removeClass('label-success').addClass('label-danger');
        }
        else {
            $('#system-state').removeClass('label-danger').addClass('label-success');
        }
        $('#capture-state').html(response.capture_status);
    });
    setTimeout(poll_camera_state, 1000);
}

$('#version-info-button').click(function() {
    $.post('/camera_version', function(data) {
        // Do nothing
    });
});

$('#version-modal').on('shown.bs.modal', function (e) {

    $('#version-modal-content tbody').html('');

    for (var icam = 0; icam < max_cameras/2; icam++)
    {
        $('<tr>'+
            '<td><b>' + (icam+1)  + '</b></td>'+
            '<td id="camera-commit-' + (icam+1)  + '"> &nbsp; </td>'+
            '<td id="camera-time-'   + (icam+1)  + '"> &nbsp; </td>'+
            '<td><b>' + (icam+25) + '</b></td>'+
            '<td id="camera-commit-' + (icam+25) +'"> &nbsp; </td>'+
            '<td id="camera-time-'   + (icam+25) +'"> &nbsp; </td>'+
          '</tr>').appendTo('#version-modal-content tbody');
    }
    update_camera_version_info();
});

$('#version-modal-refresh').click(function() {
    $.post('/camera_version', function(data)
    {
        setTimeout(update_camera_version_info, 1000);
    });
});

function update_camera_version_info()
{
    $.getJSON('/camera_version', function(response)
    {
        var loop_len = response.camera_version_time.length;
        for (var icam = 0; icam < loop_len; icam++)
        {
            $('#camera-commit-'+(icam+1)).html(response.camera_version_commit[icam]);
            $('#camera-time-'+(icam+1)).html(date_from_unix_time(response.camera_version_time[icam]));
        }
    });

}

function date_from_unix_time(unix_time)
{
    var date_str;
    if (unix_time == 0) {
        date_str = '-';
    } else {
        the_date = new Date(parseInt(unix_time) * 1000);
        date_str = the_date.toLocaleString();
    }
    return date_str;
}

update_camera_config();

function update_camera_config()
{
    $.getJSON('/camera_config', function(response)
    {
        $(function() {
            $('#config-resolution-select option').filter(function() {
                return ($(this).text() == response.resolution);
            }).prop('selected', true);
        });
        $(function() {
            $('#config-iso-select option').filter(function() {
                return ($(this).text() == response.iso);
            }).prop('selected', true);
        });
        $(function() {
            $('#config-shutter-select option').filter(function() {
                return ($(this).text() == response.shutter_speed);
            }).prop('selected', true);
        });
    });
}

$('#config-resolution-select').change(function() {
    post_config_change("resolution", $(this).val());
});

$('#config-iso-select').change(function() {
    post_config_change("iso", $(this).val());
});

$('#config-shutter-select').change(function() {
    post_config_change("shutter_speed", $(this).val());
});

function post_config_change(param, value)
{
    console.log("Posting config change: param: " + param + " value: " + value);
    $.post("/camera_config?" + param + "=" + value, function(data) {

    });
}
