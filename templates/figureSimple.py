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

from manipUtils.figmanip import setFigurePosition, getFigurePosition, cm2inch
import manipUtils.figmanip as figmanip

%matplotlib qt5
plt.ion()

# %% ====================== Close all other figures ===========================
plt.close('all')

# %% =========================== Negative? ====================================
negative = 0
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
# font0 = FontProperties(fname='/usr/share/fonts/truetype/lyx/cmr10.ttf')
font0 = FontProperties(fname=str(Path(r'C:\Users\carlo\github\manipUtils\templates\ttf\cmr10.ttf')))
font0.set_size(9)

mpl.rcParams['mathtext.fontset'] = 'cm'  # Change mathtext to CMR ("latex")
mpl.rcParams['svg.fonttype'] = 'none'  # Change text to text, and not paths.
# Note: mathtext output relies on absolute glyph positioning. Therefore, text
# objects that contain mathtext are trick to edit on vector graphics editors
# (inkscape, illustrator, etc...) This was reported as a bug:
# https://github.com/matplotlib/matplotlib/issues/13200

# %% ============================ Figure ======================================
# Figure position on screen
# getFigurePosition()
xPosition = 1000
yPosition = 100

# Figure size on the paper (in cm)
# PRB, 2 column: Column width 8.6 cm or 3 3/8 in.
width = 8.6
height = 5

# Use the pyplot interface for creating figures, and then use the object
# methods for the rest
fig = plt.figure(figsize=cm2inch(width, height))
setFigurePosition(xPosition, yPosition)

# %% Axes: Create axes instance
ax = fig.add_subplot(111)

# %% ================================ Plot ====================================
x = np.linspace(0, 10*np.pi, 100)
y = np.sin(x)
y2 = np.cos(x)

scale = 1e1

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
line1, = ax.plot(x, y*scale,
                 linestyle=next(linestyle),
                 linewidth=linewidth,
                 color=next(color),
                 marker='o',
                 markevery=markevery,
                 markersize=markersize,
                 markerfacecolor='blue',
                 markeredgecolor='blue',
                 markeredgewidth=0.5,
                 label='$y=\sin(x)$')

line2, = ax.plot(x, y2*scale,
                 linestyle=next(linestyle),
                 linewidth=linewidth,
                 color=next(color),
                 marker='o',
                 markevery=markevery,
                 markersize=markersize,
                 markerfacecolor='blue',
                 markeredgecolor='blue',
                 markeredgewidth=0.5,
                 label='$y=\cos(x)$')

# %% =========================== Text =========================================
if True:
    plt.vlines(6, -10, 7, linestyles='dotted', linewidth=1)
    plt.hlines(-5, 0, 7, linestyles='dotted', linewidth=1)
    plt.text(13, -6, 'text', fontproperties=font0)

# %% =========================== Axis =========================================
# Axis Labels
ax.set_xlabel(r'$T$ (K)', fontproperties=font0, labelpad=None)
pot = '{:.0f}'.format(-np.log10(scale))
ax.set_ylabel(r'$\sigma$ ($10^{' + pot + '}$ S/m)',
              fontproperties=font0, labelpad=None)

# Turn off scientific notation
ax.ticklabel_format(axis='both', style='plain')

# major ticks
if True:
    # ticks values
    xTicks = ax.get_xticks()  # xTicks = np.arange(420, 508, 10)
    # ax.set_xticks(xTicks, minor=False)
    ax.set_xticklabels(['{0:.0f}'.format(i) for i in xTicks],
                       fontproperties=font0, visible=True)

    yTicks = ax.get_yticks()
    # ax.set_yticks(yTicks, minor=False)
    ax.set_yticklabels(['{0:.0f}'.format(i) for i in yTicks],
                       fontproperties=font0, visible=True)

# minor ticks
if True:
    ax.xaxis.set_minor_locator(MultipleLocator(2))
    ax.yaxis.set_minor_locator(MultipleLocator(.5))
