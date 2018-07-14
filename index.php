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
	<br>
	<br>
	<img src="display/logo.png" width="1100">
	<br>
	<br>
	<br>
	<br>

	<?php  
		if ($loggedin) {
			echo '
				<ul class="nav nav-tabs">
				  <li class="nav-item">
				    <a class="nav-link active" data-toggle="tab" href="#home">Batch History</a>
				  </li>
				  <li class="nav-item">
				    <a class="nav-link" data-toggle="tab" href="#menu1">Batch Configurations</a>
				  </li>
				  <li class="nav-item">
				    <a class="nav-link" data-toggle="tab" href="#menu2">Vehicles</a>
				  </li>
				  <li class="nav-item">
				    <a class="nav-link" data-toggle="tab" href="#menu3">Tracks</a>
				  </li>
				</ul>

				<div class="tab-content">
				  <div class="tab-pane container active" id="home">';
			echo "<br>Here is where you'll find the history of batches run by everyone. To run a batch, click on its configuration and hit 'Save and Run'<br><br>";
			include "display/batches.php";
			echo '</div>
				  <div class="tab-pane container fade" id="menu1">';
			echo "<br>These are all the batch configuration files put together by your team. Use <a target=\"_blank\" href=\"https://codebeautify.org/yaml-validator\">this syntax checker</a> to make sure your configuration will run.<br><br>";
			include "display/configurations.php";
			echo '</div>
				  <div class="tab-pane container fade" id="menu2">';
			echo "<br>These are all the vehicle configuration files put together by your team. Use <a target=\"_blank\" href=\"https://codebeautify.org/yaml-validator\">this syntax checker</a> to make sure your configuration will run.<br><br>";
			include "display/vehicles.php";
			echo '</div>
				  <div class="tab-pane container fade" id="menu3">';
			echo "<br>These are all the tracks you can reference in your configuration files. Make sure the path is an absolute path somewhere on the COMPENSATOR.<br><br>";
			include "display/tracks.php";
			echo '</div>
				</div>
			';

			// echo "<h3>Batch History</h3>";
			// echo "Here is where you'll find the history of batches run by everyone. To run a batch, click on its configuration and hit 'Save and Run'<br><br>";
			// include "display/batches.php";
			// echo "<br><h3>Batch Configurations</h3>";
			// echo "These are all the batch configuration files put together by your team. Use <a target=\"_blank\" href=\"https://codebeautify.org/yaml-validator\">this syntax checker</a> to make sure your configuration will run.<br><br>";
			// include "display/configurations.php";
			// echo "<br><h3>Vehicles</h3>";
			// echo "These are all the vehicle configuration files put together by your team. Use <a target=\"_blank\" href=\"https://codebeautify.org/yaml-validator\">this syntax checker</a> to make sure your configuration will run.<br><br>";
			// include "display/vehicles.php";
			// echo "<br><h3>Tracks</h3>";
			// echo "These are all the tracks you can reference in your configuration files. Make sure the path is an absolute path somewhere on the COMPENSATOR.<br><br>";
			// include "display/tracks.php";
		} else {
			echo "Please make sure to log in";
		}
	?>
	<br>
	<br>
	<br>
<?php include "display/foot.php"; ?>

<style type="text/css">
/*	.table-container {
		display: block;
		max-height: 400px;
		overflow-y: auto;
	}*/

	.mono-box {
		font-family: monospace;
	}
</style>