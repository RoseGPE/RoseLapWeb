import numpy as np
import math
from scipy.interpolate import interp2d
from numpy import interp

from run import *
import logging

import matplotlib.pyplot as plt

class Run_Onetire(Run):
  "Run using the One Tire, Dual-Layer Model"

  def __init__(self, vehicle, tracks, settings):
    Run.__init__(self, vehicle, tracks, settings)

  def build_maps(s):
    "Create a velocity-curvature-acceleration (VKA) map. This creates a numeric approximation of a(v,k) for both braking and acceleration."
    N_PTS_V = 200
    N_PTS_K = 100
    maxcurv = 0
    for track in s.tracks:
      maxcurv = max(maxcurv, np.amax(track.dc[:,1]))
    s.map_v = np.linspace(0, s.vehicle.v_max*1.5, N_PTS_V)
    s.map_k = np.linspace(0, maxcurv, N_PTS_K)
    
    #s.map_states = [{"gear":i} for i in range(len(s.vehicle.gears))]
    #s.map_states.append({"gear":np.nan})
    #s.map_states = [{"gear":np.inf}]
    #s.map_states = [{}]

    s.map_a_fwd  = np.full([N_PTS_V, N_PTS_K], 0) # for i in range(len(s.map_states))]
    s.map_a_rev  = np.full([N_PTS_V, N_PTS_K], 0) # for i in range(len(s.map_states))]
    for i_v in range(0,N_PTS_V):
      for i_k in range(0,N_PTS_K):
        #for i_state in range(0,len(s.map_states)):
        v = s.map_v[i_v]
        #gear = s.map_states[i_state]["gear"]
        a_lat = v**2 * derate_curvature(s.map_k[i_k], s.vehicle.r_add)
        F_tire_lat = s.vehicle.mass * a_lat

        #F_tire_engine_limit, eng_rpm = s.vehicle.eng_force(v, gear)

        N = s.vehicle.mass*s.vehicle.g + s.vehicle.downforce(v, 0) # TODO: aero mode
        F_tire_long_available = s.vehicle.f_long_remain(4, N, F_tire_lat)[0]

        # Accel
        F_tire_long = F_tire_long_available #min(F_tire_long_available, F_tire_engine_limit)
        a_long = (F_tire_long - s.vehicle.drag(v, 0)) / s.vehicle.mass
        s.map_a_fwd[i_v, i_k] = a_long if np.isfinite(a_long) else 0

        # Brake
        a_long = (- F_tire_long_available - s.vehicle.drag(v, 0)) / s.vehicle.mass
        s.map_a_rev[i_v, i_k] = a_long if np.isfinite(a_long) else 0

        if np.isnan(s.map_a_fwd[i_v, i_k]) and np.isnan(s.map_a_rev[i_v, i_k]):
          break # dont bother computing extra points

  def plot_maps(s):
    fig, axes = plt.subplots(2, 1)
    axes[0].contourf(s.map_k, s.map_v, -s.map_a_rev, cmap="cividis")
    axes[1].contourf(s.map_k, s.map_v, +s.map_a_fwd, cmap="cividis")
    plt.show()

  def decelerate(self, v, k):
    "Compute maximum deceleration"
    a_tire = interp2d(self.map_k, self.map_v, self.map_a_rev, kind='cubic')(k, v)
    return a_tire

  def accelerate(self, v, k, gear):
    "Compute maximum acceleration"
    a_tire = interp2d(self.map_k, self.map_v, self.map_a_fwd, kind='cubic')(k, v)
    a_engine, rpm = self.vehicle.eng_force(v, gear)
    #print(self.map_v, self.map_k, self.map_a_fwd, v, k)
    #print(a_tire, a_engine)
    return min(a_tire, a_engine), rpm

  def solve(self):
    "Solve all tracks"
    for track in self.tracks:
      out = self.solve_track(track)
      self.channels.append(out)

  def solve_track(self, track):
    "Solve a specific track"

    chnl_names = ["x","t","v","k","a_long","a_lat","gear","motor_rpm"]
    mesh = np.arange(0, track.dc[-1, 0], self.settings['dx'])
    chnl = Channels(mesh, chnl_names)

    v = 0
    x = 0
    t = 0
    gear = 0
    shiftgear = 0
    t_shift = 0
    k = track.dc[0,1]
    a, rpm = self.accelerate(v, k, gear)

    chnl[0, 'x'] = x
    chnl[0, 't'] = t
    chnl[0, 'v'] = v
    chnl[0, 'k'] = k
    chnl[0, 'a_long'] = a
    chnl[0, 'a_lat']  = 0
    chnl[0, 'gear']   = gear+1
    chnl[0, 'motor_rpm'] = rpm

    i_x = 1

    while i_x < len(mesh):
      x  = mesh[i_x]
      dx = mesh[i_x] - mesh[i_x - 1]
      k = interp(x, track.dc[:,0], track.dc[:,1])
      
      newgear = self.vehicle.best_gear(v, np.inf)
      if t >= t_shift and np.isfinite(gear) and newgear != gear:
        print("better gear out there")
        t_shift = t + self.vehicle.shift_time
        shiftgear = newgear
        gear = np.nan
      elif t >= t_shift:
        print("shifting to new gear")
        gear = shiftgear
      else:
        print("currently shifting; no gear")
        gear = np.nan


      a, rpm = self.accelerate(v, k, gear)
      v = math.sqrt(v**2.0 + 2.0*a*dx)
      t = t + dx/v

      chnl[i_x, 'x'] = x
      chnl[i_x, 't'] = t
      chnl[i_x, 'v'] = v
      chnl[i_x, 'k'] = k
      chnl[i_x, 'a_long'] = a
      chnl[i_x, 'a_lat']  = v**2.0*k
      chnl[i_x, 'gear']   = gear+1
      chnl[i_x, 'motor_rpm'] = rpm
      i_x += 1

    return chnl
