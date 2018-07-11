<?php include "../display/head.php"; ?>
<?php  
	$errors = '';

	if (empty($_POST['newName']) && empty($_POST['editName'])) $errors .= '<script type="text/javascript">alert("Name is required")</script>';
	
	if (!empty($errors)) {
        echo $errors;
    } else {
		if (isset($_POST['pastName'])) {
			$past = $_POST['pastName'];
		    $name = $_POST['editName'];
			$text = $_POST['editText'];
			$text = str_replace("'", "''", $text);

	    	$query = sprintf("CALL con_Edit_Vehicle_Config('%s', %s, '%s', '%s')", $past, $_SESSION['userid'], $name, $text);
	    	$edit = mysqli_query($conn, $query);
		}

		header("Location: ../secretpage.php");
	}
?>