
function new_study() {
  $("#studyEditName").prop('disabled', true);
  $("#studyEditVersion").prop('disabled', true);
  $("#studyEditModal").modal('show');
  $("#studyEditName").val("New Study");

  $("#studyEditVersion").html('V1');
  $("#studyEditVersion").data("version", 1)

  $("#studyEdit_vehicle").html('');
  $("#studyEdit_vehicle").data("valid").forEach(function(vehicle){
    $("#studyEdit_vehicle").append(new Option(vehicle, vehicle));
  });

  $("#studyEdit_tracks_dropdown").val('');

  $("#vehicleEdit_sweeps").html('');
}

function discard_study_edit() {
  $("#studyEditModal").modal('hide')
}

function save_study(submit) {
  fdata = {}

  fdata.tracks   = $("#studyEdit_tracks").tagsinput('items');
  fdata.vehicle  = $("#studyEdit_vehicle").val();
  fdata.sweeps   = $("#studyEdit_sweeps").val();
  fdata.model    = {
    algorithm: $("#studyEdit_model").val(),
    meshsize:  $("#studyEdit_meshsize").val()
  };

  $.post(
      "/study",
      {
        "name": $("#studyEditName").val(),
        "version": $("#studyEditVersion").data("version"),
        "filedata": JSON.stringify(fdata),
        "submit": submit
      }
  ).then(function(data) {
    if (data.error) {
      alert(data.error);
      return;
    }

    //  $("#studyEditModal").modal('hide')
    location.reload();
  });
}

function edit_study(name, version, new_version) {
  $.get("/study",
    {
      "name": name,
      "version": version
    }
  ).then(function(data) {
    if (data.error) {
      alert(data.error);
      return;
    }

    $("#vehicleEdit_sweeps").html('');

    $("#studyEditName").prop('disabled', true);
    $("#studyEditVersion").prop('disabled', true);
    $("#studyEditModal").modal('show');
    $("#studyEditName").val(data.name);

    if (typeof(new_version) == 'undefined'){
      $("#studyEditVersion").html(`V${data.version}`);
      $("#studyEditVersion").data("version", data.version);
    }
    else{
      $("#studyEditVersion").html(`V${data.version} -> V${new_version}`);   
      $("#studyEditVersion").data("version", new_version);   
    }

    // unpack data

    fdata = JSON.parse(data.filedata);

    $("#studyEdit_vehicle").html('');
    $("#studyEdit_vehicle").data("valid").forEach(function(vehicle){
      $("#studyEdit_vehicle").append(new Option(vehicle, vehicle));
    });

    $("#studyEdit_tracks").data("tagsinput").removeAll();
    fdata.tracks.forEach(function(track){
      $("#studyEdit_tracks").data("tagsinput").add(track);
    });

    $("#studyEdit_vehicle").val(fdata.vehicle);
    $("#studyEdit_model").val(fdata.model);
    $("#studyEdit_sweeps").val(fdata.sweeps);
    $("#studyEdit_meshsize").val(fdata.meshsize);

    $("#studyEdit_tracks_dropdown").val('');
  });
}

function errorlog_study(name, version) {
  $.get("/study",
    {
      "name": name,
      "version": version
    }
  ).then(function(data) {
    if (data.error) {
      alert(data.error);
      return;
    }

    $("#errorLogType").html("Study Error Log");
    $("#errorLogTitle").html(data.name);
    $("#errorLogVersion").html(`V${data.version}`);
    $("#errorLogVersion").data("version", data.version);

    $("#errorLogBody").val(data.log)

    $("#errorLogModal").modal('show');
  });
}

function runlog_study(name, version) {
  $.get("/study",
    {
      "name": name,
      "version": version,
      "exlog": true
    }
  ).then(function(data) {
    if (data.error) {
      alert(data.error);
      return;
    }

    $("#errorLogType").html("Study Error Log");
    $("#errorLogTitle").html(data.name);
    $("#errorLogVersion").html(`V${data.version}`);
    $("#errorLogVersion").data("version", data.version);

    $("#errorLogBody").val(data.exlog)

    $("#errorLogModal").modal('show');
  });
}

function track_file_upload() {
  let file = $("#trackEditFileUpload").prop('files')[0];
  let fr = new FileReader();
  fr.onload = function(e) {
    extension = file.name.substring(file.name.lastIndexOf('.')+1);
    text = fr.result;

    $("#trackEditText").val(text);
    $("#trackEditFileType").val(extension);
  }
  fr.readAsText(file);
}

