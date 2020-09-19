#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Support function for fit scripts."""

# standard libraries
from copy import copy, deepcopy
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import collections
import warnings

# backpack
import sys
sys.path.append('/home/galdino/github/py-backpack')
import backpack.filemanip as fmanip
import backpack.figmanip as figmanip
import backpack.arraymanip as manip
from backpack.arraymanip import index
import backpack.calcmanip as calc
from backpack.model_functions import fwhmVoigt, fwhmLorentz, fwhmArctan, fwhmGauss
import importlib
importlib.reload(fmanip)
importlib.reload(figmanip)
importlib.reload(calc)

import inspect


def load_parameter_dict(sheetObject, dict_grouping_cols, object_hook=None):
    """
    combination of dict_grouping_cols mus be unique. Otherwise it will raise a warning.

    """

    sheet_data = calc.get_cells_value(sheetObject, row_init=0, col_init=0, type='data')
    sheet_header = sheet_data[0]

    grouping_lists = []
    for col in dict_grouping_cols:
        grouping_lists.append([row[col] for row in sheet_data[1:]])

    nested_dict = lambda: collections.defaultdict(nested_dict)
    par = nested_dict()

    for row, a in enumerate(zip(*grouping_lists)):
        a = list(a)  # change to list so we can change strings to numbers
        if '' not in a:  # ignore blank rows
            string = ''
            for i in range(len(a)):
                string += f'[a[{i}]]'
                try:  # if a[i] is a int, change it to int
                    if float(a[i]).is_integer():
                        a[i] = int(float(a[i]))
                    else:
                        a[i] = float(a[i])
                except:
                    pass
            for col, item in enumerate(sheet_header):  # find col
                if item is not '':
                    if eval(f'par{string}[item]') == {}:  # find out if key already exists
                        if object_hook is not None:
                            # print(sheet_data[row+1][col])
                            val = object_hook(sheet_data[row+1][col])
                            # print(val)
                            exec(f'par{string}[item] = val')
                        else:
                            exec(f'par{string}[item] = sheet_data[row+1][col]')
                    else:  # if key already exists, raise a warning
                        string2 = string.replace('a[', '{a[')
                        string2 = string2.replace(']]', ']}]')
                        string2 = eval(f'f"par{string2}"')
                        warnings.warn(f'keys combination not unique for {string2}[{item}]. Ignoring row={row}, col={col}.')
    return par


def dump_parameter_dict(sheetObject, par, dict_grouping_cols):

    sheet_data = calc.get_cells_value(sheetObject, row_init=0, col_init=0, type='data')
    sheet_header = sheet_data[0]

    grouping_lists = []
    for col in dict_grouping_cols:
        grouping_lists.append([row[col] for row in sheet_data[1:]])

    # change sheet_data based on par
    for row, a in enumerate(zip(*grouping_lists)):
        a = list(a)  # change to list so we can change strings to numbers
        if '' not in a: # ignore blank rows
            string = ''
            for i in range(len(a)):
                string += f'[a[{i}]]'
                try:  # if a[i] is a int, change it to int
                    if float(a[i]).is_integer():
                        a[i] = int(float(a[i]))
                    else:
                        a[i] = float(a[i])
                except:
                    pass
            for col, item in enumerate(sheet_header): # find col
                if item is not '': # ignore blank cols
                        exec(f'sheet_data[row+1][col] = par{string}[item]')
    calc.set_cells_value(sheetObject, row_init=0, col_init=0, data=sheet_data, type='formula')


