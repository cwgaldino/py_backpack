# %% PACKAGES

## Common packages
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.font_manager import FontProperties
from matplotlib.transforms import Bbox
from matplotlib.ticker import MultipleLocator, AutoLocator, ScalarFormatter, FuncFormatter
from pathlib import Path

import sys
sys.path.append(str(Path(r'D:\GitHub')))
from myModules.figs import setFigurePosition, cm2inch

# %% Close all other figures

if 0:
    plt.close('all')

# %% Negative?

negative = 0

if negative:
    plt.style.use('dark_background')
else:
    plt.style.use('default')

# %% Fonts

#Configure fonts
font0 = FontProperties(fname=str(Path(r'C:\Windows\Fonts\cmunrm_0.ttf')))
font0.set_size(9)

# Check system available fonts
#from matplotlib.font_manager import findSystemFonts
#findSystemFonts()

# Change mathtext to Computer Modern Roman ('LaTeX font')
mpl.rcParams['mathtext.fontset'] = 'cm'
# Change text to text, and not paths. This enable to edit text on vector graphics editors
mpl.rcParams['svg.fonttype'] = 'none'
# Note: mathtext output relies on absolute glyph positioning. Therefore, text objects
# that contain mathtext are trick to edit on vector graphics editors (inkscape, illustrator, etc...)
# This was reported as a bug: https://github.com/matplotlib/matplotlib/issues/13200

# %% Figure

# Figure position on screen
xPosition = 100
yPosition = 100

# Figure size on the paper (in cm)
# PRB 2 column: Column width 8.6 cm or 3 3/8 in.
width = 8.6
height = 5

# Use the pyplot interface for creating figures, and then use the object
# methods for the rest
fig = plt.figure(figsize=cm2inch(width, height))
setFigurePosition(xPosition, yPosition)

# %% Axes: Create axes instance
ax = fig.add_subplot(111)

# %% Plot

# Data
#dirpath = Path(r'D:\Co3O2BO3\__Experiments\2019-03_Raman_DEQ_Resistivity')
#filename = r'Co3O2BO3_temperature_15.dat'
#data = res.get_data(dirpath/filename)
x = np.linspace(0, 10*np.pi, 100)
y = np.sin(x)

scale = 1e1

markevery = 2
size = 0
ls = '-'
linewidth = 1
line1, = ax.plot(x, y*scale,
                        ls=ls,
                        linewidth=linewidth,
                        marker = 'o',
                        markevery=markevery,
                        ms=size,
                        color='blue',
                        markerfacecolor='blue',
                        markeredgewidth=0.5,
                        label='example: $y=\sin x$')

# %% Axis

# Axis Label
ax.set_xlabel(r'$T$ (K)', fontproperties=font0, labelpad=None)
ax.set_ylabel(r'$\sigma$ ($10^{' + '{:.0f}'.format(-np.log10(scale)) + '}$ S/m)', fontproperties=font0, labelpad=None)

# ticks properties
ax.tick_params(which='major', direction='in', top=True, left=True, right=True, labelleft=True, labelright=False)
ax.tick_params(which='minor', direction='in', top=True, left=True, right=True)

# Turn off scientific notation
ax.ticklabel_format(axis='both', style='plain')

# major ticks
if 1:
    # ticks values
    xTicks = ax.get_xticks()  # xTicks = np.arange(420, 508, 10)
#    ax.set_xticks(xTicks, minor=False)
    ax.set_xticklabels(['{0:.0f}'.format(i) for i in xTicks], fontproperties=font0, visible=True)

    yTicks = ax.get_yticks()
#    ax.set_yticks(yTicks, minor=False)
    ax.set_yticklabels(['{0:.0f}'.format(i) for i in yTicks], fontproperties=font0, visible=True)

# minor ticks
if 0:
    ax.xaxis.set_minor_locator(MultipleLocator(2))
    ax.yaxis.set_minor_locator(MultipleLocator(.5))
    #ax.xaxis.set_ticks(np.arange(0.5, 11.6, 0.5), minor=True)

# Axis limits
x_min = ax.get_xlim()[0]
x_max = ax.get_xlim()[1]
ax.set_xlim((x_min, x_max), auto=False)

y_min = ax.get_ylim()[0]
y_max = ax.get_ylim()[1]
ax.set_ylim((y_min, y_max), auto=False)

# %% Axes position on figure
ax.set_position(Bbox([[.16,.18], [.98,.98]]))
#[[x0, y0], [x1, y1]]

# %% Legend
l = ax.legend(frameon=0, labelspacing=.1, prop=font0)

# %% Save figure
if 0:
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
