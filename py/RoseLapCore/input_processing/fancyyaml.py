import ruamel.yaml
import numpy as np
from vehicle import *

class ObjectDict:
    def __init__(self, **entries):
        self.__dict__.update(entries)

def syntax_expand(o):
	if isinstance(o, int):
		return float(o)

	if isinstance(o, list):
		for i in range(len(o)):
			o[i] = syntax_expand(o[i])

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
				with open('./params/vehicles/' + o[key]) as v:
					o[key] = Vehicle(load(v))
			else:
				o[key] = syntax_expand(o[key])

		if rs != None and re != None and rd != None:
			return list(np.arange(rs,re+rd, rd))

		return ObjectDict(**o)
	return o

def load(stream):
  out = ruamel.yaml.safe_load(stream)
  s = syntax_expand(out)
  return s