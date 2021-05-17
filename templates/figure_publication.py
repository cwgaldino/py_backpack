#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create publication quality figure."""

# standard imports
import numpy as np
from pathlib import Path

# matplotlib
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.font_manager import FontProperties
from matplotlib.transforms import Bbox
from matplotlib.ticker import MultipleLocator
from matplotlib import gridspec

# backpack
import sys
sys.path.append('/home/galdino/github/py-backpack')
import backpack.figmanip as figm
import backpack.filemanip as fm
import importlib
importlib.reload(figm)

plt.ion()
# %matplotlib qt5

# %% ====================== Close all other figures ===========================
plt.close('all')

# %% =========================== Negative? ====================================
negative = False
if negative:
    plt.style.use('dark_background')
else:
    plt.style.use('default')

# %% ============================= Fonts ======================================
# Check system available fonts
# from matplotlib.font_manager import findSystemFonts
# font_list = findSystemFonts()
# matching = [s for s in font_list if 'cmr10' in s]
# print(matching)

# Configure fonts
font0 = FontProperties(fname='/home/galdino/github/py-backpack/templates/ttf/cmr10.ttf')
#font0 = FontProperties(fname=str(Path(r'C:\Users\carlo\github\py-backpack\templates\ttf\cmr10.ttf')))
font0.set_size(9)

mpl.rcParams['mathtext.fontset'] = 'cm'  # Change mathtext to CMR ("latex")
mpl.rcParams['svg.fonttype'] = 'none'  # Change text to text, and not paths.
# Note: mathtext output relies on absolute glyph positioning. Therefore, text
# objects that contain mathtext are trick to edit on vector graphics editors
# (inkscape, illustrator, etc...) This was reported as a bug:
# https://github.com/matplotlib/matplotlib/issues/13200

# %% ============================ Figure ======================================
# Figure position on screen
# figm.getWindowPosition()
figm.set_default_window_position((1280, 30))

# Figure size on the paper (in cm)
# PRB, 2 column: Column width 8.6 cm or 3 3/8 in.
# PRB, 1 column: Column width 2x8.6+0.5 = 17.7 cm.
# PRD, max figure lenght ~ 22 cm (~ 3 line caption)
width = 8.6
height = 5

# Use the pyplot interface for creating figures, and then use the object
# methods for the rest
fig = figm.figure(figsize=figm.cm2inch(width, height))
# figm.setWindowPosition()
# figm.getWindowPosition()


# %% Axes: Create axes instance ===============================================
number_of_lines = 1
number_of_columns = 1
shared_x = False
shared_y = False
height_ratios=[1]*number_of_lines
width_ratios=[1]*number_of_columns

hspace = .3
wspace = .3
if shared_x:
    hspace = 0
if shared_y:
    wspace = 0
gs = gridspec.GridSpec(number_of_lines,
                       number_of_columns,
                       height_ratios=height_ratios,
                       width_ratios=width_ratios,
                       hspace=hspace,
                       wspace=wspace)

ax = list()
for i in range(0, number_of_columns*number_of_lines):
    ax.append(fig.add_subplot(gs[i]))
# %% ================================ Plot ====================================
x = np.linspace(0, 10*np.pi, 100)
y = 5*np.sin(x)*np.exp(-0.1*x)
y2 = 10*np.cos(x)*np.exp(-0.1*x)


colors = ['black', 'red', 'blue', 'green', 'magenta']
linestyles = ['-', '--', '-.', ':', '-']
markers =    [None, 'o', None, None, 'x']
color = iter(colors)
linestyle = iter(linestyles)
marker = iter(markers)

marker = None
markevery = 2
markersize = 0
linewidth = 1
line1, = ax[0].plot(x, y,
                 linestyle=next(linestyle),
                 linewidth=linewidth,
                 color=next(color),
                 marker='o',
                 markevery=markevery,
                 markersize=markersize,
                 markerfacecolor='blue',
                 markeredgecolor='blue',
                 markeredgewidth=0.5,
                 label='$y=5\sin(x) e^{-0.1 x}$')

line2, = ax[0].plot(x, y2,
                 linestyle=next(linestyle),
                 linewidth=linewidth,
                 color=next(color),
                 marker='o',
                 markevery=markevery,
                 markersize=markersize,
                 markerfacecolor='blue',
                 markeredgecolor='blue',
                 markeredgewidth=0.5,
                 label='$y=10 \cos(x) e^{-0.1 x}$')

# %% =========================== Text =========================================
if True:
    ax[0].vlines(6, -5, 7, linestyles='dotted', linewidth=1)
    ax[0].hlines(-5, 0, 7, linestyles='dotted', linewidth=1)
    ax[0].text(4.35, 8.48, 'text', fontproperties=font0)

# %% =========================== Axis Labels ==================================
if number_of_lines>1 and shared_x:
    for i in range(number_of_columns):
        ax[-(i+1)].set_xlabel(r'R ($\AA$)', fontproperties=font0, labelpad=None)

if number_of_columns>1 and shared_y:
    for i in range(len(ax)):
        if i%(number_of_columns) == 0 or i==0:
            ax[i].set_ylabel(r'Co - O pairs (%)', fontproperties=font0, labelpad=None)

