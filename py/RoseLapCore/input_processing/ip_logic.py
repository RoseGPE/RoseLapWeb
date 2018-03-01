import fancyyaml
import track_segmentation
import vehicle
import sims

def process_input(config_filename):

	# load the config file
	with open('./params/batcher_config/' + config_filename) as data:
		conf = fancyyaml.load(data)

	tracks = [(track_segmentation.dxf_to_segments(x.dxf, x.segment_distance), x.steady_state, x.dxf) for x in conf.tracks]
	model = sims.Simulation(conf.model)
	out = (conf.filename, conf.data_percentage)

	return (conf.tests, conf.vehicle, tracks, model, out)