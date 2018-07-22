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

def frem_filter(x):
  if np.isnan(x) or np.isinf(x):
    return 0
  return x

class sim_ss_twotires:
  def __init__(self):
    pass

  def compute_Ff_Fr(self, vehicle, v, a_long, segment, prior_curvature):
    alpha = v**2*(derate_curvature(segment.curvature, vehicle.r_add)-derate_curvature(prior_curvature, vehicle.r_add))/segment.length + segment.curvature*a_long
    a_lat = derate_curvature(segment.curvature, vehicle.r_add)*v**2

    Ff_lat = (vehicle.weight_bias)*a_lat*vehicle.mass - alpha*vehicle.moi_yaw/vehicle.wheelbase_length
    Fr_lat = (1-vehicle.weight_bias)*a_lat*vehicle.mass + alpha*vehicle.moi_yaw/vehicle.wheelbase_length

    return (Ff_lat, Fr_lat, a_lat)

  def brake(self, vehicle, sector, channels_f, t0, v0, dl=0.1):
    vf = channels_f[O_VELOCITY]
    tf = channels_f[O_TIME]
    xf = channels_f[O_DISTANCE]

    Nf = channels_f[O_NF]
    Nr = channels_f[O_NR]

    a_long = channels_f[O_LONG_ACC]*vehicle.g

    n = int(sector.length/dl)
    channels = np.zeros((n, O_MATRIX_COLS))
    v = vf
    t = 0
    x = xf
    success = False
    for i in reversed(range(n)):
      aero_mode = AERO_FULL if success else AERO_BRK
      Nf = ( (vehicle.weight_bias)*vehicle.g*vehicle.mass
          + (vehicle.cp_bias[aero_mode])*vehicle.downforce(v,aero_mode)
          - vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
          - vehicle.drag(v,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )
      Nr = ( (1-vehicle.weight_bias)*vehicle.g*vehicle.mass
          + vehicle.downforce(v,aero_mode)*(1 - vehicle.cp_bias[aero_mode])
          + vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
          + vehicle.drag(v,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )

      # Calculate required lateral forces
      Ff_lat, Fr_lat, a_lat = self.compute_Ff_Fr(vehicle, v, a_long, sector, sector.curvature)

      # Calculate how much grip there is left
      remaining_long_grip = [vehicle.f_long_remain(2, Nr, Fr_lat, False)[0],vehicle.f_long_remain(2, Nf, Ff_lat, True)[0]]
      if min(remaining_long_grip) < 0:
        aero_mode = AERO_FULL
        Nf = ( (vehicle.weight_bias)*vehicle.g*vehicle.mass
          + (vehicle.cp_bias[aero_mode])*vehicle.downforce(v,aero_mode)
          - vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
          - vehicle.drag(v,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )
        Nr = ( (1-vehicle.weight_bias)*vehicle.g*vehicle.mass
            + vehicle.downforce(v,aero_mode)*(1 - vehicle.cp_bias[aero_mode])
            + vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
            + vehicle.drag(v,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )
        remaining_long_grip = [vehicle.f_long_remain(2, Nr, Fr_lat, False)[0],vehicle.f_long_remain(2, Nf, Ff_lat, True)[0]]

      ## Kinda sketchy. We enforce grip limit with the steady state limit now ##
      if remaining_long_grip[0] < 0:
        remaining_long_grip[0] = 0
      if remaining_long_grip[1] < 0:
        remaining_long_grip[1] = 0

      F_longitudinal = -sum(remaining_long_grip)-vehicle.drag(v,aero_mode)

      status = S_BRAKING
    
      a_long = F_longitudinal / vehicle.mass
      v = floor_sqrt(v**2 - 2*a_long*dl)

      if success:
        status = S_SUSTAINING
        aero_mode = AERO_FULL
        v = v0
      elif v > v0:
        # print('Sucessful brake from %.3f -> %.3f' % (v0,vf))
        success = True
        aero_mode = AERO_FULL
        v = v0

      t -= 1000 if v==0 else dl/v
      x -= dl

      channels[i,O_TIME]     = t
      channels[i,O_DISTANCE] = x
      channels[i,O_VELOCITY] = v
      channels[i,O_NR]       = Nr
      channels[i,O_NF]       = Nf
      channels[i,O_SECTORS]  = sector.i
      channels[i,O_STATUS]   = status
      channels[i,O_GEAR]     = np.nan
      channels[i,O_LONG_ACC] = a_long/vehicle.g
      channels[i,O_LAT_ACC]  = a_lat/vehicle.g
      channels[i,O_FF_REMAINING] = 0
      channels[i,O_FR_REMAINING] = 0
      channels[i,O_CURVATURE]    = sector.curvature
      channels[i,O_ENG_RPM]      = np.nan
      channels[i,O_CO2]          = 0
      channels[i,O_AERO_MODE]    = aero_mode

      if success and i > 2:
        channels[i,O_STATUS] = S_SUSTAINING
        channels[:i,:] = np.tile(channels[i,:], (i,1))
        for j in reversed(range(0,i)):
          t -= dl/v
          x -= dl
          channels[j,O_TIME] = t
          channels[j,O_DISTANCE] = x
        break

    for i in range(n):
      channels[i,O_TIME] += t0 - t
    return channels, success

  def drive(self, vehicle, sector, channels_0, vf, vmax, dl=0.1, start=False):
    n = int(sector.length / dl)
    channels = np.zeros((n, O_MATRIX_COLS))

    # perform forward integration to the end

    v0 = 0
    t0 = 0
    x0 = 0
    gear = vehicle.best_gear(v0, np.inf)
    a_long = 0
    if not (channels_0 is None):
      v0 = channels_0[O_VELOCITY]
      t0 = channels_0[O_TIME]
      x0 = channels_0[O_DISTANCE]
      gear = channels_0[O_GEAR]
      a_long = channels_0[O_LONG_ACC]*vehicle.g
    v=v0
    t=t0
    x=x0
    if np.isnan(gear):
      gear = vehicle.best_gear(v0, np.inf)

    topped = False
    t_shift = -1
    v_shift = -1
    for i in range(n):      
      aero_mode = AERO_DRS
      Nf = ( (vehicle.weight_bias)*vehicle.g*vehicle.mass
          + (vehicle.cp_bias[aero_mode])*vehicle.downforce(v,aero_mode)
          - vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
          - vehicle.drag(v,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )
      Nr = ( (1-vehicle.weight_bias)*vehicle.g*vehicle.mass
          + vehicle.downforce(v,aero_mode)*(1 - vehicle.cp_bias[aero_mode])
          + vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
          + vehicle.drag(v,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )

      # Calculate required lateral forces
      Ff_lat, Fr_lat, a_lat = self.compute_Ff_Fr(vehicle, v, a_long, sector, sector.curvature)

      ## Calculate best gear and remaining grip, and if a shift is called for ##
      best_gear = vehicle.best_gear(v, np.inf)
      if best_gear != gear and v > v_shift:
        gear += (best_gear-gear)/abs(best_gear-gear)
        t_shift = t+vehicle.shift_time
        v_shift = v*1.01
      F_tire_engine_limit, eng_rpm = vehicle.eng_force(v, int(gear))
      status = S_TOPPED_OUT

      remaining_long_grip = [vehicle.f_long_remain(2, Nr, Fr_lat, False)[0],vehicle.f_long_remain(2, Nf, Ff_lat, True)[0]]
      if remaining_long_grip[0] < F_tire_engine_limit and remaining_long_grip[1] < 0:
        aero_mode = AERO_FULL
        Nf = ( (vehicle.weight_bias)*vehicle.g*vehicle.mass
          + (vehicle.cp_bias[aero_mode])*vehicle.downforce(v,aero_mode)
          - vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
          - vehicle.drag(v,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )
        Nr = ( (1-vehicle.weight_bias)*vehicle.g*vehicle.mass
            + vehicle.downforce(v,aero_mode)*(1 - vehicle.cp_bias[aero_mode])
            + vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
            + vehicle.drag(v,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )
        remaining_long_grip = [vehicle.f_long_remain(2, Nr, Fr_lat, False)[0],vehicle.f_long_remain(2, Nf, Ff_lat, True)[0]]

      ## Kinda sketchy. We enforce grip limit with the steady state limit now ##
      fglim = False
      if remaining_long_grip[0] < 0:
        remaining_long_grip[0] = 0
      if remaining_long_grip[1] < 0:
        remaining_long_grip[1] = 0
        fglim = True

      if t < t_shift:
        ### CURRENTLY SHIFTING, NO POWER! ### 
        status = S_SHIFTING
        F_tire_long = 0
      else:
        if t_shift > 0:
          t_shift = -1

        F_tire_long = F_tire_engine_limit
        status = S_ENG_LIM_ACC
        if fglim:
          status = S_TIRE_LIM_ACC
        if F_tire_long > remaining_long_grip[0]:
          status = S_TIRE_LIM_ACC
          F_tire_long = remaining_long_grip[0]
        if eng_rpm > vehicle.engine_rpms[-1] and gear >= len(vehicle.gears)-1:
          status = S_TOPPED_OUT
    
      F_longitudinal = F_tire_long - vehicle.drag(v, aero_mode)
      a_long = F_longitudinal / vehicle.mass
      vi = v
      v = floor_sqrt(v**2 + 2*a_long*dl)
      if v > vmax:
        v = vmax
        a_long = (v**2-vi**2)/2/dl
        F_tire_long = vehicle.mass*a_long + vehicle.drag(v, aero_mode)
        topped = True
      t += 1000 if v==0 else dl/v
      x += dl

      channels[i,O_TIME] = t
      channels[i,O_DISTANCE] = x
      channels[i,O_VELOCITY] = v
      channels[i,O_NF] = Nf
      channels[i,O_NR] = Nr
      channels[i,O_SECTORS]  = sector.i
      channels[i,O_STATUS]   = status
      channels[i,O_GEAR]     = np.nan if status == S_SHIFTING else gear
      channels[i,O_LONG_ACC] = a_long/vehicle.g
      channels[i,O_LAT_ACC]  = a_lat/vehicle.g
      channels[i,O_FF_REMAINING] = frem_filter(remaining_long_grip[1])
      channels[i,O_FR_REMAINING] = frem_filter(remaining_long_grip[0])
      channels[i,O_CURVATURE] = sector.curvature
      channels[i,O_ENG_RPM]   = np.nan if status == S_SHIFTING else eng_rpm
      channels[i,O_CO2] = dl*F_tire_long*vehicle.co2_factor/vehicle.e_factor
      channels[i,O_AERO_MODE] = aero_mode
      if topped and i<n-2:
        channels[i,O_STATUS] = S_SUSTAINING
        channels[i:,:] = np.tile(channels[i,:], (n-i,1))
        for j in range(i+1,n):
          channels[j,O_TIME] += dl*(j-i)/v
          channels[j,O_DISTANCE] += dl*(j-i)
        break

      Nf = ( (vehicle.weight_bias)*vehicle.g*vehicle.mass
          + (vehicle.cp_bias[aero_mode])*vehicle.downforce(v,aero_mode)
          - vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
          - vehicle.drag(v,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )

      Nr = ( (1-vehicle.weight_bias)*vehicle.g*vehicle.mass
          + vehicle.downforce(v,aero_mode)*(1 - vehicle.cp_bias[aero_mode])
          + vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
          + vehicle.drag(v,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )


    # perform reverse integration to the beginning or vmax

    if vmax-vf > 1e-1:
      # print('doing braking... v=vf=%f' % vf)
      t_peak = t
      v = vf
      t = 0
      x = x0+dl*n
      a_long = 0
     
      for i in reversed(range(n)):
        aero_mode = AERO_BRK
        Nf = ( (vehicle.weight_bias)*vehicle.g*vehicle.mass
            + (vehicle.cp_bias[aero_mode])*vehicle.downforce(v,aero_mode)
            - vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
            - vehicle.drag(v,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )
        Nr = ( (1-vehicle.weight_bias)*vehicle.g*vehicle.mass
            + vehicle.downforce(v,aero_mode)*(1 - vehicle.cp_bias[aero_mode])
            + vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
            + vehicle.drag(v,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )

        # Calculate required lateral forces
        Ff_lat, Fr_lat, a_lat = self.compute_Ff_Fr(vehicle, v, a_long, sector, sector.curvature)

        # Calculate how much grip there is left
        remaining_long_grip = [vehicle.f_long_remain(2, Nr, Fr_lat, False)[0],vehicle.f_long_remain(2, Nf, Ff_lat, True)[0]]
        if min(remaining_long_grip) < 0:
          aero_mode = AERO_FULL
          Nf = ( (vehicle.weight_bias)*vehicle.g*vehicle.mass
            + (vehicle.cp_bias[aero_mode])*vehicle.downforce(v,aero_mode)
            - vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
            - vehicle.drag(v,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )
          Nr = ( (1-vehicle.weight_bias)*vehicle.g*vehicle.mass
              + vehicle.downforce(v,aero_mode)*(1 - vehicle.cp_bias[aero_mode])
              + vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
              + vehicle.drag(v,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )
          remaining_long_grip = [vehicle.f_long_remain(2, Nr, Fr_lat, False)[0],vehicle.f_long_remain(2, Nf, Ff_lat, True)[0]]

        ## Kinda sketchy. We enforce grip limit with the steady state limit now ##
        if remaining_long_grip[0] < 0:
          remaining_long_grip[0] = 0
        if remaining_long_grip[1] < 0:
          remaining_long_grip[1] = 0

        F_longitudinal = -sum(remaining_long_grip)-vehicle.drag(v,aero_mode)

        status = S_BRAKING
      
        a_long = F_longitudinal / vehicle.mass
        v = floor_sqrt(v**2 - 2*a_long*dl)

        # print(t,x,v,a_long/vehicle.g,a_lat/vehicle.g,F_tire_engine_limit,F_tire_long_available, F_tire_lat, N)

        if v > channels[i,O_VELOCITY]:
          for j in reversed(range(n)):
            if channels[j,O_TIME] < 0:
              channels[j,O_TIME] += channels[i,O_TIME] - t
          break

        t -= 1000 if v==0 else dl/v
        x -= dl

        # print(t,x,v,a_long,a_lat,F_tire_engine_limit,F_tire_long_available, F_tire_lat, N)

        channels[i,O_TIME]     = t
        channels[i,O_DISTANCE] = x
        channels[i,O_VELOCITY] = v
        channels[i,O_NR]       = Nr
        channels[i,O_NF]       = Nf
        channels[i,O_SECTORS]  = sector.i
        channels[i,O_STATUS]   = status
        channels[i,O_GEAR]     = np.nan
        channels[i,O_LONG_ACC] = a_long/vehicle.g
        channels[i,O_LAT_ACC]  = a_lat/vehicle.g
        channels[i,O_FF_REMAINING] = 0
        channels[i,O_FR_REMAINING] = 0
        channels[i,O_CURVATURE]    = sector.curvature
        channels[i,O_ENG_RPM]      = np.nan
        channels[i,O_CO2]          = 0
        channels[i,O_AERO_MODE]    = aero_mode

      else:
        for j in range(n):
          if channels[j,O_TIME] < 0:
            channels[j,O_TIME] += t0 - t
    
    if abs(channels[-1,O_VELOCITY] - min(vf,vmax)) < 1:
      channels[-1,O_VELOCITY] = min(vf,vmax)

    # find intersection point and splice

    # print('Straight from %.2f -> %.2f (%.2f real, %.2f limit) (%.4f s)' % (v0,vf,channels[-1,O_VELOCITY],vmax,channels[-1,O_TIME]-channels[0,O_TIME]))

    return channels, (v0-channels[0,O_VELOCITY] >= 1e-1) and (v0 != 0)
    
  def steady_corner(self, vehicle, sector):
    # solve a fuckton of physics
    v_lower = 0
    v_upper = vehicle.vmax
    v_cur   = (v_lower + v_upper)/2.0
    v_working = 1.0
    i = 0
    aero_mode = AERO_FULL

    Nf = 0
    Nr = 0
    F_tire_long_f = 0
    F_tire_long_r = 0
    F_tire_lat_f  = 0
    F_tire_lat_r  = 0

    while True:
      
      a_long = 0

      # Calculate normal force on each tire
      Nf = ( (vehicle.weight_bias)*vehicle.g*vehicle.mass
          + (vehicle.cp_bias[aero_mode])*vehicle.downforce(v_cur,aero_mode)
          - vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
          - vehicle.drag(v_cur,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )

      Nr = ( (1-vehicle.weight_bias)*vehicle.g*vehicle.mass
          + vehicle.downforce(v_cur,aero_mode)*(1 - vehicle.cp_bias[aero_mode])
          + vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
          + vehicle.drag(v_cur,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )

      # Calculate required lateral forces
      Ff_lat, Fr_lat, a_lat = self.compute_Ff_Fr(vehicle, v_cur, a_long, sector, sector.curvature)

      # Calculate how much grip there is left
      remaining_long_grip = [vehicle.f_long_remain(2, Nr, Fr_lat, False)[0],vehicle.f_long_remain(2, Nf, Ff_lat, True)[0]]
      # Calculate how much grip is needed
      F_req_long = a_long*vehicle.mass+vehicle.drag(v_cur,aero_mode)

      remaining_long_grip[0]-=F_req_long

      if min(remaining_long_grip) < 1e-1 and min(remaining_long_grip) >= 1e-3:
        break

      if min(remaining_long_grip) > 1e-3:
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
      Nf,
      0,
      Nr,
      0, 
      sector.i,
      S_SUSTAINING,
      np.nan, # no real 'gear'
      0, # no long. acc
      a_lat/vehicle.g, 
      0,
      0,
      remaining_long_grip[1]-Ff_lat,
      0,
      remaining_long_grip[0]-Fr_lat,
      0,
      sector.curvature,
      np.nan, # engine could be made but enh
      sector.length*F_req_long*vehicle.co2_factor/vehicle.e_factor,
      AERO_FULL]

    # print(sector,channels)

    channels = np.array(channels)

    return channels

  def solve(self, vehicle, sectors, output_0 = None, dl=0.2, closed_loop=False):
    # print('Sectors: %s' % repr(sectors))
    # print('Total Length: %f' % sum([x.length for x in sectors]))

    # solve all the corners
    steady_conditions = [None for i in sectors]
    steady_velocities = [vehicle.vmax for i in sectors]
    for i, sector in enumerate(sectors):
      if sector.curvature > 0:
        steady_conditions[i] = self.steady_corner(vehicle, sector)
        steady_velocities[i] = steady_conditions[i][O_VELOCITY]
    # print('Steady velocities: %s' % repr(steady_velocities))

    channel_stack = None
    starts = []

    if closed_loop:
      channels_start = np.array([
        0, # t
        0, # x
        min(steady_velocities[-1],steady_velocities[0]*0.95),
        0,
        0,
        0,
        0, 
        0,
        0,
        0, # no real 'gear'
        0, # no long. acc
        0, 
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0, # engine could be made but enh
        0,
        0])

      vf = vehicle.vmax
      if i+1<len(steady_velocities):
        vf = steady_velocities[i+1]
      elif closed_loop:
        vf = steady_velocities[-1]

      channels_corner, failed_start = self.drive(vehicle,
        sectors[0],
        channels_start,
        vf,
        steady_velocities[0], 
        dl, start=True)

      starts.append(0)
      channel_stack = channels_corner
    else:
      channels_corner, failed_start = self.drive(vehicle,
        sectors[0],
        None,
        vehicle.vmax if 1>=len(steady_velocities) else steady_velocities[1],
        steady_velocities[0], 
        dl, start=True)

      starts.append(0)
      channel_stack = channels_corner

    i = 1
    while i<len(sectors):
      # print(sectors[i])
      vf = vehicle.vmax
      if i+1>=len(steady_velocities):
        if closed_loop:
          vf = steady_velocities[0]
      else:
        vf = steady_velocities[i+1]

      channels_corner, failed_start = self.drive(vehicle,
        sectors[i],
        channel_stack[-1,:],
        vf,
        steady_velocities[i], dl)

      starts.append(channel_stack.shape[0])
      channel_stack = np.vstack((channel_stack,channels_corner))

      j = i-1
      ### DIDNT SUCCEED IN BRAKING ###
      while failed_start:
        ### KEEP WORKING BACKWARDS... ###
        # print('working backwards... (sec %d)' % j)
        k = j
        vstart = channels_corner[0,O_VELOCITY]
        if steady_velocities[k] < vstart:
          vstart = steady_velocities[k]
        
        channels_corner, success = self.brake(vehicle,
          sectors[j], # channels_f, t0, v0,
          channels_corner[0,:],
          channel_stack[starts[j],O_TIME],
          vstart,
          dl)
        failed_start = not success

        dt = (channels_corner[-1,O_TIME] - channels_corner[0,O_TIME]) - (channel_stack[starts[j+1],O_TIME]-channel_stack[starts[j],O_TIME])

        failed_start = not success
        after = channel_stack[starts[j+1]:,:]
        after[:,O_TIME] += dt

        channel_stack = np.vstack((channel_stack[:starts[j],:], channels_corner))
        channel_stack = np.vstack((channel_stack, after))

        di = (channels_corner.shape[0]) - (starts[j+1]-starts[j])
        k = j+1
        while k < len(starts):
          starts[k] += di
          k+=1
        
        j-=1

      i+=1

    channel_stack[:,O_CO2] = np.cumsum(channel_stack[:,O_CO2])

    return channel_stack

  def steady_solve(self, vehicle, segments, dl=0.2):
    return self.solve(vehicle, segments, dl=dl, closed_loop=True)