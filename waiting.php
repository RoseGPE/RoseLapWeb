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
			echo "Congrats you ran a batch configuration! This might take a while. Or not.";
		} else {
			echo "Please make sure to log in";
		}
	?>
<?php include "display/foot.php"; ?>
<script type="text/javascript">
	
</script>