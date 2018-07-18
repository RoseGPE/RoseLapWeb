import numpy as np
import better_dp_utils as dpu
import math
from constants import *
from queue import Queue

class sim_dp_nd_template:
	def __init__(self):
		self.axes = 3
		self.policies = [None for x in range(self.axes)]
		self.pre_pop = {}
		
		# self.done = set()
		# self.done.add(0)

		# self.policies[D_SHIFT_UP] = self.shift_up_policy
		self.policies[D_ACCELERATE] = self.accel_policy
		# self.policies[D_SHIFT_DOWN] = self.shift_down_policy
		self.policies[D_SUSTAIN] = self.sustain_policy
		self.policies[D_BRAKE] = self.brake_policy

	def accel_policy(self, S):
		c, Sp = self.compute_RT(S, D_ACCELERATE)

		if Sp != None:
			Sp[G_DECISION] = D_ACCELERATE
			Sp[G_PARENT_ID] = S[G_ID]

		return Sp

	def sustain_policy(self, S):
		return None

	def brake_policy(self, S):
		return None

	def shift_up_policy(self, S):
		return None

	def shift_down_policy(self, S):
		return None

	def fill_axes(self):
		for i in range(self.axes):
			policy = self.policies[i]
			S = self.sg.get_element(0)
			index = [0 for x in range(self.axes)]

			for j in range(1, self.n):
				index[i] = j
				iS = self.sg.convert_to_index(index)
				S = policy(S)

				if S == None:
					break;
				else:
					S[G_ID] = iS
					S[G_INDEX] = list(index)
					# self.sg.set_element(iS, tuple(S))
					self.pre_pop[S[G_ID]] = tuple(S)
					# self.done.add(iS)

	def compute_RT(self, S, d):
		S = list(S)

		if S[G_COST] > self.max_cost:
			return (np.inf, None)
		elif S[G_STEP] + 1 > len(self.segments):
			return (np.inf, None)
		elif S[G_GEAR_DATA][1] != 0:
			if S[G_GEAR_DATA][1] == 1 and d != D_SHIFT_UP:
				return (np.inf, None)
			elif S[G_GEAR_DATA][1] == -1 and d != D_SHIFT_DOWN:
				return (np.inf, None)

		Sp = [0, 
			[0 for i in range(self.axes)],
			S[G_STEP] + 1,
			None,
			None,
			np.inf,
			0.0,
			[]
		]

		a_long, g = self.compute_a_long(S, d)
		Sp[G_GEAR_DATA] = g

		if a_long == None:
			return (np.inf, None)

		dx = self.segments[S[G_STEP] - 1].length
		
		try:
			Sp[G_VELOCITY] = math.sqrt(S[G_VELOCITY]**2 + 2 * a_long * dx)
		except:
			return (np.inf, None)

		vavg = (S[G_VELOCITY] + Sp[G_VELOCITY]) / 2.

		if vavg <= 0:
			return (np.inf, None)

		Sp[G_COST] = S[G_COST] + (dx / vavg)

		return (Sp[G_COST], Sp)

	def compute_a_long(self, S, d):
		v = S[G_VELOCITY]
		N = (self.vp.mass * self.vp.g) + (self.vp.alpha_downforce() * v**2)
		k = self.segments[S[G_STEP] - 1].curvature

		f_tire_lim = (self.vp.mu * N)
		f_tire_lat = (k * self.vp.mass * v**2)
		if f_tire_lat > f_tire_lim:
			return (None, S[G_GEAR_DATA])
		f_tire_rem = np.sqrt(f_tire_lim**2 - f_tire_lat**2)


		gd = list(S[G_GEAR_DATA])
		if d == D_SHIFT_UP or d == D_SHIFT_DOWN:
			# if gd[1] == 0:
			# 	gd[1] = 1 if d == D_SHIFT_UP else -1
			# 	gd[2] = S[G_COST]
			# else:
			# 	dt = S[G_COST] - S[G_GEAR_DATA][2]

			# 	if dt >= self.vp.shift_time:
			# 		gd[1] = 0

			# 		gd[0] = np.min([gd[0] + gd[1], len(self.vp.gears) - 1])
			# 		gd[0] = np.max([gd[0], 0])
			gd[1] = 0

			gd[0] = np.min([gd[0] + gd[1], len(self.vp.gears) - 1])
			gd[0] = np.max([gd[0], 0])

		eng, rpm = self.vp.eng_force(v, gd[0])
		engine_force = eng if d == D_ACCELERATE else 0

		f_tire_long = np.min([engine_force, f_tire_rem]) if d != D_BRAKE else -f_tire_rem
		f_drag = self.vp.alpha_drag() * v**2
		f_long = f_tire_long - f_drag

		return (float(f_long) / self.vp.mass, tuple(gd))

	def find_optimum(self, edges):
		min_t = np.inf
		min_S = None

		for iE in edges:
			edge = self.sg.get_element(iE)

			if edge[G_COST] < min_t:
				min_t = edge[G_COST]
				min_S = iE

		path = []
		output = np.zeros([self.n, O_MATRIX_COLS])
		output[0, :] = np.array([
				0,
				0,
				0.0,
				0,
				0,
				0,
				D_ACCELERATE,
				0,
				0,
				0,
				0,
				0,
				self.segments[0].curvature,
				0,
				0
			])

		i = self.n - 1

		while min_S > 0:
			parents = self.sg.load_obj("parents" + str(i))
			# min_S = self.sg.get_element(min_S)
			min_S = parents.get(min_S)

			path.append(min_S[G_DECISION])

			output[i, :] = np.array([
				min_S[G_COST],
				min_S[G_STEP],
				min_S[G_VELOCITY],
				0,
				0,
				0,
				min_S[G_DECISION],
				min_S[G_GEAR_DATA][0],
				0,
				0,
				0,
				0,
				self.segments[min_S[G_STEP] - 1].curvature,
				0,
				0
			])

			i = i - 1

			min_S = min_S[G_PARENT_ID]

		return (path[::-1], output)

	def solve(self, vehicle, segments):
		self.vp = vehicle
		self.segments = segments
		self.n = len(segments) + 1

		print(self.n)
		print(segments[4])
		print(segments[4].length)
		print(segments[4].curvature)
		print(segments[4].sector)


		self.max_cost = ((self.n * segments[4].length / 5280) / 15) * 60 * 60
		print("max time:", self.max_cost)
		self.max_cost *= 2

		init_state = (0, 
			[0 for i in range(self.axes)],
			0,
			None,
			None,
			0.0,
			0.0,
			(0, 0, 0.0)
		)

		self.sg = dpu.nd_structure(self.n, self.axes)
		self.sg.set_element(0, init_state)

		self.fill_axes()

		c_queue = Queue()
		g_queue = Queue()
		for pi in self.pre_pop.values():
			for c in self.sg.get_children(pi[G_INDEX]):
				g_queue.put(c)

		pDict = self.pre_pop

		processed = 1
		
		end_states = []

		while(True):
			while(not g_queue.empty()):
				spid = g_queue.get()

				if self.sg.exists(spid):
					continue

				processed += 1
				if processed % 10000 == 0:
					print(processed)

				spindex = self.sg.convert_to_list(spid)

				sp = init_state
				min_cost = np.inf

				parents = self.sg.get_parents(spindex)

				for parent in parents:
					d, sid = parent

					if self.sg.exists(sid):
						cost, pSp = self.compute_RT(pDict.get(sid), d)

						if pSp != None and cost < min_cost:
							min_cost = cost
							sp = pSp

							sp[G_PARENT_ID] = sid
							sp[G_DECISION] = d
						else:
							continue

				if min_cost < np.inf:
					sp[G_ID] = spid
					sp[G_INDEX] = spindex

					if sp[G_STEP] == self.n - 1:
						end_states.append(spid)
					else:
						children = self.sg.get_children(spindex)
						for child in children:
							c_queue.put(child)

					#self.sg.set_element(spid, tuple(sp))
					pDict[spid] = tuple(sp)

			if c_queue.empty():
				break

			g_queue = c_queue
			c_queue = Queue()

			self.sg.save_obj(parents, "parents" + str((processed % 10000) - 1))

		path, output = self.find_optimum(end_states)

		print(path)

		return output

	def steady_solve(self, vehicle, segments):
		return self.solve(vehicle, segments)