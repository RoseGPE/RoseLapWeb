var app = echarts.init(document.getElementById('main'));

app.title = 'title';

option = {
    title: {text: chart_title,show:true},
    tooltip: {},
    xAxis: {
        type : 'category',
        data: xData,
        name: chart_title_x,
        nameLocation: 'middle',
        nameGap: 30
    },
    yAxis: {
        type : 'category',
        data: yData,
        right: 10,
        top: 20,
        bottom: 20,
        name: chart_title_y,
        nameLocation: 'middle',
        nameGap: 30
    },
    visualMap: {
        min: Math.min.apply(Math,data[0]['times'].map(a => a[2])),
        max: Math.max.apply(Math,data[0]['times'].map(a => a[2])),
        calculable: true,
        realtime: true,
        inRange: {
            color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
        }
    },
    legend: {
      type: 'scroll',
      orient: 'vertical',
              right: 0,
        top: 20,
        bottom: 20,
      show: true,
      selectedMode: 'single',
      data: data.map(d => d['name'])
    },
    series: data.map(d => ({
        name: d['name'],
        type: 'heatmap',
        data: d['times'],
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

function handle_clk(a){
  var i=0;
  for(;i<data.length;i++) {
    if (data[i]['name'] == a.name)
      break;
  }
  app.setOption({visualMap:{min: Math.min.apply(Math,data[i]['times'].map(a => a[2])), max: Math.max.apply(Math,data[i]['times'].map(a => a[2])) } })
};

app.on('legendselectchanged',handle_clk);

// app.setOption({
//   visualMap: {
//   min: Math.min.apply(Math,data[0]['times'].map(a => a[2])),
//   max: Math.max.apply(Math,data[0]['times'].map(a => a[2]))
// }})
