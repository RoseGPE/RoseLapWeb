import matplotlib.pyplot as plt
import mpld3
import numpy as np
from charting_tools import *

def make_plot(data, filename):
	label = makeLabel(data["axiscontents"][0])
	xlabel = label[0]
	xpoints = label[1]
	plot_title = "The effect of " + label[0] + " on lap time"

	fig, ax = plt.subplots()

	for track in data["track_data"]:
		print(generateTimeseries(track["times"]))
		line_label = track["name"]
		ax.plot(xpoints, generateTimeseries(track["times"]), label=line_label, marker='x', linestyle='-', picker=5)

	ax.grid(True)
	ax.legend()

	plt.title(plot_title)
	plt.xlabel(xlabel)
	plt.ylabel("Lap Time")

	return mpld3.fig_to_html(fig)