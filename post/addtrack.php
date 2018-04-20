<?php include "../display/head.php"; ?>
<?php  
	$errors = '';

	if (empty($_POST['name']) && empty($_POST['path'])) $errors .= '<script type="text/javascript">alert("Name and path are required")</script>';
	
	if (!empty($errors)) {
        echo $errors;
    } else {
		if (!empty($_POST['name'])) {
			$name = $_POST['name'];
			$path = $_POST['path'];

	    	$query = sprintf("CALL con_Add_Track_Config(%s, '%s', '%s')", $_SESSION['userid'], $name, $path);
	    	$insert = mysqli_query($conn, $query);

			header("Location: ../secretpage.php");
		}
	}
?>