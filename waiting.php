<?php include "display/head.php"; ?>

<!DOCTYPE html>
<html>
<head>
<title>RoseLap Web</title>
</head>
<body>
<?php include 'display/nav.php' ?>
<div class="container">

	<?php  
		if ($loggedin) {
			echo "Yeah there's nothing here";
			include 'display/emailwhendone.php';
		} else {
			echo "Please make sure to log in";
		}
	?>
<?php include "display/foot.php"; ?>