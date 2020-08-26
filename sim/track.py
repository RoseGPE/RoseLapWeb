from __future__ import print_function
import numpy as np
import math
import itertools as it
import time
#from svgpathtools import *
from scipy import signal
from scipy.interpolate import UnivariateSpline
#import matplotlib.pyplot as plt
import ezdxf as dxf
import tempfile

from ezdxf.lldxf.tagger import ascii_tags_loader, tag_compiler, binary_tags_loader

from CustomNamedTemporaryFile import *
#from ezdxf.filemanagement import dxf_file_info

np.seterr(divide='ignore')

EPSILON = 1e-4 # small amount used for distinguishing points in distance-curvature data, as well as search radius for DXF parsing

class Track:
  "Track object; new to V6"

  def __init__(self, name, filetype, filedata, unit):
    self.name = name
    self.filetype = filetype.lower()
    self.dc = np.empty([0,2])
    # self.dc is distance-curvature data; matrix is "tall" (fixed columns variable # rows)
    if self.filetype == 'dxf':
      # DXF data
      self.dc = dxf_to_dc(filedata, UCONVS[unit])
    if self.filetype == 'csv':
      # Raw distance-curvature data
      self.dc = np.fromiter([[float(y.strip()) for y in x.split(',')] for x in filedata.split('\n')])
      self.scale(UCONVS[unit])
    if self.filetype == 'log':
      # TODO: Trackwalker data (this may require special settings... metadata... yay)
      pass
    if self.filetype == 'svg':
      # TODO: Vector graphics
      pass

  def __repr__(self):
    return "Track (type=%s, n_datapts=%d)" % (self.filetype, np.size(self.dc, axis=0))

  def scale(self, factor):
    # Mutation, where this track object is scaled by provided factor.
    # Distances get multiplied by factor, curvatures get divided by factor.
    self.dc[:,0] *= factor
    self.dc[:,1] /= factor

  def prorate_curvature(self, r_add):
    "Modifies the track by an offset r_add to compensate for a wider vehicle. Not perfect, but does capture some of the physics."
    #for i in range(self.dc.shape[0]):
    #  self.dc[i,1] = 
    self.dc[:,1] = np.sign(self.dc[:,1]) * np.true_divide(1, np.true_divide(1, self.dc[:,1]) + r_add)

UCONVS = {
  "mi": 1609,
  "ft": 0.3048,
  "in": 0.0254,
  "mm": 1e-3,
  "m":  1,
  "km": 1e+3,
  "nmi": 1852 #nautical mile
}

def swept_angle(e, s):
  sa = e-s
  while sa < 360:
    sa += 360

class TrackSegment(object):
  __slots__ = ('dc', 'start', 'end', 'segmnt')
  def __init__(self, dc, start, end, segmnt=0):
    self.dc    = dc
    self.start = start
    self.end   = end
    self.segmnt = segmnt

  def reverse(self):
    self.dc = np.flipud(self.dc)
    self.dc[:, 0] = -self.dc[:, 0] + self.dc[0, 0] + self.dc[-1, 0]
    self.dc[:, 1] = -self.dc[:, 1]
    self.start, self.end = self.end, self.start
    return self

  def shift(self, amt):
    self.dc[:, 0] += amt
    return self

  def length(self):
    return self.dc[-1, 0] - self.dc[0, 0]

  def __repr__(self):
    return "TrackSegment from %s to %s" % (repr(self.start), repr(self.end))


def dxf_to_dc(filedata, scaling):
  "Converts DXF into distance-curvature data. Assumes a DXF in the X-Y plane of only lines, arcs, and splines."

  with CustomNamedTemporaryFile(mode='w') as tf:
    tfn = tf.name
    tf.write(filedata)
    tf.flush()

    doc = dxf.readfile(tfn)
    msp = doc.modelspace()

  segs = []

  for e in msp.query('LINE'):
    l = math.hypot(e.dxf.start[0]-e.dxf.end[0], e.dxf.start[1]-e.dxf.end[1])
    segs.append(TrackSegment(
      np.array([[0,0], [l, 0]]),
      e.dxf.start,
      e.dxf.end ))

  for e in msp.query('ARC'):
    # Compute swept angle; needs to be in the range of 0->360 so normalize it
    sa   = e.dxf.end_angle - e.dxf.start_angle
    while sa < 0:
        sa += 360
    l = sa*math.pi/180.0*e.dxf.radius

    # todo: signed curvature

    k = 1/float(e.dxf.radius)
    segs.append(TrackSegment(
      np.array([[0, k], [l, k]]),
      e.start_point,
      e.end_point ))

  for e in msp.query('SPLINE'):
    ct = e.construction_tool()

    # Iterate through the spline with N samples per control point
    dc = np.empty([0, 2])
    N  = 50
    ts    = np.linspace(0.0, ct.max_t, N*ct.count + 1)
    dervs = ct.derivatives(ts)
    prms  = ct.params(N*ct.count)
    ppt   = ct.point(0)
    for t, derv, prm in zip(ts, dervs, prms):
      # extract out derivative values (0-th derivative is this particular point)
      pt = derv[0]
      dx,  dy,  dz  = derv[1]
      ddx, ddy, ddz = derv[2]

      # compute the curvature of a parameterized curve
      k = (dx*ddy - dy*ddx)/math.pow(dx*dx + dy*dy, 1.5)
      d = math.hypot(ppt[0]-pt[0], ppt[1]-pt[1])
      dc = np.vstack((dc, np.array([d, k])))
      ppt = pt

    segs.append(TrackSegment(dc, ct.point(0), ct.point(ct.max_t)))

  # build connectivity (refer to old algo)
  # find an entity whose start point or end is at (0,0)
  # add the entity's end point to the big DC matrix
  ## reverse it if the end point was found
  # go to his other endpoint, and find an entity whose start or endpoint is at his endpoint
  # add the new entity's end point to the big DC matrix, adding elapsed_distance to the distance column

  nearpt = (0,0)
  elapsed_distance = 0
  dc = np.empty([0, 2])
  while len(segs) > 0:
    for i, seg in enumerate(segs):
      d = math.hypot(seg.start[0]-nearpt[0], seg.start[1]-nearpt[1])
      # If a match is found, add the DC data to the 
      if d < EPSILON:
        dc = np.vstack((dc, seg.shift(elapsed_distance).dc))
        elapsed_distance += seg.length()
        nearpt = seg.end
        segs.pop(i)
        break
    else:
      for i, seg in enumerate(segs):
        d = math.hypot(seg.end[0]-nearpt[0], seg.end[1]-nearpt[1])
        if d < EPSILON:
          dc = np.vstack((dc, seg.shift(elapsed_distance).reverse().dc))
          elapsed_distance += seg.length()
          nearpt = seg.end
          segs.pop(i)
          break
      else:
        print("Failed to connect segment.") # TODO: Graceful error handling
        break

  return dc
