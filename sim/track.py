from __future__ import print_function
import numpy as np
import math
import itertools as it
import time
#from svgpathtools import *
from scipy import signal
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt
import ezdxf as dxf
import cStringIO as StringIO

from ezdxf.lldxf.tagger import ascii_tags_loader, tag_compiler, binary_tags_loader

EPSILON = 1e-4 # small amount used for distinguishing points in distance-curvature data, as well as search radius for DXF parsing

class Track:
  "Track object; new to V6"

  def __init__(self, filetype, filedata, unit):
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

UCONVS = {
  "mi": 1609,
  "ft": 0.3048,
  "in": 0.0254,
  "mm": 1e-3,
  "m":  1,
  "km": 1e+3,
  "nmi": 1852 #nautical mile
}

def dxf_read(filedata):
  info = dxf_file_info(filename)
  #fp = open(filename, mode='rt', encoding=info.encoding, errors='ignore')
  with StringIO(filedata) as fp:
    tagger = ascii_tags_loader(fp) # takes a stream / TextIO
    tagger = tag_compiler(tagger)
  return tagger

def dxf_to_dc(filedata, scaling):
  "Converts DXF into distance-curvature data."

  dcs     = []
  starts  = []
  ends    = []
  doc = dxf_read(filedata)
  msp = doc.modelspace()

  for e in msp.query('LINE'):
    # handle line
    # set dcs, starts, ends
    entities.append(e)

  for e in msp.query('ARC'):
    # set dcs, starts, ends
    entities.append(e)

  for e in msp.query('ELLIPSE'):
    # set dcs, starts, ends
    entities.append(e)

  for e in msp.query('SPLINE'):
    # set dcs, starts, ends
    entities.append(e)

  # build connectivity (refer to old algo)

  # build 


