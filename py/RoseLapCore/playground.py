import sims
import input_processing.vehicle as ipvehicle
import input_processing.fancyyaml as yaml
import input_processing.track_segmentation as trackseg
import plottools

times = []

for st in ['two_tires']:#["one_tire","two_tires","four_tires"]: #["one_tire","two_tires","four_tires"]:
	segments = trackseg.file_to_segments('params/tracks/testtrack.svg',0.35) #AutoX_3_31_2018_ant.LOG

	times.append([])
	sim = sims.Simulation(st);

	vehicle  = ipvehicle.Vehicle(yaml.load(open('params/vehicles/START_HERE.yaml','r'),True))
	vehicle.prep()
	

	output = sim.solve(vehicle, segments)
	plottools.plot_velocity_and_events(output,'t',st)
	times[-1].append(output[-1,sims.O_TIME])
	print(st)
print("Total Times", times)

plottools.plt.show();

# import sims
# import input_processing.vehicle as ipvehicle
# import input_processing.fancyyaml as yaml
# import input_processing.track_segmentation as trackseg
# import plottools

	
# sim = sims.Simulation("one_tire");

# vehicle  = ipvehicle.Vehicle(yaml.load(open('params/vehicles/rgp007.yaml','r'),True))
# vehicle.prep()
# segments = trackseg.file_to_segments('params/tracks/testtrack.svg',0.1) #AutoX_3_31_2018_ant.LOG

# # print(vehicle.f_long_remain_pair([200,250], 500))
# # exit()

# output = sim.solve(vehicle, segments)
# plottools.plot_velocity_and_events(output,'t','Vehicle wo yaw')
# print(output[-1,sims.O_TIME])

# plottools.plot_map(segments, output, title='Map')

# plottools.plt.show();