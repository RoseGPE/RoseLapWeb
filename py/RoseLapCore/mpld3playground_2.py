import sims
import input_processing.vehicle as vehicle
import input_processing.fancyyaml as yaml
import input_processing.track_segmentation as trackseg
import plottools


import mpld3
from mpld3 import plugins, utils
from mpld3.utils import get_id
import numpy as np
import collections
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from mpld3.plugins import PluginBase
import collections
import json
import uuid

import matplotlib.cm as cmx
import matplotlib.colors as colorsx
import matplotlib.colorbar as colorbar

import math

import pandas as pd


#mpld3 hack
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        import numpy as np
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
from mpld3 import _display
_display.NumpyEncoder = NumpyEncoder

css = """
table
{
  border-collapse: collapse;
}
th
{
  color: #ffffff;
  background-color: #000000;
}
td
{
  background-color: #cccccc;
}
table, th, td
{
  font-family: Consolas, Ubuntu Mono, monospace;
  border: 1px solid black;
  text-align: right;
  font-size: 10pt;
}
"""

class InteractiveLegendPlugin(PluginBase):
    """A plugin for an interactive legends.

    Inspired by http://bl.ocks.org/simzou/6439398

    Parameters
    ----------
    plot_elements : iterable of matplotlib elements
        the elements to associate with a given legend items
    labels : iterable of strings
        The labels for each legend element
    ax :  matplotlib axes instance, optional
        the ax to which the legend belongs. Default is the first
        axes. The legend will be plotted to the right of the specified
        axes
    alpha_unsel : float, optional
        the alpha value to multiply the plot_element(s) associated alpha
        with the legend item when the legend item is unselected.
        Default is 0.2
    alpha_over : float, optional
        the alpha value to multiply the plot_element(s) associated alpha
        with the legend item when the legend item is overlaid.
        Default is 1 (no effect), 1.5 works nicely !
    start_visible : boolean, optional (could be a list of booleans)
        defines if objects should start selected on not.
    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> from mpld3 import fig_to_html, plugins
    >>> N_paths = 5
    >>> N_steps = 100
    >>> x = np.linspace(0, 10, 100)
    >>> y = 0.1 * (np.random.random((N_paths, N_steps)) - 0.5)
    >>> y = y.cumsum(1)
    >>> fig, ax = plt.subplots()
    >>> labels = ["a", "b", "c", "d", "e"]
    >>> line_collections = ax.plot(x, y.T, lw=4, alpha=0.6)
    >>> interactive_legend = plugins.InteractiveLegendPlugin(line_collections,
    ...                                                      labels,
    ...                                                      alpha_unsel=0.2,
    ...                                                      alpha_over=1.5,
    ...                                                      start_visible=True)
    >>> plugins.connect(fig, interactive_legend)
    >>> fig_to_html(fig)
    """

    JAVASCRIPT = open('mpld3playground.js').read()

    css_ = """
    .legend-box {
      cursor: pointer;
      font-size: 10pt;
    }
    """

    def __init__(self, plot_elements, labels, ax=None,
                 alpha_unsel=0.2, alpha_over=1., start_visible=True, raw_data=[], option_data=[], limits=None):

        self.ax = ax

        if ax:
            ax = get_id(ax)

        # start_visible could be a list
        if isinstance(start_visible, bool):
            start_visible = [start_visible] * len(labels)
        elif not len(start_visible) == len(labels):
            raise ValueError("{} out of {} visible params has been set"
                             .format(len(start_visible), len(labels)))     

        mpld3_element_ids = self._determine_mpld3ids(plot_elements)
        self.mpld3_element_ids = mpld3_element_ids
        self.dict_ = {"type": "interactive_legend",
                      "element_ids": mpld3_element_ids,
                      "labels": labels,
                      "ax": ax,
                      "option_data": zip(range(len(labels)), labels),
                      "raw_data": raw_data.T,
                      "limits": limits}

    def _determine_mpld3ids(self, plot_elements):
        """
        Helper function to get the mpld3_id for each
        of the specified elements.
        """
        mpld3_element_ids = []

        # There are two things being done here. First,
        # we make sure that we have a list of lists, where
        # each inner list is associated with a single legend
        # item. Second, in case of Line2D object we pass
        # the id for both the marker and the line.
        # on the javascript side we filter out the nulls in
        # case either the line or the marker has no equivalent
        # D3 representation.
        for entry in plot_elements:
            ids = []
            if isinstance(entry, collections.Iterable):
                for element in entry:
                    mpld3_id = get_id(element)
                    ids.append(mpld3_id)
                    if isinstance(element, matplotlib.lines.Line2D):
                        mpld3_id = get_id(element, 'pts')
                        ids.append(mpld3_id)
            else:
                ids.append(get_id(entry))
                if isinstance(entry, matplotlib.lines.Line2D):
                    mpld3_id = get_id(entry, 'pts')
                    ids.append(mpld3_id)
            mpld3_element_ids.append(ids)

        return mpld3_element_ids

sim = sims.Simulation("point_mass");

vehicle  = vehicle.Vehicle(yaml.load(open('params/vehicles/rgp007.yaml','r'),True))
vehicle.prep()
segments = trackseg.file_to_segments('params/DXFs/ne_2017_endurance.svg',2.0)
xys = np.array([[s.x,s.y] for s in segments])
output = sim.solve(vehicle, segments[:len(segments)/1])


fig, ax = plt.subplots()
line_collections = []
x = xys[:,0]
y = xys[:,1]
# df = pd.DataFrame(index=range(len(x)))
# for i in range(sims.O_MATRIX_COLS):
z = output[:,sims.O_VELOCITY]
line_collections.append(ax.scatter(x, y, c=z, s=8))

	# df[sims.O_NAMES[i]] = z
ax.axis('equal')
ax.grid(True, color='gray', alpha=0.2)
dx = 100.0
plt.xticks(np.arange((math.ceil(min(x)/dx)-1)*dx, math.ceil(max(x)/dx)*dx+1, dx))
plt.yticks(np.arange((math.ceil(min(y)/dx)-1)*dx, math.ceil(max(y)/dx)*dx+1, dx))

interactive_legend = InteractiveLegendPlugin(line_collections, sims.O_NAMES, alpha_unsel=0.0, raw_data=output, limits=sims.O_LIMITS)
plugins.connect(fig, interactive_legend)

labels = []
for i in range(len(x)):
    # .to_html() is unicode; so make leading 'u' go away with str()
    labels.append('<table>' + ('<tr><td>Position</td><td>ft</td><td>%.3f, %.3f</td></tr>' % (x[i],y[i]) )+''.join(['<tr><td>%s</td><td>%s</td><td>%.3f</td></tr>' % (sims.O_NAMES[o],sims.O_UNITS[o],output[i,o]) for o in range(len(output[i,:]))]) + '</table>')

tooltip = plugins.PointHTMLTooltip(line_collections[0], labels,
                                   voffset=10, hoffset=10, css=css)
plugins.connect(fig, tooltip)

mpld3.show()

