from sim_onetire import *
from sim_twotires import *
from sim_fourtires import *
from sim_dp_nd_template import *

class Simulation:
	def __init__(self, model_type="one_tire"):
		self.name = model_type
		
		if model_type == "one_tire":
			self.model = sim_onetire()
		elif model_type == "two_tires":
			self.model = sim_twotires()
		elif model_type == "four_tires":
			self.model = sim_fourtires()
		elif model_type == "dp_nd":
			self.model = sim_dp_nd_template()
		else:
			raise ValueError("Please provide a valid simulation model.")

	def copy(self):
		if self.name == "one_tire":
			return sim_onetire()
		elif self.name == "two_tires":
			return sim_twotires()
		elif self.name == "four_tires":
			return sim_fourtires()
		elif self.name == "dp_nd":
			return sim_dp_nd_template()

	def solve(self, vehicle, segments):
		return self.model.solve(vehicle, segments)

	def steady_solve(self, vehicle, segments):
		return self.model.steady_solve(vehicle, segments)