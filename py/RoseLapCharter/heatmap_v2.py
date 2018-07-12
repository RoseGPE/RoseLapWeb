import json
import pointsim
import copy
import translation
import detail
from charting_tools import *

def make_plot(result, fn_prefix, overall_title="Chart Overall Title"):
  data = []
  data_names = []
  points_total = None
  td = result['track_data']
  for trk in td:
    compute_pts = []
    for i in range(len(trk['times'])):
      pts = pointsim.compute_points(trk['scoring'], trk['min_time'], trk['min_co2'], trk['times'][i][2], trk['co2s'][i])
      # print(trk['scoring'],trk['times'][i][2],pts)
      if not (points_total is None):
        points_total[i][2] = points_total[i][2] + pts
      compute_pts.append([trk['times'][i][0], trk['times'][i][1], pts])
    if points_total is None:
      points_total = copy.deepcopy(compute_pts)
    data.append(compute_pts)
    data_names.append(trk['name'] + ' Points')
    data.append(trk['times'])
    data_names.append(trk['name'] + ' Times')
  data.append(points_total)
  data_names.append("Total Points")

  xlabel = ''
  xvals = []
  if 'label' in result['axiscontents'][0].keys():
    xvals = result['axiscontents'][0]['label'];
  else:
    xlabel = ', '.join(["%s (%s)" % (translation.names[k],translation.units[k]) for k in result['axiscontents'][0].keys()]);
    xvals = result['axiscontents'][0].values();
    xvals = [[v[i] for v in xvals] for i in range(len(xvals[0]))]
  
  ylabel = ''
  yvals = []
  if 'label' in result['axiscontents'][1].keys():
    yvals = result['axiscontents'][1]['label'];
  else:
    ylabel = ', '.join(["%s (%s)" % (translation.names[k],translation.units[k]) for k in result['axiscontents'][1].keys()]);
    yvals = result['axiscontents'][1].values();
    yvals = [[v[i] for v in yvals] for i in range(len(yvals[0]))]


  html = """
    <head>
    <script src="../../py/RoseLapCharter/echarts.min.js"></script>
    <meta charset="utf-8" />
    </head>

    <body>

      <div id="main" style="width: 100%%; height:100%%;"></div>
      <script type="text/javascript">
        var translate_names = %s;
        var translate_units = %s;
        var data = %s;
        var data_names = %s;
        var chart_title = "2D Study: " + %s;
        var chart_title_x = %s;
        var chart_title_y = %s;
        var xData = %s;
        var yData = %s;
      </script>
      <script src="../../py/RoseLapCharter/2dstudy_view.js"></script>

    </body>
  """ % tuple(json.dumps(s) for s in [translation.names,translation.units,data,data_names,overall_title,xlabel,ylabel,xvals,yvals])

  for track in td:
    outputs = track['outputs']
    filename = track['name'].split(".")[0]

    if len(outputs) > 0:
        disp = makeGraphFolder(fn_prefix + "\\" + filename) + "\\"

        for output in outputs:
            x, y, outdata = output
            iname = disp + str(x) + "-" + str(y)
            with open(iname + ".html", "w") as plot:
                plot.write(detail.make_sub_plot(outdata))

  return html


