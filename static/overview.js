function nested_obj_get(obj, keys){
  next = obj[keys[0]]
  if (keys.length == 1)
    return next

  if (next)
    return nested_obj_get(next, keys.slice(1));
}

function nested_obj_set(obj, keys, val) {
  if (keys.length == 1)
    return obj[keys[0]] = val;
  
  if (typeof(obj[keys[0]]) == 'undefined')
    obj[keys[0]] = {}
  
  return nested_obj_set(obj[keys[0]], keys.slice(1), val);
}

function ged(edt) {
  return $("#"+edt).editable("getValue")[edt];
}











function new_vehicle() {
  $("#vehicleEditModal").modal('show');

  $("#vehicleEditName").prop('disabled', false);
  $("#vehicleEditName").val("New Vehicle");

  $("#vehicleEditVersion").html(`V1`);
  $("#vehicleEditVersion").data("version", 1);
  $("#vehicleEditVersion").val(1);
}

function discard_vehicle_edit() {
  $("#vehicleEditModal").modal('hide')
}

function save_vehicle() {
  fdata = {}

  let x = 12;
  $("[id^=vehicleEdit_]").each(function(index){
    let varname = $(this).attr('id').substring(x);
    let v = ged($(this).attr('id'));
    let ptype = $(this).data("parse");
    if(ptype && ptype.includes("list")) {
      if (ptype.includes("str"))
        v = v.split(',').map(function(bit){return bit.trim();});
      else
        v = v.split(',').map(function(bit){return parseFloat(bit);});
    } else {
      if (! (ptype && ptype.includes("str")))
        v = parseFloat(v);
    }
    nested_obj_set(fdata, varname.split('-'), v);
  });

  $.post(
      "/rest/vehicle",
      {
        "name": $("#vehicleEditName").val(),
        "version": $("#vehicleEditVersion").data("version"),
        "filedata": JSON.stringify(fdata)
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
  $.get("/rest/vehicle",
    {
      "name": name,
      "version": version
    }
  ).then(function(data) {
    if (data.error) {
      alert(data.error);
      return;
    }

    $("#vehicleEditModal").modal('show');

    $("#vehicleEditName").prop('disabled', true);
    $("#vehicleEditName").val(data.name);

    $("#vehicleErrorMsg").hide();

    if (typeof(new_version) == 'undefined'){
      $("#vehicleEditVersion").html(`V${data.version}`);
      $("#vehicleEditVersion").data("version", data.version);
    }
    else{
      $("#vehicleEditVersion").html(`V${data.version} -> V${new_version}`);   
      $("#vehicleEditVersion").data("version", new_version);   
    }

    fdata = JSON.parse(data.filedata);
    //console.log(fdata);

    let x = 12;
    $("[id^=vehicleEdit_]").each(function(index){
      let varname = $(this).attr('id').substring(x);
      let v = String(nested_obj_get(fdata, varname.split('-')));
      $(this).editable("setValue", v === null || v === undefined ? "-" : v);
    });

    validate_vehicle();
  });
}

function errorlog_vehicle(name, version) {
  $.get("/rest/vehicle",
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











function validate_vehicle() {
  console.log("validating");
  if (ged("vehicleEdit_brakes-mode") == 'perfect') {
    $("#vehicleEditRow_brakes-front_bias").hide();
  } else {
    $("#vehicleEditRow_brakes-front_bias").show();
  }

  if (ged("vehicleEdit_front_axle-model") == 'mu') {
    $("#vehicleEditRow_front_axle-mu").show();
  } else {
    $("#vehicleEditRow_front_axle-mu").hide();
  }

  if (ged("vehicleEdit_rear_axle-model") == 'mu') {
    $("#vehicleEditRow_rear_axle-mu").show();
  } else {
    $("#vehicleEditRow_rear_axle-mu").hide();
  }
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

  $("#vehicleErrorMsg").hide();
}

function discard_track_edit() {
  $("#trackEditModal").modal('hide')
}

function save_track() {
  $.post(
      "/rest/track",
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
  $.get("/rest/track",
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

    $("#vehicleErrorMsg").hide();

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
  $.get("/rest/track",
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

  $("#studyEdit_vehicle").html('');
  $("#studyEdit_vehicle").data("valid").forEach(function(vehicle){
    $("#studyEdit_vehicle").append(new Option(vehicle, vehicle));
  });

  $("#studyEdit_tracks_dropdown").val('');
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
      "/rest/study",
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
  $.get("/rest/study",
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
  $.get("/rest/study",
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
  $.get("/rest/study",
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