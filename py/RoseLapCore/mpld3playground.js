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



    var legend = d3.select("body")
        //.append("svg:g").attr("class","legend")
        //.append("foreignObject").attr("width","100").attr("height","50")
        .insert("div",":first-child").attr("name", "cbar").attr("class","legend");

    lboxes = [];
    color = d3.scale.linear().domain( [0,1] ) //[Math.min.apply(Math,raw_data[n]), Math.max.apply(Math,raw_data[n])])
              .interpolate(d3.interpolateHcl)
              .range([d3.rgb("#007AFF"), d3.rgb('#FFF500')]);
    for(var i=0;i<6;i++) {
        lboxes.push(legend.insert("div",":first-child").attr("class","legend_box").style("background-color",color(i/5.0)).html(i/5.0));
    }

    var selector = d3.select("body")
        //.append("svg:g").attr("class","legend")
        //.append("foreignObject").attr("width","100").attr("height","50")
        .insert("select",":first-child").attr("name", "name-list").attr("class", "name-list");
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

        for(var i=0;i<6;i++) {
            x = (limits[n][1]-limits[n][0])*i/5.0+limits[n][0];
            console.log(x);
            console.log(Math.log10(x));
            plcs = x < 1 ? 5 : Math.ceil(4-Math.log10(Math.abs(x)));
            lboxes[i].style("background-color",color(x)).html(x.toFixed(plcs));
        }
		
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