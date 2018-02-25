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
			echo "<h3>Configurations</h3><br>";
			include "display/configurations.php";
		} else {
			echo "Please make sure to log in";
		}
	?>
<?php include "display/foot.php"; ?>