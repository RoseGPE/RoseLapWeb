<?php include "display/head.php"; ?>

<!DOCTYPE html>
<html>
<head>
<title>RoseLap Web</title>
</head>
<body>
<?php include 'display/nav.php' ?>
<div class="container">
	<br>
	<h1><?php if ($loggedin) echo "Hi, " . $_SESSION['username']; ?></h1>
	<h2>Welcome to RoseLap</h2>
	<hr>

	<?php  
		if ($loggedin) {
			echo "Yeah there's nothing here";
		} else {
			echo "Please make sure to log in";
		}
	?>
<?php include "display/foot.php"; ?>