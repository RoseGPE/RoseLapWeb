# import sims
# import input_processing.vehicle as ipvehicle
# import input_processing.fancyyaml as yaml
# import input_processing.track_segmentation as trackseg
# import plottools

# times = []

# for ss in [0.5]: #[2.0,1.5,1.0,0.7,0.5,0.4,0.3,0.25,0.2,0.15,0.1,0.05]:
# 	times.append([])
# 	sim = sims.Simulation("two_tires");

# 	vehicle  = ipvehicle.Vehicle(yaml.load(open('params/vehicles/rgp007.yaml','r'),True))
# 	vehicle.prep()
# 	segments = trackseg.file_to_segments('params/tracks/ne_2017_autox.svg',ss) #AutoX_3_31_2018_ant.LOG

# 	output = sim.solve(vehicle, segments)
# 	# plottools.plot_velocity_and_events(output,'t','Vehicle w yaw')
# 	times[-1].append(output[-1,sims.O_TIME])

# 	print('a')

# 	#vehicle.moi_yaw = -vehicle.moi_yaw
# 	vehicle.r_add = 1.0

# 	output = sim.solve(vehicle, segments)
# 	# plottools.plot_velocity_and_events(output,'t','Vehicle w -yaw')
# 	times[-1].append(output[-1,sims.O_TIME])

# 	print('a')

# 	#vehicle.moi_yaw = 0
# 	vehicle.r_add = 2.0

# 	output = sim.solve(vehicle, segments)
# 	# plottools.plot_velocity_and_events(output,'t','Vehicle wo yaw')
# 	times[-1].append(output[-1,sims.O_TIME])

# 	plottools.plot_map(segments, output, title='Map')
# 	print("Total Times at %f (yaw, -yaw, 0)" % ss, times[-1])
# print("Total Times", times)

# # plottools.plt.show();

import sims
import input_processing.vehicle as ipvehicle
import input_processing.fancyyaml as yaml
import input_processing.track_segmentation as trackseg
import plottools

	
sim = sims.Simulation("four_tires");

vehicle  = ipvehicle.Vehicle(yaml.load(open('params/vehicles/rgp007.yaml','r'),True))
vehicle.prep()
segments = trackseg.file_to_segments('params/tracks/testtrack.svg',ss) #AutoX_3_31_2018_ant.LOG

output = sim.solve(vehicle, segments)
plottools.plot_velocity_and_events(output,'t','Vehicle wo yaw')
times[-1].append(output[-1,sims.O_TIME])

plottools.plot_map(segments, output, title='Map')

# plottools.plt.show();