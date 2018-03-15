import numpy as np
import itertools

def batch(tests, vehicle, tracks, model, include_output):
	batch = {}
	batch["vehicle"] = vehicle.__dict__
	batch["model"] = model.name

	permutations, targets, flatTargets, test_vals = listify(tests, vehicle)

	batch["axes"] = len(test_vals)
	batch["axiscontents"] = buildContents(targets, test_vals)
	batch["track_data"] = batch_run(flatTargets, permutations, batch["axiscontents"], vehicle, tracks, model, include_output)

	return batch

def buildContents(targets, test_vals):
	contents = []

	for i, axis in enumerate(targets):
		d = {}
		for j, target in enumerate(axis):
			d[target] = test_vals[i][j]
		contents.append(d)

	return contents

def listify(tests, vehicle):
	targets = [[t.target for t in test.axis] for test in tests]
	test_vals = [[t.test_vals for t in test.axis] for test in tests]
	ops = [[t.operation for t in test.axis] for test in tests]
	scaled_vals = [scale(targets[i], test_vals[i], ops[i], vehicle) for i in range(len(tests))]

	# list of pivoted test values
	values = [[[t[i] for t in axis] for i in range(len(axis[0]))] for axis in scaled_vals]

	bases = values[0]
	extensions = values[1 :]
	permutations = []

	for base in bases:
		permutations.extend(permutation_extend(base, extensions))

	# list of flat lists of values that line up with targets
	flatTargets = sum(targets, [])
	return (permutations, targets, flatTargets, test_vals)

def scale(targets, vals, ops, vehicle):
	for i in range(len(ops)):
		op = ops[i]
		if op == 'product':
			base = getattr(vehicle, targets[i])
			vals[i] = [base * val for val in vals[i]]

	return vals

def permutation_extend(base, extensions):
	if len(extensions) == 0:
		return base

	res = []
	for extension in extensions[0]:
		res.append(base + extension)

	return permutation_extend(res, extensions[1 :])

def batch_run(targets, permutations, contents, vehicle, tracks, model, include_output):
	test_data = []

	for track in tracks:
		segments, steady_state, name = track

		track_data = {}
		track_data["name"] = name
		track_data["ss"] = steady_state

		times = []
		outputs = []
		indicies = generateIndexer(contents)
		p = 0

		for index in indicies():
			permutation = permutations[p]
			p += 1

			vehicle = set_values(vehicle, targets, permutation)
			data = model.steady_solve(vehicle, segments) if steady_state else model.solve(vehicle, segments)

			times.append((index[0], index[1], float(data[-1, 0])))
			
			if include_output:
				outputs.append((index[0], index[1], data.tolist()))

		track_data["times"] = times
		track_data["outputs"] = outputs

		test_data.append(track_data)

	return test_data

def generateIndexer(contents):
	lens = [len(list(d.values())[0]) for d in contents]
	ints = [[i for i in range(x)] for x in lens]
	inds = itertools.product(*ints)

	def indexer():
		for index in inds:
			yield index

	return indexer

def set_values(vehicle, targets, permutation):
	for i, target in enumerate(targets):
		setattr(vehicle, target, permutation[i])

	vehicle.prep()
	return vehicle