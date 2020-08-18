import ezdxf as dxf

doc = dxf.readfile("track2.dxf")

msp = doc.modelspace()

for e in msp.query('LINE'):
    print("LINE on layer: %s" % e.dxf.layer)
    print("start point: %s" % e.dxf.start)
    print("end point: %s" % e.dxf.end)
    print("")
    
for e in msp.query('SPLINE'):
    print("SPLINE on layer: %s" % e.dxf.layer)
    print(e.dxf.n_fit_points)
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