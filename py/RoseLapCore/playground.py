import sims
import input_processing.vehicle as ipvehicle
import input_processing.fancyyaml as yaml
import input_processing.track_segmentation as trackseg
import plottools
import input_processing.ip_logic as ip_logic
# import batcher

# a = ip_logic.process_input('test_batch_local.yaml')
# conf_tests, conf_vehicle, tracks, model, out = a
# b = batcher.batch(conf_tests, conf_vehicle, tracks, model, out)
# print(b)

# times = []

# for st in ["one_tire","two_tires","four_tires"]: #["one_tire","two_tires","four_tires"]:
# 	segments = trackseg.file_to_segments('params/tracks/acceleration.dxf',0.2) #AutoX_3_31_2018_ant.LOG

# 	times.append([])
# 	sim = sims.Simulation(st);

# 	vehicle  = ipvehicle.Vehicle(yaml.load(open('params/vehicles/VEHICLE_START_HERE.yaml','r'),True))
# 	vehicle.prep()
	

# 	output = sim.solve(vehicle, segments)
# 	plottools.plot_velocity_and_events(output,'t',st)
# 	times[-1].append(output[-1,sims.O_TIME])
# 	print(st)
# print("Total Times", times)

# plottools.plt.show();

# import sims
# import input_processing.vehicle as ipvehicle
# import input_processing.fancyyaml as yaml
# import input_processing.track_segmentation as trackseg
# import plottools

for sn in ["ss_four_tires","ss_one_tire","ss_two_tires"]:
	sim = sims.Simulation(sn);

	vehicle  = ipvehicle.Vehicle(yaml.load(open('params/vehicles/VEHICLE_START_HERE.yaml','r'),True))
	vehicle.cg_height = 0.7
	vehicle.weight_bias = 0.6
	vehicle.prep()
	segments = trackseg.file_to_segments('params/tracks/mi_2018_autox.dxf',0.4, sectors_only=True) #AutoX_3_31_2018_ant.LOG
	# exit()
	# print(vehicle.f_long_remain_pair([200,250], 500))
	# exit()

	output = sim.solve(vehicle, segments, dl=0.4)
	# print(output)
	# for i in [0,2,4]:
	plottools.plot_velocity_and_events(output,'x',sn)
	print(output[-1,sims.O_TIME])

# plottools.plot_map(segments, output, title='Map')

plottools.plt.show();