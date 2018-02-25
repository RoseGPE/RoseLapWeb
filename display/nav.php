<link rel="stylesheet" type="text/css" href="css/col-bootstrap.min.css">
<nav class="navbar sticky-top navbar-toggleable-md navbar-light bg-faded">
	<button class="navbar-toggler navbar-toggler-right" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
		<span class="navbar-toggler-icon"></span>
	</button>

	<a class="navbar-brand" href="/RoseLap">RoseLap Web</a>

	<div class="collapse navbar-collapse" id="navbarSupportedContent">
		<ul class="navbar-nav mr-auto">
			<li class="nav-item">
				<a class="nav-link" href="/RoseLap">Home</a>
			</li>
			<?php  
				if ($loggedin) {
					echo '<li class="nav-item"><a class="nav-link" href="/RoseLap" onclick="my_post(null, \'logout.php\')">Log Out</a></li>';
				} else {
					echo '<li class="nav-item"><a class="nav-link" href="/RoseLap/register.php">Register</span></a></li>';
					echo '<li class="nav-item"><a class="nav-link" href="/RoseLap" data-toggle="modal" data-target="#loginModal">Log In</a></li>';
				}
			?>
		</ul>
	</div>
</nav>