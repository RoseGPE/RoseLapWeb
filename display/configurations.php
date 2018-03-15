<div class="container">
<div class = "table-container">
<table class="table">
<thead>
<tr>
<th class="col-xs-2">Configuration Name</th>
<th class="col-xs-2">Date Created</th>
<th class="col-xs-2">Created By</th>
<th class="col-xs-2">Last Edited By</th>
<th class="col-xs-2">Last Edited On</th>
</tr>
</thead>
<tbody>
<?php
	$query = "SELECT * FROM Batch_Config_View";
	$config_table = mysqli_query($conn, $query);

	while ($row = mysqli_fetch_array($config_table)) {
		echo "<tr>";
		echo "<td class=\"col-xs-2\">
				<a href=\"#\" onclick=\"launchBatchEditModal('" . $row[0] . "')\">". $row[0] . "</a>
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
	<button type="button" class="btn btn-secondary" data-toggle="modal" data-target="#addConfigModal">Add Configuration</button>
</div>

<div class="modal fade" id="addConfigModal">
	<div class="modal-dialog modal-lg" role="document">
		<div class="modal-content">
			<form id="addConfigForm" action="post/addconfig.php" method="post">
				<div class="modal-header">
					<h5 class="modal-title">Add Configuration</h5>
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

<div class="modal fade" id="editConfigModal">
	<div class="modal-dialog modal-lg" role="document">
		<div class="modal-content">
			<form id="editConfigForm" action="post/saveandrun.php" method="post" onsubmit="window.location = window.location.href;">
				<div class="modal-header">
					<h5 class="modal-title">Edit Configuration</h5>
				</div>
	      
		      	<div class="modal-body">
				    <div class="form-group">
					    <label for="editName">Name</label><br/>
					    <input class="form-control" type="text" maxlength="50" name="editName" id="editName"/><br/>
					    <input class="form-control" type="hidden" maxlength="50" name="pastName" id="pastName"/><br/>

					    <label for="editText">Text</label><br/>
					    <textarea class="form-control" rows="30" name="editText" id="editText"></textarea><br/>
				    </div>
				</div>

				<div class="modal-footer">
					<button type="button" class="btn btn-secondary" data-dismiss="modal">Cancel</button>
					<button class="btn btn-primary" name="justsave" type="submit">Save</button>
					<button class="btn btn-primary" name="run" type="submit">Save and Run</button>
				</div>
			</form>
		</div>
	</div>
</div>

</div>

<style type="text/css">
	.table-container {
		height: 400px;
		overflow-y: auto;
	}

	#editText {
		font-family: monospace;
	}
</style>

<script type="text/javascript">
	function launchBatchEditModal(batchName) {
		my_post(batchName, 'post/getBCText.php', function(text) {
			document.getElementById("editName").value = batchName;
			document.getElementById("pastName").value = batchName;
			document.getElementById("editText").value = text;
			$('#editConfigModal').modal('show');
		});
	}
</script>