from sim_pointmass import *
from sim_twotires import *
from sim_dp_nd_template import *

class Simulation:
	def __init__(self, model_type="point_mass"):
		self.name = model_type
		
		if model_type == "point_mass":
			self.model = sim_pointmass()
		elif model_type == "two_tires":
			self.model = sim_twotires()
		elif model_type == "dp_nd":
			self.model = sim_dp_nd_template()
		else:
			raise ValueError("Please provide a valid simulation model.")

	def copy(self):
		if self.name == "point_mass":
			return sim_pointmass()
		elif self.name == "two_tires":
			return sim_twotires()
		elif self.name == "dp_nd":
			return sim_dp_nd_template()

	def solve(self, vehicle, segments):
		return self.model.solve(vehicle, segments)

	def steady_solve(self, vehicle, segments):
		return self.model.steady_solve(vehicle, segments)