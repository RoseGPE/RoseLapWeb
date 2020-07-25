from track import *
from vehicle import *
from run_onetire import *
from timeit import default_timer as timer

trk = Track('dxf', open('sample_track.dxf').read())
veh = Vehicle('yaml', open('sample_vehicle.yaml').read())
run = Run_Onetire(veh, [trk], {})

#print(trk)
#print(trk.dc)
#print(veh)
#print(veh.data)
#print(run)

run.solve()

#print(run.channels)
#print(run.results)

start = timer()
run.build_maps()
end   = timer()
print("maps built in %.10f s" % (end - start))
run.plot_maps()