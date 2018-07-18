import sys, os
import config
import detail

sys.path.append('C:\wamp\www\RoseLap\py')

# from highcharts import Highchart
from RoseLapCore import *
from charting_tools import *
import plotter
import numpy as np

def makeHeatmap(data, times, pathname, output=False, track_name=""):
    raw_times = [time[2] for time in times]

    H = Highchart()
    H.add_data_set(times, name='Track Times', type="heatmap")


    labels = [makeLabel(d) for d in data["axiscontents"]]
    print(labels)

    H.set_options('chart', {
        'type': 'heatmap',
        'marginTop': 40,
        'height': 500,
        'width': 500,
        'marginBottom': 80,
        'plotBorderWidth': 1
    })

    H.set_options('xAxis', {
        'categories': labels[0][1],
        'title': {
            'text':  labels[0][0]
        }
    })

    H.set_options('yAxis', {
        'categories': labels[1][1],
        'title': {
            'text': labels[1][0]
        }
    })

    H.set_options('title', {
        'text': track_name + " Track Times: " + labels[0][0] + " vs. " + labels[1][0]
    })

    H.set_options('colorAxis', {
        'min': min(raw_times),
        'max': max(raw_times),
        'minColor': '#E0FF4F',
        'maxColor': '#FF2ECC'
    })

    H.set_options('legend', {
        'align': 'right',
        'layout': 'vertical',
        'margin': 0,
        'verticalAlign': 'top',
        'y': 25,
        'symbolHeight': 280
    })

    if output:
        H.set_options('tooltip', {
            'style': {
                        'padding': 0,
                        'pointerEvents': 'auto'
                    },
            'formatter': '''function() {
                                return this.point.value +
                                '<br><a style="color:blue; text-decoration:underline;" target="_blank" href="''' + pathname + '''/' + parseInt(this.point.x) + '-' + parseInt(this.point.y) + '.html">details</a>';
                            }'''
        })
    else:
        H.set_options('tooltip', {
            'style': {
                        'padding': 0,
                        'pointerEvents': 'auto'
                    },
            'formatter': '''function() {
                                return this.point.value;
                            }'''
        })

    return H

def make_plot(data, filename):
    tally = ""
    for td in data["track_data"]:
        times = td["times"]
        name = td["name"].split("\\")[-1].split(".")[0] # don't worry about this, I'm just parsing the track name in the data into something nicer since the "track name" for some of the data is a path lol

        outputs = td['outputs']
        if len(outputs) > 0:
            makeGraphFolder(filename + "\\" + filename + "-" + name)
            out = True

            for output in outputs:
                x, y, outdata = output
                iname = displayDirectory(filename) + filename + "-" + name + "\\" + str(x) + "-" + str(y)
                with open(iname + ".html", "w") as plot:
                    plot.write(detail.make_sub_plot(outdata))
                # plotter.plot_velocity_and_events(np.array(outdata), saveimg=True, imgname=iname)
        else:
            out = False

        H = makeHeatmap(data, times, filename + "-" + name, output=out, track_name=name)
        tally += H.htmlcontent
        writeHTML(H, filename + "/" + filename + "-" + name + ".html")

    return tally

if __name__ == "__main__":
    absolutePath = 'C:/wamp/www/RoseLap/py/RoseLapCore/out/test_batch_results-1525219799/test_batch_results-1525219799.rslp'
    filename = "1525219799"

    make_plot(packer.unpack(absolutePath), filename)