<?php
	$conn = mysqli_connect("localhost", "rlapp", "gottagofast", "roselap");
	///echo "Debug info:<br />";
	if (!$conn) {
	    die("Ruh roh");
	}
	//echo "Success: A proper connection to MySQL was made! ";

	session_start();
	$loggedin = false;

	if(isset($_SESSION['userid']) && !empty($_SESSION['userid'])) {
		$loggedin = true;
		//echo "Someone is logged in: User #" . $_SESSION['userid'];
	} else if ($_SERVER['REQUEST_URI'] == '/RoseLap/register.php') {
		//echo "yes this is where register";
		$loggedin = true;
	} else {
		//echo "Not logged in";
	}

	if (!$loggedin) {
		include 'nav.php';
		include 'foot.php';
		die('<title>RoseLap Web</title><div class="container">You do not have access to this page. Please register or log in as a user who can access this page.');
	}
?><link rel="stylesheet" type="text/css" href="../../css/col-bootstrap.min.css"><link rel="stylesheet" type="text/css" href="css/col-bootstrap.min.css">
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
</nav><div class="container"><div class="row"><div class="col-sm-6">Map view coming (not that) soon!</div><div class="col-sm-6"><!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <link href="https://www.highcharts.com/highslide/highslide.css" rel="stylesheet" />
        <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
        <script type="text/javascript" src="https://code.highcharts.com/highcharts.js"></script>
        <script type="text/javascript" src="https://code.highcharts.com/highcharts-more.js"></script>
        <script type="text/javascript" src="https://code.highcharts.com/modules/heatmap.js"></script>
        <script type="text/javascript" src="https://code.highcharts.com/modules/exporting.js"></script>
    </head>
    <body style="margin:0;padding:0">
                <div id="container" style="width:500px;height:500px;">Loading....</div>


    <script>
        $(function(){





            Highcharts.setOptions({"lang": {}, "global": {}});
            var option = {"loading": {}, "subtitle": {}, "xAxis": {"categories": ["500.0", "520.0", "540.0", "570.0", "600.0", "640.0"], "title": {"text": "'mass'"}}, "title": {"text": "acceleration Track Times: 'mass' vs. 'shift_time'"}, "series": {}, "labels": {}, "chart": {"width": 500, "renderTo": "container", "marginTop": 40, "marginBottom": 80, "type": "heatmap", "plotBorderWidth": 1, "height": 500}, "tooltip": {"style": {"padding": 0, "pointerEvents": "auto"}, "formatter": function() {
                                return this.point.value +
                                '<br><a style="color:blue; text-decoration:underline;" target="_blank" href="testtest-acceleration/' + parseInt(this.point.x) + '-' + parseInt(this.point.y) + '.html">details</a>';
                            }}, "plotOptions": {}, "yAxis": {"categories": ["0.0", "0.05", "0.1", "0.15", "0.2"], "title": {"text": "'shift_time'"}}, "credits": {"enabled": false}, "colors": {}, "pane": {}, "exporting": {}, "drilldown": {}, "navigation": {}, "legend": {"symbolHeight": 280, "layout": "vertical", "y": 25, "verticalAlign": "top", "align": "right", "margin": 0}, "colorAxis": {"max": 4.731679765287418, "maxColor": "#FF2ECC", "minColor": "#E0FF4F", "min": 4.058923288548023}};


 

            var chart = new Highcharts.Chart(option);

            var data = [{"data": [[0, 0, 4.058923288548023], [0, 1, 4.130655400264617], [0, 2, 4.207501741820547], [0, 3, 4.283608271089042], [0, 4, 4.360454612644977], [1, 0, 4.113486226628168], [1, 1, 4.185169550264306], [1, 2, 4.261963217390756], [1, 3, 4.338017959481677], [1, 4, 4.414811626608168], [2, 0, 4.168459212604322], [2, 1, 4.240213072165111], [2, 2, 4.315268687104541], [2, 3, 4.393205577211246], [2, 4, 4.468261192150662], [3, 0, 4.250808371139948], [3, 1, 4.32262728336439], [3, 2, 4.399573267462336], [3, 3, 4.475777529678797], [3, 4, 4.551722130652944], [4, 0, 4.332812442003002], [4, 1, 4.404646304804647], [4, 2, 4.481607236332387], [4, 3, 4.556911371121916], [4, 4, 4.630477077747336], [5, 0, 4.441930287456479], [5, 1, 4.513647489021624], [5, 2, 4.588996089373802], [5, 3, 4.661224403275084], [5, 4, 4.731679765287418]], "type": "heatmap", "name": "Track Times"}];
            var dataLen = data.length;
            for (var ix = 0; ix < dataLen; ix++) {
                chart.addSeries(data[ix]);
            }
 







        
    });
        </script>

    </body>
