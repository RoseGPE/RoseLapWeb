<?php include "../display/head.php"; ?>
<?php  
	$errors = '';

	if (empty($_POST['newName']) && empty($_POST['editName'])) $errors .= '<script type="text/javascript">alert("Name is required")</script>';
	
	if (!empty($errors)) {
        echo $errors;
    } else {
		if (!empty($_POST['newName'])) {
			$name = $_POST['newName'];
			$text = $_POST['newText'];

	    	$query = sprintf("CALL con_Add_Vehicle_Config(%s, '%s', '%s')", $_SESSION['userid'], $name, $text);
	    	$insert = mysqli_query($conn, $query);

			header("Location: ../secretpage.php");
		}
	}
?>