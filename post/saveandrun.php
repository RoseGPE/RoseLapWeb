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
			$text = str_replace("'", "''", $text);

	    	$query = sprintf("CALL con_Edit_Batch_Config('%s', %s, '%s', '%s')", $past, $_SESSION['userid'], $name, $text);
	    	$edit = mysqli_query($conn, $query);
		}

		if (isset($_POST["run"])) {
			$query = sprintf("SELECT run_Queue_Batch_Run(%s, '%s')", $_SESSION['userid'], $name);
	    	$run = mysqli_query($conn, $query);

	    	while ($data = mysqli_fetch_array($run)) {
	    		$row = explode(".", $data[0]);
	    			    	var_dump($row);


	    		$WshShell = new COM("WScript.Shell");
				$oExec = $WshShell->Run("python c:/wamp/www/RoseLap/py/RoseLapCore/webrunner.py " . $row[0] . " " . $row[1], 0, false);
				//file_put_contents("c:/wamp/www/RoseLap/py/RoseLapCore/pylog.txt", $oExec, FILE_APPEND);
		    }

			header("Location: ../");
			die();
		}

		header("Location: ../");
	}
?>