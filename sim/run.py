import numpy as np
import csv as csv

class Run:
  "A run is a vehicle, as configured, going through several tracks"
  def __init__(self, vehicle, tracks, settings):
    """
      vehicle: an object with vehicle parameters
      track: a numpy array with position/curvature points. Interpolate between them
      settings: an object with simulation (e.g. mesh) settings
    """
    self.vehicle  = vehicle
    self.tracks   = tracks
    self.settings = settings
    self.channels = []
    self.results  = []

  def solve(self):
    "Solve the run with the given vehicle, track, and solver settings. Raw sim channels go to self.channels; results get stored in self.results"
    pass

  def solve_to_file(self):
    "Dump the run to a csv file"

  def __repr__(self):
    return "Run (%s, %s, %s, %s)" % (repr(self.vehicle), repr(self.tracks), repr(self.settings), "solved" if self.channels else "unsolved")

class LapNotEvenException(Exception):
  def __init__(self, levels):
    self.levels = levels

class Lap():
  def __init__(self, names, vehicle=None, track=None):
    self.map     = {}
    self.names   = names
    self.vehicle = vehicle
    self.track   = track
    for i, name in enumerate(names):
      self.map[name] = []

  def append(self, key, value):
    self.map[key].append(value)

  def prepend(self, key, value):
    self.map[key].insert(0, value)

  def knit(self, new_chnls, knit_by, correction=None):
    """
    Take the given channels, and knit them onto the end of this set of channels.
    If correction is specified, the named channel will be knitted together, using this object's channel as the baseline.
    """
    i = 0
    while i < len(self.map[knit_by]):
      if self.map[knit_by][i] > new_chnls.map[knit_by][0]:
        break
      i += 1

    for key in self.names:
      self.map[key] = self.map[key][:i] + new_chnls.map[key]

    if correction:
      offset = self.map[correction][i-1] - self.map[correction][i]
      while i < len(self.map[correction]):
        self.map[correction][i] += offset
        i += 1

  def __getitem__(self, key):
    if len(key) == 1:
      return self.map[key[0]]
    return self.map[key[0]][key[1]]

  def __setitem__(self, key, value):
    if len(key) == 1:
      return self.map[key[0]]
    self.map[key[0]][key[1]] = value

  def __len__(self):
    x = [len(self.map[name]) for name in self.names]
    if min(x) != max(x):
      raise LapNotEvenException({k:v for (k,v) in zip(self.names, x)})
    return x[0]

  def save_as_csv(self, file):
    writer = csv.DictWriter(file, delimiter=',', fieldnames=self.names)
    writer.writeheader()
    for i in range(len(self)):
      writer.writerow({name:self.map[name][i] for name in self.names})


### HELPER FUNCTIONS ###

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

### CONSTANTS ###

# Status Constant Definition
S_BRAKING = 1
S_ENG_LIM_ACC = 2
S_TIRE_LIM_ACC = 3
S_SUSTAINING = 4
S_DRAG_LIM = 5
S_SHIFTING = 6
S_TOPPED_OUT = 7

# Shifting status codes
IN_PROGRESS = 0
JUST_FINISHED = 1
NOT_SHIFTING = 2

# Decision constants for DP
D_SHIFT_UP = 3
D_ACCELERATE = 0
D_SHIFT_DOWN = 4
D_SUSTAIN = 2
D_BRAKE = 1

AERO_FULL = 0
AERO_DRS = 1
AERO_BRK = 2


" DEPRECATED "
# Output Index Constant Definitions (Columns)
# Proposal: this is bullshit.
O_TIME = 0
O_DISTANCE = 1
O_VELOCITY = 2
O_NF = 3
O_NF2 = 4
O_NR = 5
O_NR2 = 6
O_SECTORS = 7
O_STATUS = 8
O_GEAR = 9
O_LONG_ACC = 10
O_LAT_ACC = 11
O_YAW_ACC = 12
O_YAW_VEL = 13
O_FF_REMAINING = 14
O_FF2_REMAINING = 15
O_FR_REMAINING = 16
O_FR2_REMAINING = 17
O_CURVATURE = 18
O_ENG_RPM = 19
O_CO2 = 20
O_AERO_MODE = 21

O_MATRIX_COLS = 22
O_NAMES = ["Time","Distance","Velocity","Front Normal Force","Front Normal Force 2","Rear Normal Force","Rear Normal Force 2",
           "Sector","Status","Gear","Longitudinal Acc.","Lateral Acc.","Yaw Acceleration", "Yaw Velocity",
           "Remaining Front Force","Remaining Front Force 2", "Remaining Rear Force", "Remaining Rear Force 2", "Curvature", "Engine Speed", "CO2", "Aero Mode"]
O_UNITS = ["s","ft","ft/s","lb","lb","lb","lb","","","","G's","G's","rad/s^2","rad/s","lb","lb","lb","lb","ft^-1","RPM","lbm",""]

# State Tuple Items for DP
G_ID = 0 # int
G_INDEX = 1 # list of ints of length p
G_STEP = 2 # int
G_PARENT_ID = 3 # int
G_DECISION = 4 # int
G_COST = 5 # float
G_VELOCITY = 6 # float
G_GEAR_DATA = 7 # tuple(int, int, float)
