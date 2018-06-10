import sims
import input_processing.vehicle as vehicle
import input_processing.fancyyaml as yaml
import input_processing.track_segmentation as trackseg
import plottools

sim = sims.Simulation("point_mass");

vehicle  = vehicle.Vehicle(yaml.load(open('params/vehicles/rgp008_baseline.yaml','r'),True))
vehicle.prep()
segments = trackseg.file_to_segments('params/DXFs/test.svg', 1)

plottools.plot_velocity_and_events(sim.solve(vehicle, segments[0:int(len(segments)*5/5)]),'t','Vehicle 1')

plottools.plt.show();
# def points_in_each_seg_slow(path, dx):
#     a = np.array([])
#     for seg in path:
#         a = np.append(a, seg.poly()(np.linspace(0,1,seg.length()/dx)))
#     return np.stack((a.real,a.imag),axis=1)

# if __name__ == '__main__':
#     testpath,attrs = svg2paths('params/DXFs/test.svg') 
#     testpath = testpath[0]
#     tvals = np.linspace(0, 1, 10)

#     pts = points_in_each_seg_slow(testpath, 4)
#     plt.plot(pts[:,0],pts[:,1],'.')

#     plt.show()