def model2str(submodel_dict, submodels2use='all'):
    """Build a model function for the fit.

    Note:
        Use eval to create function using the model2str() string output.

    Args:
        submodel_dict (dict): dict with functions.
        submodels2use (list, optional): list with dict keys to use. The default is
            that all groups will be used.

    Returns:
        string.
    """
    var_text = ''
    functions_text = ''
    j_total = 0

    if submodels2use == 'all':
        submodels2use = list(submodel_dict.keys())

    for j, group in enumerate(submodels2use):
        n_var = len(inspect.signature(submodel_dict[group]).parameters)-1
        var_temp = ''
        for k in range(n_var):
            var_temp += f'p{j_total}, '
            j_total +=1
        var_text += var_temp
        if type(group) == str:
            functions_text += f'submodel_dict[\'{group}\'](x, {var_temp[:-2]}) + '
        else:
            functions_text += f'submodel_dict[{group}](x, {var_temp[:-2]}) + '
    var_text = var_text[:-2] + ':'
    text = functions_text[:-2]

    return f'lambda x, {var_text} {text}'


def get_data_based_on_header(par, submodel_dict, submodels2use, header_title):
    par_sequence = []
    for submodel in submodels2use:
        arguments = submodel_dict[submodel].__code__.co_varnames
        ordered_list = [0 for i in range(len(arguments)-1)]
        for par_identifier in par[submodel]:
            i = arguments.index(par_identifier)-1
            ordered_list[i] = par[submodel][par_identifier][header_title]
        par_sequence += ordered_list
    return par_sequence


def set_data_based_on_header(par, par_list, submodel_dict, submodels2use, header_title):

    i=0
    for submodel in submodels2use:
        arguments = submodel_dict[submodel].__code__.co_varnames
        for j, par_identifier in enumerate(arguments[1:]):
            par[submodel][par_identifier][header_title] = par_list[i+j]
        i = i+ j+1


def sigma(x, sigma=10**-10, sigma_specific=None):
    """Build sigma matrix to be used in scipy.optimize.curve_fit().

    Args:
        x (list): x data.
        sigma (float, optional): sigma value to be used for all points in ``x``. Sigma
            relates with uncertainty in ydata. Default value is 10^-10.
        sigma_specific (list, optional): list of triples specfing new sigma for specific ranges, e.g.,

            >>>  sigma_specific = [[x_init, x_final, sigma], [x_init2, x_final2, sigma2], ]

    Returns:
        array to be used as sigma in scipy.optimize.curve_fit().
    """
    p_sigma = np.ones(len(x))*sigma

    if sigma_specific is not None:
        for sigma in sigma_specific:
            init = index(x, sigma[0])
            final = index(x, sigma[1])
            p_sigma[init:final] = sigma[2]

    return p_sigma


def inf_hook(value):
    """Substitute 'inf' by np.inf in parameter variable.

    Args:
        parameters (dict): parameter dict.
    """
    if value == 'inf':
        return np.inf
    elif value == '-inf':
        return -np.inf
    else:
        return value








def get_id(sheet, calcObject=None):

    if type(sheet) == str:
        sheetObject = calcObject.get_sheet_by_name(sheet)
    else:
        sheetObject = sheet

    # get id_list
    stop = False
    id_list = []
    row = 1
    while stop == False:
        id = sheetObject.get_cell_range_by_position(1, row, 1, row).getDataArray()

        if id[0][0] == '':
            stop = True
        else:
            id_list.append(id[0][0])
            row += 1
    return id_list


def get_group(sheet, calcObject=None):

    if type(sheet) == str:
        sheetObject = calcObject.get_sheet_by_name(sheet)
    else:
        sheetObject = sheet

    # get id_list
    stop = False
    group_list = []
    row = 1
    while stop == False:
        group = sheetObject.get_cell_range_by_position(0, row, 0, row).getDataArray()

        if group[0][0] == '':
            stop = True
        else:
            group_list.append(group[0][0])
            row += 1
    return group_list


def get_group_rows(sheet, calcObject=None):

    if type(sheet) == str:
        sheetObject = calcObject.get_sheet_by_name(sheet)
    else:
        sheetObject = sheet

    group_list = get_group(sheetObject)
    group_rows = dict()
    for group in set(group_list):
        group_rows[group] = [i+1 for i,x in enumerate(group_list) if x==group]
    return group_rows

