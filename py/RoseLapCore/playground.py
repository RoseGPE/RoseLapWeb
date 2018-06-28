import sims
import input_processing.vehicle as vehicle
import input_processing.fancyyaml as yaml
import input_processing.track_segmentation as trackseg
import plottools

times = []

sim = sims.Simulation("two_tires");

vehicle  = vehicle.Vehicle(yaml.load(open('params/vehicles/rgp007.yaml','r'),True))
vehicle.prep()
segments = trackseg.file_to_segments('params/DXFs/ne_2017_autox_spr.svg',0.1) #AutoX_3_31_2018_ant.LOG

output = sim.solve(vehicle, segments)
plottools.plot_velocity_and_events(output,'t','Vehicle w yaw')
times.append(output[-1,sims.O_TIME])

vehicle.moi_yaw = -vehicle.moi_yaw

output = sim.solve(vehicle, segments)
plottools.plot_velocity_and_events(output,'t','Vehicle w -yaw')
times.append(output[-1,sims.O_TIME])

vehicle.moi_yaw = 0

output = sim.solve(vehicle, segments)
plottools.plot_velocity_and_events(output,'t','Vehicle wo yaw')
times.append(output[-1,sims.O_TIME])

plottools.plot_map(segments, output, title='Map')
print("Total Times (yaw, -yaw, 0)", times)

plottools.plt.show();