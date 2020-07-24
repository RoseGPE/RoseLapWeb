import ruamel.yaml
import numpy as np
from vehicle import *

class ObjectDict:
    def __init__(self, **entries):
        self.__dict__.update(entries)

def syntax_expand(o, parse_vehicle):
	if isinstance(o, int):
		return float(o)

	if isinstance(o, list):
		for i in range(len(o)):
			o[i] = syntax_expand(o[i], parse_vehicle)

		return o

	if isinstance(o, dict):
		rs = None
		re = None
		rd = None
		for key in o:
			if key == 'range_start':
				rs = o[key]
			elif key == 'range_end':
				re = o[key]
			elif key == 'range_step':
				rd = o[key]
			elif key == 'vehicle':
				if parse_vehicle:
					# TODO: NOT THIS
					with open('./params/vehicles/' + o[key]) as v:
						o[key] = Vehicle(load(v, False))
				else:
					o[key] = str(o[key])
			else:
				o[key] = syntax_expand(o[key], parse_vehicle)

		if rs != None and re != None and rd != None:
			return list(np.arange(rs,re+rd, rd))

		return ObjectDict(**o)
	return o

# Load a YAML file and apply enhancements
def load(stream, parse_vehicle):
  out = ruamel.yaml.safe_load(stream)
  s = syntax_expand(out, parse_vehicle)
  return s