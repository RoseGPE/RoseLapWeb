<div class="container">
<div class = "table-container">
<table class="table">
<thead>
<tr>
<th class="col-xs-2">Batch Name</th>
<th class="col-xs-2">Submit Time</th>
<th class="col-xs-2">Batcher</th>
<th class="col-xs-1">Status</th>
<th class="col-xs-2">Complete Time</th>
<th class="col-xs-1">Logs</th>
<th class="col-xs-2">Results</th>
</tr>
</thead>
<tbody>
<?php
	$query = "SELECT * FROM Batch_Run_View";
	$config_table = mysqli_query($conn, $query);

	while ($row = mysqli_fetch_array($config_table)) {
		echo "<tr>";
		echo "<td class=\"col-xs-2\">". $row[0] . "</td>";
		echo "<td class=\"col-xs-2\">". $row[1] . "</td>";
		echo "<td class=\"col-xs-2\">". $row[2] . "</td>";
		echo "<td class=\"col-xs-2\">". $row[3] . "</td>";
		echo "<td class=\"col-xs-2\">". $row[4] . "</td>";
		if ($row[6] != "") {
			echo "<td class=\"col-xs-2\"><a target=\"_blank\" href='". $row[6] . "'>Log</a></td>";
		} else {
			echo "<td class=\"col-xs-2\"></td>";
		}
		if ($row[7] != "") {
			echo "<td class=\"col-xs-2\"><a target=\"_blank\" href='". $row[7] . "'>Dashboard</a></td>";
		} else {
			echo "<td class=\"col-xs-2\"></td>";
		}
		echo "</tr>";
	}
?>
</tbody>
</table>
</div>
</div>