#    ax.xaxis.set_ticks(np.arange(0.5, 11.6, 0.5), minor=True)

# ticks properties
ax.tick_params(which='major', direction='in', top=True, left=True, right=True,
               labelleft=True, labelright=False, labeltop=False)
ax.tick_params(which='minor', direction='in', top=True, left=True, right=True)

# Axis limits
x_min = ax.get_xlim()[0]
x_max = ax.get_xlim()[1]
ax.set_xlim((x_min, x_max), auto=False)

y_min = ax.get_ylim()[0]
y_max = ax.get_ylim()[1]
ax.set_ylim((y_min, y_max), auto=False)

# %% =============== Axes position on figure ==================================
ax.set_position(Bbox([[.16, .18], [.98, .98]]))
# [[x0, y0], [x1, y1]]

# %% ====================== Legend ============================================
if True:
    leg = ax.legend(frameon=0, labelspacing=.1, prop=font0)

# %% ======================= Inset ============================================
if True:
    ax2putInset = ax

    # position
    x_init = 25
    x_final = 31
    y_init = -8
    y_final = -5

    # create inset
    ax_inset = fig.add_axes(figmanip.axBox2figBox(ax2putInset, [x_init, y_init, x_final, y_final]))
    # ax_inset = fig.add_axes([0.13, 0.81, 0.17, 0.17])
    # ax_inset = fig.add_axes(Bbox([[.25, .38], [.3, .5]]))
    # ax_inset.set_position([.685,.32,.25,.3], which='both')

    line2, = ax_inset.plot(x, y,
                          ls='-',
                          linewidth=1,
                          marker = 'o',
                          markevery=2,
                          ms=2,
                          color='blue',
                          markerfacecolor='blue',
                          markeredgewidth=0.5,
                          label='example: $y=\sin x$')

    # Turn off scientific notation
    ax_inset.ticklabel_format(axis='both', style='plain')

    # major ticks
    if False:
        # ticks values
        xTicks = ax_inset.get_xticks()  # xTicks = np.arange(420, 508, 10)
        # ax_inset.set_xticks(xTicks, minor=False)
        ax_inset.set_xticklabels(['{0:.0f}'.format(i) for i in xTicks],
                           fontproperties=font0, visible=True)

        yTicks = ax_inset.get_yticks()
        # ax_inset.set_yticks(yTicks, minor=False)
        ax_inset.set_yticklabels(['{0:.0f}'.format(i) for i in yTicks],
                           fontproperties=font0, visible=True)

    # minor ticks
    if False:
        ax_inset.xaxis.set_minor_locator(MultipleLocator(2))
        ax_inset.yaxis.set_minor_locator(MultipleLocator(.5))
    #    ax_inset.xaxis.set_ticks(np.arange(0.5, 11.6, 0.5), minor=True)

    # ticks properties
    ax_inset.tick_params(which='major', direction='in', top=True, left=True, right=True,
                   labelleft=True, labelright=False, labeltop=False)
    ax_inset.tick_params(which='minor', direction='in', top=True, left=True, right=True)

    # Axis limits
    x_min = 0
    x_max = 10
    ax_inset.set_xlim((x_min, x_max), auto=False)

    y_min = -5
    y_max = 5
    ax_inset.set_ylim((y_min, y_max), auto=False)

# %% ======================== Save figure =====================================
if False:
    dirpath = FIGURE

    name_prefix = 'plot'

    if negative:
        # pdf is for fast visualization (svg has to open inkscape)
        plt.savefig(str(dirpath / (name_prefix + '_negative.pdf')))
        plt.savefig(str(dirpath / (name_prefix + '_negative.svg')),
                    transparent=False)
    else:
        # pdf is for fast visualization (svg has to open inkscape)
        plt.savefig(str(dirpath / (name_prefix + '_raw.pdf')))
        plt.savefig(str(dirpath / (name_prefix + '_raw.svg')),
                    transparent=True)

    del dirpath, name_prefix, negative
