import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colors
from sims.constants import *

def plot_velocity_and_events(output, axis='distance', title='Velocity and Events', saveimg=False, imgname="broken.png"):
  fig, ax = plt.subplots(5, sharex=True)
  fig.canvas.set_window_title(title)
  fig.set_size_inches(12, 8)

  fig.suptitle(title)

  t = output[:, O_TIME]
  x = output[:, O_DISTANCE]
  v = output[:, O_VELOCITY]

  sectors = output[:, O_SECTORS]
  status = output[:, O_STATUS]
  gear = output[:, O_GEAR]

  along = output[:, O_LONG_ACC]
  alat = output[:, O_LAT_ACC]
  eng_rpm = output[:, O_ENG_RPM]

  curv = output[:, O_CURVATURE]*100

  if axis == 'time':
    plt.xlabel('Elapsed time')
    xaxis = t
  else:
    xaxis = x
    plt.xlabel('Distance travelled')

  ax[0].plot(xaxis,v,lw=5,label='Velocity')
  ax[0].set_ylim((0,max(v)*1.05))
  

  ax[1].plot(xaxis,curv,lw=5,label='Curvature',marker='.',linestyle='none')
  ax[1].set_ylim(0,max(curv)*1.05)

  ax[2].plot(xaxis,output[:, O_LONG_ACC], lw=4,label='Longitudinal g\'s')
  ax[2].plot(xaxis,output[:, O_LAT_ACC],lw=4,label='Lateral g\'s')
  ax[2].set_ylim(-3,3)

  ax[3].plot(xaxis,output[:, O_GEAR]+1,lw=4,label='Gear')
  ax[3].plot(xaxis,output[:, O_ENG_RPM]/1000, lw=4, label='RPM x1000')
  ax[3].set_ylim(0, 10)

  forces = output[:, [O_NF, O_NR, O_FF_REMAINING, O_FR_REMAINING]]
  force_lim = max(forces.min(), forces.max(), key=abs)*1.05
  ax[4].plot(xaxis,output[:, O_NF], lw=4,label='Front normal force')
  ax[4].plot(xaxis,output[:, O_NR], lw=4,label='Rear normal force')
  ax[4].plot(xaxis,output[:, O_FF_REMAINING], lw=4,label='Remaining front long. force')
  ax[4].plot(xaxis,output[:, O_FR_REMAINING], lw=4,label='Remaining rear long. force')
  ax[4].set_ylim(-force_lim,force_lim)

  lim = max(curv)
  alpha =  1

  ax[1].fill_between(xaxis, 0, lim, where= status==S_BRAKING,      facecolor='#e22030', alpha=alpha)
  ax[1].fill_between(xaxis, 0, lim, where= status==S_ENG_LIM_ACC,  facecolor='#50d21d', alpha=alpha)
  ax[1].fill_between(xaxis, 0, lim, where= status==S_TIRE_LIM_ACC, facecolor='#1d95d2', alpha=alpha)
  ax[1].fill_between(xaxis, 0, lim, where= status==S_SUSTAINING,   facecolor='#d2c81c', alpha=alpha)
  ax[1].fill_between(xaxis, 0, lim, where= status==S_DRAG_LIM,     facecolor='#e2952b', alpha=alpha)
  ax[1].fill_between(xaxis, 0, lim, where= status==S_SHIFTING,     facecolor='#454545', alpha=alpha)
  ax[1].fill_between(xaxis, 0, lim, where= status==S_TOPPED_OUT,   facecolor='#7637a2', alpha=alpha)

  sector = sectors[0]
  for idx,sec in enumerate(sectors):
    if sec!=sector:
      ax[1].axvline(xaxis[idx], color='black', lw=2, alpha=0.9)
      sector=sec
  
  plt.xlim((0,max(xaxis)))

  #sectors = set(output[:,3])
  #for sector in sectors:
  #  ax.fill_between(t, -100, 100, where=output[:,3]==sector, facecolor=colorgen(len(sectors), sector), alpha=0.3)

  for a in ax:
    a.grid(True)
    a.legend()

  plt.draw()

  if saveimg:
    plt.savefig(imgname, dpi=100)


class DetailZoom:
  def __init__(self, record, seg_no):
    self.record = record
    self.outputs = record.output
    self.seg_no = seg_no

  def onpick(self, event):
    # get mouse data
    x = event.mouseevent.xdata
    y = event.mouseevent.ydata
    

    # find closest point
    distances = []
    if self.record.kind == "2D":
      print('okay now')
      distances = np.array([abs(p - x) for p in self.record.plot_points])
      minXIndex = distances.argmin()
      # if distances[minXIndex] > 0.1:
      #   print('x prob')
      #   return

      relevantTimes = np.transpose(self.record.times[:, minXIndex])
      distances = np.array([abs(t - y) for t in relevantTimes])
      minYIndex = distances.argmin()
      # if distances[minYIndex] > 0.1:
      #   print('y prob')
      #   return


      outputIndex = minYIndex * len(self.record.plot_points) + minXIndex
      title = 'Details for ' + self.record.track[minYIndex] + ', ' + self.record.plot_x_label + '= ' + ("%.3f"%self.record.plot_points[minXIndex]) + " (" + ("%.3f"%self.outputs[outputIndex][-1,O_TIME]) + "s)"
      print(title)
      self.plotDetail(outputIndex, title)

    elif self.record.kind == "3D":
      offset = len(self.record.plot_x_points)*len(self.record.plot_y_points)*self.seg_no
      distances = np.array([abs(p - x) for p in self.record.plot_x_points])
      minXIndex = distances.argmin()
      # if distances[minXIndex] > 0.1:
      #   return

      distances = np.array([abs(p - y) for p in self.record.plot_y_points])
      minYIndex = distances.argmin()
      # if distances[minYIndex] > 0.1:
      #   return

      outputIndex = minXIndex * len(self.record.plot_y_points) + minYIndex + offset
      title = 'Details for ' + self.record.track[self.seg_no] + ', ' + self.record.plot_x_label + "= " + ("%.3f"%self.record.plot_x_points[minXIndex]) + ', ' +  self.record.plot_y_label + ": " + ("%.3f"%self.record.plot_y_points[minYIndex]) + " (" + ("%.3f"%self.outputs[outputIndex][-1,O_TIME]) + "s)"
      self.plotDetail(outputIndex, title)

  def plotDetail(self, i, title='Details'):
    plot_velocity_and_events(self.outputs[i], title=title)
    plt.show()