import sims
import input_processing.vehicle as vehicle
import input_processing.fancyyaml as yaml
import input_processing.track_segmentation as trackseg
import plottools

sim = sims.Simulation("two_tires");

vehicle  = vehicle.Vehicle(yaml.load(open('params/vehicles/rgp007.yaml','r'),True))
vehicle.prep()
segments = trackseg.file_to_segments('params/DXFs/ne_2017_endurance.svg',2.0)
output = sim.solve(vehicle, segments[:len(segments)/1])
plottools.plot_velocity_and_events(output,'t','Vehicle TT')

sim = sims.Simulation("point_mass");

output = sim.solve(vehicle, segments)
plottools.plot_velocity_and_events(output,'t','Vehicle PM')
print("Total Time: %f s" % output[-1,sims.O_TIME])
plottools.plot_map(segments, output, title='Map')

plottools.plt.show();