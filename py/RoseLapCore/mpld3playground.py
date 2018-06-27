

import mpld3
from mpld3 import plugins, utils
from mpld3.utils import get_id
import numpy as np
import collections
import matplotlib
import matplotlib.pyplot as plt

from mpld3.plugins import PluginBase
import collections
import json
import uuid


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

    JAVASCRIPT = """
    mpld3.register_plugin("interactive_legend", InteractiveLegend);
    InteractiveLegend.prototype = Object.create(mpld3.Plugin.prototype);
    InteractiveLegend.prototype.constructor = InteractiveLegend;
    InteractiveLegend.prototype.requiredProps = ["element_ids", "labels"];
    InteractiveLegend.prototype.defaultProps = {"ax":null,
                                                "alpha_unsel":0.2,
                                                "alpha_over":1.0,
                                                "start_visible":true,
                                                "active_start":0}
    function InteractiveLegend(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    InteractiveLegend.prototype.draw = function(){
        var alpha_unsel = this.props.alpha_unsel;
        var alpha_over = this.props.alpha_over;

        var legendItems = new Array();
        var previous_box = null;
        var previous_d = null;
        for(var i=0; i<this.props.labels.length; i++){
            var obj = {};
            obj.index = i;
            obj.label = this.props.labels[i];

            var element_id = this.props.element_ids[i];
            mpld3_elements = [];
            for(var j=0; j<element_id.length; j++){
                var mpld3_element = mpld3.get_element(element_id[j], this.fig);

                // mpld3_element might be null in case of Line2D instances
                // for we pass the id for both the line and the markers. Either
                // one might not exist on the D3 side
                if(mpld3_element){
                    mpld3_elements.push(mpld3_element);
                }
            }

            obj.mpld3_elements = mpld3_elements;
            obj.visible = false; //this.props.start_visible[i]; // should become be setable from python side
            legendItems.push(obj);
            set_alphas(obj, false);
        }

        // determine the axes with which this legend is associated
        var ax = this.props.ax
        if(!ax){
            ax = this.fig.axes[0];
        } else{
            ax = mpld3.get_element(ax, this.fig);
        }

        // add a legend group to the canvas of the figure
        var legend = this.fig.canvas.append("svg:g")
                               .attr("class", "legend");

        // add the rectangles
        legend.selectAll("rect")
                .data(legendItems)
                .enter().append("rect")
                .attr("height", 10)
                .attr("width", 25)
                .attr("x", ax.width + ax.position[0] + 25)
                .attr("y",function(d,i) {
                           return ax.position[1] + i * 25 + 10;})
                .attr("stroke", get_color)
                .attr("class", "legend-box")
                .style("fill", function(d, i) {
                           return d.visible ? get_color(d) : "white";})
                .on("click", click).on('mouseover', over).on('mouseout', out);

        // add the labels
        legend.selectAll("text")
              .data(legendItems)
              .enter().append("text")
              .attr("x", function (d) {
                           return ax.width + ax.position[0] + 25 + 40;})
              .attr("y", function(d,i) {
                           return ax.position[1] + i * 25 + 10 + 10 - 1;})
              .text(function(d) { return d.label });


        // specify the action on click
        function click(d,i){
       		console.log(d);
        	console.log(legendItems);
        	console.log(this);

        	if (previous_box) {
        		previous_d.visible = false;
	            d3.select(previous_box)
	              .style("fill",function(d, i) {
	                return d.visible ? get_color(d) : "white";
	              })
	            set_alphas(previous_d, false);
        	}
        	previous_box = this;
        	previous_d = d;

            d.visible = true;
            d3.select(this)
              .style("fill",function(d, i) {
                return d.visible ? get_color(d) : "white";
              })
            set_alphas(d, false);

        };

        // specify the action on legend overlay 
        function over(d,i){
        	if(previous_box){
        		previous_d.visible = false;
	            d3.select(previous_box)
	              .style("fill",function(d, i) {
	                return d.visible ? get_color(d) : "white";
	              })
	            set_alphas(previous_d, false);
        	}
            d.visible = true;
            d3.select(this)
              .style("fill",function(d, i) {
                return d.visible ? get_color(d) : "white";
              })
            set_alphas(d, false);
        };

        // specify the action on legend overlay 
        function out(d,i){
        	d.visible = false;
            d3.select(this)
              .style("fill",function(d, i) {
                return d.visible ? get_color(d) : "white";
              })
            set_alphas(d, false);
        	if(previous_d){
        		previous_d.visible = true;
	            d3.select(previous_box)
	              .style("fill",function(d, i) {
	                return d.visible ? get_color(d) : "white";
	              })
	            set_alphas(previous_d, false);
        	}
            
        };

        // helper function for setting alphas
        function set_alphas(d, is_over){
            for(var i=0; i<d.mpld3_elements.length; i++){
                var type = d.mpld3_elements[i].constructor.name;

                if(type =="mpld3_Line"){
                    var current_alpha = d.mpld3_elements[i].props.alpha;
                    var current_alpha_unsel = current_alpha * alpha_unsel;
                    var current_alpha_over = current_alpha * alpha_over;
                    d3.select(d.mpld3_elements[i].path[0][0])
                        .style("stroke-opacity", is_over ? current_alpha_over :
                                                (d.visible ? current_alpha : current_alpha_unsel))
                        .style("stroke-width", is_over ? 
                                alpha_over * d.mpld3_elements[i].props.edgewidth : d.mpld3_elements[i].props.edgewidth);
                } else if((type=="mpld3_PathCollection")||
                         (type=="mpld3_Markers")){
                    var current_alpha = d.mpld3_elements[i].props.alphas[0];
                    var current_alpha_unsel = current_alpha * alpha_unsel;
                    var current_alpha_over = current_alpha * alpha_over;
                    d3.selectAll(d.mpld3_elements[i].pathsobj[0])
                        .style("stroke-opacity", is_over ? current_alpha_over :
                                                (d.visible ? current_alpha : current_alpha_unsel))
                        .style("fill-opacity", is_over ? current_alpha_over :
                                                (d.visible ? current_alpha : current_alpha_unsel));
                } else{
                    console.log(type + " not yet supported");
                }
            }
        };


        // helper function for determining the color of the rectangles
        function get_color(d){
            var type = d.mpld3_elements[0].constructor.name;
            var color = "black";
            if(type =="mpld3_Line"){
                color = d.mpld3_elements[0].props.edgecolor;
            } else if((type=="mpld3_PathCollection")||
                      (type=="mpld3_Markers")){
                color = d.mpld3_elements[0].props.facecolors[0];
            } else{
                console.log(type + " not yet supported");
            }
            return color;
        };
    };
    """

    css_ = """
    .legend-box {
      cursor: pointer;
    }
    """

    def __init__(self, plot_elements, labels, ax=None,
                 alpha_unsel=0.2, alpha_over=1., start_visible=True, default_data=0):

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
                      "alpha_unsel": alpha_unsel,
                      "alpha_over": alpha_over,
                      "start_visible": [i==default_data for i in range(len(labels))],
                      "active_start": default_data}

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


N_paths = 5
N_steps = 100

x = np.linspace(0, 10, 100)
y = 0.1 * (np.random.random((N_paths, N_steps)) - 0.5)
y = y.cumsum(1)

fig, ax = plt.subplots()
labels = ["apple", "banana", "cherry", "date", "eggplant"]
line_collections = ax.plot(x, y.T, lw=4, alpha=1.0)
interactive_legend = InteractiveLegendPlugin(line_collections, labels, alpha_unsel=0.0, default_data=0)
plugins.connect(fig, interactive_legend)

mpld3.show()

