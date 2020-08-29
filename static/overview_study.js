function new_study() {
  $("#studyEditName").prop('disabled', false);
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

  $("#studyEdit_sweeps").html('');
  add_sweep_axis();
  add_postproc();
}

function discard_study_edit() {
  $("#studyEditModal").modal('hide')
}

function save_study(submit) {
  fdata = {}

  fdata.tracks   = $("#studyEdit_tracks").tagsinput('items');
  fdata.vehicle  = $("#studyEdit_vehicle").val();
  fdata.sweeps   = [];
  fdata.postprocs = [];
  fdata.model    = $("#studyEdit_model").val();
  fdata.settings = {
    dt:  $("#studyEdit_settings_dt").val()
  };

  $("#studyEdit_sweeps").children().each(function(axis){
    let tbl   = $(this).find('table tr');
    let title = ged($(this).find('.studyEdit_sweeps_title'));
    let swp   = []

    let rows    = $($(`.studyEdit_sweeps_table`)[axis]).find('tr');
    let vars    = rows[0].cells.length-1;

    for (let col = 0; col<vars; col++) {
      let varname = $($(rows[0]).find('input')[col]).val()
      let mode    = get_var_mode(axis, col);
      let operation    = get_var_operation(axis, col);
      if (mode == 'range') {
        swp.push({
          'varname': varname,
          'operation': operation,
          'values': {
            'start': ged($(rows[1].cells[col]).find('.editable')),
            'end':   ged($(rows[rows.length-1].cells[col]).find('.editable')),
            'length': rows.length-1
          }
        });
      } else {
        let lst = []
        for (let i = 1; i<rows.length; i++) {
          lst.push(ged($(rows[i].cells[col]).find('.editable')))        
        }
        swp.push({
          'varname': varname,
          'operation': operation,
          'values': lst
        });
      }
    }
    fdata.sweeps.push({"name": title, "variables": swp});
  });

  $("#studyEdit_postproc").children().each(function(pp){
    let name = ged($(this).find('.studyEdit_postproc_name'));
    let script_run = $(this).find('.studyEdit_postproc_script_run').val();
    let script_lap = $(this).find('.studyEdit_postproc_script_lap').val();

    fdata.postprocs.push({"name": name, "scripts":{"run": script_run, "lap": script_lap}});
  });

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

    $("#studyEdit_sweeps").html('');
    $("#studyEdit_postproc").html('');

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

    console.log(fdata);

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
    $("#studyEdit_settings_dt").val(fdata.settings.dt);
    $("#studyEdit_meshsize").val(fdata.model.meshsize);

    $("#studyEdit_tracks_dropdown").val('');

    // unpack fdata.sweeps
    for (m in fdata.sweeps) {
      add_sweep_axis(fdata.sweeps[m].name, fdata.sweeps[m].variables);
    }
    for (m in fdata.postprocs) {
      add_postproc(fdata.postprocs[m].name, fdata.postprocs[m].scripts);
    }
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

/* Sweeps */

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

function add_sweep_axis(name, vars) {
  let i = $("#studyEdit_sweeps").children().length;
  let x = $(`<div>
    <label>Sweep Axis "<a class="editable studyEdit_sweeps_title" data-type="text"></a>"</label>
    <table class="table table-condensed studyEdit_sweeps_table">
      <tr class="active">
        <th style="text-align: right"></th>
      </tr>
      <tr>
        <td></td>
      </tr>
      <tr>
        <td></td>
      </tr>
    </table>
    <div class="row">

      <div class="col-sm-3"><button style="float:right" class="btn btn-block btn-danger"  onclick="remove_sweep(parentIdx($(this), 3));">Delete Sweep Axis</button></div>
      <div class="col-sm-3"><button style="float:right" class="btn btn-block btn-success" onclick="add_sweep_variable(parentIdx($(this), 3));">+ Add Variable</button></div>
      <div class="col-sm-3"><button class="btn btn-block btn-info" onclick="add_sweep_entry(parentIdx($(this), 3));">+ Add Entries</button></div>
      <div class="col-sm-3"><button class="btn btn-block btn-warning" onclick="remove_sweep_entry(parentIdx($(this), 3));">- Remove Last Entry</button></div>
    </div>
    <hr/>
    </div>`);
  $("#studyEdit_sweeps").append(x);

  $("#studyEdit_sweeps .editable").editable({
      type: 'text',
      title: '',
      mode: 'inline',
      toggle: 'click',
      showbuttons: false,
      placeholder: "undefined",
      saveonchange: true,
      emptytext: "unset",
    }).on('shown', function(ev, editable) {
        setTimeout(function() {
            editable.input.$input.select();
        },0);
    });

  if (name === undefined) {
    add_sweep_variable(i);
  } else {
    // set name
    x.find('.studyEdit_sweeps_title').editable('setValue', name);

    // create enough rows
    for (let i=2; i<vars[0].values.length; i++) {
      $("<tr><td></td></tr>").insertAfter(x.find('table tr').last());
    }

    // add more vars
    for (varset in vars) {
      add_sweep_variable(i, vars[varset])
    }
  }
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

function parent(x, n) {
  if(n)
    return parent(x.parent(), n-1);
  return x;
}

function parentIdx(x, n) {
  return parent(x, n).prevAll().length;
}

function add_sweep_variable(axis, spec) {
  console.log("add_sweep_variable", axis, spec);

  if (spec === undefined) {
    spec = {operation: 'replace', values: []}
  }

  let rows    = $($(`.studyEdit_sweeps_table`)[axis]).find('tr');
  let vars    = rows[0].cells.length-1;

  let a  = $(`<input type="text" class="form-control form-inline typeahead" data-provide="typeahead" autocomplete="off" />`);
  a.typeahead({
      source: Object.keys(VARIABLES),
      items: 20
    });
  if (spec.varname)
    a.val(spec.varname);

  let tc = $(`<th style="text-align: center; vertical-align: center;" >
    <div>
      <div class="btn-group btn-toggle btn-operation" onclick="togglebtn(this)" >
        <button class="btn btn-xs ${spec.operation == 'replace' ? 'active btn-info':'btn-default'}">Replace</button>
        <button class="btn btn-xs ${spec.operation != 'replace' ? 'active btn-info':'btn-default'}" >Scale</button> 
      </div> - <div class="btn-group btn-toggle btn-varmode" onclick="togglebtn(this); change_sweep_type(parentIdx($(this), 6), parentIdx($(this), 2));" >
        <button class="btn btn-xs ${spec.values.start === undefined ? 'active btn-info':'btn-default'}" >List</button>
        <button class="btn btn-xs ${spec.values.start !== undefined ? 'active btn-info':'btn-default'}" >Range</button>
      </div> - <button class="btn btn-xs btn-danger" onclick="remove_sweep_var(parentIdx($(this), 6), parentIdx($(this), 2));">&times; Remove</button>
    </div></th>`).prepend(a);
  tc.insertBefore(rows[0].cells[vars]);

  if (spec.values.start === undefined) {
    for (let i=1; i<rows.length; i++) {
      let cell = $(`<td></td>`);
      let inp  = $(`<a class="editable"></a>`);
      inp.editable({
        type: 'text',
        title: '',
        mode: 'inline',
        toggle: 'click',
        showbuttons: false,
        placeholder: "undefined",
        saveonchange: true,
        emptytext: "unset",
      }).on('shown', function(ev, editable) {
          setTimeout(function() {
              editable.input.$input.select();
          },0);
      });
      if (i-1 < spec.values.length)
        inp.editable('setValue', spec.values[i-1])

      cell.append(inp);
      cell.insertBefore(rows[i].cells[vars]);
    }
  } else {
    let cell = $(`<td></td>`);
    let inp  = $(`<a class="editable"></a>`);
    inp.editable({
      type: 'text',
      title: '',
      mode: 'inline',
      toggle: 'click',
      showbuttons: false,
      placeholder: "undefined",
      saveonchange: true,
      emptytext: "unset",
    }).on('shown', function(ev, editable) {
        setTimeout(function() {
            editable.input.$input.select();
        },0);
    }).editable('setValue', spec.values.start);
    cell.append(inp);
    cell.insertBefore(rows[1].cells[vars]);

    // filler
    for (let i=2; i<rows.length-1; i++) {
      cell = $(`<td>.</td>`);
      cell.insertBefore(rows[i].cells[vars]);
    }

    cell = $(`<td></td>`);
    inp  = $(`<a class="editable"></a>`);
    inp.editable({
      type: 'text',
      title: '',
      mode: 'inline',
      toggle: 'click',
      showbuttons: false,
      placeholder: "undefined",
      saveonchange: true,
      emptytext: "unset",
    }).on('shown', function(ev, editable) {
        setTimeout(function() {
            editable.input.$input.select();
        },0);
    }).editable('setValue', spec.values.end);
    cell.append(inp);
    cell.insertBefore(rows[rows.length-1].cells[vars]);
  }
  

  a.focus()

}

function add_sweep_entry(axis) {
  let rows = $($(`.studyEdit_sweeps_table`)[axis]).find('tr');
  let vars = rows[0].cells.length-1

  let row = $("<tr></tr>");
  for (let i=0; i<vars; i++) {
    let cell = $(`<td></td>`);

    let inp = null
    if (get_var_mode(axis, i) == 'range') {
      inp = $($(rows[rows.length-1]).children()[i].children[0]).detach()
      $($(rows[rows.length-1]).children()[i]).html('.');
    } else {
      inp  = $(`<a class="editable"></a>`);
      inp.editable({
        type: 'text',
        title: '',
        mode: 'inline',
        toggle: 'click',
        showbuttons: false,
        placeholder: "undefined",
        saveonchange: true,
        emptytext: "unset",
      }).on('shown', function(ev, editable) {
          setTimeout(function() {
              editable.input.$input.select();
          },0);
      });
    }

    cell.append(inp);
    row.append(cell);
  }
  row.append($("<td></td>"))
  $(row).insertAfter(rows[rows.length-1]);
}

function remove_sweep_var(axis, variable) {
  console.log("remove_sweep_var", axis, variable);

  let rows = $($(`.studyEdit_sweeps_table`)[axis]).find('tr');
  let vars = rows[0].cells.length-1

  for (let i=0; i<rows.length; i++) {
    $(rows[i]).children()[variable].remove()
  }
}

function remove_sweep_entry(axis) {
  console.log("remove_sweep_entry", axis);

  let rows = $($(`.studyEdit_sweeps_table`)[axis]).find('tr');
  let vars = rows[0].cells.length-1

  for (let i=0; i<vars; i++) {
    if (get_var_mode(axis, i) == 'range') {
      let inp = $($(rows[rows.length-1]).children()[i].children[0]).detach()
      $($(rows[rows.length-2]).children()[i]).html('');
      $($(rows[rows.length-2]).children()[i]).append(inp);
    }
  }
  
  $(rows[rows.length-1]).detach();
}

function remove_sweep(axis) {
  console.log("remove_sweep", axis);
  $("#studyEdit_sweeps").children()[axis].remove()
}

function get_var_mode(axis, variable) {
  let btn = $($($(`.studyEdit_sweeps_table`)[axis]).find('tr')[0].cells[variable]).find(".btn-varmode")
  return $(btn).find(".btn-primary, .btn-danger, .btn-success, .btn-info").html().toLowerCase();
}

function get_var_operation(axis, variable) {
  let btn = $($($(`.studyEdit_sweeps_table`)[axis]).find('tr')[0].cells[variable]).find(".btn-operation")
  return $(btn).find(".btn-primary, .btn-danger, .btn-success, .btn-info").html().toLowerCase();
}

function change_sweep_type(axis, variable) {
  mode = get_var_mode(axis, variable);
  console.log("change_sweep_type", axis, variable, mode)

  let rows = $($(`.studyEdit_sweeps_table`)[axis]).find('tr');
  let vars = rows[0].cells.length-1

  if (mode == 'range') {
    for (let i=2; i<rows.length-1; i++) {
      $($(rows[i]).children()[variable]).html('.');
    }
  } else {
    for (let i=2; i<rows.length-1; i++) {
      $($(rows[i]).children()[variable]).html('');

      let inp  = $(`<a class="editable"></a>`);
      inp.editable({
        type: 'text',
        title: '',
        mode: 'inline',
        toggle: 'click',
        showbuttons: false,
        placeholder: "undefined",
        saveonchange: true,
        emptytext: "unset",
      }).on('shown', function(ev, editable) {
          setTimeout(function() {
              editable.input.$input.select();
          },0);
      });

      $($(rows[i]).children()[variable]).append(inp);
    }
    
  }
}

ppscripts = {
  "points": {
    "run": "[hahaha please fix this run]",
    "lap": "[hahaha please fix this lap]"
  },
  "energy": {
    "run": "please clap",
    "lap": "please lap"
  }
}

function select_postproc_preset(pp) {
  let ppdiv = $($("#studyEdit_postproc").children()[pp]);
  let key = ppdiv.find(".studyEdit_postproc_selectPre").val();
  if (ppscripts[key]) {
    ppdiv.find(".studyEdit_postproc_script_lap").val(ppscripts[key].lap);
    ppdiv.find(".studyEdit_postproc_script_run").val(ppscripts[key].run);
  }
}

function remove_postproc(pp) {
  console.log("remove_postproc", pp);
}

/* Post Processing */
function add_postproc(name, scripts) {
  let i = $("#studyEdit_postproc").children().length;
  let x = $(`<div>
    <div>
      <a class="editable studyEdit_postproc_name" data-type="text"></a>:
      <select class="studyEdit_postproc_selectPre" onchange="select_postproc_preset(parentIdx($(this), 2));">
        <option value="" ${scripts ? '':'selected'}>Select a builtin script...</option>
        <option value="" ${scripts ? 'selected':''}>Custom script</option>
        <option value="points">Points</option>
        <option value="energy">Energy</option>
      </select>
      <button style="float: right;" class="btn btn-danger" onclick="remove_postproc(parentIdx($(this), 2));">Delete Script</button>
    </div>
    <table class="table" style="font-family: monospace">
      <tr>
        <td width="20em">&lambda;(lap):</td>
        <td><textarea class="studyEdit_postproc_script_lap textarea-short" >${scripts ? scripts.lap:''}</textarea></td>
      </tr>
      <tr>
        <td width="20em">&lambda;(run):</td>
        <td><textarea class="studyEdit_postproc_script_run textarea-short" >${scripts ? scripts.run:''}</textarea></td>
      </tr>
    </table>
    <hr/>
    </div>`);
  $("#studyEdit_postproc").append(x);
  x.find(".studyEdit_postproc_name").editable({
      type: 'text',
      title: '',
      mode: 'inline',
      toggle: 'click',
      showbuttons: false,
      placeholder: "UNNAMED FILTER",
      saveonchange: true,
      emptytext: "UNNAMED FILTER",
    }).on('shown', function(ev, editable) {
        setTimeout(function() {
            editable.input.$input.select();
        },0);
    }).editable('setValue', name);
}