import numpy as np
import itertools
import multiprocessing
from multiprocessing import Pool as ThreadPool
import time
import copy as shallow
import input_processing.track_segmentation as track_segmentation
# import gc
from sims import constants
import logging
import psutil
import os

def batch(tests, vehicle, tracks, model, include_output):
    batch = {}
    batch["vehicle"] = vehicle.__dict__
    batch["model"] = model.name

    permutations, targets, flatTargets, test_vals = listify(tests, vehicle)

    batch["axes"] = len(test_vals)
    batch["test_vals"] = buildContents(targets, test_vals)
    batch["track_data"] = batch_run(flatTargets, permutations, batch["test_vals"], vehicle, tracks, model, include_output)

    batch["axiscontents"] = appendLabels(batch["test_vals"], tests)

    return batch

def buildContents(targets, test_vals):
    contents = []

    for i, axis in enumerate(targets):
        d = {}
        for j, target in enumerate(axis):
            d[target] = test_vals[i][j]
        contents.append(d)

    return contents

def appendLabels(ac, tests):
    for i, axis in enumerate(tests):
        axis = axis.axis
        for target in axis:
            if "labels" in target.__dict__.keys():
                ac[i][target.target] = target.labels

    return ac


def listify(tests, vehicle):
    targets = [[t.target for t in test.axis] for test in tests]
    test_vals = [[t.test_vals for t in test.axis] for test in tests]
    ops = [[t.operation for t in test.axis] for test in tests]
    scaled_vals = [scale(targets[i], test_vals[i], ops[i], vehicle) for i in range(len(tests))]

    # list of pivoted test values
    values = [[[t[i] for t in axis] for i in range(len(axis[0]))] for axis in scaled_vals] # I don't understand the axis[0] here - Thad
    logging.debug("values = %s" % repr(values))

    bases = values[0]
    extensions = values[1 :]
    permutations = []

    # logging.debug('values = %s, bases = %s, extensions = %s' % (repr(values),repr(bases),repr(extensions)))

    for base in bases:
        if len(tests) > 1:
            permutations.extend(permutation_extend(base, extensions))
        else:
            permutations.append(permutation_extend(base, extensions))
    logging.debug("permutations = %s" % permutations)

    # list of flat lists of values that line up with targets
    flatTargets = sum(targets, []) # what does this mean / do, wtf? - Thad; whatever
    return (permutations, targets, flatTargets, test_vals)

def scale(targets, vals, ops, vehicle):
    for i in range(len(ops)):
        op = ops[i]
        if op == 'product':
            base = getattr(vehicle, targets[i])
            vals[i] = [base * val for val in vals[i]]

    return vals

def permutation_extend(base, extensions):
    logging.debug("base = %s, extensions = %s" % (repr(base),repr(extensions)))
    if len(extensions) == 0:
        return base

    res = []
    for extension in extensions[0]:
        res.append(base + extension)

    return permutation_extend(res, extensions[1 :])

def run_permutation(thread_data):
    index, prepped_vehicle, solver, steady_state, include_output, segments, perm = thread_data
    print('\tRunning Permutation: %s' % (repr(perm)))
    logging.info("Running Permutation: %s" % repr(perm))
    logging.debug(repr(psutil.Process(os.getpid()).memory_info().rss))

    # gc.collect()
    data = solver.steady_solve(prepped_vehicle, segments) if steady_state else solver.solve(prepped_vehicle, segments)

    time = index + (float(data[-1, constants.O_TIME]),)
    co2 = float(data[-1, constants.O_CO2])
    #times.append((*index, float(data[-1, 0])))
    #times.append(args)
    
    if include_output:
        return (time, co2, (index + (data.tolist(),)))
    else:
        return (time, co2)


def generate_co2s(outputs):
    # logging.debug('generating co2s for %s' % outputs)
    co2s = []

    for output in outputs:
        co2s.append(output[-1][-1][constants.O_CO2])

    return co2s

def batch_run(targets, permutations, contents, vehicle, tracks, model, include_output):

    test_data = []
    n_threads = partitions(len(permutations))

    # logging.debug('permutations = %s' % repr(permutations))
    
    if type(permutations[0]) != list:
        permutations = [[p] for p in permutations]

    print("threading...", n_threads)
    logging.info("Threading %d threads..." % n_threads)

    # pool = ThreadPool(n_threads)
    # pool.map(stretch, [i for i in range(n_threads)])

    print("running...")

    for track in tracks:
        fn, dl_default, steady_state, name, point_formula, mins = track
        # print('making segments for %s at %f' % (fn, dl_default))
        # logging.debug('hi there')
        

        t0 = time.time()

        unique_segments = False
        segments = None
        for target in targets:
            if target[:6] == 'track.':
                unique_segments = True
                break
        else:
            segments = track_segmentation.file_to_segments(fn, dl_default)


        track_data = {}
        track_data["name"] = name
        track_data["ss"] = steady_state

        indicies = generateIndicies(contents)
        # thread_data = [(indicies[i], set_values(vehicle, targets, permutations[i]), model.copy(),
        # steady_state, include_output, segments[i]) for i in range(len(indicies))]
        # [(index, vehicle, model, steady_state, inclue_output, segments), ...]

        thread_data = []
        for i in range(len(indicies)):
            v = shallow.copy(vehicle)
            dl = dl_default
            opts = {}
            repres = {}
            for j, target in enumerate(targets):
                # logging.debug("i=%d, j=%d, perm=%s" % (i,j,repr(permutations)))
                repres[target] = permutations[i][j]
                if target == 'label':
                    pass
                elif target[:6] == 'track.':
                    if target[6:] == 'segment_distance':
                        dl = permutations[i][j]
                    else:
                        opts[target[6:]] = permutations[i][j]
                else:
                    setattr(v, target, permutations[i][j])
            if unique_segments:
                segments = track_segmentation.file_to_segments(fn, dl, opts=opts)
            v.prep()
            td = (indicies[i],
                v,
                model.copy(),
                steady_state,
                include_output,
                segments,
                repres)
            # print(fn, dl, opts)
            thread_data.append(td)
                

        # thread_results = pool.map(run_permutation, thread_data)
        thread_results = [run_permutation(d) for d in thread_data]

        print("\ttrack completed in:", time.time() - t0, "seconds")

        times = []
        outputs = []
        co2s = []

        for result in thread_results:
            if include_output:
                t, co2, output = result
                times.append(t)
                co2s.append(co2)
                outputs.append(output)
            else:
                t, co2 = result
                times.append(t)
                co2s.append(co2)

        track_data["times"] = times
        track_data["outputs"] = outputs
        track_data["min_time"] = mins[0]
        track_data["min_co2"] = mins[1]
        track_data["scoring"] = point_formula
        track_data["co2s"] = co2s # generate_co2s(outputs)

        test_data.append(track_data)

    return test_data

def generateIndicies(contents):
    lens = [len(list(d.values())[0]) for d in contents]
    ints = [[i for i in range(x)] for x in lens]
    inds = itertools.product(*ints)

    return list(inds)

# def set_values(vehicle, targets, permutation):
#   v = shallow.copy(vehicle)

#   for i, target in enumerate(targets):
#       setattr(v, target, permutation[i])

#   v.prep()
#   return v

def stretch(i):
    while i < 2**25:
        i += 1

def partitions(n):
    return int(np.max([np.min([np.floor(np.sqrt(n)) / 2, multiprocessing.cpu_count()]), 1]))
