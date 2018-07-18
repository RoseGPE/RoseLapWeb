import fancyyaml
import track_segmentation
import vehicle
import sims
import io

def process_input(config_filename):

	# load the config file
	with open('./params/batcher_config/' + config_filename) as data:
		conf = fancyyaml.load(data, True)

	tracks = [process_track(x, "./params/tracks/") for x in conf.tracks]
	model = sims.Simulation(conf.model)
	out = (conf.filename, conf.data_percentage)

	return (conf.tests, conf.vehicle, tracks, model, out)

def process_web_config(config_text):
	config_stream = io.StringIO(config_text)
	conf = fancyyaml.load(config_stream, False)
	config_stream.close()

	return conf

def process_web_input(conf):
	vehicle_stream = io.StringIO(conf.vehicle)
	conf.vehicle = vehicle.Vehicle(fancyyaml.load(vehicle_stream, False))
	vehicle_stream.close()

	for x in conf.tracks:
		x.name = x.file
		x.file = x.path

	tracks = [process_track(x) for x in conf.tracks]
	model = sims.Simulation(conf.model)
	out = (conf.filename, conf.data_percentage)

	return (conf.tests, conf.vehicle, tracks, model, out)

def process_track(x, pre=""):
	if x.point_formula == "endurance":
		mins = (x.min_time, x.min_co2)
	else:
		mins = (x.min_time, 0.0)
	return (pre + x.file, x.segment_distance, x.steady_state, x.name, x.point_formula, mins)
