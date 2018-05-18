import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colors
from sims.constants import *

def plot_velocity_and_events(output, axis='time', title='Velocity and Events'):
  fig, ax = plt.subplots(3, sharex=True)
  fig.canvas.set_window_title(title)

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
  

  ax[1].plot(xaxis,curv,lw=5,label='Curvature')
  ax[1].set_ylim(0,max(curv)*1.05)

  ax[2].plot(xaxis,output[:, O_GEAR]+1,lw=4,label='Gear')
  ax[2].set_ylim(0, 10)


  lim = max(curv)
  alpha =  1

  ax[1].fill_between(xaxis, 0, lim, where= status>=D_ACCELERATE,  facecolor='#238957', alpha=alpha)
  ax[1].fill_between(xaxis, 0, lim, where= status>=D_BRAKE,       facecolor='#C1292E', alpha=alpha)
  ax[1].fill_between(xaxis, 0, lim, where= status>=D_SUSTAIN,     facecolor='#777777', alpha=alpha)
  ax[1].fill_between(xaxis, 0, lim, where= status>=D_SHIFT_UP,    facecolor='#93BEB7', alpha=alpha)
  ax[1].fill_between(xaxis, 0, lim, where= status>=D_SHIFT_DOWN,  facecolor='#EB6534', alpha=alpha)

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
  plt.show()


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