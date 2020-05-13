#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Set of functions that eases matplotlib figure manipulation.

Author: Carlos Galdino
Email: galdino@ifi.unicamp.br
"""

from matplotlib.pyplot import get_current_fig_manager
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
from pathlib import Path


def setFigurePosition(*args):
    """Change position of a maptplotlib figure on screen.

    Tipically, (0, 0) is the top left corner.

    Args:
        *args: A tuple with x and y positions or two separate xy values (in px).
    """
    if len(args) > 1:
        xPosition = args[0]
        yPosition = args[1]
    elif len(args) == 1 and len(args[0]) == 2:
        xPosition = args[0][0]
        yPosition = args[0][1]
    else:
        print('Warning! Wrong input')
        return

    figManager = get_current_fig_manager()

    try:  # tested under tKinter backend
        figurePosition = '+' + str(int(xPosition)) + '+' + str(int(yPosition))
        figManager.window.wm_geometry(figurePosition)

    except AttributeError:
        try:  # tested under qt4 and qt5 backends
            figGeometry = figManager.window.geometry()
            figManager.window.setGeometry(xPosition, yPosition, figGeometry.width(), figGeometry.height())
        except AttributeError:
            print('setFigurePosition(): Backend not suported.\n')


def getFigurePosition():
    """Get the position of a matplotlib position on the screen.

    Tipically, (0, 0) is the top left corner.

    Returns:
        Tuple with the x and y position.
    """
    figManager = get_current_fig_manager()

    try:  # tested under tKinter backend
        return (int(figManager.window.geometry().split('x')[0]), int(figManager.window.geometry().split('x')[1].split('+')[0]))

    except AttributeError:  # tested under qt4 and qt5 backends
        try:
            return (figManager.window.geometry().x(), figManager.window.geometry().y())
        except AttributeError:
            print('Backend not suported.\n')
            return (0, 0)


def cm2inch(*tupl):
    """Convert values from cm to inches.

    Args:
        *Args: A tuple with values to convert

    Returns:
        A tuple with values converted
    """
    inch = 2.54
    if isinstance(tupl[0], tuple):
        return tuple(i/inch for i in tupl[0])
    else:
        return tuple(i/inch for i in tupl)


def plot_ruler(orientation, height=4, width=4):
    """Open matplotlib figure which can be used as a ruler.

    Ruler goes from 0 to 1.

    Args:
        orientation (string): 'v' for vertical ruler and 'h' for horizontal ruler.
        height (float): height in cm. If orientation is 'v', width is ignored.
        width (float): width in cm. If orientation is 'h', height is ignored.
    """
    aux = plt.figure()
    aux_ax = plt.subplot(111)
    temp = np.linspace(0, 1, 11)
    if orientation == 'v':
        aux.set_size_inches(1, cm2inch(height)[0])
        aux.subplots_adjust(left=0, bottom=0, right=.001, top=1)
        aux_ax.set_yticks(temp, minor=False)  # Major
        aux_ax.yaxis.set_minor_locator(MultipleLocator(temp[1]/5))  # Minor
    else:
        aux.set_size_inches(cm2inch(width)[0], .5)
        aux.subplots_adjust(left=0, bottom=0, right=1, top=.01)
        aux_ax.set_xticks(temp, minor=False)  # Major
        aux_ax.xaxis.set_minor_locator(MultipleLocator(temp[1]/5))  # Minor
    aux_ax.tick_params(which='major',direction='out',top=True,left=True,right=True, labeltop=True, labelright=True)
    aux_ax.tick_params(which='minor',direction='out',top=True,left=True,right=True)


def saveFigsInPDF(dirname, filename, figs='all'):
    """Save multiple matplotlib figures in pdf.

    Args:
        dirname (string or pathlib.Path): directory path
        filename (string): filename
        figs (list, optional): list with the figure numbers to save. Use 'all' to save all.
    """
    # check extension
    if filename.split('.')[-1] != 'pdf':
        filename += '.pdf'

    if figs is 'all':
        figs = [plt.figure(n) for n in plt.get_fignums()]
    if len(figs) > 1:
        pp = PdfPages(str(Path(dirname)/filename))
        for fig in figs:
            fig.savefig(pp, format='pdf')
        pp.close()
    else:
        plt.savefig(str(Path(dirname)/filename), format='pdf')


def axBox2figBox(ax, points):
    """Transform bbox like ax position values to percentage fig position.

    Args:
        points (list): [x_init, y_init, x_final, y_final]

    Retuns:
        list with fig positions.
    """
    [x_init, y_init, x_final, y_final] = points

    x_init = axPos2figPos(ax, x_init, direction='x')
    y_init = axPos2figPos(ax, y_init, direction='y')
    delta_x = axPos2figPos(ax, x_final, direction='x') - x_init
    delta_y = axPos2figPos(ax, y_final, direction='y') - y_init

    return [x_init, y_init, delta_x, delta_y]


def axPos2figPos(ax, x, direction='x'):
    """Transform ax position values to percentage fig position.

    Args:
        x (float): x value
        direction (string): x or y.

    Retuns:
        fig positions from 0 to 1.
    """
    if direction == 'x':
        point1 = (ax.get_xlim()[0], ax.get_position().xmin)
        point2 = (ax.get_xlim()[1], ax.get_position().xmax)
    else:
        point1 = (ax.get_ylim()[0], ax.get_position().ymin)
        point2 = (ax.get_ylim()[1], ax.get_position().ymax)
    delta = (point2[1]-point1[1])/(point2[0]-point1[0])
    x0 = point2[1] - (delta*point2[0])

    return x0 + delta*x
