import numpy as np
import math

from constants import *

"""
Two tire model
Imagine a point mass with two tires, that's this model!
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

class sim_twotires:
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

  def compute_Ff_Fr(self, vehicle, v, a_long, segment, prior_curvature):
    alpha = v**2*(derate_curvature(segment.curvature, vehicle.r_add)-derate_curvature(prior_curvature, vehicle.r_add))/segment.length + segment.curvature*a_long
    a_lat = derate_curvature(segment.curvature, vehicle.r_add)*v**2

    Ff_lat = (vehicle.weight_bias)*a_lat*vehicle.mass - alpha*vehicle.moi_yaw/vehicle.wheelbase_length
    Fr_lat = (1-vehicle.weight_bias)*a_lat*vehicle.mass + alpha*vehicle.moi_yaw/vehicle.wheelbase_length

    return (Ff_lat, Fr_lat)
    
  def substep(self, vehicle, prior_result, segment, segment_next, brake, shifting, gear, aero_mode):
    """
    Takes a vehicle step. Returns (see last line) if successful, returns None if vehicle skids off into a wall.
    @param v0 the initial vehicle speed for this step
    @param segment the Segment of the track the vehicle is on
    @param brake a boolean value specifying whether or not to apply the brakes (with full available force)
    @param shifting a shifting status code
    """

    # Initialize values to those from the previous step
    Nf = prior_result[O_NF];
    Nr = prior_result[O_NR];
    v0 = prior_result[O_VELOCITY];
    x0 = prior_result[O_DISTANCE];
    t0 = prior_result[O_TIME];
    a_long = prior_result[O_LONG_ACC]*vehicle.g
    co2_elapsed = prior_result[O_CO2];
    status = S_TOPPED_OUT

    

    # Determine how much grip is used keeping the car from skidding away
    Ff_lat, Fr_lat = self.compute_Ff_Fr(vehicle, v0, a_long, segment, prior_result[O_CURVATURE])

    # Determine the remaining longitudinal grip. If there isn't any, then we're out of luck.
    Ff_remaining, Ff_max_long = vehicle.f_long_remain(2, Nf, Ff_lat, True)
    Fr_remaining, Fr_max_long = vehicle.f_long_remain(2, Nr, Fr_lat, False)
    if Ff_remaining < 0 or Fr_remaining < 0:
      # print('failpt A')
      return None

    # Determine how much force the engine can produce.
    Fr_engine_limit, eng_rpm = vehicle.eng_force(v0, int(gear))

    # Initialize these values which will be overriden later asneedbe.
    Ff_long = 0
    Fr_long = 0
    F_longitudinal = 0

    if brake:
      # Two different brake strategies: Perfect biasing and static bias
      status = S_BRAKING
      if vehicle.perfect_brake_bias:
        Fr_long = -Fr_remaining
        Ff_long = -Ff_remaining
      else:
        # Find which tire limits the force, and base force off of it
        F_brake = min(Ff_remaining/vehicle.front_brake_bias(), Fr_remaining/vehicle.rear_brake_bias())
        Fr_long = -F_brake*vehicle.rear_brake_bias()
        Ff_long = -F_brake*vehicle.front_brake_bias()
      # Gear is undefined when shifting
      gear = np.nan
    elif shifting:
      # No force (or gear) when you're shifting
      status = S_SHIFTING
      Fr_long = 0
      Ff_long = 0
      gear = np.nan
    else:
      # @FIXME NOT PLAYED AROUND WITH ENOUGH WITH TWO TIRE MODEL!!!!
      # This logic helps absorb simulation oscillations (brake-accel oscillation on corners)
      # If there's curvature, and we were braking before (we are not anymore) or we were sustaining before with negligible curvature change, continue sustaining
      if segment.curvature > 0 and (prior_result[O_STATUS] == S_BRAKING  or ((segment.curvature-prior_result[O_CURVATURE])>=0 and prior_result[O_STATUS] == S_SUSTAINING)):
        status = S_SUSTAINING
        Fr_long = vehicle.drag(v0, aero_mode)
      # If not sustaining, jammalam that throttle
      else:
        status = S_ENG_LIM_ACC
        Fr_long = Fr_engine_limit
        if Fr_long <= vehicle.drag(v0, aero_mode):
          status = S_DRAG_LIM

      # Still not allowed to use more force than your tire can provide
      if Fr_long > Fr_remaining:
        status = S_TIRE_LIM_ACC
        Fr_long = Fr_remaining

      if eng_rpm > vehicle.engine_rpms[-1]:
        status = S_TOPPED_OUT  

    # Determine the longitudinal force and resulting acceleration
    F_longitudinal = Ff_long + Fr_long - vehicle.drag(v0, aero_mode)
    a_long = F_longitudinal / vehicle.mass

    # Determine the vehicle velocity after said acceleration
    vf = floor_sqrt(v0**2 + 2*a_long*segment.length)

    # Also determine limits for top and low speeds if grip were reassigned
    vfu = floor_sqrt(v0**2 + 2*(Fr_engine_limit - vehicle.drag(v0, aero_mode))/vehicle.mass*segment.length)
    vfl = floor_sqrt(v0**2 + 2*(-Ff_remaining -Fr_remaining - vehicle.drag(v0, aero_mode))/vehicle.mass*segment.length)

    
    # Calculate normal force on each tire
    Nf = ( (vehicle.weight_bias)*vehicle.g*vehicle.mass
        + (vehicle.cp_bias[aero_mode])*vehicle.downforce(vf,aero_mode)
        - vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
        - vehicle.drag(vf,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )

    Nr = ( (1-vehicle.weight_bias)*vehicle.g*vehicle.mass
        + vehicle.downforce(vf,aero_mode)*(1-vehicle.cp_bias[aero_mode])
        + vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
        + vehicle.drag(vf,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )

    # Determine lateral force requirements
    Ff_lat, Fr_lat = self.compute_Ff_Fr(vehicle, vf, a_long, segment_next, segment.curvature)

    # Figure out how much longitudinal grip remains
    remaining_long_grip = min(vehicle.f_long_remain(2, Nr, Fr_lat, False)[0], vehicle.f_long_remain(2, Nf, Ff_lat, True)[0])

    # Loop through a range of acceleration possiblities if the result from this step was invalid (try to fix this step)
    # This was bisection in single tire (for sustaining usage) but I couldn't get that to work here. Thus dumb iteration.
    vf_working = None
    N_ITERS = 25
    if remaining_long_grip < 0:
      # If we were scheduled to coast, we're not using our tires anyways, so we're kinda screwed anyways. 
      # @FIXME: THIS MIGHT BE THE PROBLEM!!!!!!! If you are midway through a shift when you hit a corner, there's no recourse. Not sure how to solve.
      if shifting == IN_PROGRESS and not brake:
        # print('failpt B')
        vfu = floor_sqrt(v0**2 + 2*(- vehicle.drag(v0, aero_mode))/vehicle.mass*segment.length)
        return None
      valid_entries = []
      for n in range(N_ITERS):
        vf = (vfu+vfl)/2

        # Prescribe an acceleration
        a_long = (vf**2-v0**2)/2/segment.length

        # Calculate normal force on each tire
        Nf = ( (vehicle.weight_bias)*vehicle.g*vehicle.mass
            + (vehicle.cp_bias[aero_mode])*vehicle.downforce(vf,aero_mode)
            - vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
            - vehicle.drag(vf,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )

        Nr = ( (1-vehicle.weight_bias)*vehicle.g*vehicle.mass
            + vehicle.downforce(vf,aero_mode)*(1 - vehicle.cp_bias[aero_mode])
            + vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
            + vehicle.drag(vf,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )

        # Calculate required lateral forces
        Ff_lat, Fr_lat = self.compute_Ff_Fr(vehicle, vf, a_long, segment_next, segment.curvature)

        # Calculate how much grip there is left
        remaining_long_grip = [vehicle.f_long_remain(2, Nr, Fr_lat, False)[0],vehicle.f_long_remain(2, Nf, Ff_lat, True)[0]]
        # Calculate how much grip is needed
        F_req_long = a_long*vehicle.mass+vehicle.drag(vf,aero_mode)

        # Calculate how grip has to be distributed
        if F_req_long < 0:
          status = S_BRAKING
          if vehicle.perfect_brake_bias:
            order = np.argsort(remaining_long_grip)
            if remaining_long_grip[order[0]] < F_req_long:
              F_req_long -= remaining_long_grip[order[0]]
              remaining_long_grip[order[0]] = 0
            else:
              remaining_long_grip[order[0]] -= F_req_long
              F_req_long = 0
            remaining_long_grip[order[1]] -= F_req_long
          else:
            F_brake = -F_req_long
            remaining_long_grip[0] -= F_brake*vehicle.rear_brake_bias()
            remaining_long_grip[1] -= F_brake*vehicle.front_brake_bias()
        else:
          # If this requires more force than the engine will allow (for some reason) then move along, it's not working out.
          status = S_TIRE_LIM_ACC
          remaining_long_grip[0]-=F_req_long

        if brake:
          if remaining_long_grip[0] >= 0 and remaining_long_grip[1] >=0:
            vfu = vf # if you can, brake harder
            vf_working = vf
          elif remaining_long_grip[0] < remaining_long_grip[1]: # grip problem is worse on the rear, maybe try less braking
            vfl = vf
          else:
            vfu = vf
        else:
          if F_req_long > Fr_engine_limit or shifting == IN_PROGRESS:
            vfu = vf # force bisect down; you can't be here
          elif remaining_long_grip[0] >= 0 and remaining_long_grip[1] >=0:
            vfl = vf # try to go faster
            vf_working = vf
          elif remaining_long_grip[0] < remaining_long_grip[1]: # grip problem is worse on the rear, maybe try more acceleration
            vfl = vf
          else:
            vfu = vf
        
        if abs(vfu - vfl) < 1e-5:
          break
      # If nothing was valid then nothing will work on this step. Gotta brake earlier.
      if remaining_long_grip[0] < 0 or remaining_long_grip[1] < 0:
        if vf_working is None:
          # print('failpt C')
          return None



        # we have found the range of workable solutions, let's hone in on those now
        # by hone in I mean pick the best one
        # Then go through and do the same set of calculations...
        vf = vf_working

        a_long = (vf**2-v0**2)/2/segment.length

        # Calculate normal force on each tire
        Nf = ( (vehicle.weight_bias)*vehicle.g*vehicle.mass
            + (vehicle.cp_bias[aero_mode])*vehicle.downforce(vf,aero_mode)
            - vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
            - vehicle.drag(vf,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )

        Nr = ( (1-vehicle.weight_bias)*vehicle.g*vehicle.mass
            + vehicle.downforce(vf,aero_mode)*(1 - vehicle.cp_bias[aero_mode])
            + vehicle.mass*a_long*vehicle.cg_height/vehicle.wheelbase_length
            + vehicle.drag(vf,aero_mode)*vehicle.cp_height[aero_mode]/vehicle.wheelbase_length )

        Ff_lat, Fr_lat = self.compute_Ff_Fr(vehicle, vf, a_long, segment_next, segment.curvature)


        remaining_long_grip = [vehicle.f_long_remain(2, Nr, Fr_lat, False)[0],vehicle.f_long_remain(2, Nf, Ff_lat, True)[0]]
        F_req_long = a_long*vehicle.mass+vehicle.drag(vf,aero_mode)
        if F_req_long < 0:
          status = S_BRAKING
          if vehicle.perfect_brake_bias:
            order = np.argsort(remaining_long_grip)
            if remaining_long_grip[order[0]] < F_req_long:
              F_req_long -= remaining_long_grip[order[0]]
              remaining_long_grip[order[0]] = 0
            else:
              remaining_long_grip[order[0]] -= F_req_long
              F_req_long = 0
            remaining_long_grip[order[1]] -= F_req_long
          else:
            F_brake = -F_req_long
            remaining_long_grip[0] -= F_brake*vehicle.rear_brake_bias()
            remaining_long_grip[1] -= F_brake*vehicle.front_brake_bias()
          Fr_long = -1
        else:
          status = S_TIRE_LIM_ACC
          remaining_long_grip[0]-=F_req_long
          Fr_long = F_req_long

        Fr_remaining = vehicle.f_long_remain(2, Nr, Fr_lat, False)[0]
        Ff_remaining = vehicle.f_long_remain(2, Nf, Ff_lat, True)[0]

    if v0+vf > 0:
      tf = t0 + segment.length/((v0+vf)/2)
    else:
      tf = t0
    xf = x0 + segment.length

    if Fr_long > 0:
      co2_elapsed += segment.length*Fr_long*vehicle.co2_factor/vehicle.e_factor

    # output = np.array([
    #   tf,
    #   xf,
    #   vf,
    #   Nf,
    #   Nr, 
    #   segment.sector,
    #   status,
    #   gear,
    #   a_long / vehicle.g, 
    #   (v0 ** 2) * derate_curvature(segment.curvature, vehicle.r_add) / vehicle.g, 
    #   Ff_remaining, 
    #   Fr_remaining, 
    #   segment.curvature,
    #   eng_rpm,

    #   co2_elapsed,
    #   aero_mode
    # ])

    output = np.array([
      tf,
      xf,
      vf,
      Nf,
      0,
      Nr,
      0, 
      segment.sector,
      status,
      gear,
      a_long / vehicle.g, 
      (v0 ** 2) * derate_curvature(segment.curvature, vehicle.r_add) / vehicle.g, 
      0,
      0,
      Ff_remaining, 
      0,
      Fr_remaining,
      0,
      segment.curvature,
      eng_rpm,
      co2_elapsed,
      aero_mode
    ])

    return output

  def solve(self, vehicle, segments, output_0 = None):
    """
    The solver! The big, bad boy that does all the dirty work.
    """

    # set up initial stuctures
    output = np.zeros((len(segments), O_MATRIX_COLS))
    precrash_output = np.zeros((len(segments), O_MATRIX_COLS))
    shifting = NOT_SHIFTING
    STALLED_SPEED = 2
    launched = False
    brake = False
    shiftpt = -1
    shift_v_req = 0
    
    # Initialize the output matrix appropriately
    if output_0 is None:
      output[0,O_NF] = vehicle.mass*(vehicle.weight_bias)*vehicle.g
      output[0,O_NR] = vehicle.mass*(1-vehicle.weight_bias)*vehicle.g
      gear = vehicle.best_gear(output[0,O_VELOCITY], np.inf)
    else:
      output[0,:] = output_0
      output[0,O_TIME] = 0
      output[0,O_DISTANCE] = 0
      gear = vehicle.best_gear(output_0[O_VELOCITY], output_0[O_FR_REMAINING])
      launched = True

    # Take the first step...
    step_result = self.step(vehicle, output[0], segments[0], segments[1], brake, shiftpt>=0, gear)

    # OK, the first step shouldn't fail, so put it into the output matrix
    output[0] = step_result

    # step loop set up
    i = 1
    backup_amount = int(6.0/segments[0].length)
    bounds_found = False
    failpt = -1
    precrash_i = -1
    middle_brake_bound = -1
    lower_brake_bound = -1
    upper_brake_bound = -1

    while i<len(segments):
      if i<0:
        # print('sim_twotires.solve had a major catastrophe; index moved below zero. Unable to restart.')
        output[:] = np.nan 
        return output

      # If the gear was undefined and the point where shifting happened is not defined, pick the best gear right off
      if (gear is None) and shiftpt < 0:
        gear = vehicle.best_gear(output[i-1,O_VELOCITY], output[i,O_FR_REMAINING])

      # Take a step.
      # print("execute %d" % i)
      step_result = self.step(vehicle,output[i-1,:], segments[i], (segments[i+1] if i+1<len(segments) else segments[i]), brake, shiftpt>=0, gear)
      if step_result is None:
        # Vehicle crashed. Initiate braking algorithm!
        if not brake:
          # print("%d,%.2f: start braking" % (i,output[i,O_DISTANCE]))
          # Start braking

          # Make a backup (deep) copy of the output matrix prior to crash. (enables bisection algorithm)
          precrash_output = np.copy(output)
          brake = True
          bounds_found = False
          failpt = i-1
          precrash_i = i
          # while segments[failpt-1].curvature < segments[failpt].curvature and failpt<len(segments):
          #   failpt += 1
          upper_brake_bound = i
          lower_brake_bound = i
          i = lower_brake_bound
        elif bounds_found:
          # print("%d,%.2f: too short (%d, %d, %d)" % (i,output[i,O_DISTANCE],lower_brake_bound,middle_brake_bound,upper_brake_bound))
          # If the bounds for braking have been found, then clearly we're on the 'too short' side of the bisection algorithm. Scoot away.
          
          middle_brake_bound_prop = int(float(upper_brake_bound+lower_brake_bound)/2) 
          upper_brake_bound = middle_brake_bound
          if abs(upper_brake_bound-lower_brake_bound) <= 1:
            # print('bam')
            i = middle_brake_bound - 1
            middle_brake_bound = i
            upper_brake_bound = i-1
            lower_brake_bound-=1
          else:
            # print ('no bam; %d' % middle_brake_bound)
            middle_brake_bound = middle_brake_bound_prop
            i = middle_brake_bound
          output = np.copy(precrash_output)
        else:
          # print("%d,%.2f: move back" % (i,output[i,O_DISTANCE]))
          # If we haven't found bounds yet, need to keep moving backwards til a survivable point is reached.
          upper_brake_bound=lower_brake_bound
          lower_brake_bound-=backup_amount
          i = lower_brake_bound
          output = np.copy(precrash_output)
        # reset shifting params when braking
        gear = None
        shiftpt = -1
      elif i<=failpt:
        # print("%d,%.2f: still braking at v=%.2f" % (i,output[i,O_DISTANCE],output[i,O_VELOCITY]))
        # Vehicle still braking
        output[i] = step_result
        i+=1
        brake = True
        # reset shifting params
        gear = None
        shiftpt = -1
        shift_v_req = 0
      # FIXME: This is needed for the bisection algorithm
      elif failpt>=0 and not bounds_found:
        # print('%d,%.2f: nailed it at %d' % (i, step_result[O_VELOCITY], lower_brake_bound))
        bounds_found = True
        # upper_brake_bound = precrash_i-1 #lower_brake_bound+backup_amount
        middle_brake_bound = int(float(upper_brake_bound+lower_brake_bound)/2)
        i = middle_brake_bound
        output = np.copy(precrash_output)
      elif failpt>=0 and bounds_found and abs(lower_brake_bound - upper_brake_bound) > 1:
        # print("%d,%.2f: converged (%d,%d,%d)" % (i,output[i,O_DISTANCE],lower_brake_bound,middle_brake_bound,upper_brake_bound))
        # If past the point of crashing and we've not yet successfully bisected to convergence
        lower_brake_bound = middle_brake_bound
        middle_brake_bound = int(float(upper_brake_bound+lower_brake_bound)/2)
        i = middle_brake_bound
        output = np.copy(precrash_output)
      else:
        # print("%d,%.2f: normal op" % (i,output[i,O_DISTANCE]))
        # normal operation

        # quit braking
        brake = False # problematic??
        failpt = -1
        lower_brake_bound = -1
        upper_brake_bound = -1
        bounds_found = False

        output[i] = step_result

        better_gear = vehicle.best_gear(output[i,O_VELOCITY], output[i,O_FR_REMAINING])

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

  def steady_solve(self, vehicle,segments):
    output = self.solve(vehicle,segments)
    output[-1,O_VELOCITY] = output[-1,O_VELOCITY]*0.95
    return self.solve(vehicle,segments,output[-1, :])

  def colorgen(num_colors, idx):
    color_norm  = colors.Normalize(vmin=0, vmax=num_colors-1)
    scalar_map = cmx.ScalarMappable(norm=color_norm, cmap='hsv') 
    def map_index_to_rgb_color(index):
      return scalar_map.to_rgba(index)
    return map_index_to_rgb_color(idx)
