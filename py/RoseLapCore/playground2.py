# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.widgets import CheckButtons

# t = np.arange(0.0, 2.0, 0.01)
# s0 = np.sin(2*np.pi*t)
# s1 = np.sin(4*np.pi*t)
# s2 = np.sin(6*np.pi*t)

# fig, ax = plt.subplots()
# l0, = ax.plot(t, s0, visible=False, lw=2)
# l1, = ax.plot(t, s1, lw=2)
# l2, = ax.plot(t, s2, lw=2)
# plt.subplots_adjust(left=0.2)

# rax = plt.axes([0.05, 0.4, 0.1, 0.15])
# check = CheckButtons(rax, ('2 Hz', '4 Hz', '6 Hz'), (False, True, True))


# def func(label):
#     if label == '2 Hz':
#         l0.set_visible(not l0.get_visible())
#     elif label == '4 Hz':
#         l1.set_visible(not l1.get_visible())
#     elif label == '6 Hz':
#         l2.set_visible(not l2.get_visible())
#     plt.draw()
# check.on_clicked(func)

# plt.show()

# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.widgets import RadioButtons

# t = np.arange(0.0, 2.0, 0.01)
# s0 = np.sin(2*np.pi*t)
# s1 = np.sin(4*np.pi*t)
# s2 = np.sin(8*np.pi*t)

# fig, ax = plt.subplots()
# l, = ax.plot(t, s0, lw=2, color='red')
# plt.subplots_adjust(left=0.3)

# axcolor = 'lightgoldenrodyellow'
# rax = plt.axes([0.05, 0.7, 0.15, 0.15], facecolor=axcolor)
# radio = RadioButtons(rax, ('2 Hz', '4 Hz', '8 Hz'))


# def hzfunc(label):
#     hzdict = {'2 Hz': s0, '4 Hz': s1, '8 Hz': s2}
#     ydata = hzdict[label]
#     l.set_ydata(ydata)
#     plt.draw()
# radio.on_clicked(hzfunc)

# rax = plt.axes([0.05, 0.4, 0.15, 0.15], facecolor=axcolor)
# radio2 = RadioButtons(rax, ('red', 'blue', 'green'))


# def colorfunc(label):
#     l.set_color(label)
#     plt.draw()
# radio2.on_clicked(colorfunc)

# rax = plt.axes([0.05, 0.1, 0.15, 0.15], facecolor=axcolor)
# radio3 = RadioButtons(rax, ('-', '--', '-.', 'steps', ':'))


# def stylefunc(label):
#     l.set_linestyle(label)
#     plt.draw()
# radio3.on_clicked(stylefunc)

# plt.show()

# import matplotlib
# import matplotlib.pyplot as plt
# import random

# # We have three dimensions of data. x and y will be plotted on the x and y axis, while z will 
# # be represented with color.
# # If z is a numpy array, matplotlib refuses to plot this.
# x = list(range(300))
# y = sorted([random.random()*10 for i in range(300)])
# z = list(reversed([i**3 for i in y]))

# # cmap will generate a tuple of RGBA values for a given number in the range 0.0 to 1.0 
# # (also 0 to 255 - not used in this example).
# # To map our z values cleanly to this range, we create a Normalize object.
# cmap = matplotlib.cm.get_cmap('viridis')
# normalize = matplotlib.colors.Normalize(vmin=min(z), vmax=max(z))
# colors = [cmap(normalize(value)) for value in z]

# fig, ax = plt.subplots()
# ax.scatter(x, y, color=colors)

# # Optionally add a colorbar
# cax, _ = matplotlib.colorbar.make_axes(ax)
# cbar = matplotlib.colorbar.ColorbarBase(cax, cmap=cmap, norm=normalize)

# print('wtf')

# plt.show()

engine_reduction= 2.81
gears=[ 2.416, 1.92, 1.562, 1.277, 1.05]
tire_radius= 0.75
vel = 25.0 / 3600 * 5280
final_drive_reduction = 30.0 / 13.0 

gear_ratio = gears[1]
eng_output_rpm = vel / tire_radius * 9.5493 * final_drive_reduction
crank_rpm = eng_output_rpm * engine_reduction * gear_ratio
print('crank rpm = %.3f' % crank_rpm)

gear_ratio = gears[2]
eng_output_rpm = vel / tire_radius * 9.5493 * final_drive_reduction
crank_rpm = eng_output_rpm * engine_reduction * gear_ratio
print('crank rpm = %.3f' % crank_rpm)

gear_ratio = gears[3]
eng_output_rpm = vel / tire_radius * 9.5493 * final_drive_reduction
crank_rpm = eng_output_rpm * engine_reduction * gear_ratio
print('crank rpm = %.3f' % crank_rpm)