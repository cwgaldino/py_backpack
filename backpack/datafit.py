#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fit.

TODO:
-method to plot parameter for various temperatures
-add fit button to libreoffice
-fit various data (like first and second der)


New atributes added to sheet object:
parameters
var_string
model_string
p_min
p_max
p_guess
p_fitted
p_error
linked_parameters
id_list
submodel
residue
p_cov

new methods:
get_parameters
update_model
update_submodels
fit

functions:
fake_sigma
"""

# standard libraries
import copy
import numpy as np
from pathlib import Path
import inspect
import sys
import importlib

# matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# backpack
from .model_functions import *
from .libremanip2 import sheet
from .arraymanip import index

# fit
from scipy.optimize import curve_fit
from scipy.integrate import trapz

last_col = 'L'
header_row = 1
hashtag_col = 1

exp_def     = dict(linewidth=2, markersize=8, color='black')
guess_def   = dict(linewidth=2, linestyle='--', color='green')
fit_def     = dict(linewidth=2, color='red')
ties_def    = dict(markersize=8, color='orange')
der_def     = dict(linewidth=0, marker='o', color='black')
der_fit_def = dict(linewidth=2, color='red')
der_guess_def = dict(linewidth=2, linestyle='--', color='green')
sub_def     = dict(linewidth=1)


def get_parameters(self,):
    # self = sheet

    # set # col
    self.set_col_values(np.arange(0, self.get_last_row()-1), col=hashtag_col, row_start=header_row+1)

    # get header and submodels
    header = self.get_row_values(header_row, col_stop=last_col)
    submodel_col = header.index('submodel')+1
    arg_col = header.index('arg')+1
    submodel_list = self.get_col_values(submodel_col)[1:]

    self.parameters = dict()
    for row_number, submodel in enumerate(submodel_list):
        if submodel == '':
            pass
        else:
            row_values = self.get_row_values(row_number+2, col_stop=last_col)
            arg = row_values[arg_col-1]

            try:
                if arg in self.parameters[submodel]: # check for repeated parameter id's
                    for key, value in self.parameters[submodel][arg].items():
                        # if type(value) != list:
                        #     value = [value]
                        value.append(row_values[header.index(key)])
                        self.parameters[submodel][arg][key] = value
                else:
                    self.parameters[submodel][arg]={header[col_number]: [value] for col_number, value in enumerate(row_values)}
            except KeyError:
                self.parameters[submodel] = {arg:{header[col_number]: [value] for col_number, value in enumerate(row_values)}}


def update_model(self):
    refresh()

    var_string = ''
    model_string = ''
    self.p_min = []
    self.p_max = []
    self.p_guess = []
    self.p_fitted = []
    self.p_error = []

    # get parameters
    self.get_parameters()

    # get header and submodels
    header = self.get_row_values(header_row, col_stop=last_col)
    guess_col = header.index('guess')+1
    fitted_col = header.index('fitted')+1
    error_col = header.index('error')+1
    id_col = header.index('id')+1
    self.set_col_values(data=['' for i in range(self.get_last_row()-1)], row_start=header_row+1, col=id_col)

    p = 0
    x = 0
    self.linked_parameters = {}
    for submodel in self.parameters:

        # check if this submodel should be used
        if 'y' in [use for sublist in [self.parameters[submodel][arg]['use'] for arg in self.parameters[submodel]] for use in sublist]:

            # get tag
            try:
                submodel_tag = submodel.split('#')[-1]
            except IndexError:
                submodel_tag = None
            submodel_name = submodel.split('#')[0]

            # get arguments from function
            args_expected = list(inspect.signature(eval(submodel_name)).parameters)

            # initialize model
            model_string += f"{submodel_name}(x, "

            # build min, max, guess, model
            for arg in args_expected[1: ]:
                # print(submodel, arg)

                # check if submodel has active argument
                missing_arg = False
                try:
                    to_use = self.parameters[submodel][arg]['use'].index('y')
                except ValueError:
                    missing_arg = True
                if missing_arg: raise MissingArgument(submodel, arg)

                # check if parameter must vary =========================================================
                vary = list(self.parameters[submodel][arg]['vary'])[to_use]
                hashtag = list(self.parameters[submodel][arg]['#'])[to_use]
                # linked parameter ===================================
                if vary != 'y' and vary != 'n':
                    submodel2link = vary.split(',')[0]
                    arg2link = vary.split(',')[-1]
                    if submodel2link in self.parameters and arg2link in self.parameters[submodel]:
                        to_use_linked = self.parameters[submodel2link][arg2link]['use'].index('y')
                        vary2 = list(self.parameters[submodel2link][arg2link]['vary'])[to_use_linked]
                    else:
                        raise ValueError(f"Cannot find submodel '{submodel2link}' with arg '{arg2link}'.")
                    while vary2 != 'y' and vary2 != 'n':
                        # print(vary2)
                        submodel2link = vary2.split(',')[0]
                        arg2link = vary2.split(',')[-1]
                        # print(submodel2link, arg2link)
                        if submodel2link in self.parameters and arg2link in self.parameters[submodel]:
                            to_use_linked = self.parameters[submodel2link][arg2link]['use'].index('y')
                            vary2 = list(self.parameters[submodel2link][arg2link]['vary'])[to_use_linked]
                        else:
                            raise ValueError(f"Cannot find submodel '{submodel2link}' with arg '{arg2link}'.")

                    if vary2 == 'n': #
                        v = list(self.parameters[submodel2link][arg2link]['guess'])[to_use_linked]
                        model_string += f'{v}, '
                        self.set_cell_value(value='-', row=hashtag+header_row+1, col=id_col)
                        self.set_cell_value(value=v, row=hashtag+header_row+1, col=guess_col)
                        self.set_cell_value(value=v, row=hashtag+header_row+1, col=fitted_col)
                        self.set_cell_value(value=0, row=hashtag+header_row+1, col=error_col)
                    else:
                        if submodel2link+','+arg2link in self.linked_parameters:
                            x_temp = self.linked_parameters[submodel2link+','+arg2link]
                            self.set_cell_value(value='x' + str(x_temp), row=hashtag+header_row+1, col=id_col)
                            self.parameters[submodel][arg]['id'][to_use] = 'x' + str(x_temp)
                            # var_string += f'x{x_temp}, '
                            model_string += f'x{x_temp}, '
                        else:
                            self.linked_parameters[submodel2link+','+arg2link] = x
                            self.set_cell_value(value='x' + str(x), row=hashtag+header_row+1, col=id_col)
                            self.parameters[submodel][arg]['id'][to_use] = 'x' + str(x)
                            # var_string += f'x{x}, '
                            model_string += f'x{x}, '
                            x += 1


                # fixed parameter ================================
                elif vary == 'n':
                    v = list(self.parameters[submodel][arg]['guess'])[to_use]
                    model_string += f'{v}, '
                    self.set_cell_value(value='-', row=hashtag+header_row+1, col=id_col)
                    self.parameters[submodel][arg]['id'][to_use] = '-'
                    self.set_cell_value(value=v, row=hashtag+header_row+1, col=fitted_col)
                    self.parameters[submodel][arg]['fitted'][to_use] = v
                    self.set_cell_value(value=0, row=hashtag+header_row+1, col=error_col)
                    self.parameters[submodel][arg]['error'][to_use] = 0


                # variable parameter =============================
                else:
                    self.p_min.append(list(self.parameters[submodel][arg]['min'])[to_use])
                    self.p_max.append(list(self.parameters[submodel][arg]['max'])[to_use])
                    self.p_guess.append(list(self.parameters[submodel][arg]['guess'])[to_use])
                    self.p_fitted.append(list(self.parameters[submodel][arg]['fitted'])[to_use])
                    self.p_error.append(list(self.parameters[submodel][arg]['error'])[to_use])

                    try:
                        if submodel+','+arg in self.linked_parameters:
                            x_temp = self.linked_parameters[submodel+','+arg]
                            self.set_cell_value(value='x' + str(x_temp), row=hashtag+header_row+1, col=id_col)
                            self.parameters[submodel][arg]['id'][to_use] = 'x' + str(x_temp)
                            var_string += f'x{x_temp}, '
                            model_string += f'x{x_temp}, '
                        else:
                            self.set_cell_value(value='p' + str(p), row=hashtag+header_row+1, col=id_col)
                            self.parameters[submodel][arg]['id'][to_use] = 'p' + str(p)
                            var_string += f'p{p}, '
                            model_string += f'p{p}, '
                            p += 1
                    except UnboundLocalError:
                        var_string += f'p{p}, '
                        model_string += f'p{p}, '
                        p += 1

            model_string += ') + '

    # finish model
    self.id_list = [s.strip() for s in eval('["' + var_string[:-2].replace(',', '","') + '"]')]

    self.model_string = f'lambda x, {var_string[:-2]}: {model_string[:-3]}'
    self.model = eval(self.model_string)

    # check guess, min, max ============================
    if '' in self.p_guess:
        guess_missing = [self.id_list[i] for i, x in enumerate(self.p_guess) if x == '']
        raise ValueError(f'Parameters with id {guess_missing} do not have a guess value.')

    if '' in self.p_min:
        self.p_min = [-np.inf if x == '' else x for x in self.p_min]
    if '' in self.p_max:
        self.p_max = [np.inf if x == '' else x for x in self.p_max]
    if '' in self.p_fitted:
        self.p_fitted = [0 if x == '' else x for x in self.p_fitted]
    if '' in self.p_error:
        self.p_error = [0 if x == '' else x for x in self.p_error]

    # submodel
    self.update_submodels()


def update_submodels(self):

    self.submodel = {}

    for submodel in self.parameters:

        # check if submodel should be used
        if 'y' in [use for sublist in [self.parameters[submodel][arg]['use'] for arg in self.parameters[submodel]] for use in sublist]:
            self.submodel[submodel] = {'guess_string': '', 'fit_string':''}

            # get tag
            try:
                submodel_tag = submodel.split('#')[-1]
            except IndexError:
                submodel_tag = None
            submodel_name = submodel.split('#')[0]

            # get arguments from function
            import __main__
            try:
                args_expected = list(inspect.signature(eval(f'__main__.{submodel_name}')).parameters)
            except AttributeError:
                args_expected = list(inspect.signature(eval(submodel_name)).parameters)

            # initialize submodel
            self.submodel[submodel]['guess_string'] += f'{submodel_name}(x, '
            self.submodel[submodel]['fit_string'] += f'{submodel_name}(x, '


            for arg in args_expected[1: ]:

                # check if submodel has active argument
                missing_arg = False
                try:
                    to_use = self.parameters[submodel][arg]['use'].index('y')
                except ValueError:
                    missing_arg = True
                if missing_arg: raise MissingArgument(submodel, arg)

                # build min, max, guess, model
                if self.parameters[submodel][arg]['id'][to_use] != '-':
                    id = self.parameters[submodel][arg]['id'][to_use]
                    self.submodel[submodel]['guess_string'] += str(self.p_guess[self.id_list.index(id)]) + ', '
                    self.submodel[submodel]['fit_string']   += str(self.p_fitted[self.id_list.index(id)]) + ', '
                else:
                    self.submodel[submodel]['guess_string'] += str(self.parameters[submodel][arg]['guess'][to_use]) + ', '
                    self.submodel[submodel]['fit_string'] += str(self.parameters[submodel][arg]['fitted'][to_use]) + ', '

            self.submodel[submodel]['guess_string'] = self.submodel[submodel]['guess_string'][:-2] + ')'
            self.submodel[submodel]['fit_string'] = self.submodel[submodel]['fit_string'][:-2] + ')'

            self.submodel[submodel]['guess'] = eval(f'lambda x:' + self.submodel[submodel]['guess_string'])
            self.submodel[submodel]['fit'] = eval(f'lambda x:' + self.submodel[submodel]['fit_string'])


def fit(self, x, y, ties=None, global_sigma=1e-13, save=True):

    self.update_model()

    # fit
    if global_sigma is not None:
        sigma = fake_sigma(x, global_sigma=global_sigma, sigma_specific=ties)
    self.p_fitted, self.p_cov = curve_fit(self.model, x, y, self.p_guess, sigma=sigma, bounds=[self.p_min, self.p_max])
    self.p_error = np.sqrt(np.diag(self.p_cov))  # One standard deviation errors on the parameters

    # get residue
    self.residue = trapz(abs(y - self.model(x, *self.p_fitted)), x)

    # save to sheet and self.parameter =====================================================
    # get header and submodels
    header = self.get_row_values(header_row, col_stop=last_col)
    fitted_col = header.index('fitted')+1
    error_col = header.index('error')+1

    for submodel in self.parameters:
        # check if submodel should be used
        if 'y' in [use for sublist in [self.parameters[submodel][arg]['use'] for arg in self.parameters[submodel]] for use in sublist]:

            # get tag
            try:
                submodel_tag = submodel.split('#')[-1]
            except IndexError:
                submodel_tag = None
            submodel_name = submodel.split('#')[0]

            # get arguments from function
            args_expected = list(inspect.signature(eval(submodel_name)).parameters)

            # build min, max, guess, model
            for arg in args_expected[1: ]:

                # check if submodel has active argument
                missing_arg = False
                try:
                    to_use = self.parameters[submodel][arg]['use'].index('y')
                except ValueError:
                    missing_arg = True
                if missing_arg: raise MissingArgument(submodel, arg)

                hashtag = list(self.parameters[submodel][arg]['#'])[to_use]
                if self.parameters[submodel][arg]['id'][to_use] != '-':
                    id = self.parameters[submodel][arg]['id'][to_use]
                    v1 = self.p_fitted[self.id_list.index(id)]
                    v2 = self.p_error[self.id_list.index(id)]
                    self.set_cell_value(value=v1, row=hashtag+header_row+1, col=fitted_col)
                    self.set_cell_value(value=v2, row=hashtag+header_row+1, col=error_col)
                    self.parameters[submodel][arg]['fitted'][to_use] = v1
                    self.parameters[submodel][arg]['error'][to_use] = v2

    self.update_submodels()

    if save:
        self.calc.save()


def fake_sigma(x, global_sigma=10**-10, sigma_specific=None):
    """Build a fake sigma array which determines the uncertainty in ydata.

    Adaptaded from the `scipy.optimize.curve_fit() <https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html>`_ documentation:

        If we define residuals as ``r = ydata - model(xdata, *popt)``, then sigma
        for a 1-D data should contain values of standard deviations of errors in
        ydata. In this case, the optimized function is ``chisq = sum((r / sigma) ** 2)``.

    Args:
        x (list): x array.
        sigma (float, optional): sigma value to be used for all points in ``x``.
        sigma_specific (list, optional): list of triples specfing new sigma for specific ranges, e.g.,
            ``sigma_specific = [[x_init, x_final, sigma], [x_init2, x_final2, sigma2], ]``.

    Returns:
        array.
    """
    p_sigma = np.ones(len(x))*global_sigma

    if sigma_specific is not None:
        for sigma in sigma_specific:
            init = index(x, sigma[0])
            final = index(x, sigma[1])
            p_sigma[init:final] = global_sigma/sigma[2]

    return p_sigma


def refresh():

    importlib.reload(sys.modules[__name__])


def plot_fit(self, x, y, ax=None, show_exp=True, show_derivative=False, show_submodels=False, smoothing=10, ties=None, submodels_bkg=None, derivative_order=1, derivative_offset=None, derivative_factor=None, derivative_window_size=1):

    if smoothing == 0:
        x_smooth = x
    elif smoothing < 1:
        smoothing = 1
        x_smooth = np.linspace(min(x), max(x), len(x)*smoothing)
    else:
        x_smooth = np.linspace(min(x), max(x), len(x)*smoothing)

    if ax is None:
        fig = figm.figure()
        ax = fig.add_subplot(111)

    # exp
    if show_exp:
        ax.plot(x, y, **exp_def, label='exp')

    # ties
    if ties is not None:
        for pair in ties:
            ax.plot(x[am.index(x, pair[0]):am.index(x, pair[1])], y[am.index(x, pair[0]):am.index(x, pair[1])], **ties_def)

    # derivative
    if show_derivative:
        x_der, y_der = am.derivative(x, y, order=derivative_order, window_size=derivative_window_size)

        if derivative_factor is None:
            derivative_factor = (max(y) - np.mean(y))/(max(y_der) - np.mean(y_der))
        if derivative_offset is None:
            derivative_offset = -(max(y_der*derivative_factor) - np.mean(y))

        ax.plot(x_der, y_der*derivative_factor+derivative_offset, **der_def)

    # fit
    self.update_model()
    y_fit = self.model(x_smooth, *self.p_fitted)
    ax.plot(x_smooth, y_fit, **fit_def)

    if show_derivative:
        x_fir_der, y_fit_der = am.derivative(x_smooth, y_fit, order=derivative_order)
        ax.plot(x_fir_der, y_fit_der*derivative_factor+derivative_offset, **der_fit_def)

    # submodels
    if show_submodels:
        sub_colors = cm.get_cmap('Set1').colors
        if submodels_bkg is not None:
            bkg = self.submodel[submodels_bkg]['fit'](x_smooth)
        else:
            bkg=0
        for submodel, color in zip(self.submodel, sub_colors):
            if submodel != submodels_bkg:
                ax.plot(x_smooth, self.submodel[submodel]['fit'](x_smooth) + bkg, **sub_def, color=color, label=submodel)

    plt.legend()
    return ax


def plot_guess(self, x, y, ax=None, show_exp=True, show_derivative=False, show_submodels=False, smoothing=10, ties=None, submodels_bkg=None, derivative_order=1, derivative_offset=None, derivative_factor=None, derivative_window_size=1):

    if smoothing == 0:
        x_smooth = x
    elif smoothing < 1:
        smoothing = 1
        x_smooth = np.linspace(min(x), max(x), len(x)*smoothing)
    else:
        x_smooth = np.linspace(min(x), max(x), len(x)*smoothing)

    if ax is None:
        fig = figm.figure()
        ax = fig.add_subplot(111)

    # exp
    if show_exp:
        ax.plot(x, y, **exp_def, label='exp')

    # ties
    if ties is not None:
        for pair in ties:
            ax.plot(x[am.index(x, pair[0]):am.index(x, pair[1])], y[am.index(x, pair[0]):am.index(x, pair[1])], **ties_def)

    # derivative
    if show_derivative:
        x_der, y_der = am.derivative(x, y, order=derivative_order, window_size=derivative_window_size)

        if derivative_factor is None:
            derivative_factor = (max(y) - np.mean(y))/(max(y_der) - np.mean(y_der))
        if derivative_offset is None:
            derivative_offset = -(max(y_der*derivative_factor) - np.mean(y))

        ax.plot(x_der, y_der*derivative_factor+derivative_offset, **der_def)

    # fit
    y_guess = self.model(x_smooth, *self.p_guess)
    ax.plot(x_smooth, y_guess, **guess_def)

    if show_derivative:
        x_fir_der, y_fit_der = am.derivative(x_smooth, y_guess, order=derivative_order)
        ax.plot(x_fir_der, y_fit_der*derivative_factor+derivative_offset, **der_guess_def)

    # submodels
    if show_submodels:
        sub_colors = cm.get_cmap('Set1').colors
        if submodels_bkg is not None:
            bkg = self.submodel[submodels_bkg]['guess'](x_smooth)
        else:
            bkg=0
        for submodel, color in zip(self.submodel, sub_colors):
            if submodel != submodels_bkg:
                ax.plot(x_smooth, self.submodel[submodel]['guess'](x_smooth) + bkg, **sub_def, color=color, label=submodel)
    plt.legend()
    return ax


class MissingArgument(Exception):

    # Constructor or Initializer
    def __init__(self, submodel, arg):
        self.submodel = submodel
        self.arg = arg

    # __str__ is to print() the value
    def __str__(self):
        msg = f"Submodel '{self.submodel}' is missing argument '{self.arg}'."
        return(msg)

sheet.get_parameters = get_parameters
sheet.update_model = update_model
sheet.update_submodels = update_submodels
sheet.fit = fit
sheet.plot_fit = plot_fit
sheet.plot_guess = plot_guess


try:
    from __main__ import *
except ImportError:
    pass
