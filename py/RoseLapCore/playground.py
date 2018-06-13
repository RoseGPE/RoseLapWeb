import sims
import input_processing.vehicle as vehicle
import input_processing.fancyyaml as yaml
import input_processing.track_segmentation as trackseg
import plottools

sim = sims.Simulation("point_mass");

vehicle  = vehicle.Vehicle(yaml.load(open('params/vehicles/rgp007.yaml','r'),True))
vehicle.prep()
segments = trackseg.file_to_segments('params/DXFs/autoX_ME18.LOG',0.3)
output = sim.solve(vehicle, segments)
plottools.plot_velocity_and_events(output,'t','Vehicle 1')

# sim = sims.Simulation("point_mass");

# plottools.plot_velocity_and_events(sim.solve(vehicle, segments[0:int(len(segments)*5/5)]),'t','Vehicle 1')

#plottools.plot_velocity_and_events(sim.solve(vehicle, segments),'x','Vehicle 2')

print("Total Time: %f s" % output[-1,sims.O_TIME])

plottools.plt.show();