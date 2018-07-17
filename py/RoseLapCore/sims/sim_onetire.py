import numpy as np
import math

from constants import *
import logging

"""
Point mass model
It's a unicycle! Fast, right?
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

class sim_onetire:
  def __init__(self):
    pass

  def step(self, vehicle, prior_result, segment, segment_next, brake, shifting, gear):
    """
    Takes a vehicle step. Picks the aerodynamic strategy that works out to be the best.
    See substep for return value. If no aero strategy is valid, returns None, else returns the best.
    """
    # return self.substep(vehicle, prior_result, segment, segment_next, brake, shifting, gear, AERO_FULL)
    if brake:
      if abs(vehicle.downforce(prior_result[O_VELOCITY],AERO_BRK)-vehicle.downforce(prior_result[O_VELOCITY],AERO_FULL)) < 1e-3 and abs(vehicle.drag(prior_result[O_VELOCITY],AERO_BRK)-vehicle.drag(prior_result[O_VELOCITY],AERO_FULL)) < 1e-3: 
          return self.substep(vehicle, prior_result, segment, segment_next, brake, shifting, gear, AERO_FULL)
      out_brk = self.substep(vehicle, prior_result, segment, segment_next, brake, shifting, gear, AERO_BRK)
      out_nor = self.substep(vehicle, prior_result, segment, segment_next, brake, shifting, gear, AERO_FULL)
      if out_nor is not None:
        if out_brk is not None:
          if out_brk[O_VELOCITY] < out_nor[O_VELOCITY]:
            return out_brk
          else:
            return out_nor
        else:
          return out_nor
      elif out_brk is not None:
        return out_brk
      else:
        return None
    else:
      if abs(vehicle.downforce(prior_result[O_VELOCITY],AERO_DRS)-vehicle.downforce(prior_result[O_VELOCITY],AERO_FULL)) < 1e-3 and abs(vehicle.drag(prior_result[O_VELOCITY],AERO_DRS)-vehicle.drag(prior_result[O_VELOCITY],AERO_FULL)) < 1e-3: 
          return self.substep(vehicle, prior_result, segment, segment_next, brake, shifting, gear, AERO_FULL)
      out_drs = self.substep(vehicle, prior_result, segment, segment_next, brake, shifting, gear, AERO_DRS)
      out_nor = self.substep(vehicle, prior_result, segment, segment_next, brake, shifting, gear, AERO_FULL)
      if out_nor is not None:
        if out_drs is not None:
          if out_drs[O_VELOCITY] > out_nor[O_VELOCITY]:
            return out_drs
          else:
            return out_nor
        else:
          return out_nor
      elif out_drs is not None:
        return out_drs
      else:
        return None


    
  def substep(self, vehicle, prior_result, segment, segment_next, brake, shifting, gear, aero_mode):
    """
    Takes a vehicle step. Returns (see last line) if successful, returns None if vehicle skids off into a wall.
    @param v0 the initial vehicle speed for this step
    @param segment the Segment of the track the vehicle is on
    @param brake a boolean value specifying whether or not to apply the brakes (with full available force)
    @param shifting a shifting status code
    """

    # Initialize values to those from the previous step
    v0 = prior_result[O_VELOCITY];
    x0 = prior_result[O_DISTANCE];
    t0 = prior_result[O_TIME];
    status = S_TOPPED_OUT;
    co2_elapsed = prior_result[O_CO2];

    
    # How much grip is needed to keep the car from skidding away
    Ftire_lat = derate_curvature(segment.curvature,vehicle.r_add)*vehicle.mass*v0**2

    # Determine the remaining longitudinal grip. If there isn't any, then we're out of luck.
    Ftire_remaining, Ftire_max_long = vehicle.f_long_remain(4, vehicle.mass*vehicle.g+vehicle.downforce(v0,aero_mode), Ftire_lat)
    if Ftire_remaining < 0:
      return None

    # Determine how much force the engine can produce.
    Ftire_engine_limit, eng_rpm = vehicle.eng_force(v0, int(gear))

    if brake:
      status = S_BRAKING
      Ftire_long = -Ftire_remaining
      gear = np.nan
    elif shifting:
      status = S_SHIFTING
      Ftire_long = 0
      gear = np.nan
    else:
      # This logic helps absorb simulation oscillations (brake-accel oscillation on corners)
      # If there's curvature, and we were braking before (we are not anymore) or we were sustaining before with negligible curvature change, continue sustaining
       # 
      if segment.curvature > 0 and (prior_result[O_CURVATURE] - segment.curvature)>=0 and (prior_result[O_STATUS] == S_BRAKING or prior_result[O_STATUS] == S_SUSTAINING):
        status = S_SUSTAINING
        Ftire_long = vehicle.drag(v0, aero_mode)
      else:
        status = S_ENG_LIM_ACC
        Ftire_long = Ftire_engine_limit
        if Ftire_long <= vehicle.drag(v0, aero_mode):
          status = S_DRAG_LIM

      if Ftire_long > Ftire_remaining:
        status = S_TIRE_LIM_ACC
        Ftire_long = Ftire_remaining
      if eng_rpm > vehicle.engine_rpms[-1]:
        status = S_TOPPED_OUT

    # Determine the longitudinal force and resulting vehicle acceleration
    F_longitudinal = Ftire_long - vehicle.drag(v0, aero_mode)
    a_long = F_longitudinal / vehicle.mass

    try:
      vf = floor_sqrt(v0**2 + 2*a_long*segment.length)
      vfmax = floor_sqrt(v0**2 + 2*(Ftire_engine_limit - vehicle.drag(v0, aero_mode))/vehicle.mass*segment.length)
      vfmin = floor_sqrt(v0**2 + 2*(-Ftire_remaining - vehicle.drag(v0, aero_mode))/vehicle.mass*segment.length)
    except:
      # This try-except block probably isn't needed
      a_long=0
      vf=0
      vfmax=0

    # Use bisection to generate tire limit for sustaining, since there is no explicit solution
    if (not brake and shifting != IN_PROGRESS and self.compute_excess(vehicle,segment_next,vf,aero_mode) < 0) or status==S_SUSTAINING:
      vfu = min(vf*1.3, vfmax)
      vfb = max(vf*0.5, vfmin)
      vf = min(vf, vfmax)
      excess = self.compute_excess(vehicle, segment_next, vf, aero_mode)

      n = 50
      while excess<1e-3 or excess>1e-1:
        # print excess
        if (excess<0):
          vfu = vf
        else:
          vfb = vf
        vf = (vfu+vfb)/2
        n-=1
        if n <= 0:
          if excess<0:
            return None
          else:
            break
        excess = self.compute_excess(vehicle, segment_next, vf, aero_mode)

      status = S_SUSTAINING
      a_long = (vf**2-v0**2)/2/segment.length
    vavg = ((v0+vf)/2)
    if vavg > 0:
      tf = t0 + segment.length/vavg
    else:
      tf = t0
    xf = x0 + segment.length

    if not (brake or shifting):
      co2_elapsed += segment.length*F_longitudinal*vehicle.co2_factor/vehicle.e_factor

    # output = np.array([
    #   tf,
    #   xf,
    #   vf,
    #   vehicle.mass*vehicle.g + vehicle.downforce(v0,aero_mode),
    #   0,
    #   segment.sector,
    #   status,
    #   gear,
    #   a_long / vehicle.g, 
    #   (vavg ** 2) * derate_curvature(segment.curvature,vehicle.r_add) / vehicle.g, 
    #   Ftire_remaining,
    #   0,
    #   segment.curvature,
    #   eng_rpm,
    #   co2_elapsed,
    #   aero_mode
    # ])

    output = np.array([
      tf,
      xf,
      vf,
      0,
      0,
      vehicle.mass*vehicle.g + vehicle.downforce(v0,aero_mode),
      0, 
      segment.sector,
      status,
      gear,
      a_long / vehicle.g, 
      (v0 ** 2) * derate_curvature(segment.curvature, vehicle.r_add) / vehicle.g, 
      0,
      0,
      0,
      0,
      Ftire_remaining,
      0,
      segment.curvature,
      eng_rpm,
      co2_elapsed,
      aero_mode
    ])

    return output

  def compute_excess(self, vehicle, segment, vf, aero_mode):
    # Returns how much tire grip there is after that needed to overcome drag
    return vehicle.f_long_remain(4, vehicle.mass*vehicle.g+vehicle.downforce(vf, aero_mode), vehicle.mass*vf**2*derate_curvature(segment.curvature,vehicle.r_add))[0] - vehicle.drag(vf, aero_mode)

  def solve(self, vehicle, segments, output_0 = None):
    logging.debug("Segments is %d long" % len(segments))
    logging.debug("Gear ratio is %.5f" % vehicle.final_drive_reduction)
    # set up initial stuctures
    output = np.zeros((len(segments), O_MATRIX_COLS))
    precrash_output = np.zeros((len(segments), O_MATRIX_COLS))
    shifting = NOT_SHIFTING
    
    if output_0 is None:
      output[0,O_NF] = vehicle.mass*vehicle.g
      gear = vehicle.best_gear(output[0,O_VELOCITY], np.inf)
    else:
      output[0,:] = output_0
      output[0,O_TIME] = 0
      output[0,O_DISTANCE] = 0
      gear = vehicle.best_gear(output_0[O_VELOCITY], output_0[O_FR_REMAINING])

    brake = False
    shiftpt = -1
    shift_v_req = 0
    
    step_result = self.step(vehicle, output[0], segments[0], segments[1], brake, shiftpt>=0, gear)

    output[0] = step_result

    # step loop set up
    i = 1
    backup_amount = int(7.0/segments[0].length)
    bounds_found = False
    failpt = -1
    precrash_i = -1
    middle_brake_bound = -1
    lower_brake_bound = -1
    upper_brake_bound = -1

    while i<len(segments):
      if i<0:
        print('damnit bobby')
        output[:] = np.nan 
        return output
      if (gear is None) and shiftpt < 0:
        gear = vehicle.best_gear(output[i-1,O_VELOCITY], output[i,O_FF_REMAINING])

      step_result = self.step(vehicle,output[i-1,:], segments[i], (segments[i+1] if i+1<len(segments) else segments[i]), brake, shiftpt>=0, gear)
      if step_result is None:
        #print('crash at',i)
        if not brake:
          # Start braking
          del precrash_output
          precrash_output = np.copy(output)
          precrash_i = i
          brake = True
          bounds_found = False
          failpt = i
          # while segments[failpt-1].curvature < segments[failpt].curvature and failpt<len(segments):
          #   failpt += 1
          lower_brake_bound = i
          i = lower_brake_bound
        elif bounds_found:
          upper_brake_bound = middle_brake_bound

          middle_brake_bound = int((upper_brake_bound + lower_brake_bound) / 2)
          
          i = middle_brake_bound
          del output
          output = np.copy(precrash_output)
        else:
          # Try again from an earlier point
          lower_brake_bound-=backup_amount
          i = lower_brake_bound
          del output
          output = np.copy(precrash_output)
        # reset shifting params
        gear = None
        shiftpt = -1
      elif i<=failpt:
        output[i] = step_result
        i+=1
        brake = True
        # reset shifting params
        gear = None
        shiftpt = -1
        shift_v_req = 0
      elif failpt>=0 and not bounds_found:
        bounds_found = True

        upper_brake_bound = precrash_i-1 #lower_brake_bound+backup_amount

        middle_brake_bound = int((upper_brake_bound+lower_brake_bound)/2)
        
        i = middle_brake_bound
        del output
        output = np.copy(precrash_output)
      elif failpt>=0 and bounds_found and abs(lower_brake_bound - upper_brake_bound) > 1:
        lower_brake_bound = middle_brake_bound

        middle_brake_bound = int((upper_brake_bound+lower_brake_bound)/2)
        
        i = middle_brake_bound
        del output
        output = np.copy(precrash_output)
      else:
        # normal operation

        # quit braking
        brake = False # problematic??
        failpt = -1
        lower_brake_bound = -1
        upper_brake_bound = -1
        bounds_found = False

        output[i] = step_result

        better_gear = vehicle.best_gear(output[i,O_VELOCITY], output[i,O_FF_REMAINING])

        if shiftpt < 0 and gear != better_gear and output[i,O_STATUS]==S_ENG_LIM_ACC and output[i,O_VELOCITY]>shift_v_req:
          gear += int((better_gear-gear)/abs(better_gear-gear))
          shiftpt = i
          shift_v_req = output[i,O_VELOCITY]*1.01
        elif shiftpt < 0 and output[i,O_STATUS]==S_TOPPED_OUT and gear<len(vehicle.gears)-1:
          gear += 1
          shiftpt = i
          shift_v_req = output[i,O_VELOCITY]*1.01

        if shiftpt >= 0 and output[i,O_TIME] > output[shiftpt,O_TIME]+vehicle.shift_time:
          shiftpt = -1
          i-=1
        
        i+=1

    #np.savetxt('dump.csv', output, delimiter=",")
    return output

  def steady_solve(self, vehicle, segments):
    output = self.solve(vehicle,segments)
    output[-1,O_VELOCITY] = output[-1,O_VELOCITY]*0.95
    return self.solve(vehicle,segments,output[-1, :])

  def colorgen(num_colors, idx):
    color_norm  = colors.Normalize(vmin=0, vmax=num_colors-1)
    scalar_map = cmx.ScalarMappable(norm=color_norm, cmap='hsv') 
    def map_index_to_rgb_color(index):
      return scalar_map.to_rgba(index)
    return map_index_to_rgb_color(idx)
