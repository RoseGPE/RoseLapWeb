import sys, os
import config
import json

# Decide wether to make a line graph or heat map (Line map only taking two variables).
# Time is an implicit variable

sys.path.append('C:\wamp\www\RoseLap\py')
print(sys.path)

# from highcharts import Highchart
from RoseLapCore import packer
from charting_tools import *
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

# def makeLineGraph(data, times):
def makeLineGraphTrial(data):

	u = 'track_data'
	s = 'times'
	data_y = [data[u][0][s][0][1], data[u][0][s][1][1], data[u][0][s][2][1], data[u][0][s][3][1], data[u][0][s][4][1], data[u][0][s][5][1]]
	a='axiscontents'
	data_x = [data[a][0]['mass'][0], data[a][0]['mass'][1], data[a][0]['mass'][2], data[a][0]['mass'][3], data[a][0]['mass'][4], data[a][0]['mass'][5]]

	H = Highchart()

	H.add_data_set(data_x, 'line', 'Mass')

	 #Have to do H.add_data sets with data sets I make
	# H.add_data_set(times, name='Track Times', type="linegraph")
	#I don't know why I'd need to take in times for a line-graph

	H.set_options('yAxis',{'title': { 'text': 'Lap-Times'},
	 	'plotLines': {'value': 0, 'width':1, 'color': '#808080'}})

	# H.set_options('xAxis', {'categories': })

	H.set_options('legend', {'layout': 'vertical','align': 'right',
		'verticalAlign': 'middle','borderWidth': 0})

	H.set_options('colors',{})

	H.set_options('plotOptions',{'line': {'dataLabels': {
		'enabled': True}}})

	return H

def makeChart(absolutePath, filename):

	data = packer.unpack(absolutePath)
	times = data["track_data"][0]["times"]
	times = [(t[0], t[1], str(t[2])[0:6]) for t in times]

	# filename += ".html"

	# H = makeLineGraph(data, times)
	H = makeLineGraphTrial(data)

	writeHTML(H, filename)

if __name__ == "__main__":

	data = json.load(open('1axissample.fakedata'))

	absolutePath = 'C:/wamp/www/RoseLap/py/RoseLapCore/out/test_batch_results-1525219799/test_batch_results-1525219799.rslp'
	filename = "test_batch_results-linegraph"
	
	makeChart(absolutePath, filename)



	# makeLineGraph(data, times)
	H = makeLineGraphTrial(data)

	print(data)

