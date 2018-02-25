<?php include "display/head.php"; ?>

<!DOCTYPE html>
<html>
<head>
<title>Register</title>
</head>
<body>
<?php include 'display/nav.php' ?>
<div class="container">
<br>
<h1>Register</h1>

<form action="post/registeruser.php" method="post">
	<div class="form-group">
	    <label for="name">Name</label><br/>
	    <input class="form-control" type="text" name="name" maxlength="50"/><br/>
    </div>

    <div class="form-group">
	    <label for="email">E-mail</label><br/>
	    <input class="form-control" type="text" name="email" maxlength="100"/><br/>
    </div>

    <div class="form-group">
	    <label for="password">Password</label><br/>
	    <input class="form-control" type="password" maxlength="50" name="password" /><br/>
    </div>

    <div class="form-group">
	    <label for="confirmpassword">Confirm Password</label><br/>
	    <input class="form-control" type="password" maxlength="50" name="confirmpassword"/><br/>
    </div>
    <button type="submit" class="btn btn-primary">Register</button>
</form>

</div>

<?php include "display/foot.php"; ?>
