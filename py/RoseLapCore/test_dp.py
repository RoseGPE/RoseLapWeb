import sys,os
sys.path.append(os.path.dirname(__file__))

import input_processing
import batcher
import matplotlib.pyplot as plt
import math

class Object(object):
    pass

def makeSegment():
	x = Object()
	x.length = 2.
	x.curvature = 0.
	x.sector = 0

	return x

def makeCurvedSegment(r):
	x = Object()
	x.length = 2.
	x.curvature = 1. / r
	x.sector = 0

	return x

def draw_track(segs):
    t = [0]
    x = [0]
    y = [0]

    l = [s.length for s in segs]
    k = [s.curvature for s in segs]

    for s in segs:
    	t.append(t[-1] + s.length * s.curvature * 180 / math.pi)

    	dx = math.degrees(math.sin(math.radians(t[-1]*s.length)))
    	x.append(x[-1] + dx)

    	dy = math.degrees(math.cos(math.radians(t[-1]*s.length)))
    	y.append(y[-1] + dy)

    plt.scatter(x, y)
    plt.show()

circle = [makeCurvedSegment(15) for x in range(15)]
tight = [makeCurvedSegment(3) for x in range(15)]
line = [makeSegment() for x in range(15)]

hook = line + circle
double_loop = (line * 3) + (circle * 3) + (line * 3) + (tight * 3)
ax = line * 30

tests, vehicle, tracks, model, out = input_processing.process_input("dp.yaml")

track = []
s = 0
l = 0

for i, t in enumerate(tracks[1][0]):
	s += t.curvature
	l += t.length

	if i % 5 == 0:
		o = Object()
		o.length = l
		o.curvature = s / 5
		o.sector = t.sector

		track.append(o)

		s = 0
		l = 0

for t in track:
	print("1," + str(t.curvature) + "," + str(t.length))

tracks = [(line, False, "track name")]

print(len(tracks[0][0]))
draw_track(tracks[0][0])

results = batcher.batch(tests, vehicle, tracks, model, out[1] != 0)

print results