def group_color(sheet, calcObject=None):

    if type(sheet) == str:
        sheetObject = calcObject.get_sheet_by_name(sheet)
    else:
        sheetObject = sheet

    # header old_color_max
    sheetObject.get_cell_range_by_position(0, 0, 10, 0).setPropertyValue('CellBackColor', 11711154)
    sheetObject.get_cell_range_by_position(0, 0, 10, 0).setPropertyValue('CharWeight', 150)  # bold


    group_rows = get_group(sheetObject)
    old_group = group_rows[0]
    color = -1
    for row, group in enumerate(group_rows):
        if group == old_group:
            sheetObject.get_cell_range_by_position(0, row+1, 10, row+1).setPropertyValue('CellBackColor', color)
        else:
            old_group = group_rows[row]
            if color == -1:
                color = 12771502
            else:
                color = -1
            sheetObject.get_cell_range_by_position(0, row+1, 10, row+1).setPropertyValue('CellBackColor', color)



# def warnings(parameters, submodels2use='all'):
#     """Check if fitted values are too close to min, max, and guess values.
#
#     Args:
#         parameters (dict): parameter dictionary created using load_xlsx().
#         submodels2use (list, optional): list with group keys used in the fit.
#             The default is that all groups will be used.
#     """
#     if submodels2use == 'all':
#         submodels2use = list(parameters.keys())
#
#     for par_identifier in submodels2use:
#         warn = []
#         for j in range(len(parameters[par_identifier]['fit'])):
#             if np.isclose(parameters[par_identifier]['fit'][j], parameters[par_identifier]['min'][j]):
#                 warn += ['MIN']
#             elif np.isclose(parameters[par_identifier]['fit'][j], parameters[par_identifier]['max'][j]):
#                 warn += ['MAX']
#             elif np.isclose(parameters[par_identifier]['fit'][j], parameters[par_identifier]['guess'][j]):
#                 warn += ['Did not change']
#             else:
#                 warn += ['OK']
#         parameters[par_identifier]['warning'] = warn
#
#     # not used groups
#     for par_identifier in [x for x in parameters if x not in submodels2use]:
#         warn = []
#         for j in range(len(parameters[par_identifier]['fit'])):
#             warn += ['Not used']
#         parameters[par_identifier]['warning'] = warn


# def buildGuess(parameters, submodels2use='all'):
#     """Build guess matrix to be used in scipy.optimize.curve_fit().
#
#     Args:
#         parameters (dict): parameter dictionary created using load_xlsx().
#         submodels2use (list, optional): list with dict keys to use. The default is
#             that all groups will be used.
#
#     Returns:
#         array to be used as guess in scipy.optimize.curve_fit().
#     """
#     if submodels2use == 'all':
#         submodels2use = list(parameters.keys())
#
#     p_guess = []
#     for group in submodels2use:
#         p_guess += parameters[group]['guess']
#     return p_guess



# def load_xlsx(sheetObject):
#     """Load xlsx file with fit parameters.
#
#     Args:
#         calcObject (Calc object): Object created by connect2calc().
#         filename (str or pathlib.Path): path to xlsx file.
#
#     Returns:
#         parameter dictionary.
#     """
#
#     sheet_data = calc.get_cells_value(sheetObject, row_init, col_init, type='data')
#
#     # get groups
#     submodel_list = calc.get_cells_value(sheetObject, row_init=1, col_init=submodel_col, col_final=submodel_col, type='data')
#
#     submodel_parameter_dict = dict()
#     for submodel in set(submodel_list):
#         group_rows[group] = [i+1 for i,x in enumerate(group_list) if x==group]
#     return group_rows
#
#     groups_unique =
#
#     # get data
#     id_list = get_id(sheetObject)
#     values = sheetObject.get_cell_range_by_position(0, 0, 10, len(id_list)+1).getDataArray()
#
#     # separate data by group
#     group_rows = get_group_rows(sheetObject)
#     parameters = dict()
#     for group in group_rows:
#         for item, row in enumerate([group]):
#             parameters[group] = dict()
#             parameters[group]['id']          = [values[i][1] for i in range(1, len(values)) if values[i][0] == group]
#             parameters[group]['description'] = [values[i][2] for i in range(1, len(values)) if values[i][0] == group]
#             parameters[group]['dummy']       = [values[i][3] for i in range(1, len(values)) if values[i][0] == group]
#             parameters[group]['min']         = [values[i][4] for i in range(1, len(values)) if values[i][0] == group]
#             parameters[group]['guess']       = [values[i][5] for i in range(1, len(values)) if values[i][0] == group]
#             parameters[group]['max']         = [values[i][6] for i in range(1, len(values)) if values[i][0] == group]
#             parameters[group]['fit']         = [values[i][7] for i in range(1, len(values)) if values[i][0] == group]
#             parameters[group]['error']       = [values[i][8] for i in range(1, len(values)) if values[i][0] == group]
#             parameters[group]['warning']     = [values[i][9] for i in range(1, len(values)) if values[i][0] == group]
#             parameters[group]['comments']    = [values[i][10] for i in range(1, len(values)) if values[i][0] == group]
#
#     fixInf(parameters)
#     fixNone(parameters)
#
#     return sheetObject, parameters











