from track import *
from vehicle import *
from onetire_ss import *

trk = Track('dxf', open('sample.dxf').read())
veh = Vehicle('yaml', open('sample_vehicle.yaml').read())
run = Run_Onetire_SS(veh, trk, {})

print(trk)
print(trk.dc)
print(veh)
print(veh.data)
print(run)

run.solve()

print(run.channels)
print(run.results)