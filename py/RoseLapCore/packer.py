import shelve
import time
import os
	
def pack(results, filename):
	base = os.path.dirname(__file__)
	filename = toRslpFilename(filename)
	os.makedirs(os.path.dirname(base + "/out/" + filename + "/"))
	filename = base + "/out/" + filename + "/" + filename + ".rslp"
	print(filename)

	r = shelve.open(filename)
	r["data"] = results
	r.close()

	return filename

def unpack(filename):
	return shelve.open(filename)["data"]

def toRslpFilename(filename):
	return filename + '-' + str(time.time()).split(".")[0]