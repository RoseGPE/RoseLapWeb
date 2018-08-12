from __future__ import print_function
import numpy as np
import math
import itertools as it
import time
from svgpathtools import *
from scipy import signal
from scipy.interpolate import UnivariateSpline
import json
import matplotlib.pyplot as plt

epsilon = 1e-4
option_names = ['dl', 'd_nom', 'd_scale', 'D', 'maxcurv', 'smoothing', 'savgol_amt', 'savgol_dof']

def sectors_dxf(dxf_output, connectivity, open_ended):
  sectors = []
  # print(connectivity)
  for index in connectivity:
    shape = dxf_output[index]
    if shape[0] == 'line':
      dx=shape[3]-shape[1]
      dy=shape[4]-shape[2]
      length = math.hypot(dx, dy)
      sectors.append(Sector(index, length, 0))
    elif shape[0] == 'arc':
      # xc yc radius start_angle end_angle direction x1 y1 x2 y2
      arc_angle = shape[5] - shape[4]
      # if shape[6] > 0:
        # arc_angle = arc_angle-360
      # arc_angle = arc_angle % 360
      if shape[6] < 0:
        arc_angle+=360
      arc_angle = arc_angle % 360
      # print('arc angle: %.2f direction = %.1f' % (arc_angle,shape[6]))
      length = shape[3]*math.radians(arc_angle)
      sectors.append(Sector(index, length, 1.0/shape[3]))
  return sectors  

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

def points_in_each_seg_slow(path, dx, plot, opts={}):
  a = np.array([])
  s = np.array([])
  k = np.array([])
  d = np.array([])
  l = np.array([0])
  firsttime = True
  sectors = []
  for seg in path:
    ls = np.linspace(0,1,seg.length()/dx)[:-1]
    x = seg.poly()(ls)
    for i in ls:
      k = np.append(k, seg.curvature(i))
    a = np.append(a, x)
    s = np.append(s, np.ones_like(x)*len(sectors))
    sectors.append(a.shape[0])
  for i in range(1,len(a)):
    l = np.append(l, l[-1]+math.hypot(a.real[i]-a.real[i-1],-a.imag[i]+a.imag[i-1]))
  # print(k)
  smoothing = opts['smoothing'] if 'smoothing' in opts else 0.005
  smoothing_dof = opts['smoothing_dof'] if 'smoothing_dof' in opts else 2
  spl = UnivariateSpline(l, k, k=smoothing_dof)
  spl.set_smoothing_factor(smoothing)
  lsp = l #np.linspace(min(l),max(l), l[-1]/dx)
  knew = spl(lsp)

  if plot:
    plt.plot(l,k,'.')
    plt.plot(lsp,knew, lw=2)

  return (np.stack((a.real,-a.imag,knew,s.real),axis=1),sectors)

class Sector:
    def __init__(self, i, length, curvature):
        self.i, self.length, self.curvature = i, length, curvature

    def __repr__(self):
        return "Sector(%d, %.1f, %.3f)" % (self.i,self.length,self.curvature)


class Segment(object):
  def __init__(self,x1=None,y1=None,x2=None,y2=None,x3=None,y3=None,sector=0,endpoint=False,length=None,curvature=None):
    if length is None:
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

        if self.length_m <= 0 or self.length_p <=0:
          self.curvature = 0
        else:
          self.curvature = 4*area/(self.length_m*self.length_p*self.length_secant)
      if not (curvature is None):
        # print('override curv')
        self.curvature = curvature
    else:
      # print('override all')
      self.x = x2
      self.y = y2
      self.length = length
      self.length_m = length
      self.length_p = length
      self.length_secant = length
      self.curvature = curvature
      self.sector = sector
    if self.curvature > 0.05:
      self.curvature = 0.05

class RLT(object):
  def __init__(self, k, l, s):
    self.curvature = k
    self.length = l
    self.sector = s
    
