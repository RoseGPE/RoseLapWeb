import sys, os
import config

# Decide wether to make a line graph or heat map (Line map only taking two variables).
# Time is an implicit variable

from highcharts import Highchart
from RoseLapCore import *

def makeLabel(d):

	data = list(d.values())
	label = []

	for i in range(len(data[0])):
		label.append(str([v[i] for v in data])[1:-1])
	return(str([k for k in list(d.keys())])[1:-1], label)

def writeHTML(H, filename):
	with open("../graph/" + filename + ".html", "w") as chart:
		chart.write(H.htmlcontent)

def makeLineGraph(data, times):

	H = Highchart()
	H.add_data_set(times, name='Track Times', type="linegraph")

	labels = [makeLabel(d) for d in data["axiscontents"]]
	print(labels)

	H.set_options('chart', {'type': 'linegraph',
		'marginTop': 40,
		'heigh': 500,
		'width': 500,
		'marginBottom': 80,
		'plotBorderWidth': 1
	})

#Start by just listing data. When mass is x, time is y.

	H.set_options('xAxis,'{
		'categories': labels[0][1],
		'title': {
			'text': labels[0][0]
		}
	})

	H.set_options('yAxis',{
		'categories': labels[1][1],
		'title': {
			'text': labels[1][0]
		}
	})
def makeChart(absolutePath, filename):
	data = packer.unpack(absolutePath)
	times = data["track_data"][0]["times"]

#From there, add in element of using highcharts output
