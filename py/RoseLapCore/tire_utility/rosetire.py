import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

fn = 'A1654run45.dat'
tire_data = np.genfromtxt('./data/'+fn, skip_header=3, delimiter='\t')


# TTC Tire data has X as longitudinal, Y as lateral, Z as normal (negative)

# Names of every channel
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

# Histogram the tire data
plt.figure(1)
plt.hist(tire_data[:,FZ], 50)
plt.title('Histogram of FZs')

# USERDEF the 'bins' of tire data tested, and the median data at each
bins = [-275,-220,-170,-100,0]
avgs = [-225, -175, -135, -35]
xmax = []
ymax = []

sigmas = 2 # how many standard deviations to accept

def reject_outliers(data, m, by_col):
    s = abs(data[:,by_col] - np.mean(data[:,by_col])) < m * np.std(data[:,by_col])
    print('rejecting',np.where(abs(data[:,by_col] - np.mean(data[:,by_col])) >= m * np.std(data[:,by_col])))
    return data[s]

plt.figure(2)
for i in range(0,len(avgs)):
    tire_data_filtered = tire_data[(tire_data[:,FZ] > bins[i]) & (tire_data[:,FZ] < bins[i+1])]
    plt.plot(tire_data_filtered[:,FX], tire_data_filtered[:,FY], '.', markersize=1)
    tire_data_filtered = reject_outliers(reject_outliers(tire_data_filtered,sigmas,FX), sigmas,FY)
    plt.title('Friction ellipses for Fz ~= %f' % avgs[i])
    xmax.append(max(abs(tire_data_filtered[:,FX])))
    ymax.append(max(abs(tire_data_filtered[:,FY])))
    print('@%f lbf normal, X friction %f, Y friction %f' % (avgs[i], xmax[-1], ymax[-1]))

slope_x,intercept_x = np.linalg.lstsq(np.vstack([avgs, np.ones(len(avgs))]).T, xmax)[0]
slope_y,intercept_y = np.linalg.lstsq(np.vstack([avgs, np.ones(len(avgs))]).T, ymax)[0]
xm = intercept_x+slope_x*bins[0]
ym = intercept_y+slope_y*bins[0]

plt.figure(3)
plt.plot(avgs,xmax,'bo')
plt.plot([0,bins[0]],[intercept_x, xm], 'r')
plt.plot(tire_data[:,FZ], tire_data[:,FX], '.', markersize=1)
plt.ylim([0,max(xm,ym)*1.15])

plt.figure(4)
plt.plot(avgs,ymax,'bo')
plt.plot([0,bins[0]],[intercept_y, ym], 'r')
plt.plot(tire_data[:,FZ], tire_data[:,FY], '.', markersize=1)
plt.ylim([0,max(ym,xm)*1.15])


print('Longitudinal: Fx = Fz * %f + %f' % (slope_x, intercept_x))
print('Lateral: Fy = Fz * %f + %f' % (slope_y, intercept_y))

# ax = plt.gca(projection='3d')
# ax.scatter(tire_data[:,FX], tire_data[:,FY], tire_data[:,FZ], '.', markersize=1)
# mtd = min(tire_data[:,FZ]);
# print(mtd);
# color = [str(item/mtd/255.) for item in tire_data[:,FZ]]
# plt.plot(tire_data[:,FX], tire_data[:,FY], '.', markersize=1)
plt.show()