import sims
import input_processing.vehicle as vehicle
import input_processing.fancyyaml as yaml
import input_processing.track_segmentation as trackseg
import plottools

sim = sims.Simulation("two_tires");

vehicle  = vehicle.Vehicle(yaml.load(open('params/vehicles/tirecar.yaml','r'),True))
vehicle.prep()
segments = trackseg.dxf_to_segments('params/DXFs/NE_autocross_2015.DXF',0.3)

plottools.plot_velocity_and_events(sim.solve(vehicle, segments[0:int(len(segments)*5/5)]),'t','Vehicle 1')

sim = sims.Simulation("point_mass");

plottools.plot_velocity_and_events(sim.solve(vehicle, segments[0:int(len(segments)*5/5)]),'t','Vehicle 1')

#plottools.plot_velocity_and_events(sim.solve(vehicle, segments),'x','Vehicle 2')


plottools.plt.show();