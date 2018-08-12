import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colorsx
import matplotlib.colorbar as colorbar
import sims.constants as sim

def plot_velocity_and_events(output, axis='x', title='Velocity and Events'):
  fig, ax = plt.subplots(5, sharex=True)
  fig.canvas.set_window_title(title)

  fig.suptitle(title)

  t = output[:, sim.O_TIME]
  x = output[:, sim.O_DISTANCE]
  v = output[:, sim.O_VELOCITY]

  sectors = output[:, sim.O_SECTORS]
  status = output[:, sim.O_STATUS]
  aero_status = output[:, sim.O_AERO_MODE]
  gear = output[:, sim.O_GEAR]

  along = output[:, sim.O_LONG_ACC]
  alat = output[:, sim.O_LAT_ACC]
  eng_rpm = output[:, sim.O_ENG_RPM]

  curv = output[:, sim.O_CURVATURE]

  if axis == 'time':
    plt.xlabel('Elapsed time')
    xaxis = t
  else:
    xaxis = x
    plt.xlabel('Distance travelled')

  ax[0].plot(xaxis,v,lw=5,label='Velocity')
  ax[0].set_ylim((0,120.0))
  

  ax[1].plot(xaxis,curv,lw=5,label='Curvature',marker='.',linestyle='none')
  ax[1].set_ylim(0,0.15)

  ax[2].plot(xaxis,output[:, sim.O_LONG_ACC], lw=4,label='Longitudinal g\'s')
  ax[2].plot(xaxis,output[:, sim.O_LAT_ACC],lw=4,label='Lateral g\'s')
  ax[2].set_ylim(-5,3.5)

  ax[3].plot(xaxis,output[:, sim.O_GEAR]+1,lw=4,label='Gear')
  ax[3].plot(xaxis,output[:, sim.O_ENG_RPM]/1000, lw=4, label='RPM x1000')
  ax[3].set_ylim(0, 10)

  forces = output[:, [sim.O_NF, sim.O_NR, sim.O_FF_REMAINING, sim.O_FR_REMAINING]]
  force_lim = max(forces.min(), forces.max(), key=abs)*1.05
  ax[4].plot(xaxis,output[:, sim.O_NF], lw=4,label='Front normal force')
  ax[4].plot(xaxis,output[:, sim.O_NR], lw=4,label='Rear normal force')
  ax[4].plot(xaxis,output[:, sim.O_FF_REMAINING], lw=4,label='Remaining front long. force')
  ax[4].plot(xaxis,output[:, sim.O_FR_REMAINING], lw=4,label='Remaining rear long. force')
  ax[4].set_ylim(-1000,1000)

  lim = max(curv)
  alpha =  1

  ax[1].fill_between(xaxis, 0, lim, where= status==sim.S_BRAKING,      facecolor='#e22030', alpha=alpha) #red
  ax[1].fill_between(xaxis, 0, lim, where= status==sim.S_ENG_LIM_ACC,  facecolor='#50d21d', alpha=alpha) #green
  ax[1].fill_between(xaxis, 0, lim, where= status==sim.S_TIRE_LIM_ACC, facecolor='#1d95d2', alpha=alpha) #blue
  ax[1].fill_between(xaxis, 0, lim, where= status==sim.S_SUSTAINING,   facecolor='#d2c81c', alpha=alpha) #yellow
  ax[1].fill_between(xaxis, 0, lim, where= status==sim.S_DRAG_LIM,     facecolor='#e2952b', alpha=alpha) #orange
  ax[1].fill_between(xaxis, 0, lim, where= status==sim.S_SHIFTING,     facecolor='#454545', alpha=alpha) #gray
  ax[1].fill_between(xaxis, 0, lim, where= status==sim.S_TOPPED_OUT,   facecolor='#7637a2', alpha=alpha) #purple

  ax[0].fill_between(xaxis, 0, 100, where= aero_status==sim.AERO_FULL,  facecolor='#1d95d2', alpha=alpha) #blue
  ax[0].fill_between(xaxis, 0, 100, where= aero_status==sim.AERO_DRS,   facecolor='#50d21d', alpha=alpha) #green
  ax[0].fill_between(xaxis, 0, 100, where= aero_status==sim.AERO_BRK,   facecolor='#e22030', alpha=alpha) #red

  sector = sectors[0]
  for idx,sec in enumerate(sectors):
    if sec!=sector:
      ax[1].axvline(xaxis[idx], color='black', lw=2, alpha=0.9)
      sector=sec
  
  plt.xlim((0,max(xaxis)))

  #sectors = set(output[:,3])
  #for sector in sectors:
  #  ax.fill_between(t, -100, 100, where=output[:,3]==sector, facecolor=colorgen(len(sectors), sector), alpha=0.3)

  # print("get ready for a wild nite")
  for a in ax:
    a.grid(True)
    a.legend()

  plt.draw()
  # print("chill")

def plot_map(segments, output, title='Map'):
  fig, ax = plt.subplots(figsize=(10,10))

  

  x = np.array([s.x for s in segments]);
  y = np.array([s.y for s in segments]);
  z = output[:,sim.O_VELOCITY]

  cmap = cmx.get_cmap('viridis')
  normalize = colorsx.Normalize(vmin=min(z), vmax=max(z))
  colors = [cmap(normalize(value)) for value in z]

  ax.scatter(x,y, color=colors)

  cax, _ = colorbar.make_axes(ax)
  cbar = colorbar.ColorbarBase(cax, cmap=cmap, norm=normalize)

  fig.canvas.set_window_title(title)
  fig.suptitle(title)
  ax.axis('equal')

  plt.draw()


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
      title = 'Details for ' + self.record.track[minYIndex] + ', ' + self.record.plot_x_label + '= ' + ("%.3f"%self.record.plot_points[minXIndex]) + " (" + ("%.3f"%self.outputs[outputIndex][-1,sim.O_TIME]) + "s)"
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
      title = 'Details for ' + self.record.track[self.seg_no] + ', ' + self.record.plot_x_label + "= " + ("%.3f"%self.record.plot_x_points[minXIndex]) + ', ' +  self.record.plot_y_label + ": " + ("%.3f"%self.record.plot_y_points[minYIndex]) + " (" + ("%.3f"%self.outputs[outputIndex][-1,sim.O_TIME]) + "s)"
      self.plotDetail(outputIndex, title)

  def plotDetail(self, i, title='Details'):
    plot_velocity_and_events(self.outputs[i], title=title)
    plt.show()
