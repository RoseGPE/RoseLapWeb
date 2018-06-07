import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

fn = 'A1654run45.dat'
tire_data = np.genfromtxt('./data/'+fn, skip_header=3, delimiter='\t')
# TTC Tire data has X as longitudinal, Y as lateral, Z as normal (negative)
ET = 0
V  = 1
N  = 2
SA = 3
IA = 4
RL = 5
RE = 6
P  = 7
FX = 8
FY = 9
FZ = 10
MX = 11
MZ = 12
NFX = 13
NFY = 14
RST = 15
TSTI = 16
TSTC = 17
TSTO = 18
AMBTMP = 19
SR = 20

plt.figure(1)
plt.hist(tire_data[:,FZ], 50)
plt.title('Histogram of FZs')

bins = [-275,-220,-170,-100,0]
avgs = [-245, -195, -145, -45]
xmax = []
ymax = []

plt.figure(2)
for i in range(0,4):
	tire_data_filtered = tire_data[(tire_data[:,FZ] > bins[i]) & (tire_data[:,FZ] < bins[i+1])]
	plt.plot(tire_data_filtered[:,FX], tire_data_filtered[:,FY], '.', markersize=1)
	plt.title('Friction ellipses for Fz ~= %f' % avgs[i])
	xmax.append(max(abs(tire_data_filtered[:,FX])))
	ymax.append(max(abs(tire_data_filtered[:,FY])))
	print('@%f lbf normal, X friction %f, Y friction %f' % (avgs[i], xmax[-1], ymax[-1]))

plt.figure(3)
plt.plot(avgs,xmax)


slope,intercept = np.linalg.lstsq(np.vstack([avgs, np.ones(len(avgs))]).T, xmax)[0]
print('X: Fx = Fz * %f + %f' % (slope, intercept))
plt.figure(4)
plt.plot(avgs,ymax)
slope,intercept = np.linalg.lstsq(np.vstack([avgs, np.ones(len(avgs))]).T, ymax)[0]
print('Y: Fy = Fz * %f + %f' % (slope, intercept))

# ax = plt.gca(projection='3d')

# ax.scatter(tire_data[:,FX], tire_data[:,FY], tire_data[:,FZ], '.', markersize=1)

# mtd = min(tire_data[:,FZ]);
# print(mtd);
# color = [str(item/mtd/255.) for item in tire_data[:,FZ]]

# plt.plot(tire_data[:,FX], tire_data[:,FY], '.', markersize=1)
plt.show()