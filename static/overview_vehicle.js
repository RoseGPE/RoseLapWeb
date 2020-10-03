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
  let a = edt.editable("getValue");
  return a[Object.keys(a)[0]];
}

/* ACTIONS */

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
    let v = ged($(this));
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
  if (ged($("#vehicleEdit_brakes-mode")) == 'perfect') {
    $("#vehicleEditRow_brakes-front_bias").hide();
  } else {
    $("#vehicleEditRow_brakes-front_bias").show();
  }

  if (ged($("#vehicleEdit_front_axle-model")) == 'mu') {
    $("#vehicleEditRow_front_axle-tire-mu").show();
  } else {
    $("#vehicleEditRow_front_axle-tire-mu").hide();
  }

  if (ged($("#vehicleEdit_rear_axle-model")) == 'mu') {
    $("#vehicleEditRow_rear_axle-tire-mu").show();
  } else {
    $("#vehicleEditRow_rear_axle-tire-mu").hide();
  }
}