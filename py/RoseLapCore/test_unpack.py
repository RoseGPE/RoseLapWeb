import packer
import plotter
import numpy as np

print('unpacking')
r = packer.unpack('c:\wamp\www\RoseLap\py\RoseLapCore/out/test_batch_results-1530501717/test_batch_results-1530501717.rslp')
print(r)
exit()
# r = packer.unpack('C:/wamp/www/RoseLap/py/RoseLapCore/out/test_batch_results-1521152969/test_batch_results-1521152969.rslp')
# print(r)
# r = packer.unpack('C:/wamp/www/RoseLap/py/RoseLapCore/out/test_batch_results-1521154903/test_batch_results-1521154903.rslp')
d = r['track_data'][0]['outputs'][0][1]

for di in d:
	print(di)
# plotter.plot_velocity_and_events(np.array(d))
plotter.plot_velocity_and_events(np.array(d), saveimg=True, imgname="testunpack.png")