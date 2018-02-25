<?php 
	if ($_POST) {
		include 'display/head.php';
		session_unset(); 
		session_destroy();
		header('Location: ../RoseLap');
		die();
	}
?>