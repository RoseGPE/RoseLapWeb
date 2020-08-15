from __future__ import print_function
import enhanced_yaml as yaml
import numpy as np
import math

EPSILON = 1e-4
G = 9.81 # Gravity

# Remember, use ISO coordinate system.
# X: Longitudinal   / Roll
# Y: Lateral (Left) / Pitch
# Z: Vertical       / Yaw

# Constants for convenience
LONG  = 0
LAT   = 1
VERT  = 2
ROLL  = 0
PITCH = 1
YAW   = 2

# Tire numbers
FL = 0
FR = 1
BL = 2
BR = 3

class Vehicle:
  """
  Vehicles consist of:
   - mass:   Mass
   - aero:   Aero
   - tires:  Multiple tires
   - brakes: Brakes
   - powertrain: Powertrain
  """

  def __init__(self, filetype, filedata):
    self.filetype = filetype.lower()
    # self.dc is distance-curvature data; matrix is "tall" (fixed columns variable # rows)
    if self.filetype == 'object':
      # Raw object data, pre-parsed
      self.__dict__.update(filedata.__dict__)

    elif self.filetype == 'yaml':
      # YAML data
      self.__dict__.update(yaml.load(filedata).__dict__)

    self.mass = Mass(self.mass)
    self.aero = Aero(self.aero)
    #self.tires = [Tire(tire) for tire in self.tires]
    self.powertrain = Powertrain(self.powertrain)
    self.brakes = Brakes(self.brakes)

    self.g = 9.81
    self.v_max = self.powertrain.omega_max

  def __repr__(self):
    return "Vehicle (type=%s)" % (self.filetype)

class Aero:
  """
    Aero takes parameters:
    - force_v : Velocity at which force is evaluated
    - force:    Force at specified velocity
    - cp:       list, position of center of pressure relative to vehicle origin
  """
  def __init__(self, var):
    if var.force:
      self.force_1ms = [force/var.force_v/var.force_v for force in var.force] # Scale back based on input speed
    else:
      self.force_1ms = [0,0,0]

    if var.cp: self.cp = var.cp

    # TODO: Moments
    # TODO: DRS

  def force(self, v):
    return [force*v*v for force in self.force_1ms]

class Mass:
  """
    Mass takes parameters:
    - mass : total mass of object
    - moi  : (optional) list of moments of inertia about CG
    - cg   : (optional) position of CG relative to vehicle origin
  """
  def __init__(self, var):
    self.mass  = var.mass # Should be a float
    if var.moi: self.moi   = var.moi # Optional; should be a list: roll, pitch, yaw
    if var.cg:  self.cg    = var.cg  # Optional; should be a list: long, lat, vert

class Tire:
  """
    Tires are really complex.
  """
  def __init__(self, var):
    self.model = var.model.lower() # Should be a string (see below for options)
    if var.mass: self.mass  = Tire(var.mass)    # Optional; should be a Mass object (also used to control position)

    if self.model == 'mu':
      self.mu = var.mu
    # TODO: other models

  def force_lat_remain(self, N, f_long):
    if self.model == 'mu':
      return math.sqrt((self.mu*N)**2 - f_long**2)

  def force_long_remain(self, N, f_lat):
    if self.model == 'mu':
      return math.sqrt((self.mu*N)**2 - f_lat**2)

class Powertrain:
  """
    Powertrains take parameters:
    - omega_map, torque_map: A torque curve
    - power_map: A list whose primary axis is oriented in omega, and secondary axis is oriented in throttle (assuming even spacing)
  """
  def __init__(self, var):
    self.omega_map    = [spd*math.pi/30 for spd in var.rpm_map] # Motor velocity map; convert RPM to rad/s
    self.torque_map   = var.torque_map   # Torque output map
    self.power_map    = var.power_map    # Power consumption map
    self.trans_gears  = var.trans_gears  # Transmission ratios
    self.gear_ratio   = var.gear_ratio   # Final Drive Ratio
    self.trans_type   = var.trans_type   # Transmission type
    self.shift_time   = var.shift_time   # Shift time

    self.omega_max    = max(self.omega_map)*min(self.trans_gears)

  def state(self, gear, wheel_rpm, traction_limit):
    """ return: a tuple with
     - Gear Number
     - Throttle Percentage
     - Crank RPM
     - Power Consumption
     - Torque """
    pass

  def ideal_gear(self, wheel_rpm, traction_limit):
    pass

