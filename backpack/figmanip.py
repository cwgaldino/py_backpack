#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Set of functions that eases matplotlib figure manipulation.

Author: Carlos Galdino
Email: galdino@ifi.unicamp.br
"""

# standard libraries
import numpy as np
from pathlib import Path
import copy
import warnings

# matplotlib libraries
from matplotlib.pyplot import get_current_fig_manager
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# backpack
from .arraymanip import index



def setFigurePosition(*args):
    """Change position of a maptplotlib figure on screen.

    Tipically, (0, 0) is the top left corner.

    Args:
        *args: A tuple like (x, y) or two separate x, y values (in px).
    """
    if len(args) > 1:
        x = int(args[0])
        y = int(args[1])
    elif len(args) == 1 and len(args[0]) == 2:
        x = int(args[0][0])
        y = int(args[0][1])
    else:
        warnings.warn('Wrong input')
        return

    figManager = get_current_fig_manager()
    width,height = getFigureSize()

    try:  # tested on tKinter backend
        figureGeometry = str(width) + 'x' + str(height) + '+' + str(x) + '+' + str(y)
        figManager.window.wm_geometry(figureGeometry)

    except AttributeError:
        try:  # tested on qt4 and qt5 backends
            figManager.window.setGeometry(int(x), int(y), width, height)
        except AttributeError:
            warnings.warn('Backend not suported.')


def setFigureSize(*args):
    """Change size of a maptplotlib figure on screen.

    Args:
        *args: A tuple like (width, height) or two separate width, height  values (in px).
    """
    if len(args) > 1:
        width = int(args[0])
        height = int(args[1])
    elif len(args) == 1 and len(args[0]) == 2:
        width = int(args[0][0])
        height = int(args[0][1])
    else:
        warnings.warn('Wrong input')
        return

    figManager = get_current_fig_manager()
    x,y = getFigurePosition()

    try:  # tested on tKinter backend
        figureGeometry = str(width) + 'x' + str(height) + '+' + str(x) + '+' + str(y)
        figManager.window.wm_geometry(figureGeometry)

    except AttributeError:
        try:  # tested on qt4 and qt5 backends
            figManager.window.setGeometry(x, y, width, height)
        except AttributeError:
            warnings.warn('Backend not suported.')


def maximize():
    "Maximize current fig."""
    figManager = plt.get_current_fig_manager()

    try:  # tested on tKinter backend
        figManager.frame.Maximize(True)

    except AttributeError:  # tested on qt4 and qt5 backends
        try:
            figManager.window.showMaximized()
        except AttributeError:
            warnings.warn('Backend not suported.')
            return (0, 0)



def getFigurePosition():
    """Get the position of a matplotlib position on the screen.

    Tipically, (0, 0) is the top left corner of your monitor.

    Returns:
        Tuple with the x and y position.
    """
    figManager = get_current_fig_manager()

    try:  # tested under tKinter backend
        return (figManager.window.winfo_x(), figManager.window.winfo_y())

    except AttributeError:  # tested under qt4 and qt5 backends
        try:
            return (figManager.window.geometry().x(), figManager.window.geometry().y())
        except AttributeError:
            warnings.warn('Backend not suported.')
            return (0, 0)


def getFigureSize():
    """Get the size of a matplotlib figure.

    Returns:
        Tuple with the width and height values.
    """
    figManager = get_current_fig_manager()

    try:  # tested on tKinter backend
        return (figManager.window.winfo_width(), figManager.window.winfo_height())

    except AttributeError:  # tested on qt4 and qt5 backends
        try:
            return (figManager.window.geometry().width(), figManager.window.geometry().height())
        except AttributeError:
            warnings.warn('Backend not suported.')
            return (0, 0)


def zoom(xinit, xfinal, fig=None, marginy=2, marginx=2):
    """pass.
    margin in percentage.
    """
    if fig is None:
        fig = plt.gcf()

    ymax = 0
    ymin = 0

    for axis in fig.axes:
        for line in axis.get_lines():
            try:
                ymax_temp = max(line.get_data()[1][index(line.get_data()[0], xinit): index(line.get_data()[0], xfinal)])
                ymin_temp = min(line.get_data()[1][index(line.get_data()[0], xinit): index(line.get_data()[0], xfinal)])
            except ValueError:
                warnings.warn("All points of some data are outside of the required range.")
            try:
                if ymax_temp > ymax:
                    ymax = copy.copy(ymax_temp)
                if ymin_temp < ymin:
                    ymin = copy.copy(ymin_temp)

                m =  (ymax-ymin)*marginy/100
                plt.ylim(ymin-m, ymax+m)

                m =  (xfinal-xinit)*marginx/100
                plt.xlim(xinit, xfinal)
            except UnboundLocalError:
                warnings.warn("All data are outside of the required range. Cannot zoom.")



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



# from tkinter import Tk
# def dataX_to_clipboard(event):
#     r = Tk()
#     r.withdraw()
#     r.clipboard_clear()
#     r.clipboard_append(str(event.xdata))
#     r.update() # now it stays on the clipboard after the window is closed
#     # r.destroy()





def onclick(event):
    # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
    #       ('double' if event.dblclick else 'single', event.button,
    #        event.x, event.y, event.xdata, event.ydata))
    global fig_dataX, fig_dataY
    fig_dataX = event.xdata
    fig_dataY = event.ydata



# old but useful. I do not remenber why I use these
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
