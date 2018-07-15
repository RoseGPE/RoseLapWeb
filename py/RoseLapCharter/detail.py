import matplotlib.pyplot as plt, mpld3
import numpy as np
from charting_tools import *
from RoseLapCore import sims
from sims.constants import *

def make_sub_plot(file, output):
    file.write('<div id="distance" style="display: none;">')
    plotter(output, file=file)
    file.write('</div><div id="time" style="display: block;">')
    plotter(output, 'time', file=file)
    file.write('''</div><button onclick="setDistance()">Distance</button>
        <button onclick="setTime()">Time</button>
        <script type="text/javascript">
            var setDistance = function () {
                document.getElementById("distance").style.display = "block";
                document.getElementById("time").style.display = "none";
            }
            var setTime = function () {
                document.getElementById("time").style.display = "block";
                document.getElementById("distance").style.display = "none";
            }
        </script>''')

def plotter(output, axis='distance', title='Velocity and Events', saveimg=False, imgname="broken.png", file=None):
    output = np.array(output)

    fig, ax = plt.subplots(5, sharex=True)
    fig.canvas.set_window_title(title)
    fig.set_size_inches(12, 8)

    fig.suptitle(title)

    t = output[:, O_TIME]
    x = output[:, O_DISTANCE]
    v = output[:, O_VELOCITY]

    sectors = output[:, O_SECTORS]
    status = output[:, O_STATUS]
    gear = output[:, O_GEAR]

    along = output[:, O_LONG_ACC]
    alat = output[:, O_LAT_ACC]
    eng_rpm = output[:, O_ENG_RPM]

    curv = output[:, O_CURVATURE]

    if axis == 'time':
        plt.xlabel('Elapsed time')
        xaxis = t
    else:
        xaxis = x
        plt.xlabel('Distance travelled')

    ax[0].plot(xaxis,v,lw=5,label='Velocity')
    ax[0].set_ylim((0,max(v)*1.05))


    ax[1].plot(xaxis,curv,lw=5,label='Curvature',marker='.',linestyle='none')
    ax[1].set_ylim(0,max(curv)*1.05)

    ax[2].plot(xaxis,output[:, O_LONG_ACC], lw=4,label='Longitudinal g\'s')
    ax[2].plot(xaxis,output[:, O_LAT_ACC],lw=4,label='Lateral g\'s')
    ax[2].set_ylim(-3,3)

    ax[3].plot(xaxis,output[:, O_GEAR]+1,lw=4,label='Gear')
    ax[3].plot(xaxis,output[:, O_ENG_RPM]/1000, lw=4, label='RPM x1000')
    ax[3].set_ylim(0, 18)

    forces = output[:, [O_NF, O_NR, O_FF_REMAINING, O_FR_REMAINING]]
    force_lim = max(forces.min(), forces.max(), key=abs)*1.05
    ax[4].plot(xaxis,output[:, O_NF], lw=4,label='Front normal force')
    ax[4].plot(xaxis,output[:, O_NR], lw=4,label='Rear normal force')
    ax[4].plot(xaxis,output[:, O_FF_REMAINING], lw=4,label='Remaining front long. force')
    ax[4].plot(xaxis,output[:, O_FR_REMAINING], lw=4,label='Remaining rear long. force')
    ax[4].set_ylim(-force_lim,force_lim)

    lim = max(curv)
    alpha =  1

    ax[1].fill_between(xaxis, 0, lim, where= status==S_BRAKING,      facecolor='#e22030', alpha=alpha)
    ax[1].fill_between(xaxis, 0, lim, where= status==S_ENG_LIM_ACC,  facecolor='#50d21d', alpha=alpha)
    ax[1].fill_between(xaxis, 0, lim, where= status==S_TIRE_LIM_ACC, facecolor='#1d95d2', alpha=alpha)
    ax[1].fill_between(xaxis, 0, lim, where= status==S_SUSTAINING,   facecolor='#d2c81c', alpha=alpha)
    ax[1].fill_between(xaxis, 0, lim, where= status==S_DRAG_LIM,     facecolor='#e2952b', alpha=alpha)
    ax[1].fill_between(xaxis, 0, lim, where= status==S_SHIFTING,     facecolor='#454545', alpha=alpha)
    ax[1].fill_between(xaxis, 0, lim, where= status==S_TOPPED_OUT,   facecolor='#7637a2', alpha=alpha)

    sector = sectors[0]
    for idx,sec in enumerate(sectors):
        if sec!=sector:
            ax[1].axvline(xaxis[idx], color='black', lw=2, alpha=0.9)
            sector=sec

    plt.xlim((0,max(xaxis)))

    for a in ax:
        a.grid(True)
        a.legend()

    if file is None:
        x = mpld3.fig_to_html(fig)
        plt.close(fig)
        return x
    else:
        mpld3.save_html(fig, file)
        plt.close(fig)