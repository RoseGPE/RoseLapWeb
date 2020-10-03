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