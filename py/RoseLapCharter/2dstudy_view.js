var app = echarts.init(document.getElementById('main'));

app.title = 'title';

range_ryb = ['#d73027','#dd472e','#e35936','#e86a3f','#ed7948','#f18851','#f5965b','#f8a466','#fbb170','#fdbe7b','#ffca87','#ffd693','#ffe29f','#ffeeab','#fff9b8','#fafcc2','#f0f6c8','#e5efcd','#dae8d2','#d0dfd6','#c4d6d9','#b9ccdc','#adc2df','#a1b7e1','#94abe2','#879fe3','#7992e3','#6985e3','#5777e2','#4169e1'];
range_gyo = ['#228b22','#399a24','#4da726','#60b326','#71be27','#82c827','#92d026','#a2d725','#b0dc23','#bfe021','#cce21e','#d9e21a','#e5e115','#f0de0e','#fada05','#ffd400','#ffcd00','#ffc500','#ffbe00','#ffb600','#ffad00','#ffa500','#ff9c00','#ff9200','#ff8800','#ff7d00','#ff7100','#ff6500','#ff5600','#ff4500'];

option = {
    title: {text: chart_title,show:true},
    tooltip: {},
    xAxis: {
        type : 'category',
        data: xData,
        name: chart_title_x,
        nameLocation: 'middle',
        nameGap: 30,
        axisLabel: {
            formatter: function(x) {return x}
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
            formatter: function(x) {return x}
        }
    },
    visualMap: {
        min: Math.min.apply(Math,data[0].map(a => a[2])),
        max: Math.max.apply(Math,data[0].map(a => a[2])),
        calculable: true,
        realtime: true,
        inRange: {
            color: range_ryb
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
      data: data_names
    },
    series: [...Array(data_names.length).keys()].map(i => ({
        name: data_names[i],
        type: 'heatmap',
        data: data[i],
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
};

app.on('legendselectchanged',handle_clk);

// app.setOption({
//   visualMap: {
//   min: Math.min.apply(Math,data[0]['times'].map(a => a[2])),
//   max: Math.max.apply(Math,data[0]['times'].map(a => a[2]))
// }})
