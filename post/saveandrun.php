<?php include "../display/head.php"; ?>
<?php  
	$errors = '';

	if (empty($_POST['newName']) && empty($_POST['editName'])) $errors .= '<script type="text/javascript">alert("Name is required")</script>';
	
	if (!empty($errors)) {
        echo $errors;
    } else {
    	$name = isset($_POST['configname']) ? $_POST['configname'] : "iamnotreal";

		if (isset($_POST['pastName'])) {
			$past = $_POST['pastName'];
		    $name = $_POST['editName'];
			$text = $_POST['editText'];

	    	$query = sprintf("CALL con_Edit_Batch_Config('%s', %s, '%s', '%s')", $past, $_SESSION['userid'], $name, $text);
	    	$edit = mysqli_query($conn, $query);
	    	echo "ey";
		}

		if (isset($_POST["run"])) {
			// set up run
			// run the run
			// go to waiting page and send runid
			header("Location: ../waiting.php");
		}

		header("Location: ../secretpage.php");
	}
?>