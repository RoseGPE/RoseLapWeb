import numpy as np
import math

from constants import *
import logging

"""
Point mass model
It's a unicycle! Fast, right?
Even faster with steady state assumptions
"""

def derate_curvature(curv, raddl):
  return curv/(1.0 + raddl*curv)

def floor_sqrt(x):
  """
  Like sqrt but with a floor. If x <= 0, return 0.
  """
  if x > 0:
    return math.sqrt(x)
  return 0

class sim_ss_onetire:
  def __init__(self):
    pass

  def step_straight(self, vehicle, prior_result, segment, segment_next, brake, shifting, gear):
    return "lol not yet"

  def straight(self, vehicle, sector, x0, t0, v0, vf, dl=0.2):
    n = int(sector.length / dl)
    channels = np.zeros((n, O_MATRIX_COLS))

    # perform forward integration to the end
    v = v0
    t = t0
    x = x0
    gear = 0
    for i in range(n):
      N = vehicle.mass*vehicle.g + vehicle.downforce(v, AERO_DRS)
      a_lat = v**2 * derate_curvature(sector.curvature, vehicle.r_add)
      F_tire_lat = vehicle.mass * a_lat
      F_tire_long_available = vehicle.f_long_remain(4, N, F_tire_lat)
      gear = vehicle.best_gear(v, np.inf)
      F_tire_engine_limit, eng_rpm = vehicle.eng_force(v, int(gear))
      status = S_TOPPED_OUT

      F_tire_long = F_tire_engine_limit
      status = S_ENG_LIM_ACC

      if F_tire_long > F_tire_long_available[0]:
        status = S_TIRE_LIM_ACC
        F_tire_long = F_tire_long_available
      if eng_rpm > vehicle.engine_rpms[-1]:
        status = S_TOPPED_OUT
    
      F_longitudinal = F_tire_long - vehicle.drag(v, AERO_DRS)
      a_long = F_longitudinal / vehicle.mass
      v = floor_sqrt(v**2 + 2*a_long*dl)
      t += dl/v
      x += dl

      channels[i,O_TIME] = t
      channels[i,O_DISTANCE] = x
      channels[i,O_VELOCITY] = v
      channels[i,O_NR] = N
      channels[i,O_SECTORS]  = sector.i
      channels[i,O_STATUS]   = status
      channels[i,O_GEAR]     = gear
      channels[i,O_LONG_ACC] = a_long
      channels[i,O_LAT_ACC]  = a_lat
      channels[i,O_FR_REMAINING] = F_tire_long_available[0] 
      channels[i,O_CURVATURE] = sector.curvature
      channels[i,O_ENG_RPM]   = eng_rpm
      channels[i,O_CO2] = dl*F_tire_long*vehicle.co2_factor/vehicle.e_factor
      channels[i,O_AERO_MODE] = AERO_DRS

    # perform reverse integration to the beginning or vmax

    t_peak = t
    v = vf
    t = 0
    x = x0+dl*n
    for i in reversed(range(n)):
      N = vehicle.mass*vehicle.g + vehicle.downforce(v, AERO_BRK)
      a_lat = v**2 * derate_curvature(sector.curvature, vehicle.r_add)
      F_tire_lat = vehicle.mass * a_lat
      F_tire_long_available = vehicle.f_long_remain(4, N, F_tire_lat)

      F_tire_long = -F_tire_long_available[0]
      status = S_BRAKING
    
      F_longitudinal = F_tire_long - vehicle.drag(v, AERO_BRK)
      a_long = F_longitudinal / vehicle.mass
      v = floor_sqrt(v**2 - 2*a_long*dl)

      if v > channels[i,O_VELOCITY]:
        break

      t -= dl/v
      x -= dl

      channels[i,O_TIME] = t
      channels[i,O_DISTANCE] = x
      channels[i,O_VELOCITY] = v
      channels[i,O_NR] = N
      channels[i,O_SECTORS]  = sector.i
      channels[i,O_STATUS]   = status
      channels[i,O_GEAR]     = gear
      channels[i,O_LONG_ACC] = a_long
      channels[i,O_LAT_ACC]  = a_lat
      channels[i,O_FR_REMAINING] = F_tire_long_available[0] 
      channels[i,O_CURVATURE] = sector.curvature
      channels[i,O_ENG_RPM]   = np.nan
      channels[i,O_CO2] = dl*F_tire_long*vehicle.co2_factor/vehicle.e_factor
      channels[i,O_AERO_MODE] = AERO_DRS

    # fix up the times...
    
    for i in reversed(range(n)):
      if channels[i,O_TIME] < 0:
        channels[i,O_TIME] += t_peak - t

    # find intersection point and splice

    print('Straight from %.2f -> %.2f' % (v0,vf))

    return channels
    
  def steady_corner(self, vehicle, sector):
    # solve a fuckton of physics
    v_lower = 0
    v_upper = vehicle.vmax
    v_cur   = (v_lower + v_upper)/2.0
    v_working = 1.0
    i = 0

    N = 0
    a_lat = 0
    F_tire_long = 0
    F_tire_lat  = 0
    F_tire_lat_available = 0
    F_tire_lat_excess    = 0

    while True:
      
      N = vehicle.mass*vehicle.g + vehicle.downforce(v_cur, AERO_FULL)
      F_tire_long = vehicle.drag(v_cur, AERO_FULL)
      a_lat = v_cur**2 * derate_curvature(sector.curvature, vehicle.r_add)
      F_tire_lat  = vehicle.mass * a_lat
      F_tire_lat_available = vehicle.f_long_remain(4, N, F_tire_long)
      F_tire_lat_excess = F_tire_lat_available[0] - F_tire_lat

      # print('iter %d; k= %.4f, v= %.2f, avail= %.3f, req= %.3f, excess= %.4f' % (i,sector.curvature,v_cur,F_tire_lat_available[0],F_tire_lat,F_tire_lat_excess))

      if F_tire_lat_excess < 1e-3 and F_tire_lat_excess >= 0:
        break

      if F_tire_lat_excess > 0:
        v_working = v_cur
        v_lower   = v_cur
      else:
        v_upper   = v_cur
      v_cur   = (v_lower + v_upper)/2.0

      i+=1
      if i > 100:
        v_cur = v_working
        break
    
    channels = [
      1000 if v_cur == 0 else sector.length/v_cur, # t
      sector.length, # x
      v_cur,
      0,
      0,
      N,
      0, 
      sector.i,
      S_SUSTAINING,
      np.nan, # no real 'gear'
      0, # no long. acc
      a_lat/vehicle.g, 
      0,
      0,
      0,
      0,
      F_tire_lat_available[0],
      0,
      sector.curvature,
      np.nan, # engine could be made but enh
      sector.length*F_tire_long*vehicle.co2_factor/vehicle.e_factor,
      AERO_FULL]

    channels = np.array([channels,channels])

    return channels

    

  def solve(self, vehicle, sectors, output_0 = None):

    # solve all the corners
    sector_results = [None for i in sectors]
    for i, sector in enumerate(sectors):
      if sector.curvature > 0:
        sector_results[i] = self.steady_corner(vehicle, sector)

    x = 0
    t = 0
    for i, sector in enumerate(sectors):
      if sector_results[i] is None:
        v0 = 0 if i==0 else sector_results[i-1][-1,O_VELOCITY]
        vf = np.inf if i==len(sectors)-1 else sector_results[i+1][-1,O_VELOCITY]
        sector_results[i] = self.straight(vehicle, sector, x, t, v0, vf)
        t = sector_results[i][-1,O_TIME]
        x = sector_results[i][-1,O_DISTANCE]
      else:
        tmp = t
        sector_results[i][0,O_DISTANCE] = x
        t += sector_results[i][-1,O_TIME]
        x += sector.length
        sector_results[i][0,O_TIME] = tmp
        sector_results[i][-1,O_TIME] = t
        sector_results[i][-1,O_DISTANCE] = x
    
    return np.vstack(sector_results)

  def steady_solve(self, vehicle, segments):
    pass