<?php
	include "../display/head.php";
	$query = sprintf("SELECT VehicleText FROM vehicle_config WHERE Name = '%s'", $_POST['post']);
	$text = mysqli_fetch_array(mysqli_query($conn, $query))[0];
	echo($text);
?>