def dxf_to_dc_OLD(data, scaling):
  "Converts DXF data into distance-curvature data. DXF will start at the endpoint which is connected to the origin (0,0)"

  dxf_output = []   # list of elements

  # STEP 1: Iterate through all lines of the DXF and get all the entities
  lines = [x.strip() for x in data.splitlines()]
  i=0
  while i<len(lines):
    # Lines are called out as AcDbLine entities
    if lines[i] == 'AcDbLine':
      # shape_type x1 y1 x2 y2
      this_shape = ['line',0,0,0,0] 

      # find codes which correspond to line dimensions
      headers = ['10','20','11','21']
      while i<len(lines):
        if lines[i] in headers:
          this_shape[headers.index(lines[i])+1]=float(lines[i+1])
        elif lines[i] == '0':
          break;
        else:
          i-=1
        i+=2;

      dxf_output.append(this_shape)

    # Arcs are called out as AcDbCircle entities
    elif lines[i] == 'AcDbCircle':
      # shape_type xc yc radius start_angle end_angle direction x1 y1 x2 y2
      this_shape = ['arc',0,0,0,0,0,1]

      # find the codes which correspond to arc dimensions
      headers = ['10','20','40','50','51']
      while i<len(lines):
        if lines[i] in headers:
          this_shape[headers.index(lines[i])+1]=float(lines[i+1])
        elif lines[i] == '0':
          break;
        else:
          i-=1
        i+=2;

      # compute the endpoints of the arc
      this_shape.append(math.cos(math.radians(this_shape[4]))*this_shape[3]+this_shape[1])
      this_shape.append(math.sin(math.radians(this_shape[4]))*this_shape[3]+this_shape[2])
      this_shape.append(math.cos(math.radians(this_shape[5]))*this_shape[3]+this_shape[1])
      this_shape.append(math.sin(math.radians(this_shape[5]))*this_shape[3]+this_shape[2])

      dxf_output.append(this_shape)

    i+=1

  # STEP 2: connect the elements together
  connectivity = [] # list of which elements are connected to which (since they are in no particular order in the DXF file)

  first_time = True
  hop = [0,0];
  if len(dxf_output) == 1:
    connectivity = [0]
  else:
    while len(connectivity) < len(dxf_output):
      matches_pos = []
      matches_neg = []
      for i in range(len(dxf_output)):
        if len(connectivity) < len(dxf_output)-1:
          if i in connectivity:
            continue
        elif i == connectivity[-1]:
          continue
        shape = dxf_output[i];
        if abs(shape[-4] - hop[0]) < EPSILON and abs(shape[-3] - hop[1]) < EPSILON:
          matches_pos.append(i)
        elif abs(shape[-2] - hop[0]) < EPSILON and abs(shape[-1] - hop[1]) < EPSILON:
          matches_neg.append(i)
      if first_time:
        fine = False
        for mp in matches_pos:
          if dxf_output[mp][-2] > dxf_output[mp][-1]:
            connectivity.append(mp)
            hop = dxf_output[mp][-2:]
            fine = True
        for mn in matches_neg:
          if dxf_output[mn][-4] > dxf_output[mn][-3]:
            connectivity.append(mn)
            temp = dxf_output[mn][-2:]
            dxf_output[mn][-2:] = dxf_output[mn][-4:-2]
            dxf_output[mn][-4:-2] = temp
            if dxf_output[mn][0] == 'arc':
              dxf_output[mn][6]*=-1;
            hop = dxf_output[mn][-2:]
            fine = True
        if fine:
          continue
      if len(matches_pos) > 0:
        connectivity.append(matches_pos[0])
        hop = dxf_output[matches_pos[0]][-2:]
      else:
        connectivity.append(matches_neg[0])
        temp = dxf_output[matches_neg[0]][-2:]
        dxf_output[matches_neg[0]][-2:] = dxf_output[matches_neg[0]][-4:-2]
        dxf_output[matches_neg[0]][-4:-2] = temp
        #print('flipper', matches_neg[0])
        if (dxf_output[matches_neg[0]][0] == 'arc'):
          dxf_output[matches_neg[0]][6]*=-1;
        hop = dxf_output[matches_neg[0]][-2:]
      first_time = False
  open_ended = False
  if ( (abs(dxf_output[connectivity[-1]][-4] - dxf_output[connectivity[0]][-2]) > EPSILON or abs(dxf_output[connectivity[-1]][-3] - dxf_output[connectivity[0]][-1]) > EPSILON)
    and (abs(dxf_output[connectivity[-1]][-2] - dxf_output[connectivity[0]][-4]) > EPSILON or abs(dxf_output[connectivity[-1]][-1] - dxf_output[connectivity[0]][-3]) > EPSILON)) :
    open_ended=True

  # STEP 3: Turn the entities and connectivity into distance-from-start and curvature data
  sectors = np.empty([0,2])
  length  = 0
  for index in connectivity:
    shape = dxf_output[index]
    if shape[0] == 'line':
      # Add start point of sector
      sectors = np.vstack((sectors, np.array([length*scaling, 0])))

      # Compute distance of line in straightforward fashion
      dx=shape[3]-shape[1]
      dy=shape[4]-shape[2]
      length = math.hypot(dx, dy)

      # Add a point that has no curvature
      sectors = np.vstack((sectors, np.array([length*scaling-EPSILON, 0])))
    elif shape[0] == 'arc':
      # xc yc radius start_angle end_angle direction x1 y1 x2 y2
      arc_angle = shape[5] - shape[4]
      # if shape[6] > 0:
        # arc_angle = arc_angle-360
      # arc_angle = arc_angle % 360
      if shape[6] < 0:
        arc_angle+=360
      arc_angle = arc_angle % 360

      # Add start point of sector
      sectors = np.vstack((sectors, np.array([length*scaling, 1.0/shape[3]/scaling])))

      length = shape[3]*math.radians(arc_angle)

      # Add end point of sector
      sectors = np.vstack((sectors, np.array([length*scaling-EPSILON, 1.0/shape[3]/scaling])))
  
  return sectors
