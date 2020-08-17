import ezdxf as dxf

doc = dxf.readfile("sample_track.dxf")

msp = doc.modelspace()

for e in msp:
	print_entity(e)