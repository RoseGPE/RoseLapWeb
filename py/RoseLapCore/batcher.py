import numpy as np
import itertools
import multiprocessing
from multiprocessing import Pool as ThreadPool
import time
import copy as shallow

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

def run_permutation(thread_data):
	index, prepped_vehicle, solver, steady_state, include_output, segments = thread_data

	data = solver.steady_solve(prepped_vehicle, segments) if steady_state else solver.solve(prepped_vehicle, segments)

	args = index + (float(data[-1, 0]),)
	#times.append((*index, float(data[-1, 0])))
	#times.append(args)
	
	if include_output:
		return (args, (index + (data.tolist(),)))
	else:
		return args

def batch_run(targets, permutations, contents, vehicle, tracks, model, include_output):
	test_data = []
	n_threads = partitions(len(permutations))
	
	if type(permutations[0]) != list:
		permutations = [[p] for p in permutations]

	print "threading...", n_threads

	# pool = ThreadPool(n_threads)
	# pool.map(stretch, [i for i in range(n_threads)])

	print "running..."

	for track in tracks:
		segments, steady_state, name = track

		t0 = time.time()

		track_data = {}
		track_data["name"] = name
		track_data["ss"] = steady_state

		indicies = generateIndicies(contents)
		thread_data = [(indicies[i], set_values(vehicle, targets, permutations[i]), model.copy(), steady_state, include_output, segments) for i in range(len(indicies))]

		# thread_results = pool.map(run_permutation, thread_data)
		thread_results = [run_permutation(d) for d in thread_data]

		print "\ttrack completed in:", time.time() - t0, "seconds"

		times = []
		outputs = []

		for result in thread_results:
			if include_output:
				t, output = result
				times.append(t)
				outputs.append(output)
			else:
				times.append(result)

		track_data["times"] = times
		track_data["outputs"] = outputs

		test_data.append(track_data)

	return test_data

def generateIndicies(contents):
	lens = [len(list(d.values())[0]) for d in contents]
	ints = [[i for i in range(x)] for x in lens]
	inds = itertools.product(*ints)

	return list(inds)

def set_values(vehicle, targets, permutation):
	v = shallow.copy(vehicle)

	for i, target in enumerate(targets):
		setattr(v, target, permutation[i])

	v.prep()
	return v

def stretch(i):
	while i < 2**25:
		i += 1

def partitions(n):
	return int(np.max([np.min([np.floor(np.sqrt(n)) / 2, multiprocessing.cpu_count()]), 1]))
