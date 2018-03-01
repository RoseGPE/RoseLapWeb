from __future__ import print_function
import numpy as np
import math
import itertools as it
import time

epsilon = 1e-4

def load_dxf(path_to_file):
  #print(path_to_file)
  with open(path_to_file,'r') as p:
    
    lines = [x.strip() for x in p.read().splitlines()]
    connectivity = []
    dxf_output = []
    i=0
    while i<len(lines):
      if lines[i] == 'AcDbLine':
        
        this_shape = ['line',0,0,0,0];
        # x1 y1 x2 y2
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
      elif lines[i] == 'AcDbCircle':
        this_shape = ['arc',0,0,0,0,0,1]
        # xc yc radius start_angle end_angle direction x1 y1 x2 y2
        headers = ['10','20','40','50','51']
        while i<len(lines):
          if lines[i] in headers:
            this_shape[headers.index(lines[i])+1]=float(lines[i+1])
          elif lines[i] == '0':
            break;
          else:
            i-=1
          i+=2;
        this_shape.append(math.cos(math.radians(this_shape[4]))*this_shape[3]+this_shape[1])
        this_shape.append(math.sin(math.radians(this_shape[4]))*this_shape[3]+this_shape[2])
        this_shape.append(math.cos(math.radians(this_shape[5]))*this_shape[3]+this_shape[1])
        this_shape.append(math.sin(math.radians(this_shape[5]))*this_shape[3]+this_shape[2])
        dxf_output.append(this_shape)
      i+=1

    connectivity = []
    #[print(x) for x in dxf_output]

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
          if abs(shape[-4] - hop[0]) < epsilon and abs(shape[-3] - hop[1]) < epsilon:
            matches_pos.append(i)
          elif abs(shape[-2] - hop[0]) < epsilon and abs(shape[-1] - hop[1]) < epsilon:
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
    if ( (abs(dxf_output[connectivity[-1]][-4] - dxf_output[connectivity[0]][-2]) > epsilon or abs(dxf_output[connectivity[-1]][-3] - dxf_output[connectivity[0]][-1]) > epsilon)
      and (abs(dxf_output[connectivity[-1]][-2] - dxf_output[connectivity[0]][-4]) > epsilon or abs(dxf_output[connectivity[-1]][-1] - dxf_output[connectivity[0]][-3]) > epsilon)) :
      open_ended=True
    return (dxf_output, connectivity, open_ended)

def pointify_dxf(dxf_output, connectivity, dl):
  pts = []
  intermediates = []
  for index in connectivity:
    shape = dxf_output[index]
    #print(shape[0])
    if shape[0] == 'line':
      dx=shape[3]-shape[1]
      dy=shape[4]-shape[2]
      length = math.sqrt(dx**2 + dy**2)
      n = int(math.ceil(length/dl))
      for i in range(n):
        x=shape[1] + dx/n*(i+0)
        y=shape[2] + dy/n*(i+0)
        pts.append((x,y ,index))
        #print(x,y)
    if shape[0] == 'arc':
      dtheta = math.degrees(dl/shape[3])
      theta_range = (shape[5]-shape[4]) %360;
      n = int(math.ceil(theta_range/dtheta))
      if shape[6] > 0:
        for i in range(n):
          x=shape[1]+shape[3]*math.cos(math.radians(shape[4] + theta_range/n*(i)))
          y=shape[2]+shape[3]*math.sin(math.radians(shape[4] + theta_range/n*(i)))
          pts.append((x,y, index))
          #print(x,y)
      else:
        for i in range(n):
          x=shape[1]+shape[3]*math.cos(math.radians(shape[5] - theta_range/n*(i)))
          y=shape[2]+shape[3]*math.sin(math.radians(shape[5] - theta_range/n*(i)))
          pts.append((x,y, index))
          #print(x,y)
    if index!=connectivity[-1]:
      intermediates.append(len(pts))
  return (np.array(pts),intermediates)

class Segment(object):
  def __init__(self,x1,y1,x2,y2,x3,y3,sector,endpoint):
    self.x_m=x1; self.x=x2; self.x_p=x3; self.y_m=y1; self.y=y2; self.y_p=y3;
    self.length_m = math.hypot(self.x_m-self.x, self.y_m-self.y)
    self.length_p = math.hypot(self.x_p-self.x, self.y_p-self.y)
    self.length_secant = math.hypot(self.x_p-self.x_m, self.y_p-self.y_m)
    self.length = (self.length_m+self.length_p)/2
    self.sector = sector;

    if endpoint:
      self.curvature = 0
    else:
      p = (self.length_m+self.length_p+self.length_secant)/2
      #print(p, self.length_m, self.length_p, self.length_secant)
      try:
        area = math.sqrt(p*(p-self.length_m)*(p-self.length_p)*(p-self.length_secant))
      except ValueError:
        area=0

      self.curvature = 4*area/(self.length_m*self.length_p*self.length_secant)
    

def seg_points(points,intermediates,open_ended):
  segs=[]
  for i in range(points.shape[0]):
    overk = False
    im=i-1
    if im < 0:
      im = points.shape[0]-1
      if open_ended:
        overk = True
        im = 0
    ip=i+1
    if ip >= points.shape[0]:
      ip = 0
      if open_ended:
        overk = True
        ip = i
    segs.append(Segment(points[im,0], points[im,1], points[i,0], points[i,1], points[ip,0], points[ip,1], points[i,2], overk))
  for i in intermediates:
    #print (segs[i-1].curvature, segs[i].curvature, segs[i-1].curvature)
    segs[i].curvature = (segs[i-1].curvature+segs[i+1].curvature)/2
  return segs

def plot_segments(segments):
  sectors = []
  labels = []
  i=0
  for segment in segments:
    if len(sectors) <= 0 or segment.sector != i:
      sectors.append(np.array([segment.x,segment.y]))
      labels.append(segment.sector)
      i = segment.sector
    else:
      sectors[-1] = np.vstack((sectors[-1], np.array([segment.x,segment.y])))

  fig, ax = plt.subplots()
  for idx,sector in enumerate(sectors):
    ax.scatter(sector[:,0], sector[:,1], label=labels[idx])

  
  ax.legend()
  ax.grid(True)

  plt.show()

def dxf_to_segments(filename, dl):
  # The function you came here for. Hand it a filename and desired segment distance, you get segments of the track.
  dxf_geometry,connectivity,open_ended = load_dxf('./params/DXFs/' + filename)
  points,intermediates = pointify_dxf(dxf_geometry,connectivity,dl)
  #print (connectivity)
  segs = seg_points(points,intermediates,open_ended)
  return segs

if __name__ == '__main__':
  segs = dxf_to_segments('./track.dxf', 2)
  #[print(x.x, x.y, x.curvature, x.sector) for x in segs]
  plot_segments(segs)