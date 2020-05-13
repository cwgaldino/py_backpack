#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create publication quality figure."""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.font_manager import FontProperties
from matplotlib.transforms import Bbox
from matplotlib.ticker import MultipleLocator
# from matplotlib.ticker import AutoLocator, ScalarFormatter, FuncFormatter
from pathlib import Path

from matplotlib import gridspec

from manipUtils.figmanip import setFigurePosition, getFigurePosition, cm2inch

%matplotlib qt5
plt.ion()

# %% ================== Close all other figures ===============================
# plt.close('all')

# %% ======================== Negative ========================================
negative = False
if negative:
    plt.style.use('dark_background')
else:
    plt.style.use('default')

# %% ============================ Fonts =======================================
# Check system available fonts
# from matplotlib.font_manager import findSystemFonts
# font_list = findSystemFonts()
# matching = [s for s in font_list if 'cmr10' in s]
# print(matching)

# Configure fonts
# font0 = FontProperties(fname='/usr/share/fonts/truetype/lyx/cmr10.ttf')
font0 = FontProperties(fname=str(Path(r'C:\Users\carlo\github\manipUtils\templates\ttf\cmr10.ttf')))
font0.set_size(9)

# Change mathtext to Computer Modern Roman ('LaTeX font')
mpl.rcParams['mathtext.fontset'] = 'cm'
# Change text to text, and not paths. This enable to edit text on vector graphics editors
mpl.rcParams['svg.fonttype'] = 'none'
# Note: mathtext output relies on absolute glyph positioning. Therefore, text
# objects that contain mathtext are trick to edit in vector graphics editors
# (inkscape, illustrator, etc...) This was reported as a bug:
# https://github.com/matplotlib/matplotlib/issues/13200

# %% ============================ Figure ======================================
# Figure position on screen
# getFigurePosition()
xPosition = 100
yPosition = 100

# Figure size on the paper (in cm)
# PRB 2 column: Column width 8.6 cm or 3 3/8 in.
width = 8.6
height = 15

# Use the pyplot interface for creating figures, and then use the object
# methods for the rest
fig = plt.figure(figsize=cm2inch(width, height))
setFigurePosition(xPosition, yPosition)

# %% ================================ Axes ====================================
number_of_lines = 4
number_of_columns = 1
height_ratios=[1, 1, 1, 1]
width_ratios=[1]
gs = gridspec.GridSpec(number_of_lines, number_of_columns, height_ratios=height_ratios, width_ratios=width_ratios)
fig.subplots_adjust(hspace=0, wspace=.3) #Set distance between subplots

ax = list()
ax.append(fig.add_subplot(gs[0]))
for i in range(1, number_of_lines):
    ax.append(fig.add_subplot(gs[i], sharex=ax[0]))

# %% =================================== Plot =================================
# Data
x = np.linspace(0, 10*np.pi, 100)
y = np.sin(x)

scale = 1e1

colors = ['black', 'red', 'blue', 'green', 'magenta']
linestyles = ['-', '--', '-.', ':', '-']
markers =    [None, 'o', None, None, 'x']
color = iter(colors)
linestyle = iter(linestyles)
marker = iter(markers)

markevery = 2
markersize = 3
linewidth = 1

line1, = ax[0].plot(x, y*scale,
                        ls=next(linestyle),
                        linewidth=linewidth,
                        marker=next(marker),
                        markevery=markevery,
                        ms=markersize,
                        color=next(color),
                        markerfacecolor='blue',
                        markeredgewidth=0.5,
                        label='$y=\sin(x)$')

line2, = ax[1].plot(x, y**2,
                        ls=next(linestyle),
                        linewidth=linewidth,
                        marker=next(marker),
                        markevery=markevery,
                        ms=markersize,
                        color=next(color),
                        markerfacecolor='blue',
                        markeredgewidth=0.5,
                        label='$y=\sin(x)$')

line1, = ax[2].plot(x, y*scale,
                        ls=next(linestyle),
                        linewidth=linewidth,
                        marker=next(marker),
                        markevery=markevery,
                        ms=markersize,
                        color=next(color),
                        markerfacecolor='blue',
                        markeredgewidth=0.5,
                        label='$y=\sin(x)$')

line1, = ax[3].plot(x, y*scale,
                        ls=next(linestyle),
                        linewidth=linewidth,
                        marker=next(marker),
                        markevery=markevery,
                        ms=markersize,
                        color=next(color),
                        markerfacecolor='blue',
                        markeredgewidth=0.5,
                        label='$y=\sin(x)$')

# %% ================================== Axis ==================================
# Axis Label
ax[-1].set_xlabel(r'$T$ (K)', fontproperties=font0, labelpad=None)
for a in ax:
    a.set_ylabel(r'$\sigma$ ($10^{' + '{:.0f}'.format(-np.log10(scale)) + '}$ S/m)', fontproperties=font0, labelpad=None)

# Turn off scientific notation
for a in ax:
    a.ticklabel_format(axis='both', style='plain')

# major ticks
if True:
    for a in ax:
        # ticks values
        xTicks = a.get_xticks()  # xTicks = np.arange(420, 508, 10)
    #    a.set_xticks(xTicks, minor=False)
        a.set_xticklabels(['{0:.0f}'.format(i) for i in xTicks], fontproperties=font0, visible=False)

        yTicks = a.get_yticks()
    #    a.set_yticks(yTicks, minor=False)
        a.set_yticklabels(['{0:.0f}'.format(i) for i in yTicks], fontproperties=font0, visible=True)

    ax[-1].set_xticklabels(['{0:.0f}'.format(i) for i in xTicks], fontproperties=font0, visible=True)

# minor ticks
if True:
    for a in ax:
        a.xaxis.set_minor_locator(MultipleLocator(2))
        a.yaxis.set_minor_locator(MultipleLocator(2))
    #    a.xaxis.set_ticks(np.arange(0.5, 11.6, 0.5), minor=True)

# ticks properties
for a in ax:
    a.tick_params(which='major', direction='in', top=True, left=True, right=True, labeltop=False, labelleft=True, labelright=False)
    a.tick_params(which='minor', direction='in', top=True, left=True, right=True)

# Axis limits
for a in ax:
    x_min = a.get_xlim()[0]
    x_max = a.get_xlim()[1]
    a.set_xlim((x_min, x_max), auto=False)

    y_min = a.get_ylim()[0]
    y_max = a.get_ylim()[1]
    a.set_ylim((y_min, y_max), auto=False)

# %% ======================== Axes position on figure =========================
fig.subplots_adjust(left=0.13, bottom=0.06, right=0.98, top=0.98)

# %% ========================== Legend ========================================
for a in ax:
    a.legend(frameon=0, labelspacing=.1, prop=font0)

# %% ========================= Save figure ====================================
if False:
    dirpath = Path(r'C:\Users\Carlos\Desktop')

    name_prefix = 'plot'

    if negative:
        # pdf is for fast visualization (svg has to open inkscape)
        plt.savefig(str(dirpath / (name_prefix + '_negative.pdf')))
        plt.savefig(str(dirpath / (name_prefix + '_negative.svg')), transparent=False)
    else:
        # pdf is for fast visualization (svg has to open inkscape)
        plt.savefig(str(dirpath / (name_prefix + '_raw.pdf')))
        plt.savefig(str(dirpath / (name_prefix + '_raw.svg')), transparent=True)

    del dirpath, name_prefix, negative
