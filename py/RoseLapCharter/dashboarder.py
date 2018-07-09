import sys, os
sys.path.append('C:\wamp\www\RoseLap\py')

import singleaxis
import heatmap
import mapview
import detail
import packer
import pprint

from charting_tools import *

def make_dashboard(results, display_name):
	graph_dir = makeGraphFolder(display_name)

	spawn_details(results, display_name)

	axes = len(results["axiscontents"])

	if axes == 1:
		summary_plot = singleaxis.make_plot(results, display_name)
	elif axes == 2:
		summary_plot = heatmap.make_plot(results, display_name)
	else:
		print("Unsupported plot dimensions! Please submit data with 1 or 2 axes.") 
		exit()

	map_plot = mapview.make_plot(results, display_name)
	plots = make_row(make_col(map_plot, 6) + make_col(summary_plot, 6))

	metadata = make_col(append_raw("", generate_metadata(results, display_name)), 6)


	dashboard = ""
	dashboard = dashboard + plots
	dashboard = append_raw(dashboard, metadata)
	dashboard = finalize_page(dashboard)

	with open(graph_dir + "\\" + display_name + "-dashboard.php", "w") as file:
		file.write(dashboard)

def generate_metadata(results, display_name):
	db_id = "Dashboard ID: " + display_name + "\n"
	model = "Model: " + results["model"] + "\n"
	axes = "Axes: " + str(len(results["axiscontents"])) + "\n"
	vehicle = "Vehicle parameters: \n" + pprint.pformat(results["vehicle"])
	tracks = "Tracks: " + str([td["name"] for td in results["track_data"]])

	md = db_id + model + axes + tracks + vehicle
	return md

def append_frame(base, page):
	return base + "<iframe src=\"" + page + "\"></iframe>"

def append_raw(base, page):
	return base + "<div><pre>" + page + "</pre></div>"

def make_col(text, size):
	return '<div class="col-sm-' + str(size) + '">' + text + "</div>"

def make_row(text):
	return '<div class="row">' + text + "</div>"

def finalize_page(page):
	return getHead() + '<div class="container">' + page + "</div>"

def spawn_details(results, display_name):
	pass
	# print detail.make_sub_plot(results["track_data"][0]["outputs"][0][axes])

if __name__ == "__main__":
	# r = packer.unpack('C:\wamp\www\RoseLap\py\RoseLapCore/out/test_batch_results-1530737683/test_batch_results-1530737683.rslp')
	r = packer.unpack('C:\wamp\www\RoseLap\py\RoseLapCore/out/test_batch_results-1530737757/test_batch_results-1530737757.rslp')
	make_dashboard(r, "testtest")