# %% specific

# def loadCalc(sheet, calcObject=None):
#     """Load xlsx file with fit parameters.
#
#     Args:
#         calcObject (Calc object): Object created by connect2calc().
#         filename (str or pathlib.Path): path to xlsx file.
#
#     Returns:
#         parameter dictionary.
#     """
#
#     # connect to sheet
#     if type(sheet) == str:
#         sheetObject = calcObject.get_sheet_by_name(sheet)
#     else:
#         sheetObject = sheet
#
#     # get data
#     id_list = get_id(sheetObject)
#     values = sheetObject.get_cell_range_by_position(0, 0, 10, len(id_list)+1).getDataArray()
#
#     # separate data by group
#     group_rows = get_group_rows(sheetObject)
#     parameters = dict()
#     for group in group_rows:
#         for item, row in enumerate([group]):
#             parameters[group] = dict()
#             parameters[group]['id']          = [values[i][1] for i in range(1, len(values)) if values[i][0] == group]
#             parameters[group]['description'] = [values[i][2] for i in range(1, len(values)) if values[i][0] == group]
#             parameters[group]['dummy']       = [values[i][3] for i in range(1, len(values)) if values[i][0] == group]
#             parameters[group]['min']         = [values[i][4] for i in range(1, len(values)) if values[i][0] == group]
#             parameters[group]['guess']       = [values[i][5] for i in range(1, len(values)) if values[i][0] == group]
#             parameters[group]['max']         = [values[i][6] for i in range(1, len(values)) if values[i][0] == group]
#             parameters[group]['fit']         = [values[i][7] for i in range(1, len(values)) if values[i][0] == group]
#             parameters[group]['error']       = [values[i][8] for i in range(1, len(values)) if values[i][0] == group]
#             parameters[group]['warning']     = [values[i][9] for i in range(1, len(values)) if values[i][0] == group]
#             parameters[group]['comments']    = [values[i][10] for i in range(1, len(values)) if values[i][0] == group]
#
#     fixInf(parameters)
#     fixNone(parameters)
#
#     return sheetObject, parameters


# def fixInf(parameters):
#     """Substitute 'inf' by np.inf in parameter variable.
#
#     Args:
#         parameters (dict): parameter dict.
#     """
#     for group in parameters:
#         for t in ('min', 'max'):
#             matching = [j for j in range(len(parameters[group][t])) if 'inf' == parameters[group][t][j]]
#             for k in matching:
#                 parameters[group][t][k] = np.inf
#             matching = [j for j in range(len(parameters[group][t])) if '-inf' == parameters[group][t][j]]
#             for k in matching:
#                 parameters[group][t][k] = -np.inf
#     return


