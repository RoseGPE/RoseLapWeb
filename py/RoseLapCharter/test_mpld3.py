# import matplotlib.pyplot as plt, mpld3
# from mpld3 import plugins
# fig, ax = plt.subplots(1,1)
# xx = yy = range(10)
# scat = ax.scatter(xx, range(10))
# targets = map(lambda (x, y): "<marquee>It works!<br><h1>{}, {}</h1></marquee>".format(x, y),
#               zip(xx, yy))
# labels = map(lambda (x, y): "{}, {}".format(x,y), zip(xx, yy))
# from mpld3.plugins import PointClickableHTMLTooltip
# plugins.connect(fig, PointClickableHTMLTooltip(scat, labels=labels, targets=targets))

# mpld3.save_html(fig, "mpld3-newtab.html")

import matplotlib.pyplot as plt, mpld3
import numpy as np
from mpld3 import fig_to_html, plugins
N_paths = 5
N_steps = 100
x = np.linspace(0, 10, 100)
y = 0.1 * (np.random.random((N_paths, N_steps)) - 0.5)
y = y.cumsum(1)
fig, ax = plt.subplots()
labels = ["a", "b", "c", "d", "e"]
line_collections = ax.plot(x, y.T, lw=4, alpha=0.6)
interactive_legend = plugins.InteractiveLegendPlugin(line_collections, labels, alpha_unsel=0.2, alpha_over=1.5, start_visible=True)
plugins.connect(fig, interactive_legend)

mpld3.save_html(fig, "mpld3-filter.html")