if __name__ == "__main__":
  import webbrowser, os
  filename = 'out.html'
  fakedata = {'axiscontents': 
              [{'mass': [500.0, 520.0, 540.0, 570.0, 600.0, 650.0], 'label':['A','B','C','D','E','F']},
              {'drag_35mph': [10, 15, 20, 25, 30, 35, 40, 45, 50], 'downforce_35mph': [0, 10, 20, 30, 40, 50, 60, 70, 80]}],
             'model': 'point_mass',
             'axes': 2,
             'track_data': 
              [{'ss': 0.0,
                'outputs': [],
                'name': 'acceleration1.dxf',
                'scoring': 'acceleration',
                'min_time': 3.9,
                'min_co2': 3.5,
                'co2s': [0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06],
                'times': [(0, 0, 4.3984311673416645), (0, 1, 4.417491653981809), (0, 2, 4.43893369136528), (0, 3, 4.459502240546215), (0, 4, 4.4805883700952425), (0, 5, 4.498773608459982), (0, 6, 4.519566679429729), (0, 7, 4.540011401480001), (0, 8, 4.558941284988691), (1, 0, 4.453563557185642), (1, 1, 4.473720746498945), (1, 2, 4.492748281066066), (1, 3, 4.513109089667391), (1, 4, 4.532685552912901), (1, 5, 4.55252545708322), (1, 6, 4.571039840414426), (1, 7, 4.590631191425516), (1, 8, 4.609417633411254), (2, 0, 4.5078064048207), (2, 1, 4.527345972013742), (2, 2, 4.545773168759282), (2, 3, 4.565700321573944), (2, 4, 4.584436500654918), (2, 5, 4.604096057085603), (2, 6, 4.621637326528386), (2, 7, 4.640841765215703), (2, 8, 4.659393696123258), (3, 0, 4.587323902406092), (3, 1, 4.605876354071692), (3, 2, 4.622771300633113), (3, 3, 4.642101847262711), (3, 4, 4.660720009651942), (3, 5, 4.679404859125047), (3, 6, 4.69592929821352), (3, 7, 4.714430379019609), (3, 8, 4.7326736927743305), (4, 0, 4.664275949161986), (4, 1, 4.681964398406456), (4, 2, 4.700509749273947), (4, 3, 4.717214364033443), (4, 4, 4.734572182323529), (4, 5, 4.7525941564836485), (4, 6, 4.768905356915772), (4, 7, 4.786033171195522), (4, 8, 4.803658538179397), (5, 0, 4.7881898020453475), (5, 1, 4.805203258686899), (5, 2, 4.822229008633095), (5, 3, 4.839371384208359), (5, 4, 4.855174638507283), (5, 5, 4.871462098642664), (5, 6, 4.888166112137376), (5, 7, 4.902946659656104), (5, 8, 4.919251970754819)]},
              {'ss': 0.0, 
                'outputs': [],
                'name': 'skidpad_loop.dxf',
                'scoring': 'skidpad',
                'min_time': 4.5,
                'min_co2': 3.4,
                'co2s': [0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06],
                'times': [(0, 0, 4.851640580252629), (0, 1, 4.8262287248005045), (0, 2, 4.801338909535513), (0, 3, 4.775359176700175), (0, 4, 4.750408501438183), (0, 5, 4.725440834591015), (0, 6, 4.700458764049374), (0, 7, 4.6743820888329175), (0, 8, 4.649379652798423), (1, 0, 4.8727752578665395), (1, 1, 4.849092030530443), (1, 2, 4.825388308224503), (1, 3, 4.801667448189768), (1, 4, 4.776900201878468), (1, 5, 4.753149407339543), (1, 6, 4.729394357220413), (1, 7, 4.7056409243913), (1, 8, 4.680837561908651), (2, 0, 4.894478216436311), (2, 1, 4.871885476028336), (2, 2, 4.849281827199479), (2, 3, 4.826670688058198), (2, 4, 4.803057357739787), (2, 5, 4.7804341614015735), (2, 6, 4.75781509582927), (2, 7, 4.735205916427676), (2, 8, 4.711589855159773), (3, 0, 4.934275528685309), (3, 1, 4.905983460766859), (3, 2, 4.88488613598941), (3, 3, 4.863792408715269), (3, 4, 4.841755550518452), (3, 5, 4.820670862328589), (3, 6, 4.799601310691153), (3, 7, 4.7785524767977865), (3, 8, 4.756558203455529), (4, 0, 4.962622091673156), (4, 1, 4.93997287820576), (4, 2, 4.920232046940206), (4, 3, 4.900503940209748), (4, 4, 4.880792786775974), (4, 5, 4.860187038245252), (4, 6, 4.840511931953497), (4, 7, 4.820865709228878), (4, 8, 4.800326025787232), (5, 0, 5.016672129858258), (5, 1, 4.9972364976861545), (5, 2, 4.978657120703051), (5, 3, 4.960930054480518), (5, 4, 4.943231401098953), (5, 5, 4.924715070429228), (5, 6, 4.907076557851308), (5, 7, 4.889478479603892), (5, 8, 4.871061595032214)]}],
             'vehicle': 
              {'co2_factor': 2.31,
              'drag_35mph': 50,
              'g': 32.2,
              'final_drive_reduction': 2.7692,
              'downforce_35mph': 80,
              'engine_reduction': 2.81,
              'cg_height': 0.8,
              'engine_torque': [24.3, 26.2, 27.4, 26.5, 25.5, 23.8, 23.9],
              'cp_height': 0.9,
              'weight_bias': 0.55,
              'mu': 2.0,
              'engine_rpms': [3500.0, 4500.0, 5500.0, 6500.0, 7500.0, 8500.0, 9500.0],
              'shift_time': 0.2,
              'mass': 20.186335403726705,
              'gears': [2.416, 1.92, 1.562, 1.277, 1.05],
              'e_factor': 2271700.0,
              'tire_radius': 0.75,
              'brake_bias': 0.5,
              'cp_bias': 0.7,
              'wheelbase_length': 5.1666667,
              'perfect_brake_bias': 0.0}}
  with open(filename,'w') as f:
    f.write(make_plot(fakedata,None))
  webbrowser.open('file://' + os.path.realpath(filename))