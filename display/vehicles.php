<div class="container">
<div class = "table-container">
<table class="table">
<thead>
<tr>
<th class="col-xs-2">Vehicle Name</th>
<th class="col-xs-2">Date Created</th>
<th class="col-xs-2">Created By</th>
<th class="col-xs-2">Last Edited By</th>
<th class="col-xs-2">Last Edited On</th>
</tr>
</thead>
<tbody>
<?php
	$query = "SELECT * FROM Vehicle_Config_View";
	$config_table = mysqli_query($conn, $query);

	while ($row = mysqli_fetch_array($config_table)) {
		echo "<tr>";
		echo "<td class=\"col-xs-2\">
				<a href=\"#\" onclick=\"launchVehicleEditModal('" . $row[0] . "')\">". $row[0] . "</a>
		 	  </td>";
		echo "<td class=\"col-xs-2\">". $row[1] . "</td>";
		echo "<td class=\"col-xs-2\">". $row[2] . "</td>";
		echo "<td class=\"col-xs-2\">". $row[3] . "</td>";
		echo "<td class=\"col-xs-2\">". $row[4] . "</td>";
		echo "</tr>";
	}
?>
</tbody>
</table>
</div>

<br>
<div class="btn-group" role="group">
	<button type="button" class="btn btn-secondary" data-toggle="modal" data-target="#addVehicleModal">Add Vehicle</button>
</div>

<div class="modal fade" id="addVehicleModal">
	<div class="modal-dialog modal-lg" role="document">
		<div class="modal-content">
			<form id="addVehicleForm" action="post/addvehicle.php" method="post">
				<div class="modal-header">
					<h5 class="modal-title">Add Vehicle</h5>
				</div>
	      
		      	<div class="modal-body">
				    <div class="form-group">
					    <label for="newName">Name</label><br/>
					    <input class="form-control" type="text" maxlength="50" name="newName"/><br/>

					    <label for="newText">Text</label><br/>
					    <textarea class="form-control" rows="30" name="newText"></textarea><br/>
				    </div>
				</div>

				<div class="modal-footer">
					<button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
					<button class="btn btn-primary" type="submit">Add</button>
				</div>
			</form>
		</div>
	</div>
</div>

<div class="modal fade" id="editVehicleModal">
	<div class="modal-dialog modal-lg" role="document">
		<div class="modal-content">
			<form id="editVehicleForm" action="post/editVehicle.php" method="post" onsubmit="window.location = window.location.href;">
				<div class="modal-header">
					<h5 class="modal-title">Edit Vehicle</h5>
				</div>
	      
		      	<div class="modal-body">
				    <div class="form-group">
					    <label for="editName">Name</label><br/>
					    <input class="form-control" type="text" maxlength="50" name="editName" id="editNameV"/><br/>
					    <input class="form-control" type="hidden" maxlength="50" name="pastName" id="pastNameV"/><br/>

					    <label for="editText">Text</label><br/>
					    <textarea class="form-control mono-box" rows="30" name="editText" id="editTextV"></textarea><br/>
				    </div>
				</div>

				<div class="modal-footer">
					<button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
					<button class="btn btn-primary" type="submit">Save</button>
				</div>
			</form>
		</div>
	</div>
</div>

</div>

<script type="text/javascript">
	function launchVehicleEditModal(vName) {
		my_post(vName, 'post/getVehicleText.php', function(text) {
			document.getElementById("editNameV").value = vName;
			document.getElementById("pastNameV").value = vName;
			document.getElementById("editTextV").value = text;
			$('#editVehicleModal').modal('show');
		});
	}
</script>