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
		}

		if (isset($_POST["run"])) {
			$query = sprintf("CALL run_Queue_Batch_Run(%s, '%s')", $_SESSION['userid'], $name);
	    	$run = mysqli_query($conn, $query);

	    	if ($run) {
	    		$WshShell = new COM("WScript.Shell");
				$oExec = $WshShell->Run("python c:/wamp/www/RoseLap/py/RoseLapCore/webrunner.py", 0, false);
	    	}

			header("Location: ../waiting.php");
			die();
		}

		header("Location: ../secretpage.php");
	}
?>