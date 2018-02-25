<div class="modal fade" id="loginModal">
		<div class="modal-dialog" role="document">
		<div class="modal-content">
			<form id="loginform" action="" method="post" onsubmit="window.location = window.location.href;">
				<div class="modal-header">
					<h5 class="modal-title" id="exampleModalLabel">Log In</h5>
				</div>
	      
		      	<div class="modal-body">
				    <div class="form-group">
					    <label for="email">E-mail</label><br/>
					    <input class="form-control" type="text" maxlength="100" name="email"/><br/>
				    </div>
				    <div class="form-group">
					    <label for="password">Password</label><br/>
					    <input class="form-control" type="password" maxlength="50" name="password" /><br/>
				    </div>
				</div>

				<div class="modal-footer">
					<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
					<button class="btn btn-primary" type="submit">Log In</button>
				</div>
			</form>
		</div>
		</div>
	</div>
</div>


<?php
	if ($_SERVER['REQUEST_METHOD'] == 'POST') {
	    $errors = '';

	    $email = $_POST['email'];
	    if (empty($email) || filter_var($email, FILTER_VALIDATE_EMAIL) === false) {
	    	$errors = '<script type="text/javascript">alert("Please enter a valid email address")</script>';
	    }

	    $password = $_POST['password'];
	    if (empty($password)) $errors .= '<script type="text/javascript">alert("Password is required")</script>';

	    if (!empty($errors)) {
	        echo '<ul>' . $errors . '</ul>';
	    } else {
	    	$query = sprintf("SELECT gen_Login_User('%s', '%s')", $email, $password);
			$logged_in = mysqli_query($conn, $query);
			$user_data = explode("|", mysqli_fetch_row($logged_in)[0]);
			$username = $user_data[0];
			$userID = $user_data[1];

			if ($userID == 0) {
				echo '<script type="text/javascript">alert("Incorrect login information");window.location = window.location.href;</script>';
			} else {
				$_SESSION['userid'] = $userID;
				$_SESSION['username'] = $username;
				echo '<script type="text/javascript">window.location = window.location.href;</script>';
		    }
		}
	}
?>

<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
<script src="js/bootstrap.min.js"></script>

<script type="text/javascript">
	function post_to_element(contents, page, domItem) {
		data = $.ajax({
			'url': page,
			'type': 'POST',
			'data': {'post' : contents},
			'success': function(data) {
				console.log(data);
				document.getElementById(domItem).innerHTML = data;
			},
			'error': function(data) {
				console.log('Something awful happened');
				console.log(data);
			}
		});
	}
	function my_post(contents, page, onSuccess) {
		d = $.ajax({
			'url': page,
			'type': 'POST',
			'data': {'post' : contents},
			'success': function(data) {
				console.log(data);
				onSuccess(data);
			},
			'error': function(data) {
				console.log('Something awful happened');
				console.log(data);
			}
		});
	}
</script>