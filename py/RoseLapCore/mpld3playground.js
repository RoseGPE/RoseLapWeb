function Colorbar() {
    var scale, // the input scale this represents;
        margin = {top: 5, right: 30, bottom: 25, left: 0}
    orient = "vertical",
    origin = {
        x: 0,
        y: 0
    }, // where on the parent to put it
    barlength = 100, // how long is the bar
    thickness = 50, // how thick is the bar
    title = "", // title for the colorbar
    scaleType = "linear";




    checkScaleType = function (scale) {
        // AFAIK, d3 scale types aren't easily accessible from the scale itself.
        // But we need to know the scale type for formatting axes properly
        //Or do we? this variable seems not to be used.
        cop = scale.copy();
        cop.range([0, 1]);
        cop.domain([1, 10]);

        if (typeof(cop.invertExtent)!="undefined") {
            return "quantile"
        }
        if (Math.abs((cop(10) - cop(1)) / Math.log(10) - (cop(10) - cop(2)) / Math.log(5)) < 1e-6) {
            return "log"
        }
        else if (Math.abs((cop(10) - cop(1)) / 9 - (cop(10) - cop(2)) / 8) < 1e-6) {
            return "linear"
        }
        else if (Math.abs((cop(10) - cop(1)) / (Math.sqrt(10) - 1) - (cop(10) - cop(2)) / (Math.sqrt(10) - Math.sqrt(2))) < 1e-6) {
            return "sqrt"
        }
        else {
            return "unknown"
        }
    }


    function chart(selection) {
        var fillLegend,
            fillLegendScale;
        selection.pointTo = function(inputNumbers) {
            var pointer = fillLegend.selectAll(".pointer");
            var pointerWidth = Math.round(thickness*3/4);


            //Also creates a pointer if it doesn't exist yet.
            pointers = fillLegend
                .selectAll('.pointer')
                .data([inputNumbers]);

	    pointerSVGdef = function() {
		return (
                orient=="horizontal" ? 
		    'M ' + 0 +' '+ thickness + ' l -' +  pointerWidth + ' -' + pointerWidth + ' l ' + 2*pointerWidth + ' -' + 0 + ' z' :
		    'M ' + thickness +' '+ 0 + ' l -' +  pointerWidth + ' -' + pointerWidth + ' l ' + 0 + ' ' +  2*pointerWidth + ' z' 
			
		)
	    }

            pointers
                .enter()
                .append('path')
                .attr('transform',"translate(0," + (
                    fillLegendScale(inputNumbers) - pointerWidth)+ ')'
                     )
                .classed("pointer",true)
                .classed("axis",true)
                .attr('d', pointerSVGdef())
                .attr("fill","grey")
                .attr("opacity","0");

            //whether it's new or not, it updates it.
            pointers
                .transition()
                .duration(1000)
                .attr('opacity',1)
                .attr('transform',
		      orient=="vertical" ?
		      "translate(0," + (fillLegendScale(inputNumbers))+ ')':
		      "translate(" + (fillLegendScale(inputNumbers))+ ',0)'
		     )
            //and then it fades the pointer out over 5 seconds.
                .transition()
                .delay(2000)
                .duration(3000)
                .attr('opacity',0)
                .remove();
        }

        selection.each(function(data) {

            var scaleType = checkScaleType(scale);
            var thickness_attr;
            var length_attr;
            var axis_orient;
            var position_variable,non_position_variable;
            var axis_transform;

            if (orient === "horizontal") {
                var tmp = [margin.left, margin.right, margin.top, margin.bottom]
                margin.top = tmp[0]
                margin.bottom = tmp[1]
                margin.left = tmp[2]
                margin.right = tmp[3]
                thickness_attr = "height"
                length_attr = "width"
                axis_orient = "bottom"
                position_variable = "x"
		non_position_variable = "y"
                axis_transform = "translate (0," + thickness + ")"
            }

            else {
                thickness_attr = "width"
                length_attr = "height"
                axis_orient = "right"
                position_variable = "y"
                non_position_variable = "x"
                axis_transform = "translate (" + thickness + "," + 0 + ")"
            }

            // select the svg if it exists
            var svg = d3.select(this)
                .selectAll("svg.colorbar")
                .data([origin]);

            // otherwise create the skeletal chart
            var new_colorbars = svg.enter()
                .append("svg")
                .classed("colorbar", true)
                .attr("x",function(d) {return d[0]-margin.right})
                .attr("y",function(d) {return d[1]-margin.top})

	    offsetGroup = new_colorbars
                .append("g")
                .classed("colorbar", true)
	        .attr("transform","translate(" + margin.left + "," + margin.top + ")")

            offsetGroup.append("g")
		.attr("class","legend rectArea")

            offsetGroup.append("g")
		.attr("class","axis color")

            svg
                .attr(thickness_attr, thickness + margin.left + margin.right)
                .attr(length_attr, barlength + margin.top + margin.bottom)
                .style("margin-top", origin.y - margin.top + "px")
                .style("margin-left", origin.x - margin.left + "px")


            // This either creates, or updates, a fill legend, and drops it
            // on the screen. A fill legend includes a pointer chart can be
            // updated in response to mouseovers, because that's way cool.

            fillLegend = svg.selectAll("g.colorbar")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            fillLegendScale = scale.copy();

            if (typeof(fillLegendScale.invert)=="undefined") {
                //console.log("assuming it's a quantile scale")
                fillLegendScale = d3.scale
                    .linear()
                    .domain(d3.extent(fillLegendScale.domain()))
            }

            var legendRange = d3.range(
                0, barlength,
                by=barlength / (fillLegendScale.domain().length - 1));

            legendRange.push(barlength);

	    if (orient=="vertical") {
		//Vertical should go bottom to top, horizontal from left to right.
		//This should be changeable in the options, ideally.
		legendRange.reverse()
	    }
	    fillLegendScale.range(legendRange);
	    
            colorScaleRects = fillLegend
                .selectAll("rect.legend")
                .data(d3.range(0, barlength));

            colorScaleRects
                .enter()
                .append("rect")
                .attr("class", "legend")
                .style("opacity", 0)
                .style("stroke-thickness", 0)
                .style("fill", function(d) {
                    return scale(fillLegendScale.invert(d));
                })

            colorScaleRects
                .exit()
                .remove();

	    //Switch to using the original selection so that the transition will be inheirited
	    selection
	        .selectAll("rect.legend")
                .style("opacity", 1)
                .attr(thickness_attr, thickness)
                .attr(length_attr, 2) // single pixel thickness produces ghosting on some browsers
                .attr(position_variable, function(d) {return d;})
                .attr(non_position_variable, 0)
                .style("fill", function(d) {
                    return scale(fillLegendScale.invert(d));
                })


            colorAxisFunction = d3.svg.axis()
                .scale(fillLegendScale)
                .orient(axis_orient);

	    if (typeof(scale.quantiles) != "undefined") {
		quantileScaleMarkers = scale.quantiles().concat( d3.extent(scale.domain()))
		console.log(quantileScaleMarkers)
		colorAxisFunction.tickValues(quantileScaleMarkers)
	    }

            //Now make an axis
            fillLegend.selectAll(".color.axis")
                .attr("transform", axis_transform)
                .call(colorAxisFunction);

            //make a title
            titles = fillLegend.selectAll(".axis.title")
                .data([{label: title}])
                .attr("id", "#colorSelector")
                .attr('transform', 'translate (0, -10)')
                .style("text-anchor", "middle")
                .text(function(d) {return d.label});

            titles
                .exit()
                .remove();

//            return this;
        });
    }

    function prettyName(number) {

        var comparisontype = comparisontype || function() {return ""}

        if (comparisontype()!='comparison') {
            suffix = ''
            switch(true) {
            case number>=1000000000:
                number = number/1000000000
                suffix = 'B'
                break;
            case number>=1000000:
                number = number/1000000
                suffix = 'M'
                break;
            case number>=1000:
                number = number/1000
                suffix = 'K'
                break;
            }
            if (number < .1) {
                return(Math.round(number*100)/100+suffix)
            }
            return(Math.round(number*10)/10+suffix)
        }
        if (comparisontype()=='comparison') {
            if (number >= 1) {return(Math.round(number)) + ":1"}
            if (number < 1) {return("1:" + Math.round(1/number))}
        }
    }


    //getter-setters
    chart.origin = function(value) {
        if (!arguments.length) return origin;
        origin = value;
        return chart;
    }

    chart.margin = function(value) {
        if (!arguments.length) return margin;
        margin = value;
        return chart;
    }

    chart.thickness = function(value) {
        if (!arguments.length) return thickness;
        thickness = value;
        return chart;
    }

    chart.barlength = function(value) {
        if (!arguments.length) return barlength;
        barlength = value;
        return chart;
    }

    chart.title = function(value) {
        if (!arguments.length) return title;
        title = value;
        return chart;
    }

    chart.scale = function(value) {
        if (!arguments.length) return scale;
        scale = value;
        return chart;
    }

    chart.orient = function(value) {
        if (!arguments.length) return orient;
        if (value === "vertical" || value === "horizontal")
            orient = value;
        else
            console.warn("orient can be only vertical or horizontal, not", value);
        orient = value;
        return chart;
    }

    return chart;
}


    mpld3.register_plugin("interactive_legend", InteractiveLegend);
    InteractiveLegend.prototype = Object.create(mpld3.Plugin.prototype);
    InteractiveLegend.prototype.constructor = InteractiveLegend;
    InteractiveLegend.prototype.requiredProps = ["element_ids", "labels", "raw_data", "option_data", "limits"];
    InteractiveLegend.prototype.defaultProps = {"ax":null,"active_start":0}
    function InteractiveLegend(fig, props){
        mpld3.Plugin.call(this, fig, props);
    };

    InteractiveLegend.prototype.draw = function(){
        var legendItems = new Array();

        var previous_box = 0;
        var previous_d = 0;
        var raw_data = this.props.raw_data;



        /*for(var i=0; i<this.props.labels.length; i++){
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
            obj.visible = i==0;
            set_alphas(obj);
            legendItems.push(obj);
        }*/

        var element_id = this.props.element_ids;
        var limits = this.props.limits;
        var cax = this.props.cax;
        var mpld3_elements = [];
        for(var j=0; j<element_id.length; j++){
            var mpld3_element = mpld3.get_element(element_id[j][0], this.fig);

            // mpld3_element might be null in case of Line2D instances
            // for we pass the id for both the line and the markers. Either
            // one might not exist on the D3 side
            if(mpld3_element){
                mpld3_elements.push(mpld3_element);
            }
        }
        


        // determine the axes with which this legend is associated
        var ax = this.props.ax
        ax = this.fig.axes[0];

        //if(!ax){
            
        //} else{
        //    ax = mpld3.get_element(ax, this.fig);
        //}

        // add a legend group to the canvas of the figure

        var selector = d3.select("body")
        	//.append("svg:g").attr("class","legend")
        	//.append("foreignObject").attr("width","100").attr("height","50")
        	.insert("select",":first-child").attr("name", "name-list").attr("class","legend");
        var options = selector.selectAll("option").data(this.props.option_data).enter().append("option");

        options.text(function(d) {
		    return d[1];
		  })
		  .attr("value", function(d) {
		    return d[0];
		  });

		function select() {
			/*console.log(selector.property('value'));
			for(var i=0; i<legendItems.length; i++) {
				legendItems[i].visible = selector.property('value') == i;
				set_alphas(legendItems[i]);
			}*/


			n = selector.property('value');
			color = d3.scale.linear().domain( limits[n] ) //[Math.min.apply(Math,raw_data[n]), Math.max.apply(Math,raw_data[n])])
			      .interpolate(d3.interpolateHcl)
			      .range([d3.rgb("#007AFF"), d3.rgb('#FFF500')]);
			
			var type = mpld3_elements[0].constructor.name;

            if(type =="mpld3_Line"){
                d3.select(mpld3_elements[0].path[0][0])
                    .style("fill",col);
            } else if((type=="mpld3_PathCollection")||(type=="mpld3_Markers")){
            	for (var i = 0; i<mpld3_elements[0].pathsobj[0].length; i++) {
            		col = isNaN(raw_data[n][i]) ? "gray" : color(raw_data[n][i]);
	                d3.select(mpld3_elements[0].pathsobj[0][i])
	                    .style("stroke",col)
	                    .style("fill",col)
                        .style("stroke-opacity", isNaN(raw_data[n][i]) ? 0.08:1.0)
                        .style("fill-opacity", isNaN(raw_data[n][i]) ? 0.08:1.0);
                
                }
            } else{
                console.log(type + " not yet supported");
            }
		}

		selector.on("change",select);

        select();

        
        // helper function for setting alphas
        function set_alphas(d){
            for(var i=0; i<d.mpld3_elements.length; i++){
                var type = d.mpld3_elements[i].constructor.name;

                if(type =="mpld3_Line"){
                    d3.select(d.mpld3_elements[i].path[0][0])
                        .style("stroke-opacity", (d.visible ? 1.0 : 0.0));
                } else if((type=="mpld3_PathCollection")||
                         (type=="mpld3_Markers")){
                    d3.selectAll(d.mpld3_elements[i].pathsobj[0])
                        .style("stroke-opacity", (d.visible ? 1.0 : 0.0))
                        .style("fill-opacity", (d.visible ? 1.0 : 0.0));
                } else{
                    console.log(type + " not yet supported");
                }
            }
        };
    };