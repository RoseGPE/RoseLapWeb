import sys, os
sys.path.append('C:\wamp\www\RoseLap\py')

import singleaxis
import singleaxis_v2
import heatmap
import heatmap_v2
import mapview
import detail
import packer
import pprint

from charting_tools import *

def make_dashboard(results, display_name, display_dir):
    axes = len(results["axiscontents"])
    pre = ""
    page = ""

    if axes == 1:
        summary_plot = singleaxis_v2.make_plot(results, display_dir, display_name)
        plots = make_row(make_col(summary_plot, 12))
        page = page + plots
    elif axes == 2:
        summary_plot = heatmap_v2.make_plot(results, display_dir, display_name)
        plots = make_row(make_col(summary_plot, 12))
        pre = pre + plots
    else:
        print("Unsupported plot dimensions! Please submit data with 1 or 2 axes.") 
        exit()  

    metadata = make_col(append_raw("", generate_metadata(results, display_name)), 6)
    page = append_raw(page, metadata)

    dashboard = finalize_page(pre, page)

    with open(display_dir + "/" + display_name + "-dashboard.php", "w") as file:
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
    return '<div style="height: 100%" class="row">' + text + "</div>"

def finalize_page(pre, page):
    return getHead() + pre + '<div class="container">' + page + "</div>"

if __name__ == "__main__":
    # r = packer.unpack('C:\wamp\www\RoseLap\py\RoseLapCore/out/test_batch_results-1530737683/test_batch_results-1530737683.rslp')
    r = packer.unpack('C:\wamp\www\RoseLap\py\RoseLapCore/out/test_batch_results-1530737757/test_batch_results-1530737757.rslp')
    make_dashboard(r, "testtest")