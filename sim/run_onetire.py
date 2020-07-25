import numpy as np
import math

from run import *
import logging

import matplotlib.pyplot as plt

class Run_Onetire(Run):
  "Run using the One Tire, Dual-Layer Model"

  def __init__(self, vehicle, tracks, settings):
    Run.__init__(self, vehicle, tracks, settings)

  def build_maps(s):
    "Create a velocity-curvature-acceleration (VKA) map. This creates a numeric approximation of a(v,k) for both braking and acceleration."
    N_PTS_V = 100
    N_PTS_K = 100
    maxcurv = 0
    for track in s.tracks:
      maxcurv = max(maxcurv, np.amax(track.dc[:,1]))
    s.map_v = np.linspace(0, s.vehicle.v_max, N_PTS_V)
    s.map_k = np.linspace(0, maxcurv, N_PTS_K)
    
    #s.map_states = [{"gear":i} for i in range(len(s.vehicle.gears))]
    #s.map_states.append({"gear":np.nan})
    #s.map_states = [{"gear":np.inf}]
    #s.map_states = [{}]

    s.map_a_fwd  = np.full([N_PTS_V, N_PTS_K], -np.inf) # for i in range(len(s.map_states))]
    s.map_a_rev  = np.full([N_PTS_V, N_PTS_K], -np.inf) # for i in range(len(s.map_states))]
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
        F_longitudinal = F_tire_long - s.vehicle.drag(v, 0)
        s.map_a_fwd[i_v, i_k] = F_longitudinal / s.vehicle.mass

        # Brake
        F_longitudinal = - F_tire_long_available - s.vehicle.drag(v, 0)
        s.map_a_rev[i_v, i_k] = F_longitudinal / s.vehicle.mass

        if np.isnan(s.map_a_fwd[i_v, i_k]) and np.isnan(s.map_a_rev[i_v, i_k]):
          break # dont bother computing extra points

  def plot_maps(s):
    fig, axes = plt.subplots(2, 1)
    axes[0].contourf(s.map_k, s.map_v, -s.map_a_rev, cmap="cividis")
    axes[1].contourf(s.map_k, s.map_v, +s.map_a_fwd, cmap="cividis")
    plt.show()

  def decelerate(self, v, k):
    "Compute maximum deceleration"
    pass

  def accelerate(self, v, k, gear):
    "Compute maximum acceleration"


  def solve(self):
    "Solve all tracks"
    pass

  def solve_track(self):
    "Solve a specific track"
    pass
  
