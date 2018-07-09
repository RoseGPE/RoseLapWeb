import sys,os
sys.path.append(os.path.dirname(__file__))

import input_processing
import batcher
import matplotlib.pyplot as plt, mpld3
import math
import plotter
import numpy as np

name = "ignore.png"

class Object(object):
    pass

def makeSegment():
	x = Object()
	x.length = 2.
	x.curvature = 0
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


   	fig, ax = plt.subplots()
    ax.axis('equal')
    ax.scatter(x, y, marker=".")
    mpld3.save_html(fig, "mpld3-" + name)
    fig.savefig("track2-" + name
)
circle = [makeCurvedSegment(15) for x in range(15)]
tight = [makeCurvedSegment(3) for x in range(15)]
supertight = [makeCurvedSegment(1) for x in range(15)]
line = [makeSegment() for x in range(15)]

hook = line + circle
complexturns = (line * 2) + (circle * 3) + (tight * 3) + (supertight * 3) + line + (tight * 3)
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

# for t in track:
# 	print("1," + str(t.curvature) + "," + str(t.length))

tracks = [(complexturns, False, "track name")]

print(len(tracks[0][0]))
draw_track(tracks[0][0])
exit()

results = batcher.batch(tests, vehicle, tracks, model, out[1] != 0)

d = results['track_data'][0]['outputs'][0][1]

plotter.plot_velocity_and_events(np.array(d), saveimg=True, imgname=name)
print results
