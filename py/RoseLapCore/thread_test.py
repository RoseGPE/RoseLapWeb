import time
from multiprocessing.dummy import Pool as ThreadPool

n_threads = 10
max_t = 30

def test_wait(n):
	time.sleep(n)
	print "thread", n, "done"
	return True

pool = ThreadPool(n_threads)
results = [i for i in range(max_t)]
print "go"
results = pool.map(test_wait, results)