# def fixNone(parameters):
#     """Substitute None in max by +np.inf, min by -np.inf, and guess by 0 .
#
#     Args:
#         parameters (dict): parameter dict.
#     """
#     for group in parameters:
#         t = 'min'
#         matching = [j for j in range(len(parameters[group][t])) if parameters[group][t][j] == '']
#         for k in matching:
#             parameters[group][t][k] = -np.inf
#
#         t = 'max'
#         matching = [j for j in range(len(parameters[group][t])) if parameters[group][t][j] == '']
#         for k in matching:
#             parameters[group][t][k] = np.inf
#
#         t = 'guess'
#         matching = [j for j in range(len(parameters[group][t])) if parameters[group][t][j] == '']
#         for k in matching:
#             parameters[group][t][k] = 0
#     return




# def get_submodels(sheetObject, submodel_col=1):
#
#     return calc.get_cells_value(sheetObject, row_init=1, col_init=submodel_col, col_final=submodel_col, type='data')


# def get_group_rows(sheetObject):
#
#     group_list = get_group(sheetObject)
#     group_rows = dict()
#     for group in set(group_list):
#         group_rows[group] = [i+1 for i,x in enumerate(group_list) if x==group]
#     return group_rows


# def update_xlsx(parameters, sheet, calcObject=None):
#
#     # connect to sheet
#     if type(sheet) == str:
#         sheetObject = calcObject.get_sheet_by_name(sheet)
#     else:
#         sheetObject = sheet
#
#     group_rows = get_group_rows(sheetObject)
#
#     for group in group_rows:
#         for item, row in enumerate(group_rows[group]):
#             sheetObject.set_rows_formula(1, row, [parameters[group]['id'][item], ])
#             sheetObject.set_rows_formula(2, row, [parameters[group]['description'][item], ])
#             sheetObject.set_rows_formula(3, row, [parameters[group]['dummy'][item], ])
#
#             if parameters[group]['min'][item] == -np.inf:
#                 sheetObject.set_rows_formula(4, row, ['-inf', ])
#             else:
#                 sheetObject.set_rows_formula(4, row, [parameters[group]['min'][item], ])
#
#             sheetObject.set_rows_formula(5, row, [parameters[group]['guess'][item], ])
#
#             if parameters[group]['max'][item] == np.inf:
#                 sheetObject.set_rows_formula(6, row, ['inf', ])
#             else:
#                 sheetObject.set_rows_formula(6, row, [parameters[group]['max'][item], ])
#
#             sheetObject.set_rows_formula(7, row, [parameters[group]['fit'][item], ])
#             sheetObject.set_rows_formula(8, row, [parameters[group]['error'][item], ])
#             sheetObject.set_rows_formula(9, row, [parameters[group]['warning'][item], ])
#             sheetObject.set_rows_formula(10, row, [parameters[group]['comments'][item], ])















# xlsx




# def fixInf(parameters):
#     """Substitute 'inf' by np.inf in parameter variable.
#
#     Args:
#         parameters (dict): parameter dict.
#     """
#     for group in parameters:
#         for t in ('min', 'max'):
#             matching = [j for j in range(len(parameters[group][t])) if 'inf' == parameters[group][t][j]]
#             for k in matching:
#                 parameters[group][t][k] = np.inf
#             matching = [j for j in range(len(parameters[group][t])) if '-inf' == parameters[group][t][j]]
#             for k in matching:
#                 parameters[group][t][k] = -np.inf
#     return


# def fixNone(parameters):
#     """Substitute None in max by +np.inf, min by -np.inf, and guess by 0 .
#
#     Args:
#         parameters (dict): parameter dict.
#     """
#     for group in parameters:
#         t = 'min'
#         matching = [j for j in range(len(parameters[group][t])) if parameters[group][t][j] == '']
#         for k in matching:
#             parameters[group][t][k] = -np.inf
#
#         t = 'max'
#         matching = [j for j in range(len(parameters[group][t])) if parameters[group][t][j] == '']
#         for k in matching:
#             parameters[group][t][k] = np.inf
#
#         t = 'guess'
#         matching = [j for j in range(len(parameters[group][t])) if parameters[group][t][j] == '']
#         for k in matching:
#             parameters[group][t][k] = 0
#     return


