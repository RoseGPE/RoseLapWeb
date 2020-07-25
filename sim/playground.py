from track import *
from vehicle import *
from run_onetire import *
from timeit import default_timer as timer

trk = Track('dxf', open('sample_track.dxf').read())
veh = Vehicle('yaml', open('sample_vehicle.yaml').read())
settings = {'dt': 0.005}
run = Run_Onetire(veh, [trk], settings)

#print(trk)
#print(trk.dc)
#print(veh)
#print(veh.data)
#print(run)

#print(run.channels)
#print(run.results)

start = timer()
run.build_maps()
end   = timer()
print("maps built in %.10f s" % (end - start))

start = timer()
run.solve()
end   = timer()
print("run solved in %.10f s" % (end - start))

for i, chnl in enumerate(run.channels):
	chnl.save_as_csv(open("run_%d.csv" % i, 'w'))

#run.plot_maps()