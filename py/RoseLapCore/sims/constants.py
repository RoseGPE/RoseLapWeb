# Status Constant Definition
S_BRAKING = 1
S_ENG_LIM_ACC = 2
S_TIRE_LIM_ACC = 3
S_SUSTAINING = 4
S_DRAG_LIM = 5
S_SHIFTING = 6
S_TOPPED_OUT = 7

# Output Index Constant Definitions (Columns)
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

# State Tuple Items for DP
G_ID = 0 # int
G_INDEX = 1 # list of ints of length p
G_STEP = 2 # int
G_PARENT_ID = 3 # int
G_DECISION = 4 # int
G_COST = 5 # float
G_VELOCITY = 6 # float
G_GEAR_DATA = 7 # tuple(int, int, float)

AERO_FULL = 0
AERO_DRS = 1
AERO_BRK = 2
