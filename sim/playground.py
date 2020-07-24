from track import *

trk = Track('dxf', open('sample.dxf').read())

print(trk)
print(trk.dc)

