from __future__ import print_function
import enhanced_yaml as yaml
import numpy as np
import math

EPSILON = 1e-4

class Vehicle:
  "Vehicle object; new to V6"

  def __init__(self, filetype, filedata):
    self.filetype = filetype.lower()
    # self.dc is distance-curvature data; matrix is "tall" (fixed columns variable # rows)
    if self.filetype == 'yaml':
      # YAML data
      # TODO: units
      # for key, value in yaml.load(filedata).__dict__.items():
      self.__dict__.update(yaml.load(filedata).__dict__) 

    self.g = 9.81
    self.v_max = self.engine_rpms[-1]*2.0*3.1415/60.0/self.engine_reduction/self.gears[-1]/self.final_drive_reduction*self.comb_tire_radius

  def __repr__(self):
    return "Vehicle (type=%s)" % (self.filetype)

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


