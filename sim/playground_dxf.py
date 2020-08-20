import ezdxf as dxf
from math import *
import numpy as np

doc = dxf.readfile("track2.dxf")

msp = doc.modelspace()

for e in msp.query('LINE'):
    print("LINE on layer: %s" % e.dxf.layer)
    print("start point: %s" % e.dxf.start)
    print("end point: %s" % e.dxf.end)
    print("length: %s" % hypot(e.dxf.start[0]-e.dxf.end[0], e.dxf.start[1]-e.dxf.end[1]))
    print("")
    
for e in msp.query('SPLINE'):
    print("SPLINE on layer: %s" % e.dxf.layer)
    ct = e.construction_tool()
    print(e.fit_points)
    print(e.knots)
    print(ct.max_t)
    N = 20
    ts    = np.linspace(0.0,ct.max_t,N+1)
    dervs = ct.derivatives(ts)
    prms  = ct.params(N)
    ppt = ct.point(0)
    for t, derv, prm in zip(ts, dervs, prms):
        pt = derv[0]
        dx,  dy,  dz  = derv[1]
        ddx, ddy, ddz = derv[2]
        k = (dx*ddy - dy*ddx)/pow(dx*dx + dy*dy, 1.5)
        d = hypot(ppt[0]-pt[0], ppt[1]-pt[1]) # crude...
        print(t, prm, derv[0], d, k)
        ppt = pt
    print("")

for e in msp.query('ARC'):
    print("ARC on layer: %s" % e.dxf.layer)
    print("Start: %s" % repr(e.start_point))
    print("End:   %s" % repr(e.end_point))
    print("Curvature: %f" % (1/float(e.dxf.radius)))
    angs = [a for a in e.angles(2)]
    sa   = angs[1] - angs[0]
    while sa < 0:
        sa += 360
    length = sa*3.1415/180.0*e.dxf.radius
    print("Length: %f" % length)
    print("")