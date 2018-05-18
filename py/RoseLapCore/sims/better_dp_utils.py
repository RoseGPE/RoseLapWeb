import numpy as np
from itertools import permutations
import time

class nd_structure:
	def __init__(self, n, p):
		self.n = n
		self.p = p
		self.np = [self.n ** i for i in range(self.p)]

		self.maxi = n**(p - 1) * (n - 1)
		self.edges = None

		self.data = {}

	def get_element(self, i):
		return self.data.get(i)

	def set_element(self, i, item):
		self.data[i] = item

	def exists(self, i):
		return i in self.data

	def get_parents(self, iS):
		parents = []

		for i in range(self.p):
			if iS[i] > 0:
				parent = list(iS)
				parent[i] = iS[i] - 1
				parents.append((i, self.convert_to_index(parent)))

		return parents

	def get_children(self, iS):
		children = []

		for i in range(self.p):
			if iS[i] < self.n - 1:
				child = list(iS)
				child[i] = iS[i] + 1
				children.append(self.convert_to_index(child))

		return children

	def get_edges(self):
		if self.edges != None:
			return self.edges

		print "\ttime start"
		t0 = time.time()

		def get_edges_recursive(n, p):
			if p == 1:
				return [tuple([n])]
			else:
				result = []

				for i in range(n):
					tails = get_edges_recursive(n - i, p - 1)

					for tail in tails:
						result.append(tail + tuple([i]))

				return result

		iE = get_edges_recursive(self.n - 1, self.p)
		print "\t", time.time() - t0
		perms = [list(permutations(e)) for e in iE]
		print "\t", time.time() - t0
		edges = []
		
		for perm in perms:
			edges.extend(perm)

		print "\t", time.time() - t0

		p = self.p
		np = self.np
		def coi(iS):
			i = 0
			for x in range(p):
				i += np[x] * iS[x]
			return i

		final = []
		for edge in edges:
			final.append(coi(edge))

		print "\t", time.time() - t0

		self.edges = set(final)

		return self.edges

	def convert_to_index(self, iS):
		i = 0

		for x in range(self.p):
			i += self.np[x] * iS[x]

		return i

	def convert_to_list(self, i):
		iS = []

		for x in range(self.p):
			iS.append(i % self.n)
			i = (i - iS[-1]) / self.n

		return iS