<div class="container">
<div class = "table-container">
<table class="table">
<thead>
<tr>
<th class="col-xs-2">Track Name</th>
<th class="col-xs-2">Date Uploaded</th>
<th class="col-xs-2">Uploaded By</th>
<th class="col-xs-2">Additional Info</th>
</tr>
</thead>
<tbody>
<?php
	$query = "SELECT * FROM Track_Config_View";
	$config_table = mysqli_query($conn, $query);

	while ($row = mysqli_fetch_array($config_table)) {
		echo "<tr>";
		echo "<td class=\"col-xs-2\">". $row[0] . "</td>";
		echo "<td class=\"col-xs-2\">". $row[1] . "</td>";
		echo "<td class=\"col-xs-2\">". $row[2] . "</td>";
		echo "<td class=\"col-xs-2\">". $row[3] . "</td>";
		echo "</tr>";
	}
?>
</tbody>
</table>
</div>

<br>
<div class="btn-group" role="group">
	<button type="button" class="btn btn-secondary" data-toggle="modal" data-target="#addTrackModal">Add Track</button>
</div>

<div class="modal fade" id="addTrackModal">
	<div class="modal-dialog" role="document">
		<div class="modal-content">
			<form id="addTrackForm" action="post/addtrack.php" method="post">
				<div class="modal-header">
					<h5 class="modal-title">Add Track</h5>
				</div>
	      
		      	<div class="modal-body">
				    <div class="form-group">
					    <label for="name">Name</label><br/>
					    <input class="form-control" type="text" maxlength="50" name="name"/><br/>

					    <label for="path">Path to File</label><br/>
					    <textarea class="form-control" rows="4" maxlength="255" name="path"></textarea><br/>
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

</div>