# def update_xlsx(parameters, sheet, calcObject=None):
#
#     # connect to sheet
#     if type(sheet) == str:
#         sheetObject = calcObject.get_sheet_by_name(sheet)
#     else:
#         sheetObject = sheet
#
#     group_rows = get_group_rows(sheetObject)
#
#     for group in group_rows:
#         for item, row in enumerate(group_rows[group]):
#             sheetObject.set_rows_formula(1, row, [parameters[group]['id'][item], ])
#             sheetObject.set_rows_formula(2, row, [parameters[group]['description'][item], ])
#             sheetObject.set_rows_formula(3, row, [parameters[group]['dummy'][item], ])
#
#             if parameters[group]['min'][item] == -np.inf:
#                 sheetObject.set_rows_formula(4, row, ['-inf', ])
#             else:
#                 sheetObject.set_rows_formula(4, row, [parameters[group]['min'][item], ])
#
#             sheetObject.set_rows_formula(5, row, [parameters[group]['guess'][item], ])
#
#             if parameters[group]['max'][item] == np.inf:
#                 sheetObject.set_rows_formula(6, row, ['inf', ])
#             else:
#                 sheetObject.set_rows_formula(6, row, [parameters[group]['max'][item], ])
#
#             sheetObject.set_rows_formula(7, row, [parameters[group]['fit'][item], ])
#             sheetObject.set_rows_formula(8, row, [parameters[group]['error'][item], ])
#             sheetObject.set_rows_formula(9, row, [parameters[group]['warning'][item], ])
#             sheetObject.set_rows_formula(10, row, [parameters[group]['comments'][item], ])




# def copy_sheet(sheet2CopyFrom, sheet2PasteAt, calcObject2CopyFrom=None, calcObject2PasteAt=None):
#
#     if type(sheet2CopyFrom) == str:
#         sheetObject = calcObject.get_sheet_by_name(sheet2CopyFrom)
#     else:
#         sheetObject = sheet2CopyFrom
#
#     if type(sheet2PasteAt) == str:
#         sheetObject2 = calcObject.get_sheet_by_name(sheet2PasteAt)
#     else:
#         sheetObject2 = sheet2PasteAt
#
#     # copy/paste data
#     id_list = get_id(sheetObject)
#     sheet_data = sheetObject.get_cell_range_by_position(0, 0, 10, len(id_list)+1).getDataArray()
#
#     for row, row_data in enumerate(sheet_data):
#         sheetObject2.set_columns_formula(0, row, row_data)
#         for column in range(4, 10):  # copy/paste conditional formating
#             sheetObject2.get_cell_by_position(column, row+1).ConditionalFormat = sheetObject.get_cell_by_position(column, row+1).ConditionalFormat
#
#     # copy column Size
#     cols = sheetObject.getColumns()
#     cols2 = sheetObject2.getColumns()
#     for col_number, col in enumerate(cols[0:11]):
#         cols2[col_number].setPropertyValue('Width', col.Width)
#
#     # fix color formating
#     group_color(sheetObject2, calcObject=None)


# function



# pre fit






# def buildBounds(parameters, groups2use='all'):
#     """Build boundary matrix to be used in scipy.optimize.curve_fit().
#
#     Args:
#         parameters (dict): parameter dictionary created using load_xlsx().
#         groups2use (list, optional): list with dict keys to use. The default is
#             that all groups will be used.
#
#     Returns:
#         array to be used as boundaries in scipy.optimize.curve_fit().
#     """
#     if groups2use == 'all':
#         groups2use = list(parameters.keys())
#
#     min = []
#     max = []
#     for group in groups2use:
#         min += parameters[group]['min']
#         max += parameters[group]['max']
#     return [min, max]


