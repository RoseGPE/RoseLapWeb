
function new_vehicle() {
  $("#vehicleEditModal").modal('show')

  $("#vehicleEditName").prop('disabled', false);

  $("#vehicleEditModal").modal('show');
  $("#vehicleEditText").keyup(validate_json_vehicle);
  $("#vehicleEditText").change(validate_json_vehicle);
  
  $("#vehicleEditName").val("New Vehicle");
  $("#vehicleEditText").val("--- Insert your YAML here ---");

  $("#vehicleEditVersion").html('');
  $("#vehicleEditVersion").append(new Option(`V1`, 1));
  $("#vehicleEditVersion").val(1);

  validate_json_vehicle();
}

function discard_vehicle_edit() {
  $("#vehicleEditModal").modal('hide')
}

function save_vehicle() {
  $.post(
      "/vehicle",
      {
        "name": $("#vehicleEditName").val(),
        "version": $("#vehicleEditVersion").data("version"),
        "filedata": $("#vehicleEditText").val()
      }
  ).then(function(data) {
    if (data.error) {
      alert(data.error);
      return;
    }

    //  $("#vehicleEditModal").modal('hide')
    location.reload();
  });
}

function edit_vehicle(name, version, new_version) {
  $.get("/vehicle",
    {
      "name": name,
      "version": version
    }
  ).then(function(data) {
    if (data.error) {
      alert(data.error);
      return;
    }

    $("#vehicleEditName").prop('disabled', true);

    $("#vehicleEditModal").modal('show');
    $("#vehicleEditText").keyup(validate_json_vehicle);
    $("#vehicleEditText").change(validate_json_vehicle);

    $("#vehicleEditName").val(data.name);
    $("#vehicleEditText").val(data.filedata);

    if (typeof(new_version) == 'undefined'){
      $("#vehicleEditVersion").html(`V${data.version}`);
      $("#vehicleEditVersion").data("version", data.version);
    }
    else{
      $("#vehicleEditVersion").html(`V${data.version} -> V${new_version}`);   
      $("#vehicleEditVersion").data("version", new_version);   
    }

    validate_json_vehicle();
  });
}

function validate_json_vehicle() {
  let txt = $("#vehicleEditText").val();
  try {
    obj = jsyaml.load(txt);
    
    $("#vehicleErrorMsg").alert()
    $("#vehicleErrorMsg").html(`Valid YAML (may not be fully formed, but syntax is correct)`);
    $("#vehicleErrorMsg").removeClass('alert-danger');
    $("#vehicleErrorMsg").addClass('alert-success');

    $("#vehicleSaveButton").html('Save');
    $("#vehicleSaveButton").removeClass('btn-warning');
    $("#vehicleSaveButton").addClass('btn-primary');
  } catch (error) {
    $("#vehicleErrorMsg").alert()
    $("#vehicleErrorMsg").html(`ERROR: ${error.message}`);
    $("#vehicleErrorMsg").addClass('alert-danger');
    $("#vehicleErrorMsg").removeClass('alert-success');

    $("#vehicleSaveButton").html('Save (with errors)');
    $("#vehicleSaveButton").addClass('btn-warning');
    $("#vehicleSaveButton").removeClass('btn-primary');
  }
}

function errorlog_vehicle(name, version) {
  $.get("/vehicle",
    {
      "name": name,
      "version": version
    }
  ).then(function(data) {
    if (data.error) {
      alert(data.error);
      return;
    }

    $("#errorLogType").html("Vehicle Error Log");
    $("#errorLogTitle").html(data.name);
    $("#errorLogVersion").html(`V${data.version}`);
    $("#errorLogVersion").data("version", data.version);

    $("#errorLogBody").val(data.log)

    $("#errorLogModal").modal('show');
  });
}

function new_track() {
  $("#trackEditModal").modal('show')

  $("#trackEditName").prop('disabled', false);

  $("#trackEditFileUpload").val('');

  $("#trackEditModal").modal('show');
  
  $("#trackEditName").val("New Track");
  $("#trackEditText").val("--- Insert your track data here ---");

  $("#trackEditVersion").html(`V1`);
  $("#trackEditVersion").data("version", 1);
}

function discard_track_edit() {
  $("#trackEditModal").modal('hide')
}

function save_track() {
  $.post(
      "/track",
      {
        "name": $("#trackEditName").val(),
        "version": $("#trackEditVersion").data("version"),
        "filedata": $("#trackEditText").val(),
        "unit": $("#trackEditUnit").val(),
        "filetype": $("#trackEditFileType").val()
      }
  ).then(function(data) {
    if (data.error) {
      alert(data.error);
      return;
    }

    //  $("#trackEditModal").modal('hide')
    location.reload();
  });
}

function edit_track(name, version, new_version) {
  $.get("/track",
    {
      "name": name,
      "version": version
    }
  ).then(function(data) {
    if (data.error) {
      alert(data.error);
      return;
    }

    $("#trackEditName").prop('disabled', true);

    $("#trackEditFileUpload").val('');

    $("#trackEditModal").modal('show');

    $("#trackEditName").val(data.name);
    $("#trackEditText").val(data.filedata);
    $("#trackEditUnit").val(data.unit);
    $("#trackEditFileType").val(data.filetype);

    if (typeof(new_version) == 'undefined'){
      $("#trackEditVersion").html(`V${data.version}`);
      $("#trackEditVersion").data("version", data.version);
    }
    else{
      $("#trackEditVersion").html(`V${data.version} -> V${new_version}`);   
      $("#trackEditVersion").data("version", new_version);   
    }
  });
}

function errorlog_track(name, version) {
  $.get("/track",
    {
      "name": name,
      "version": version
    }
  ).then(function(data) {
    if (data.error) {
      alert(data.error);
      return;
    }

    $("#errorLogType").html("Track Error Log");
    $("#errorLogTitle").html(data.name);
    $("#errorLogVersion").html(`V${data.version}`);
    $("#errorLogVersion").data("version", data.version);

    $("#errorLogBody").val(data.log)

    $("#errorLogModal").modal('show');
  });
}

function new_study() {
  $("#studyEditName").prop('disabled', true);
  $("#studyEditVersion").prop('disabled', true);
  $("#studyEditModal").modal('show');
  $("#studyEditName").val("New Study");

  $("#studyEditVersion").html('V1');
  $("#studyEditVersion").data("version", 1)

  // unpack data

  //fdata = JSON.parse(data.filedata)

  $("#studyEdit_vehicle").html('');
  $("#studyEdit_vehicle").data("valid").forEach(function(vehicle){
    $("#studyEdit_vehicle").append(new Option(vehicle, vehicle));
  });

  $("#studyEdit_tracks_dropdown").val('');
  //$("#studyEdit_vehicle").val(fdata.vehicle);

  /*$("#studyEdit_tracks").tagsinput('items', fdata.tracks);
  $("#studyEdit_vehicle").val(fdata.vehicle);
  $("#studyEdit_model").val(fdata.model);
  $("#studyEdit_sweeps").val(fdata.sweeps);
  $("#studyEdit_meshsize").val(fdata.meshsize);*/
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