def seg_points_trackwalker(fn,dx,plot=False,opts={}):
  f = open(fn,'r')
  params = json.loads(f.readline())
  f.close()

  encoder_data = np.loadtxt(fn,delimiter=',',skiprows=1)
  x1 = encoder_data[:,0]/(600.0*4)*((opts["d_nom"] if "d_nom" in opts else params["d_nom"])/12.0*math.pi)
  x2 = encoder_data[:,1]/(600.0*4)*((opts["d_nom"] if "d_nom" in opts else params["d_nom"])*(opts["d_scale"] if "d_scale" in opts else params["d_scale"])/12.0*math.pi)

  if not (params["cutoff_start"] is None or params["cutoff_end"] is None):
    cut_low = x1.searchsorted(params["cutoff_start"],'right')-1
    cut_high = x1.searchsorted(params["cutoff_end"],'left')-1
    x1 = x1[cut_low:cut_high]
    x2 = x2[cut_low:cut_high]
  x1 = x1-x1[0]
  x2 = x2-x2[0]

  k = np.zeros(x1.shape,dtype=float)
  d = np.zeros(x1.shape,dtype=float)
  l = np.zeros(x1.shape,dtype=float)
  theta = np.zeros(x1.shape,dtype=float)
  x = np.zeros(x1.shape,dtype=float)
  y = np.zeros(x1.shape,dtype=float)

  D = (opts["D"] if "D" in opts else params["D"])/12.0

  for i in range(1,np.size(x1)):
    d[i] = (x1[i]-x1[i-1]+x2[i]-x2[i-1])/2
    k[i] = 2/D *(x1[i]-x1[i-1]-x2[i]+x2[i-1])/(x1[i]-x1[i-1]+x2[i]-x2[i-1])
    theta[i] = theta[i-1] + d[i]*k[i]
    x[i] = x[i-1] + math.sin(theta[i])*d[i]
    y[i] = y[i-1] + math.cos(theta[i])*d[i]
    l[i] = l[i-1] + d[i]

  l=l[1:]*np.sign(np.sum(l))
  k=np.clip(k[1:], -params["maxcurv"], params["maxcurv"])

  l_tot = l[-1]-l[1]

  if plot:
    plt.figure()
    plt.plot(l,k,'.',ms=1)
  savgol_amt = opts['savgol_amt'] if 'savgol_amt' in opts else params["savgol_amt"]
  savgol_dof = opts['savgol_dof'] if 'savgol_dof' in opts else params["savgol_dof"]
  smoothing = opts['smoothing'] if 'smoothing' in opts else params["smoothing"]
  smoothing_dof = opts['smoothing_dof'] if 'smoothing_dof' in opts else 5
  l = signal.savgol_filter(l,savgol_amt,savgol_dof)
  k = signal.savgol_filter(k,savgol_amt,savgol_dof)
  if plot:
    plt.plot(l,k,'-',lw=1)
  spl = UnivariateSpline(l, k, k=smoothing_dof)
  spl.set_smoothing_factor(smoothing)
  lsp = np.linspace(min(l),max(l), l_tot/dx)
  k = spl(lsp)
  l = lsp
  if plot:
    plt.plot(lsp,k, lw=2)
    plt.title('Filtered l-k')

  d = np.zeros(l.shape,dtype=float)
  theta = np.zeros(l.shape,dtype=float)
  xf = np.zeros(l.shape,dtype=float)
  yf = np.zeros(l.shape,dtype=float)
  for i in range(1,np.size(l)):
    d[i] = (l[i]-l[i-1])
    theta[i] = theta[i-1] + d[i]*k[i]
    xf[i] = xf[i-1] + math.sin(theta[i])*d[i]
    yf[i] = yf[i-1] + math.cos(theta[i])*d[i]
  if plot:
    plt.figure()
    plt.plot(x,y,'.b',ms=1)
    plt.plot(xf,yf,'.r',ms=2)
  segs = []
  for i in range(len(k)):
    segs.append(Segment(0,0, xf[i],yf[i], 0,0, 0,False,dx,abs(k[i])))

  return segs


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

def seg_points_svg(points,open_ended):
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
    segs.append(Segment(points[im,0], points[im,1], points[i,0], points[i,1], points[ip,0], points[ip,1], points[i,3], overk, curvature=points[i,2]))
  # for i in range(1,len(segs)-1):
  #   d1 = segs[i].curvature-segs[i-1].curvature
  #   d2 = segs[i].curvature-segs[i+1].curvature

  #   if d1 > 0.005 and d2 > 0.005:
  #     segs[i].curvature = (segs[i-1].curvature+segs[i+1].curvature)/2

  return segs

def plot_segments(segments):
  plt.figure()
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

def file_to_segments(filename, dl, plot=False, opts={}, sectors_only=False):
  if sectors_only:
    dxf_geometry,connectivity,open_ended = load_dxf(filename)
    return sectors_dxf(dxf_geometry,connectivity,open_ended)
  elif filename[-4:].lower() == '.dxf':
    dxf_geometry,connectivity,open_ended = load_dxf(filename)
    points,intermediates = pointify_dxf(dxf_geometry,connectivity,dl)
    return seg_points(points,intermediates,open_ended)
  elif filename[-4:].lower() == '.svg':
    testpath,attrs = svg2paths(filename) 
    # print(testpath)
    testpath = testpath[0]
    pts,sectors = points_in_each_seg_slow(testpath, dl, plot, opts)
    return seg_points_svg(pts, max(abs(pts[0,:]-pts[-1,:])) > epsilon)
  elif filename[-4:].lower() == '.log':
    return seg_points_trackwalker(filename, dl, plot, opts)
  elif filename[-4:].lower() == '.rlt':
    return rlt_to_segments(filenam, opts)
  else:
    return None

def rlt_to_segments(filename, opts={}):
  with open(filename, "r") as rlt:
    segs = []

    for i, line in enumerate(rlt):
      line = line.strip().split(",")
      n = int(line[0])
      k = float(line[1])
      l = float(line[2])

      for j in range(n):
        segs.append(RLT(k, l, i))

  return segs

if __name__ == '__main__':
  import sys
  # segs = file_to_segments(sys.argv[1], float(sys.argv[2]), True, sectors_only=True)
  segs = file_to_segments('../params/tracks/testtrack.dxf', 0.2, True, sectors_only=True)
  print(segs)
  exit()
  
  #[print(x.x, x.y, x.curvature, x.sector) for x in segs]
  # try:
  #   plot_segments (segs)
  # except:
  #   print("plot_segments failed")
  plt.show()