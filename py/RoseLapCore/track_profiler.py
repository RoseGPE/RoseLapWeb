import sims
import input_processing.vehicle as ipvehicle
import input_processing.fancyyaml as yaml
import input_processing.track_segmentation as trackseg
import plottools
import input_processing.ip_logic as ip_logic
import batcher
import numpy as np

# a = ip_logic.process_input('test_batch_local.yaml')
# conf_tests, conf_vehicle, tracks, model, out = a
# b = batcher.batch(conf_tests, conf_vehicle, tracks, model, out)

for track in ['acceleration.dxf','mi_2018_autox.svg','mi_2018_endurance.svg','ne_2015_autox.svg','ne_2015_endurance.svg','skidpad_loop.dxf','skidpad_start.dxf']:
	times = []
	gears = np.arange(1.0,6.0,0.2)
	for gr in gears:
		segments = trackseg.file_to_segments('params/tracks/'+track,0.2)

		sim = sims.Simulation("one_tire");

		vehicle  = ipvehicle.Vehicle(yaml.load(open('params/vehicles/SUPERCAR.yaml','r'),True))
		vehicle.final_drive_reduction = gr
		vehicle.prep()

		output = sim.solve(vehicle, segments)
		# plottools.plot_velocity_and_events(output,'t',st)
		times.append((track,output[-1,sims.O_TIME],gr))
		print('\t%s: %.3f s, gr=%.2f' % times[-1])
	print('Best time for %s was %.3f at fdr=%.2f' % min(times, key=lambda x:x[1]))