# %% =========================== Axis ticks ==================================
x_ticks_default = dict(min_value        = None,
                       max_value        = None,
                       n_ticks          = None,
                       ticks_sep        = None,
                       pad              = None,
                       n_minor_ticks    = 3,
                       n_decimal_places = None,
                       fontproperties   = font0,
                      )

y_ticks_default = dict(min_value        = None,
                       max_value        = None,
                       n_ticks          = None,
                       ticks_sep        = None,
                       pad              = None,
                       n_minor_ticks    = 4,
                       n_decimal_places = None,
                       fontproperties   = font0,
                      )

for i in range(len(ax)):
    figm.set_ticks(ax[i], axis='x', **x_ticks_default)
    figm.set_ticks(ax[i], axis='y', **y_ticks_default)

for i in range(len(ax)):
    ax[i].tick_params(which='major', direction='in', top=True, right=True, labelright=False, labeltop=False)
    ax[i].tick_params(which='minor', direction='in', top=True, right=True)

# remove tick labels
if number_of_lines>1 and shared_x:
    for i in range(len(ax)-number_of_columns):
        ax[i].tick_params(which='major', direction='in', top=True, right=True, labelbottom=False)
if number_of_columns>1 and shared_y:
    for i in range(len(ax)):
        if i%(number_of_columns) != 0 and i!=0:
            ax[i].tick_params(which='major', direction='in', top=True, right=True, labelleft=False)

# remove tick at edge
for i in range(len(ax)):
    figmanip.remove_ticks_edge(ax[i])
# %% =============== Axes position on figure ==================================
left   = 0.13
bottom = 0.18
right  = 0.995
top    = 0.995
fig.subplots_adjust(left=left, bottom=bottom, right=right, top=top)
# ax[0].set_position(Bbox([[left, bottom], [right, top]]))

# %% ====================== Legend ============================================
for i in range(len(ax)):
    leg = ax[i].legend(frameon=False, labelspacing=.1, prop=font0)
    # leg = ax[i].legend(frameon=True, labelspacing=.1, prop=font0)


# %% ======================= Inset ============================================
ax2putInset = ax[0]
x_init      = 21
x_final     = 31
y_init      = -5.5
y_final     = -1.75

if True:
    # create inset
    inset = fig.add_axes(figm.axBox2figBox(ax2putInset, [x_init, y_init, x_final, y_final]))
    # inset = fig.add_axes([0.13, 0.81, 0.17, 0.17])
    # inset = fig.add_axes(Bbox([[.25, .38], [.3, .5]]))
    # inset.set_position([.685,.32,.25,.3], which='both')

    for line in ax2putInset.get_lines():
        line2, = inset.plot(line.get_xdata(), line.get_ydata(),
                              ls=line.get_linestyle(),
                              linewidth=line.get_linewidth(),
                              marker = line.get_marker(),
                              markevery=line.get_markevery(),
                              ms=line.get_markersize(),
                              color=line.get_color(),
                              markerfacecolor=line.get_markerfacecolor(),
                              markeredgewidth=line.get_markeredgewidth(),
                              label=line.get_label())

    x_ticks_default = dict(min_value        = 10,
                           max_value        = 15,
                           n_ticks          = 3,
                           ticks_sep        = None,
                           pad              = (0.2, 0),
                           n_minor_ticks    = 1,
                           n_decimal_places = None,
                           fontproperties   = font0,
                          )

    y_ticks_default = dict(min_value        = 0.05,
                           max_value        = 4,
                           n_ticks          = 3,
                           ticks_sep        = None,
                           pad              = 0.1,
                           n_minor_ticks    = 1,
                           n_decimal_places = None,
                           fontproperties   = font0,
                          )

    figm.set_ticks(inset, axis='x', **x_ticks_default)
    figm.set_ticks(inset, axis='y', **y_ticks_default)

    inset.tick_params(which='major', direction='in', top=True, right=True, labelright=False, labeltop=False)
    inset.tick_params(which='minor', direction='in', top=True, right=True)

    figm.remove_ticks_edge(inset)

    # Rectangle
    l = ax2putInset.spines['left'].get_linewidth()
    rect = plt.Rectangle((inset.get_xlim()[0], inset.get_ylim()[0]), inset.get_xlim()[1]-inset.get_xlim()[0], inset.get_ylim()[1]-inset.get_ylim()[0], linewidth=0.6, edgecolor='gray', fc='none', zorder=3)
    ax2putInset.add_patch(rect)

# %% ======================== Save figure =====================================
dirpath = '.'
name_prefix = 'plot'

if True:
    if negative:
        plt.savefig(str(Path(dirpath) / (name_prefix + '_negative.pdf')))
        plt.savefig(str(Path(dirpath) / (name_prefix + '_negative.svg')), transparent=False)
        figm.ungroup(str(Path(dirpath) / (name_prefix + '_negative.svg')))
    else:
        plt.savefig(str(Path(dirpath) / (name_prefix + '_raw.pdf')))
        plt.savefig(str(Path(dirpath) / (name_prefix + '_raw.svg')), transparent=False)
        figm.ungroup(str(Path(dirpath) / (name_prefix + '_raw.svg')))
