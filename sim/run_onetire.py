import numpy as np
import math
from scipy.interpolate import interp2d
from scipy.interpolate import interp1d
from numpy import interp

from sim.run import *
import logging

import matplotlib.pyplot as plt

EPSILON = 1e-4
CHAN_NAMES = ["x","t","v","k","a_long","a_lat","gear","motor_rpm"]

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

    s.map_a_fwd  = np.full([N_PTS_V, N_PTS_K], -EPSILON) # for i in range(len(s.map_states))]
    s.map_a_rev  = np.full([N_PTS_V, N_PTS_K], EPSILON) # for i in range(len(s.map_states))]
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
        s.map_a_fwd[i_v, i_k] = a_long if np.isfinite(a_long) else -EPSILON

        # Brake
        a_long = (- F_tire_long_available - s.vehicle.drag(v, 0)) / s.vehicle.mass
        s.map_a_rev[i_v, i_k] = a_long if np.isfinite(a_long) else EPSILON

        if np.isnan(s.map_a_fwd[i_v, i_k]) and np.isnan(s.map_a_rev[i_v, i_k]):
          break # dont bother computing extra points

  def plot_maps(s):
    fig, axes = plt.subplots(2, 1)
    axes[0].contourf(s.map_k, s.map_v, -s.map_a_rev, cmap="cividis")
    axes[1].contourf(s.map_k, s.map_v, +s.map_a_fwd, cmap="cividis")
    plt.show()

  def save_map_as_csv(self):
    np.savetxt('map_fwd.csv', self.map_a_fwd, delimiter=',')

  def decelerate(self, v, k):
    "Compute maximum deceleration"
    a_tire = interp2d(self.map_k, self.map_v, self.map_a_rev, kind='linear')(k, v)[0]
    return a_tire

  def accelerate(self, v, k, gear):
    "Compute maximum acceleration"
    a_tire = interp2d(self.map_k, self.map_v, self.map_a_fwd, kind='linear')(k, v)[0]
    a_engine, rpm = self.vehicle.eng_force(v, gear)
    return min(a_tire, a_engine), rpm

  def find_local_minima(self, track, start_from):
    "From the start_from x position, move forwards on the track until the steady-state velocity stops decreasing"

    i = 0
    # find our place in the track
    while track.dc[i,0] < start_from:
      i += 1
    i -= 1
    # now fast forward to the problem point
    # this is where dv(a=0,k=k(x))/dx = 0

    v_last = np.inf
    v      = np.inf
    while i < track.dc.shape[0]:
      av = interp1d(self.map_k, self.map_a_fwd, 'linear', axis=1)(track.dc[i,1])
      v = np.inf
      for j, ap in enumerate(av):
        if ap < 0:
          v = self.map_v[j]
          break

      if np.isfinite(v) and v >= v_last:
        return track.dc[i, 0], v
      v_last = v
      i += 1


  def solve(self):
    "Solve all tracks"
    for track in self.tracks:
      out = self.solve_track(track)
      self.channels.append(out)

  def solve_track(self, track):
    "Solve a specific track"

    dt   = self.settings['dt']
    chnl = Channels(CHAN_NAMES)

    v = 0
    x = 0
    t = 0
    gear = 0
    shiftgear = 0
    t_shift = 0
    k = track.dc[0,1]
    a, rpm = self.accelerate(v, k, gear)

    chnl.append('x', x)
    chnl.append('t', t)
    chnl.append('v', v)
    chnl.append('k', k)
    chnl.append('a_long', a)
    chnl.append('a_lat',  0)
    chnl.append('gear',   gear+1)
    chnl.append('motor_rpm', rpm)

    while x < track.dc[-1,0]:
      k = interp(x, track.dc[:,0], track.dc[:,1])
      
      # Gearshift delay logic
      newgear = self.vehicle.best_gear(v, np.inf)
      if t >= t_shift and np.isfinite(gear) and newgear != gear:
        t_shift = t + self.vehicle.shift_time
        shiftgear = newgear
        gear = np.nan
      elif t >= t_shift:
        gear = shiftgear
      else:
        gear = np.nan

      # Accelerate
      a, rpm = self.accelerate(v, k, gear)

      # If we fail to accelerate, initiate backup algorithm
      if a < -EPSILON:
        # Find where to backup from
        x, v = self.find_local_minima(track, x)
        chnl_rev = Channels(CHAN_NAMES)

        t = 0

        xfwd = np.asarray(chnl.map['x'])
        vfwd = np.asarray(chnl.map['v'])

        # Reverse integrate until we hit the initial solution
        while x > 0 and (x > xfwd[-1] or interp(x, xfwd, vfwd) > v):
          k = interp(x, track.dc[:,0], track.dc[:,1])
          a = self.decelerate(v, k)

          # Reverse integration
          v = v - a*dt
          t = t - dt
          x = x - v*dt

          chnl_rev.prepend('x', x)
          chnl_rev.prepend('t', t)
          chnl_rev.prepend('v', v)
          chnl_rev.prepend('k', k)
          chnl_rev.prepend('a_long', a)
          chnl_rev.prepend('a_lat',  v**2.0*k)
          chnl_rev.prepend('gear',   np.nan)
          chnl_rev.prepend('motor_rpm', np.nan)

        # Knit the reverse integration into the forward integration
        chnl.knit(chnl_rev, 'x', 't')
        v = chnl['v', -1]
        x = chnl['x', -1] + dt*v
        t = chnl['t', -1] + dt
        gear = self.vehicle.best_gear(v, np.inf)
        continue

      # Forward integration
      v = v + a*dt
      t = t + dt
      x = x + v*dt

      chnl.append('x', x)
      chnl.append('t', t)
      chnl.append('v', v)
      chnl.append('k', k)
      chnl.append('a_long', a)
      chnl.append('a_lat',  v**2.0*k)
      chnl.append('gear',   gear+1)
      chnl.append('motor_rpm', rpm)

    return chnl
