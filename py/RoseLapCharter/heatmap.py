import sys, os
import config

sys.path.append(config.basepath.replace("/", "\\"))

from highcharts import Highchart
from RoseLapCore import *
from charting_tools.py import *

def makeHeatmap(data, times):
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
        'text': "Track Times: " + labels[0][0] + " vs. " + labels[1][0]
    })

    H.set_options('colorAxis', {
        'min': 4.4,
        'max': 4.9,
        'minColor': '#FFFFFF',
        'maxColor': '#000000'
    })

    H.set_options('legend', {
        'align': 'right',
        'layout': 'vertical',
        'margin': 0,
        'verticalAlign': 'top',
        'y': 25,
        'symbolHeight': 280
    })

    H.set_options('tooltip', {
        'formatter': "function () {" + 
                    "return this.point.value + '<br>mass of ' + this.series.xAxis.categories[this.point.x] +" +
                        "'<br>aero stuff of ' + this.series.yAxis.categories[this.point.y];" +
                "}"
    })

    return H

def makeChart(absolutePath, filename):
    data = packer.unpack(absolutePath)
    times = data["track_data"][0]["times"]
    times = [(t[0], t[1], str(t[2])[0:6]) for t in times]

    filename + ".html"H = makeHeatmap(data, times)
    

    
    writeHTML(H, filename + ".html")