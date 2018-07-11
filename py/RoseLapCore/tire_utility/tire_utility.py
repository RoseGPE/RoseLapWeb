import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

fn = 'A1654run45.dat' # USERDEF select from the data folder
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
plt.figure(num=None, figsize=(20, 11), dpi=80, facecolor='w', edgecolor='k')

plt.subplot(221)
plt.hist(tire_data[:,FZ], 50)
plt.title('Histogram of Normal Forces')
plt.xlabel('Normal Force (lb)')
plt.ylabel('Frequency in Dataset')

# USERDEF the 'bins' of tire data tested, and the median data at each
bins = [[-275,-230],[-210,-170],[-155,-130],[-100,0]]
avgs = [-230, -185, -140, -45]
xmax = []
ymax = []

sigmas = 1.7 # USERDEF how many standard deviations to accept

def reject_outliers(data, m, by_col):
    s = abs(data[:,by_col] - np.mean(data[:,by_col])) < m * np.std(data[:,by_col])
    print('rejecting',np.where(abs(data[:,by_col] - np.mean(data[:,by_col])) >= m * np.std(data[:,by_col])))
    return data[s]

plt.subplot(222)
for i in range(0,len(avgs)):
    tire_data_filtered = tire_data[(tire_data[:,FZ] > bins[i][0]) & (tire_data[:,FZ] < bins[i][1])]
    plt.plot(tire_data_filtered[:,FX], tire_data_filtered[:,FY], '.', markersize=1, label=("Raw, FZ=%.1f" % avgs[i]))
    tire_data_filtered = reject_outliers(reject_outliers(tire_data_filtered,sigmas,FX), sigmas,FY)
    plt.title('Friction Ellipses')
    plt.xlabel('X (Longitudinal) Force (lb)')
    plt.ylabel('Y (Lateral) Force (lb)')
    xmax.append(max(abs(tire_data_filtered[:,FX])))
    ymax.append(max(abs(tire_data_filtered[:,FY])))
    print('@%f lbf normal, X friction %f, Y friction %f' % (avgs[i], xmax[-1], ymax[-1]))

slope_x,intercept_x = np.linalg.lstsq(np.vstack([avgs, np.ones(len(avgs))]).T, xmax)[0]
slope_y,intercept_y = np.linalg.lstsq(np.vstack([avgs, np.ones(len(avgs))]).T, ymax)[0]
print('Regression results:')
print('Longitudinal: Fx = %f * Fz + %f' % (slope_x, intercept_x))
print('Lateral: Fy = %f * Fz + %f' % (slope_y, intercept_y))
# USERDEF: Override slopes and intercepts as you please
# slope_x
# slope_y
# intercept_x
# intercept_y
xm = intercept_x+slope_x*bins[0][0]
ym = intercept_y+slope_y*bins[0][0]

plt.subplot(223)
plt.plot(avgs,xmax,'bo',label='Captured Points')
plt.plot([0,bins[0][0]],[intercept_x, xm], 'r', label='Fit Line')
plt.plot(tire_data[:,FZ], abs(tire_data[:,FX]), '.', markersize=1, label='Tire Data')
plt.ylim([0,max(xm,ym)*1.05])
plt.title('X (Longitudinal) Force vs. Normal Force')
plt.xlabel('Normal Force (lb)')
plt.ylabel('Longitudinal Force (lb)')
plt.text(0,max(ym,xm)*0.7,'Fx = %.4f * Fz + %.2f ' % (slope_x, intercept_x),horizontalalignment='right')
plt.legend()

plt.subplot(224)
plt.plot(avgs,ymax,'bo',label='Captured Points')
plt.plot([0,bins[0][0]],[intercept_y, ym], 'r', label='Fit Line')
plt.plot(tire_data[:,FZ], abs(tire_data[:,FY]), '.', markersize=1, label='Tire Data')
plt.ylim([0,max(ym,xm)*1.05])
plt.title('Y (Lateral) Force vs. Normal Force')
plt.xlabel('Normal Force (lb)')
plt.ylabel('Lateral Force (lb)')
plt.text(0,max(ym,xm)*0.7,'Fy = %.4f * Fz + %.2f ' % (slope_y, intercept_y),horizontalalignment='right')
plt.legend()

plt.subplot(222)
for i in range(0,len(avgs)):
    xm = intercept_x + slope_x*avgs[i]
    ym = intercept_y + slope_y*avgs[i]
    X = np.linspace(-xm,xm,num=200)
    Y = ym*np.sqrt(1-X**2/xm**2)
    plt.plot(X,Y,'--',label=("Fit, FZ=%.1f" % avgs[i]))
plt.legend()

print('Final decision:')
print('Longitudinal: Fx = %f * Fz + %f' % (slope_x, intercept_x))
print('Lateral: Fy = %f * Fz + %f' % (slope_y, intercept_y))

# ax = plt.gca(projection='3d')
# ax.scatter(tire_data[:,FX], tire_data[:,FY], tire_data[:,FZ], '.', markersize=1)
# mtd = min(tire_data[:,FZ]);
# print(mtd);
# color = [str(item/mtd/255.) for item in tire_data[:,FZ]]
# plt.plot(tire_data[:,FX], tire_data[:,FY], '.', markersize=1)
plt.subplots_adjust(wspace=0.12)
plt.tight_layout()
plt.show()