import sys, os
import config
import json

# Decide wether to make a line graph or heat map (Line map only taking two variables).
# Time is an implicit variable

sys.path.append(config.basepath.replace("/", "\\"))
print(sys.path)

from highcharts import Highchart
from io import StringIO
import RoseLapCore.packer
# from RoseLapCore import *

# def makeLabel(d):

# 	data = list(d.values())
# 	label = []

# 	for i in range(len(data[0])):
# 		label.append(str([v[i] for v in data])[1:-1])
# 	return(str([k for k in list(d.keys())])[1:-1], label)

# def writeHTML(H, filename):
# 	with open("../graph/" + filename + ".html", "w") as chart:
# 		chart.write(H.htmlcontent)

# def makeLineGraph(data, times):

# 	H = Highchart()
# 	H.add_data_set(times, name='Track Times', type="linegraph")

# 	labels = [makeLabel(d) for d in data["axiscontents"]]
# 	print(labels)

# 	H.set_options('chart', {'type': 'linegraph',
# 		'marginTop': 40,
# 		'heigh': 500,
# 		'width': 500,
# 		'marginBottom': 80,
# 		'plotBorderWidth': 1
# 	})

# #Start by just listing data. When mass is x, time is y.

# 	H.set_options('xAxis,'{
# 		'categories': labels[0][1],
# 		'title': {
# 			'text': labels[0][0]
# 		}
# 	})

# 	H.set_options('yAxis',{
# 		'categories': labels[1][1],
# 		'title': {
# 			'text': labels[1][0]
# 		}
# 	})
# def makeChart(absolutePath, filename):
# 	data = packer.unpack(absolutePath)
# 	times = data["track_data"][0]["times"]
def writeHTML(Boi, filename):
	with open("../graph/" + filename + ".html", "w") as chart:
		chart.write(Boi.htmlcontent)

def makeLineGraph(data, times):
	Boi = Highcart()
	 #Have to do Boi.add_data sets with data sets I make
	Boi.add_data_set(times, name='Track Times', type="linegraph")

	Boi.set_options('yAxis',{'title': { 'text': 'Lap-Times'},
	 	'plotLines': {'value': 0, 'width':1, 'color': '#808080'}})

	Boi.set_options('legend', {'layout': 'vertical','align': 'right',
		'verticalAlign': 'middle','borderWidth': 0})

	Boi.set_options('colors',{})

	Boi.set_options('plotOptions',{'line': {'dataLabels': {
		'enabled': True}}})

	return Boi

def makeChart(absolutePath, filename):
	data = packer.unpack(absolutePath)
	times = data["track_data"][0]["times"]
	times = [(t[0], t[1], str(t[2])[0:6]) for t in times]

	Boi = makeLineGraph(data, times)

	writeHTML(Boi, filename)

if __name__ == "__main__":

	data = json.load(open('1axissample.fakedata'))

	absolutePath = config.basepath + 'RoseLapCore/out/test_batch_results-1521588335/test_batch_results-1521588335.rslp'
	filename = "test_batch_results-1521588335"
	
	makeChart(absolutePath, filename)

	print(data)

#From there, add in element of using highcharts output
