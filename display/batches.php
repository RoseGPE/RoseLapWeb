<div class="container">
<div class = "table-container">
<table class="table">
<thead>
<tr>
<th class="col-xs-2">Batch Name</th>
<th class="col-xs-2">Submit Time</th>
<th class="col-xs-2">Batcher</th>
<th class="col-xs-2">Status</th>
<th class="col-xs-2">Complete Time</th>
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
		echo "<td class=\"col-xs-2\"><a href='". $row[6] . "'>View</a></td>";
		echo "</tr>";
	}
?>
</tbody>
</table>
</div>
</div>