class Brakes:
  """
    Brakes take parameters:
    - mode: fixed or perfect
    - front_bias: front brake bias as a percentage
  """
  def __init__(self, var):
    self.mode = var.mode
    if self.mode == 'fixed':
      self.front_bias = float(var.front_bias)/100 # convert from pct
      self.rear_bias  = 1-self.front_bias

### Old code not following new OO standard ###
"""
def eng_force(self, vel, gear):
    if np.isinf(gear):
      gear = self.best_gear(vel, np.inf)

    if np.isnan(gear):
      return (0, 0)
    elif self.transmission_type.lower() == 'cvt':
      eng_power = [self.engine_torque[i]*self.engine_rpms[i] for i in range(len(self.engine_torque))]
      eng_torque = self.engine_torque[eng_power.index(max(eng_power))]
      crank_rpm  = self.engine_rpms  [eng_power.index(max(eng_power))]
      cvt_ratio = np.inf
      if vel > 0:
        cvt_ratio = crank_rpm/(vel / self.rear_tire_radius * 9.5493)
      return (cvt_ratio*eng_torque*self.transmission_efficiency, crank_rpm)
    else:
      # Compute the angular speed of the crankshaft. 9.5493 is a conversion factor from rad/s to RPM.
      gear_ratio = self.gears[gear]
      eng_output_rpm = vel / self.rear_tire_radius * 9.5493 * self.final_drive_reduction
      crank_rpm = eng_output_rpm * self.engine_reduction * gear_ratio

      if crank_rpm <= self.engine_rpms[0]:
        # If under RPM range, use the lowest torque value
        return (self.engine_torque[0] * self.engine_reduction * gear_ratio * self.final_drive_reduction / self.front_tire_radius *self.transmission_efficiency, crank_rpm)
      elif crank_rpm > self.engine_rpms[-1]:
        # If over RPM range, no power because you're hitting the rev limiter
        return (0,crank_rpm)
      else:
        # Otherwise, linearly interpolate
        for i in range(1, len(self.engine_rpms)):
          if crank_rpm < self.engine_rpms[i]:
            torque = self.engine_torque[i] + (crank_rpm - self.engine_rpms[i]) * (self.engine_torque[i-1] - self.engine_torque[i]) / (self.engine_rpms[i-1] - self.engine_rpms[i])
            return (torque * self.engine_reduction * gear_ratio * self.final_drive_reduction / self.rear_tire_radius *self.transmission_efficiency, crank_rpm)
      return (0,crank_rpm)

  def best_gear(self, v, fr_limit):
    if self.transmission_type.lower() == 'cvt':
      return 0
    # Find the best gear and return the number for it.
    # Doesn't actually do anything with the friction limitation. It did at one point.
    opts = [self.eng_force(v, int(gear))[0] for gear in range(len(self.gears))]
    best = 0
    besti = -1
    for i in range(len(opts)):
      if opts[i] >= best:
        best = opts[i]
        besti = i
    return besti

  def downforce(self, v, aero_mode):
    return self.downforce_15ms[aero_mode] / (15.0 ** 2.0) * v**2.0

  def drag(self, v, aero_mode):
    return self.drag_15ms[aero_mode] / (15.0 ** 2.0) * v**2.0

  def front_brake_bias(self):
    return self.brake_bias

  def rear_brake_bias(self):
    return 1 - self.brake_bias

  def f_lat_remain(self, n_tires, f_norm, f_long, front=None):
    if f_norm <= 0.0:
      return (0.0, 0.0)
    if front is None:
      f_x_max = self.comb_tire_mu_x*(f_norm/n_tires) + self.comb_tire_offset_x
      f_y_max = self.comb_tire_mu_y*(f_norm/n_tires) + self.comb_tire_offset_y
    elif front:
      f_x_max = self.front_tire_mu_x*(f_norm/n_tires) + self.front_tire_offset_x
      f_y_max = self.front_tire_mu_y*(f_norm/n_tires) + self.front_tire_offset_y
    else:
      f_x_max = self.rear_tire_mu_x*(f_norm/n_tires) + self.rear_tire_offset_x
      f_y_max = self.rear_tire_mu_y*(f_norm/n_tires) + self.rear_tire_offset_y

    if f_x_max < abs(f_long/n_tires):
      return (-np.inf, f_y_max*n_tires)
    f_lat = math.sqrt(max(1-(abs(f_long)/n_tires)**2/f_x_max/f_x_max,0))*f_y_max
    return (f_lat*n_tires, f_y_max*n_tires)

  def f_long_remain(self, n_tires, f_norm, f_lat, front=None):
    if f_norm <= 0.0:
      return (0.0, 0.0)
    if front is None:
      f_x_max = self.comb_tire_mu_x*(f_norm/n_tires) + self.comb_tire_offset_x
      f_y_max = self.comb_tire_mu_y*(f_norm/n_tires) + self.comb_tire_offset_y
    elif front:
      f_x_max = self.front_tire_mu_x*(f_norm/n_tires) + self.front_tire_offset_x
      f_y_max = self.front_tire_mu_y*(f_norm/n_tires) + self.front_tire_offset_y
    else:
      f_x_max = self.rear_tire_mu_x*(f_norm/n_tires) + self.rear_tire_offset_x
      f_y_max = self.rear_tire_mu_y*(f_norm/n_tires) + self.rear_tire_offset_y
    
    if f_y_max < abs(f_lat/n_tires):
      return (-np.inf, f_x_max*n_tires)
    f_long = math.sqrt(max(1-(abs(f_lat)/n_tires)**2/f_y_max/f_y_max,0))*f_x_max
    return (f_long*n_tires, f_x_max*n_tires)

  def f_long_remain_pair(self, f_norm, f_lat, front=None):
    f_lat = abs(f_lat)
    if front is None:
      f_x_max = [self.comb_tire_mu_x*N + self.comb_tire_offset_x for N in f_norm]
      f_y_max = [self.comb_tire_mu_y*N + self.comb_tire_offset_y for N in f_norm]
    elif front:
      f_x_max = [self.front_tire_mu_x*N + self.front_tire_offset_x for N in f_norm]
      f_y_max = [self.front_tire_mu_y*N + self.front_tire_offset_y for N in f_norm]
    else:
      f_x_max = [self.rear_tire_mu_x*N + self.rear_tire_offset_x for N in f_norm]
      f_y_max = [self.rear_tire_mu_y*N + self.rear_tire_offset_y for N in f_norm]

    eps = 1e-4
    for i in range(len(f_x_max)):
      if f_norm[i] <= eps or f_x_max[i] <=eps or f_y_max[i] <=eps:
        # print('yoinks')
        f_x_max[i] = eps
        f_y_max[i] = eps

    if sum(f_y_max) < f_lat:
      return ([-np.inf,-np.inf],f_x_max)

    b = 1
    s = 0
    if f_norm[s] > f_norm[b]:
      # 0th is bigger grip
      b = 0
      s = 1

    f_y = [0,0]
    f_y[s] = f_lat*f_norm[s]/(f_norm[b]+f_norm[s]) #f_y_max[s]-eps
    f_y[b] = f_lat-f_y[s]

    f_long = [0,0]
    
    f_long[b] = f_x_max[b]*math.sqrt(max(1-f_y[b]**2/f_y_max[b]**2,0.0))
    f_long[s] = f_x_max[s]*math.sqrt(max(1-f_y[s]**2/f_y_max[s]**2,0.0))

    return (f_long,f_x_max)
"""