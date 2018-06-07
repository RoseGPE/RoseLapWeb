import fancyyaml as yaml
import numpy as np
import math

g = 32.2 # ft/s^2

class Vehicle(object):
  def downforce(self, v, aero_mode):
    return self.downforce_35mph[aero_mode] / (51.33333 ** 2) * v**2

  def drag(self, v, aero_mode):
    return self.drag_35mph[aero_mode] / (51.33333 ** 2) * v**2

  def front_brake_bias(self):
    return self.brake_bias

  def rear_brake_bias(self):
    return 1 - self.brake_bias

  def eng_force(self, vel, gear):
    # Compute the angular speed of the crankshaft. 9.5493 is a conversion factor from rad/s to RPM.
    gear_ratio = self.gears[gear]
    eng_output_rpm = vel / self.tire_radius * 9.5493 * self.final_drive_reduction
    crank_rpm = eng_output_rpm * self.engine_reduction * gear_ratio

    if crank_rpm <= self.engine_rpms[0]:
      # If under RPM range, use the lowest torque value
      return (self.engine_torque[0] * self.engine_reduction * gear_ratio * self.final_drive_reduction / self.tire_radius, crank_rpm)
    elif crank_rpm > self.engine_rpms[-1]:
      # If over RPM range, no power because you're hitting the rev limiter
      return (0,crank_rpm)
    else:
      # Otherwise, linearly interpolate
      for i in range(1, len(self.engine_rpms)):
        if crank_rpm < self.engine_rpms[i]:
          torque = self.engine_torque[i] + (crank_rpm - self.engine_rpms[i]) * (self.engine_torque[i-1] - self.engine_torque[i]) / (self.engine_rpms[i-1] - self.engine_rpms[i])
          return (torque * self.engine_reduction * gear_ratio * self.final_drive_reduction / self.tire_radius, crank_rpm)

  def best_gear(self, v, fr_limit):
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

  def f_lat_remain(self, n_tires, f_norm, f_long):
    f_x_max = self.tire_mu_x*(f_norm/n_tires) + self.tire_offset_x
    f_y_max = self.tire_mu_y*(f_norm/n_tires) + self.tire_offset_y

    if f_x_max < abs(f_long/n_tires):
      return (-1, f_y_max*n_tires)
    f_lat = math.sqrt(max(1-(abs(f_long)/n_tires)**2/f_x_max/f_x_max,0))*f_y_max
    return (f_lat*n_tires, f_y_max*n_tires)

  def f_long_remain(self, n_tires, f_norm, f_lat):
    f_x_max = self.tire_mu_x*(f_norm/n_tires) + self.tire_offset_x
    f_y_max = self.tire_mu_y*(f_norm/n_tires) + self.tire_offset_y

    if f_y_max < abs(f_lat/n_tires):
      return (-1, f_x_max*n_tires)
    f_long = math.sqrt(max(1-(abs(f_lat)/n_tires)**2/f_y_max/f_y_max,0))*f_x_max
    return (f_long*n_tires, f_x_max*n_tires)

  def prep(self):
    self.mass = self.mass / self.g

  def __init__(self, v_OBJ):
    self.g = g
    self.__dict__.update(v_OBJ.__dict__)

def v_load(filename):
  vehicle_YAML = './params/vehicles/' + filename
  with open(vehicle_YAML) as data:
    v_OBJ = yaml.load(data)
  v.v_OBJ = v_OBJ

def v_getOriginalVal(name):
  return v.v_OBJ[name]