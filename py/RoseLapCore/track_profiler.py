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

models = ["ss_one_tire","ss_two_tires","ss_four_tires"]
tracks = [
	'skidpad_loop.dxf',
	'acceleration.dxf',
	'mi_2017_autox.dxf',
	'mi_2017_endurance.dxf',
	'mi_2018_autox.dxf',
	'mi_2018_endurance.dxf',
	'ne_2013_autox.dxf',
	'ne_2013_endurance.dxf',
	'ne_2015_autox.dxf',
	'ne_2015_endurance.dxf']
dl = 0.5
times = np.zeros((len(tracks), len(models)))
co2s = np.zeros((len(tracks), len(models)))

for i, track in enumerate(tracks):
	gears = np.arange(1.0,5.0,0.3)
	for j, sn in enumerate(models):
		bestco2 = None
		bestt = np.inf
		for gr in gears:
			segments = trackseg.file_to_segments('params/tracks/'+track,dl,sectors_only=True)

			sim = sims.Simulation(sn);

			vehicle  = ipvehicle.Vehicle(yaml.load(open('params/vehicles/SUPERCAR.yaml','r'),True))
			vehicle.final_drive_reduction = gr
			vehicle.prep()

			output = None
			if i == 0:
				output = sim.steady_solve(vehicle, segments)
			else:
				output = sim.solve(vehicle, segments)
			# plottools.plot_velocity_and_events(output,'t',st)
			times[i,j] = output[-1,sims.O_TIME]
			if bestt > output[-1,sims.O_TIME]:
				bestt = output[-1,sims.O_TIME]
				bestco2 = output[-1,sims.O_CO2]
			print('\t%s @ gr= %.2f: (%.4f, %.7f)' % (track, gr, output[-1,sims.O_TIME], output[-1,sims.O_CO2]))
		times[i,j] = bestt
		co2s[i,j]  = bestco2
		print('%s Best: (%.4f, %.7f)' % (track, times[i,j], co2s[i,j]))
np.savetxt('track_profile.csv', np.hstack((times,co2s)))