</html><!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <link href="https://www.highcharts.com/highslide/highslide.css" rel="stylesheet" />
        <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
        <script type="text/javascript" src="https://code.highcharts.com/highcharts.js"></script>
        <script type="text/javascript" src="https://code.highcharts.com/highcharts-more.js"></script>
        <script type="text/javascript" src="https://code.highcharts.com/modules/heatmap.js"></script>
        <script type="text/javascript" src="https://code.highcharts.com/modules/exporting.js"></script>
    </head>
    <body style="margin:0;padding:0">
                <div id="container" style="width:500px;height:500px;">Loading....</div>


    <script>
        $(function(){





            Highcharts.setOptions({"lang": {}, "global": {}});
            var option = {"loading": {}, "subtitle": {}, "xAxis": {"categories": ["500.0", "520.0", "540.0", "570.0", "600.0", "640.0"], "title": {"text": "'mass'"}}, "title": {"text": "skidpad_loop Track Times: 'mass' vs. 'shift_time'"}, "series": {}, "labels": {}, "chart": {"width": 500, "renderTo": "container", "marginTop": 40, "marginBottom": 80, "type": "heatmap", "plotBorderWidth": 1, "height": 500}, "tooltip": {"style": {"padding": 0, "pointerEvents": "auto"}, "formatter": function() {
                                return this.point.value +
                                '<br><a style="color:blue; text-decoration:underline;" target="_blank" href="testtest-skidpad_loop/' + parseInt(this.point.x) + '-' + parseInt(this.point.y) + '.html">details</a>';
                            }}, "plotOptions": {}, "yAxis": {"categories": ["0.0", "0.05", "0.1", "0.15", "0.2"], "title": {"text": "'shift_time'"}}, "credits": {"enabled": false}, "colors": {}, "pane": {}, "exporting": {}, "drilldown": {}, "navigation": {}, "legend": {"symbolHeight": 280, "layout": "vertical", "y": 25, "verticalAlign": "top", "align": "right", "margin": 0}, "colorAxis": {"max": 4.878539977719463, "maxColor": "#FF2ECC", "minColor": "#E0FF4F", "min": 4.657960345685294}};


 

            var chart = new Highcharts.Chart(option);

            var data = [{"data": [[0, 0, 4.657960345685294], [0, 1, 4.6608445886399785], [0, 2, 4.667798568364315], [0, 3, 4.67482871933143], [0, 4, 4.681783628808266], [1, 0, 4.68441322315077], [1, 1, 4.690627411439437], [1, 2, 4.697535846061375], [1, 3, 4.704381856345589], [1, 4, 4.711299872188315], [2, 0, 4.713636366863667], [2, 1, 4.719720868991718], [2, 2, 4.730460793129377], [2, 3, 4.733262960958842], [2, 4, 4.740031482468197], [3, 0, 4.760513459677727], [3, 1, 4.762424171856628], [3, 2, 4.769082914717137], [3, 3, 4.77567858902039], [3, 4, 4.782300100574503], [4, 0, 4.798552245430104], [4, 1, 4.804402720030693], [4, 2, 4.810807749930753], [4, 3, 4.81734792893988], [4, 4, 4.823812522445145], [5, 0, 4.853078997232477], [5, 1, 4.8589647986738544], [5, 2, 4.865442353955683], [5, 3, 4.871989448849662], [5, 4, 4.878539977719463]], "type": "heatmap", "name": "Track Times"}];
            var dataLen = data.length;
            for (var ix = 0; ix < dataLen; ix++) {
                chart.addSeries(data[ix]);
            }
 







        
    });
        </script>

    </body>
</html></div></div><div><pre><div class="col-sm-6"><div><pre>Dashboard ID: testtest
Model: point_mass
Axes: 2
Tracks: ['acceleration.dxf', 'skidpad_loop.dxf']Vehicle parameters: 
{'brake_bias': 0.5,
 'cg_height': 0.8,
 'co2_factor': 2.31,
 'cp_bias': 0.7,
 'cp_height': 0.9,
 'downforce_35mph': 65.0,
 'drag_35mph': 0.0,
 'e_factor': 2271700.0,
 'engine_reduction': 2.81,
 'engine_rpms': [3500.0, 4500.0, 5500.0, 6500.0, 7500.0, 8500.0, 9500.0],
 'engine_torque': [24.3, 26.2, 27.4, 26.5, 25.5, 23.8, 23.9],
 'final_drive_reduction': 2.7692,
 'g': 32.2,
 'gears': [2.416, 1.92, 1.562, 1.277, 1.05],
 'mass': 550.0,
 'mu': 2.0,
 'perfect_brake_bias': 0.0,
 'shift_time': 0.2,
 'tire_radius': 0.75,
 'weight_bias': 0.55,
 'wheelbase_length': 5.1666667}</pre></div></div></pre></div></div>