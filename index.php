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
	<h2><?php if ($loggedin) echo "Hi, " . $_SESSION['username']; ?></h2>
	<h2>Welcome to RoseLap</h2>
	<hr>

	<?php  
		if ($loggedin) {
			echo "<h3>Batches</h3><br>";
			include "display/batches.php";
			echo "<br><h3>Configurations</h3><br>";
			include "display/configurations.php";
			echo "<br><h3>Vehicles</h3><br>";
			include "display/vehicles.php";
			echo "<br><h3>Tracks</h3><br>";
			include "display/tracks.php";
		} else {
			echo "Please make sure to log in";
		}
	?>
	<br>
	<br>
	<br>
<?php include "display/foot.php"; ?>

<style type="text/css">
	.table-container {
		display: block;
		max-height: 400px;
		overflow-y: auto;
	}

	.mono-box {
		font-family: monospace;
	}
</style>