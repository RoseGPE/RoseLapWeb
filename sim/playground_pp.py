from simpleeval import *
from run import *

chnls = Channels(["x","y","z"])
chnls.append("x", 1)
chnls.append("y", 2)
chnls.append("z", 3)
chnls.append("x", 4)
chnls.append("y", 5)
chnls.append("z", 6)

x = 56
	
s = EvalWithCompoundTypes()
s.names = {"X": chnls}
s.functions = {
	"sum": sum, "abs": abs, "all": all, "any": any,
	"bool": bool, "complex": complex, "dict": dict, "float": float, "filter": filter,
	"len": len, "list": list, "iter": iter, "map": map, "max": max, "min": min,
	"next": next, "pow": pow, "range": range, "reversed": reversed, "round": round,
	"set": set, "slice": slice, "sorted": sorted, "str": str, "sum": sum, "zip": zip, "type": type
}

while True:
	dangerous_code=input()
	
	print(s.eval(dangerous_code))

# what could we really want to do?
# iterate through all of a column and return total amount
# iterate through all of a column and return a max value
# iterate through all of a column and return a (weighted) average
# iterate through multiple columns, computing some strange function
# peel off the last value of a column(s) and return a computed value