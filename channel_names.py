from types import SimpleNamespace

# Remember to follow ISO coordinate system (x/y/z > fwd/left/up > roll/pitch/yaw)
chnls = [
  "DIST", # Distance
  "CURV", # Curvature

  "ACCX", # X Acceleration
  "ACCY", # Y Acceleration
  "ACCZ", # Z Acceleration
  "VELX", # X Velocity
  "VELY", # Y Velocity
  "VELZ", # Z Velocity

  "ALPX", # RX Acceleration
  "ALPY", # RY Acceleration
  "ALPZ", # RZ Acceleration
  "OMGX", # RX Velocity
  "OMGY", # RY Velocity
  "OMGZ", # RZ Velocity

  "GEAR", # Gear
  "TPCT", # Throttle Percentage
  "ERPM", # Engine RPM
  "PCNS", # Power Consumption
  "PEFF", # Power Efficiency

  "FT1X", # Force on tire 1, X
  "....", # All tire forces follow same precedent

  "FAEX", # X Aero Force
  "FAEY", # Y Aero Force
  "FAEZ", # Z Aero Force
  "AEMD", # Aero Mode

  "BBIS" # Brake Bias
]

x = SimpleNamespace()

for i, c in enumerate(chnls):
  setattr(x, c, c)

if __name__ == "__main__":
  print(x)