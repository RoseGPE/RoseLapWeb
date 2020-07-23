var app = echarts.init(document.getElementById('main'));

app.title = 'title';
var selected_data = 0;

range_ryb = ['#d73027','#dd472e','#e35936','#e86a3f','#ed7948','#f18851','#f5965b','#f8a466','#fbb170','#fdbe7b','#ffca87','#ffd693','#ffe29f','#ffeeab','#fff9b8','#fafcc2','#f0f6c8','#e5efcd','#dae8d2','#d0dfd6','#c4d6d9','#b9ccdc','#adc2df','#a1b7e1','#94abe2','#879fe3','#7992e3','#6985e3','#5777e2','#4169e1'];
range_gyo = ['#228b22','#399a25','#4ca728','#5eb42c','#6fbf32','#7fc938','#8ed23f','#9cda46','#aae04f','#b7e557','#c3e860','#cfea6a','#d9eb73','#e3ea7d','#ece887','#f2e285','#f5d977','#f8d069','#fbc65c','#fcbd50','#feb345','#ffa93a','#ff9f2f','#ff9526','#ff8a1c','#ff7e13','#ff720a','#ff6503','#ff5600','#ff4500'];

function round (x, plcs=2) {
  if(!isNaN(+x)){
  return Math.round(+x * Math.pow(10,plcs)) / Math.pow(10,plcs);
} else {
  return x;
}
}

option = {
    title: {text: chart_title,show:true},
    tooltip: {formatter:function(params, ticket, callback){
        // console.log(params);
        return params.value[2] + (selected_data%3 == 1 ? ' s' : (selected_data%3 == 2 ? ' pts' : '"J"')) + '</br>'
             + yData[parseInt(params.value[1])] + '</br>'
             + xData[parseInt(params.value[0])];
    }},
    xAxis: {
        type : 'category',
        data: xData,
        name: chart_title_x,
        nameLocation: 'middle',
        nameGap: 30,
        axisLabel: {
            formatter: round
        }
    },
    yAxis: {
        type : 'category',
        data: yData,
        right: 10,
        top: 20,
        bottom: 20,
        name: chart_title_y,
        nameLocation: 'middle',
        nameGap: 60,
        axisLabel: {
            formatter: round
        }
    },
    visualMap: {
        min: Math.min.apply(Math,data[0].map(a => a[2])),
        max: Math.max.apply(Math,data[0].map(a => a[2])),
        calculable: true,
        realtime: true,
        inRange: {
            color: range_ryb
        },
        show:false
    },
    legend: {
      type: 'scroll',
      orient: 'vertical',
              right: 0,
        top: 20,
        bottom: 20,
      show: true,
      selectedMode: 'single',
      data: data_names
    },
    series: [...Array(data_names.length).keys()].map(i => ({
        name: data_names[i],
        type: 'heatmap',
        data: data[i],
        label: {normal:{formatter: function(x) {return Math.round(x.value[2] * 100) / 100}, show:true}},
        itemStyle: {
            emphasis: {
                borderColor: '#333',
                borderWidth: 1
            }
        },
        progressive: 1000,
        animation: false
    }))
};

app.setOption(option);

function handle_sel(a){
  var i=0;
  for(;i<data.length;i++) {
    if (data_names[i] == a.name)
      break;
  }
  app.setOption({visualMap:{
    min:Math.min.apply(Math,data[i].map(a => a[2])),
    max: Math.max.apply(Math,data[i].map(a => a[2])),
        inRange: {
            color: (i%2 ? range_gyo : range_ryb)
        }
  } })
  selected_data = i;
};

function handle_clk(a){
  //console.log(a);
  //alert('You clicked on datapoint ' + a.dataIndex + ' AKA ' + a.data[0] + ', ' + a.data[1]);
  var win = window.open(a.seriesName.split(" ")[0].split(".")[0] + '/' + a.value[0] + '-' + a.value[1] + '.html', '_blank');
  win.focus();
};

app.on('legendselectchanged',handle_sel);

app.on('click',handle_clk);