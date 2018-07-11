<?php
	$conn = mysqli_connect("localhost", "rlapp", "gottagofast", "roselap");
	///echo "Debug info:<br />";
	if (!$conn) {
	    die("Ruh roh");
	}
	//echo "Success: A proper connection to MySQL was made! ";

	session_start();
	$loggedin = false;

	if(isset($_SESSION['userid']) && !empty($_SESSION['userid'])) {
		$loggedin = true;
	} else if ($_SERVER['REQUEST_URI'] == '/RoseLap/register.php' ||
				$_SERVER['REQUEST_URI'] == '/RoseLap/post/registeruser.php') {
		$loggedin = true;
	} else {
		//echo "Not logged in";
	}

	if (!$loggedin) {
		include 'nav.php';
		include 'foot.php';
		die('<title>RoseLap Web</title><div class="container">You do not have access to this page. Please register or log in as a user who can access this page.');
	}
?>