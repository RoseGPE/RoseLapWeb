# import shelve
import _pickle as pickle
import time
import os
	
def pack(results, filename):
	base = os.path.dirname(__file__)
	filename = toRslpFilename(filename)
	os.makedirs(os.path.dirname(base + "/out/" + filename + "/"))
	filename = base + "/out/" + filename + "/" + filename + ".rslp"

	# r = shelve.open(filename, writeback=False)
	# r["data"] = results
	# r.close()

	with open(filename, 'wb') as f:
		pickle.dump(results, f, protocol=2)

	return filename

def unpack(filename):
	# return shelve.open(filename, writeback=False)["data"]
	with open(filename, 'rb') as f:
		return pickle.load(f)

def toRslpFilename(filename):
	return filename + '-' + str(time.time()).split(".")[0]