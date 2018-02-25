<?php include "../display/head.php"; ?>
<?php
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $errors = '';

    $name =  $_POST['name'];
    if (empty($name)) $errors .= '<script type="text/javascript">alert("Name is required")</script>';

    $email = $_POST['email'];
    if (empty($email)) $errors .= '<script type="text/javascript">alert("Email is required")</script>';
    if (filter_var($email, FILTER_VALIDATE_EMAIL) === false) $errors = '<script type="text/javascript">alert("Please enter a valid email address")</script>';

    $password = $_POST['password'];
    if (empty($password)) $errors .= '<script type="text/javascript">alert("Password is required")</script>';

    $confirm = $_POST['confirmpassword'];
    if (strcmp($password, $confirm) != 0) $errors .= '<script type="text/javascript">alert("Passwords do not match!")</script>';

    if (!empty($errors)) {
        echo '<ul>' . $errors . '</ul>';
    } else {
    	$query = sprintf("SELECT Email FROM User WHERE Email = '%s'", $email);
		$user_exists = mysqli_query($conn, $query);

    	if (mysqli_num_rows($user_exists) > 0) {
        	echo '<script type="text/javascript">alert("A user with your email has already registered")</script>';
		} else {
			$query = sprintf("CALL gen_Register_User('%s', '%s', '%s')", $name, $email, $password);
			mysqli_query($conn, $query) 
				or die(print_r(mysqli_error($conn), true));

        	echo '<script type="text/javascript">alert("Registration successful!"); location.href = "../RoseLap"</script>';

	        $name = '';
	        $email = '';
	    }
    }
    $_SERVER['REQUEST_METHOD'] = 'GET';
}
?>