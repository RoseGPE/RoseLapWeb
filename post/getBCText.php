<?php
	include "../display/head.php";
	$query = sprintf("SELECT BCText FROM batch_config WHERE Name = '%s'", $_POST['post']);
	$text = mysqli_fetch_array(mysqli_query($conn, $query))[0];
	echo($text);
?>