# pos fit
# def fit2Par(p_fitted, p_error, parameters, groups_used='all'):
#     """Build boundary matrix to be used in scipy.optimize.curve_fit().
#
#     Args:
#         parameters (dict): parameter dictionary created using load_xlsx().
#         groups_used (list, optional): list with group keys used in the fit.
#             The default is that all groups will be used.
#     """
#     if groups_used == 'all':
#         groups_used = list(parameters.keys())
#
#     # list associating a group with p_fitted index
#     groups_list = []
#     for group in groups_used:
#         groups_list += [group]*len(parameters[group]['guess'])
#
#     # saving back to parameters
#     for group in groups_used:
#         parameters[group]['fit']   = [p_fitted[j] for j in range(len(p_fitted)) if groups_list[j] == group]
#         parameters[group]['error'] = [p_error[j] for j in range(len(p_error)) if groups_list[j] == group]





# def buildFitted(parameters, groups2use='all'):
#     """Build fit matrix to be used as argument in eval(function_str()).
#
#     Args:
#         parameters (dict): parameter dictionary created using load_xlsx().
#         groups2use (list, optional): list with dict keys to use. The default is
#             that all groups will be used.
#
#     Returns:
#         array to be used as argument in eval(function_str()).
#     """
#     if groups2use == 'all':
#         groups2use = list(parameters.keys())
#
#     p_fitted = []
#     for group in groups2use:
#         p_fitted += parameters[group]['fit']
#     return p_fitted


# def connect2calc(file=None, port=8100):
#     """Connect with open Calc.
#
#     Open Calc using:
#         soffice --accept='socket,host=localhost,port=8100;urp;'
#
#     Args:
#         file (str or pathlib.Path, optional): file to connect. If None, it will
#             open a new Calc instance.
#         port (int, optional): port for connection.
#
#     Returns:
#         Calc object.
#     """
#     context = connect(Socket('localhost', port))
#
#     if file is None:
#         return Calc(context)
#     else:
#         file = Path(file)
#         return Calc(context, convert_path_to_url(str(file)))
#
#
# def closeConnection(calcObject):
#     """Close connection to calc.
#
#     Args:
#         calcObject (Calc object): Object created by connect2calc().
#     """
#     calcObject.close(True)
#     return
#
#
# def save_xlsx(calcObject, file):
    # """Save xlsx file.
    #
    # Args:
    #     calcObject (Calc object): Object created by connect2calc().
    # """
    # file = Path(file)
    #
    # # fix extension
    # if file.suffix == '':
    #     file = file.parent / (str(file.name) + '.xlsx')
    #
    # # save
    # url = convert_path_to_url(str(file))
    # calcObject.store_as_url(url, 'FilterName')















# calcObject = connect2calc('/home/galdino/Desktop/fit_one.xlsx')
# sheetObject, parameters = load_xlsx('Initial', calcObject)
# parameters[0]['fit'][0] = 'test'
# update_xlsx(parameters, sheetObject)
# group_color(sheetObject)
#
# a = sheetObject.get_cell_by_position(12, 2)
# a.getPropertyValue('CellBackColor')
# a.setPropertyValue('CellBackColor', 102155)
#
# a = sheetObject.get_cell_by_position(0, 0)
# a.getString()
# a.getData()[0][0]
# a.getFormula()
# a.getType().value
#
# a = sheetObject.get_cell_by_position(2, 1)
# a.getString()
# a.getData()[0][0]
# a.getFormula()
# a.getType().value
#
# sheetObject.set_rows_str(11, 2, [523, '2hh'])
# c = sheetObject.get_cell_by_position(11, 2)
# c.getString()
# c.getData()[0][0]
# c.getFormula()
# d = c.getType()
# d.value
#
# sheetObject.set_rows_formula(11, 2, ['=2+3', 'batata'])
# c = sheetObject.get_cell_by_position(11, 2)
# c.getString()
# c.getData()[0][0]
# c.getFormula()
# d = c.getType()
# d.value
#
# sheetObject.set_rows_value(11, 2, [523, 256])
# c = sheetObject.get_cell_by_position(11, 2)
# c.getString()
# c.getData()[0][0]
# c.getFormula()
# d = c.getType()
# d.value
#
# calcObject.close(True)
