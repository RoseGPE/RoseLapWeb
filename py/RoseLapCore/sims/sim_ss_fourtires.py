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

class sim_ss_fourtires:
  def __init__(self):
    pass

  def compute_Ff_Fr(self, N, vehicle, v, a_long, segment, prior_curvature):
    alpha = v**2*(derate_curvature(segment.curvature, vehicle.r_add)-derate_curvature(prior_curvature, vehicle.r_add))/segment.length + segment.curvature*a_long
    a_lat = derate_curvature(segment.curvature, vehicle.r_add)*v**2
    kf = vehicle.k_roll_front
    kr = vehicle.k_roll_rear
    kcf = vehicle.k_chassis/(vehicle.weight_bias)
    kcr = vehicle.k_chassis/(1-vehicle.weight_bias)

    Mint = a_lat*vehicle.mass*vehicle.cg_height
    Mf = Mint*kcf*kf*(kcr+kr)/(kcf*kcr*kf+kcf*kcr*kr+kcf*kf*kr+kcr*kf*kr)
    Mr = Mint*kcr*kr*(kcf+kf)/(kcf*kcr*kf+kcf*kcr*kr+kcf*kf*kr+kcr*kf*kr)

    Nf1 = N[0]/2 - Mf/vehicle.track_front
    Nf2 = N[0]/2 + Mf/vehicle.track_front
    Nr1 = N[1]/2 - Mr/vehicle.track_rear
    Nr2 = N[1]/2 + Mr/vehicle.track_rear

    Ff_lat = (vehicle.weight_bias)*a_lat*vehicle.mass - alpha*vehicle.moi_yaw/vehicle.wheelbase_length
    Fr_lat = (1-vehicle.weight_bias)*a_lat*vehicle.mass + alpha*vehicle.moi_yaw/vehicle.wheelbase_length

    return (Nf1, Nf2, Nr1, Nr2, Ff_lat, Fr_lat, alpha, a_lat)

  def brake(self, vehicle, sector, channels_f, t0, v0, dl=0.1):
    vf = channels_f[O_VELOCITY]
    tf = channels_f[O_TIME]
    xf = channels_f[O_DISTANCE]

    # Nf1 = channels_f[O_NF]
    # Nf2 = channels_f[O_NF2]
    # Nr1 = channels_f[O_NR]
    # Nr2 = channels_f[O_NR2]

    a_long = channels_f[O_LONG_ACC]*vehicle.g

    n = int(sector.length/dl)
    channels = np.zeros((n, O_MATRIX_COLS))
    v = vf
    t = 0
    x = xf
    success = False
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

      N = [Nf,Nr]
      Nf1, Nf2, Nr1, Nr2, Ff_lat, Fr_lat, alpha, a_lat = self.compute_Ff_Fr(N, vehicle, v, a_long, sector, sector.curvature)

      # Calculate how much grip there is left
      Ff_remaining,_ = vehicle.f_long_remain_pair([Nf1,Nf2], Ff_lat, True)
      Fr_remaining,_ = vehicle.f_long_remain_pair([Nr1,Nr2], Fr_lat, False)
      remaining_long_grip = Ff_remaining+Fr_remaining

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

        N = [Nf,Nr]
        Nf1, Nf2, Nr1, Nr2, Ff_lat, Fr_lat, alpha, a_lat = self.compute_Ff_Fr(N, vehicle, v, a_long, sector, sector.curvature)

        # Calculate how much grip there is left
        Ff_remaining,_ = vehicle.f_long_remain_pair([Nf1,Nf2], Ff_lat, True)
        Fr_remaining,_ = vehicle.f_long_remain_pair([Nr1,Nr2], Fr_lat, False)
        remaining_long_grip = Ff_remaining+Fr_remaining

      ## Kinda sketchy. We enforce grip limit with the steady state limit now ##
      for j in range(4):
        if remaining_long_grip[j] < 0:
          remaining_long_grip[j] = 0

      F_tire_long = -sum(remaining_long_grip)

      F_longitudinal = F_tire_long - vehicle.drag(v, aero_mode)

      status = S_BRAKING
    
      a_long = F_longitudinal / vehicle.mass
      v = floor_sqrt(v**2 - 2*a_long*dl)

      # if v <= 0:
      #   print('hello, this is v=0 in brake')

      if success:
        status = S_SUSTAINING
        v = v0
      elif v > v0:
        # print('Sucessful brake from %.3f -> %.3f' % (v0,vf))
        success = True
        v = v0

      t -= 1000 if v==0 else dl/v
      x -= dl

      channels[i,O_TIME]     = t
      channels[i,O_DISTANCE] = x
      channels[i,O_VELOCITY] = v
      channels[i,O_NR]       = Nr1
      channels[i,O_NR2]       = Nr2
      channels[i,O_NF]       = Nf1
      channels[i,O_NF2]       = Nf2
      channels[i,O_SECTORS]  = sector.i
      channels[i,O_STATUS]   = status
      channels[i,O_GEAR]     = np.nan
      channels[i,O_LONG_ACC] = a_long/vehicle.g
      channels[i,O_LAT_ACC]  = a_lat/vehicle.g
      channels[i,O_YAW_ACC]  = alpha
      channels[i,O_FF_REMAINING] = 0
      channels[i,O_FF2_REMAINING] = 0
      channels[i,O_FR_REMAINING] = 0
      channels[i,O_FR2_REMAINING] = 0
      channels[i,O_CURVATURE]    = sector.curvature
      channels[i,O_ENG_RPM]      = np.nan
      channels[i,O_CO2]          = 0
      channels[i,O_AERO_MODE]    = aero_mode

      if success and i > 2:
        channels[i,O_STATUS] = S_SUSTAINING
        channels[:i,:] = np.tile(channels[i,:], (i,1))
        for j in range(0,i):
          channels[j,O_TIME] -= dl*(i-j)/v
          channels[j,O_DISTANCE] += dl*(i-j)
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
    v=v0+0
    t=t0+0
    x=x0+0
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

      N = [Nf,Nr]
      Nf1, Nf2, Nr1, Nr2, Ff_lat, Fr_lat, alpha, a_lat = self.compute_Ff_Fr(N, vehicle, v, a_long, sector, sector.curvature)

      # Calculate how much grip there is left
      Ff_remaining,_ = vehicle.f_long_remain_pair([Nf1,Nf2], Ff_lat, True)
      Fr_remaining,_ = vehicle.f_long_remain_pair([Nr1,Nr2], Fr_lat, False)
      remaining_long_grip = Ff_remaining+Fr_remaining

      

      ## Calculate best gear and remaining grip, and if a shift is called for ##
      best_gear = vehicle.best_gear(v, np.inf)
      if best_gear != gear and v > v_shift:
        gear += (best_gear-gear)/abs(best_gear-gear)
        t_shift = t+vehicle.shift_time
        v_shift = v*1.01
      F_tire_engine_limit, eng_rpm = vehicle.eng_force(v, int(gear))

      if min(remaining_long_grip[:2]) < 0 or min(remaining_long_grip[2:]) < F_tire_engine_limit:
        # print('resorting to full aero', remaining_long_grip)
        aero_mode = AERO_FULL
        Nf = ( (vehicle.weight_bias)*vehicle.g*vehicle.mass
            + (vehicle.cp_bias[aero_mode])*vehicle.downforce(v,aero_mode)
            - vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
            - vehicle.drag(v,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )
        Nr = ( (1-vehicle.weight_bias)*vehicle.g*vehicle.mass
            + vehicle.downforce(v,aero_mode)*(1 - vehicle.cp_bias[aero_mode])
            + vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
            + vehicle.drag(v,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )

        N = [Nf,Nr]
        Nf1, Nf2, Nr1, Nr2, Ff_lat, Fr_lat, alpha, a_lat = self.compute_Ff_Fr(N, vehicle, v, a_long, sector, sector.curvature)

        # Calculate how much grip there is left
        Ff_remaining,_ = vehicle.f_long_remain_pair([Nf1,Nf2], Ff_lat, True)
        Fr_remaining,_ = vehicle.f_long_remain_pair([Nr1,Nr2], Fr_lat, False)
        remaining_long_grip = Ff_remaining+Fr_remaining

      ## Kinda sketchy. We enforce grip limit with the steady state limit now ##
      frontlim = False
      for j in range(4):
        if remaining_long_grip[j] < 0:
          remaining_long_grip[j] = 0
          if j>=2:
            frontlim = True

      if t < t_shift:
        ### CURRENTLY SHIFTING, NO POWER! ### 
        status = S_SHIFTING
        F_tire_long = 0
      else:
        if t_shift > 0:
          t_shift = -1

        F_tire_long = F_tire_engine_limit
        status = S_ENG_LIM_ACC
        if frontlim:
          status = S_TIRE_LIM_ACC
        if F_tire_long > sum(remaining_long_grip[2:]):
          status = S_TIRE_LIM_ACC
          F_tire_long = sum(remaining_long_grip[2:])
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
      channels[i,O_NF] = Nf1
      channels[i,O_NF2] = Nf2
      channels[i,O_NR] = Nr1
      channels[i,O_NR2] = Nr2
      channels[i,O_SECTORS]  = sector.i
      channels[i,O_STATUS]   = status
      channels[i,O_GEAR]     = np.nan if status == S_SHIFTING else gear
      channels[i,O_LONG_ACC] = a_long/vehicle.g
      channels[i,O_LAT_ACC]  = a_lat/vehicle.g
      channels[i,O_YAW_ACC]  = alpha
      channels[i,O_FF_REMAINING] = frem_filter(remaining_long_grip[0])
      channels[i,O_FF2_REMAINING] = frem_filter(remaining_long_grip[1])
      channels[i,O_FR_REMAINING] = frem_filter(remaining_long_grip[2])
      channels[i,O_FR2_REMAINING] = frem_filter(remaining_long_grip[3])
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

        N = [Nf,Nr]
        Nf1, Nf2, Nr1, Nr2, Ff_lat, Fr_lat, alpha, a_lat = self.compute_Ff_Fr(N, vehicle, v, a_long, sector, sector.curvature)

        # Calculate how much grip there is left
        Ff_remaining,_ = vehicle.f_long_remain_pair([Nf1,Nf2], Ff_lat, True)
        Fr_remaining,_ = vehicle.f_long_remain_pair([Nr1,Nr2], Fr_lat, False)
        remaining_long_grip = Ff_remaining+Fr_remaining

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

          N = [Nf,Nr]
          Nf1, Nf2, Nr1, Nr2, Ff_lat, Fr_lat, alpha, a_lat = self.compute_Ff_Fr(N, vehicle, v, a_long, sector, sector.curvature)

          # Calculate how much grip there is left
          Ff_remaining,_ = vehicle.f_long_remain_pair([Nf1,Nf2], Ff_lat, True)
          Fr_remaining,_ = vehicle.f_long_remain_pair([Nr1,Nr2], Fr_lat, False)
          remaining_long_grip = Ff_remaining+Fr_remaining

        # print('AERO MODE: %d, GRIP: %s' % (aero_mode, remaining_long_grip))

        ## Kinda sketchy. We enforce grip limit with the steady state limit now ##
        for j in range(4):
          if remaining_long_grip[j] < 0:
            remaining_long_grip[j] = 0

        F_tire_long = -sum(remaining_long_grip)

        F_longitudinal = F_tire_long - vehicle.drag(v, aero_mode)

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

        # if v <= 0:
        #   print('hello, this is v=0 in drive.brake')

        # print(t,x,v,a_long,a_lat,F_tire_engine_limit,F_tire_long_available, F_tire_lat, N)

        channels[i,O_TIME]     = t
        channels[i,O_DISTANCE] = x
        channels[i,O_VELOCITY] = v
        channels[i,O_NR]       = Nr1
        channels[i,O_NR2]       = Nr2
        channels[i,O_NF]       = Nf1
        channels[i,O_NF2]       = Nf2
        channels[i,O_SECTORS]  = sector.i
        channels[i,O_STATUS]   = status
        channels[i,O_GEAR]     = np.nan
        channels[i,O_LONG_ACC] = a_long/vehicle.g
        channels[i,O_LAT_ACC]  = a_lat/vehicle.g
        channels[i,O_YAW_ACC]  = alpha
        channels[i,O_FF_REMAINING] = 0
        channels[i,O_FF2_REMAINING] = 0
        channels[i,O_FR_REMAINING] = 0
        channels[i,O_FR2_REMAINING] = 0
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

      N = [Nf,Nr]
      Nf1, Nf2, Nr1, Nr2, Ff_lat, Fr_lat, alpha, a_lat = self.compute_Ff_Fr(N, vehicle, v_cur, a_long, sector, sector.curvature)

      # Calculate how much grip there is left
      Ff_remaining,_ = vehicle.f_long_remain_pair([Nf1,Nf2], Ff_lat, True)
      Fr_remaining,_ = vehicle.f_long_remain_pair([Nr1,Nr2], Fr_lat, False)
      remaining_long_grip = Ff_remaining+Fr_remaining

      F_req_long = vehicle.drag(v_cur, AERO_FULL)
      remaining_long_grip[2] -= F_req_long/2
      remaining_long_grip[3] -= F_req_long/2

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
      Nf1,
      Nf2,
      Nr1,
      Nr2, 
      sector.i,
      S_SUSTAINING,
      np.nan, # no real 'gear'
      0, # no long. acc
      a_lat/vehicle.g, 
      0,
      0,
      remaining_long_grip[0],
      remaining_long_grip[1],
      remaining_long_grip[2],
      remaining_long_grip[3],
      sector.curvature,
      np.nan, # engine could be made but enh
      sector.length*F_req_long*vehicle.co2_factor/vehicle.e_factor,
      AERO_FULL]

    # print(sector,channels)

    channels = np.array(channels)
    return channels

  def solve(self, vehicle, sectors, output_0 = None, dl=0.2):
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
      channels_corner, failed_start = self.drive(vehicle,
        sectors[i],
        channel_stack[-1,:],
        vehicle.vmax if i+1>=len(steady_velocities) else steady_velocities[i+1],
        steady_velocities[i], dl)
      # print(channels_corner)

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

  def steady_solve(self, vehicle, segments):
    pass