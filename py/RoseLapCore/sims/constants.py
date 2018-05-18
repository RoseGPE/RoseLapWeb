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
O_NR = 4
O_SECTORS = 5
O_STATUS = 6
O_GEAR = 7
O_LONG_ACC = 8
O_LAT_ACC = 9
O_FF_REMAINING = 10
O_FR_REMAINING = 11

O_CURVATURE = 12
O_ENG_RPM = 13

O_CO2 = 14

O_MATRIX_COLS = 15

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