function add_track_to_study() {
  $("#studyEdit_tracks").data("tagsinput").add($("#studyEdit_tracks_dropdown").val());
  $("#studyEdit_tracks_dropdown").val('');
}

AXIS_NAMES = ["X", "Y", "Z", "A"]
VARIABLES  = {
  "aero.force":   "xyz",
  "aero.force_v": "real",
  "aero.cp":      "xyz",
  "mass.mass":    "real",
  "mass.moi":     "xyz",
  "mass.cg":      "xyz",
  "powertrain.omega_map":   "list",
  "powertrain.torque_map":  "list",
  "powertrain.power_map":   "list",
  "powertrain.trans_gears": "list",
  "powertrain.gear_ratio":  "real",
  "powertrain.trans_type":  "str",
  "powertrain.shift_time":  "real",
  "brakes.mode":       "str",
  "brakes.front_bias": "real"
};

function add_sweep_axis() {
  i = $("#vehicleEdit_sweeps").children().length;
  $("#vehicleEdit_sweeps").append(`<div>
    <label>Sweep Axis</label><button style="float: right" class="btn btn-danger" onclick="remove_sweep_var()">Delete Sweep Axis</button><button style="float:right" class="btn btn-success" onclick="add_sweep_variable(${i});">+ Add Variable</button>
    <table class="table table-condensed" id="vehicleEdit_sweeps_table_${i}">
      <tr class="active">
        <th style="text-align: right"></th>
      </tr>
      <tr>
        <td></td>
      </tr>
      <tr>
        <td></td>
      </tr>
      <tr>
        <td colspan=100><button class="btn btn-block btn-secondary" onclick="add_sweep_entry(${i});">+ Add Entries</button></td>
      </tr>
    </table>
    </div>`);
}

function togglebtn(x) {
  $(x).find('.btn').toggleClass('active');  
  
  if ($(x).find('.btn-primary').length>0) {
    $(x).find('.btn').toggleClass('btn-primary');
  }
  if ($(x).find('.btn-danger').length>0) {
    $(x).find('.btn').toggleClass('btn-danger');
  }
  if ($(x).find('.btn-success').length>0) {
    $(x).find('.btn').toggleClass('btn-success');
  }
  if ($(x).find('.btn-info').length>0) {
    $(x).find('.btn').toggleClass('btn-info');
  }
  
  $(x).find('.btn').toggleClass('btn-default');
}

function add_sweep_variable(axis) {
  let rows    = $(`#vehicleEdit_sweeps_table_${axis} tr`);
  let vars    = rows[0].cells.length-1;

  let a  = $(`<a class="editable typeahead"></a>`);
  a.editable({
    type: 'typeaheadjs',
    title: '',
    mode: 'inline',
    toggle: 'click',
    showbuttons: true,
    placeholder: "TYPE VARIABLE HERE",
    emptytext: "DEFINE VARIABLE",
    typeahead: {
      local: Object.keys(VARIABLES),
      limit: 20
    },
    validate: function(val) {
      if (! VARIABLES.hasOwnProperty(val))
        return "Invalid Variable."
    }
  }).on('shown', function(ev, editable) {
      setTimeout(function() {
          editable.input.$input.select();
      },0);
  });

  let tc = $(`<th style="text-align: center; vertical-align: center;" >
    <div>
      <div class="btn-group btn-toggle" onclick="togglebtn(this)" >
        <button class="btn btn-xs active btn-info">Replace</button>
        <button class="btn btn-xs btn-default" >Scale</button> 
      </div> - <div class="btn-group btn-toggle" onclick="togglebtn(this)" >
        <button class="btn btn-xs active btn-info" >List</button>
        <button class="btn btn-xs btn-default" >Range</button>
      </div>
      <button class="btn btn-xs btn-danger" onclick="remove_sweep_var()">Delete</button>
    </div></th>`).prepend(a);
  tc.insertBefore(rows[0].cells[vars]);

  for (let i=1; i<rows.length-1; i++) {
    console.log(i, vars);
    $(`<td>init</td>`).insertBefore(rows[i].cells[vars]);
  }

}

function add_sweep_entry(axis) {
  let rows = $(`#vehicleEdit_sweeps_table_${axis} tr`);
  let vars = rows[0].cells.length-1

  let row = $("<tr></tr>");
  for (let i=0; i<vars; i++) {
    row.append($(`<td>new</td>`));
  }
  row.append($("<td></td>"))
  $(row).insertBefore(rows[rows.length-1]);
}