#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Support functions for connecting with libreoffice Calc."""

# standard imports
import numpy as np
from pathlib import Path
import os
import inspect
import psutil
import signal
import subprocess
import time
import warnings

# import uno
from unotools import Socket, connect
from unotools.component.calc import Calc
from unotools.unohelper import convert_path_to_url

# calcObject (xlsx)
#ok
def connect(file=None, port=8100, counter_max=5000):
    """Open libreoffice and enable conection with Calc.

    Args:
        file (str or pathlib.Path, optional): Filepath. If None, a
            new Calc instance will be opened.
        port (int, optional): port for connection.
        counter_max (int, optional): Max number of tentatives to establish a
            connection.

    Returns:
        Calc object.

    Examples:

        Open new instance of Calc:

        >>> calcObject = calc.connect()

        Adds one sheet ('Sheet2') at position 1:

        >>> calcObject.insert_sheets_new_by_name('Sheet2', 1)

        Add multiple sheets ('Sheet3' and 'Sheet4) at position 2:

        >>> calcObject.insert_multisheets_new_by_name(['Sheet3', 'Sheet4'], 2)

        >>> # Get number of sheets
        >>> print(calcObject.get_sheets_count())
        4
        >>> # Remove sheets
        >>> calcObject.remove_sheets_by_name('Sheet3')
        >>> # get sheet data
        >>> sheet1 = calcObject.get_sheet_by_name('Sheet1')
        >>> sheet2 = calcObject.get_sheet_by_index(0)

    """
    # open libreoffice
    libreoffice = subprocess.Popen([f"soffice --nodefault --accept='socket,host=localhost,port={port};urp;'"], shell=True, close_fds=True)

    # connect to libreoffice
    connected = False
    counter = 0
    while connected == False:
        time.sleep(0.5)
        try:
            context = connect(Socket('localhost', f'{port}'))
            connected = True
        except:
            counter += 1
            if counter == counter_max:
                raise ConnectionError('Cannot establish connection, maybe try increasing counter_max value.')
            pass

    if file is None:
        return Calc(context)
    else:
        file = Path(file)
        return Calc(context, convert_path_to_url(str(file)))

#ok
def closeCalc(calcObject):
    """Close Calc.

    Args:
        calcObject (Calc object): Object created by connect2calc().
    """
    calcObject.close(True)
    return

#ok


#ok
def saveCalc(calcObject, filepath=None):
    """Save xlsx file.

    Note:
        If `filepath` have no suffix, it adds '.ods' at the end of filepath.

    Args:
        calcObject (Calc object): Object created by :py:func:`calcmanip.connect2Calc`.
        filepath (string or pathlib.Path, optional): filepath to save file.
    """
    if filepath is None:
        if calcObject.Location == '':
            filepath = Path('./Untitled.ods')
            warnings.warn('Saving at ./Untitled.ods')
        else:
            filepath = Path(calcObject.Location)
    else:
        filepath = Path(filepath)

    # fix extension
    if filepath.suffix == '':
        filepath = filepath.parent / (str(filepath.name) + '.ods')

    # save
    url = convert_path_to_url(str(filepath))
    calcObject.store_as_url(url, 'FilterName')



# calcObject manipulation
#ok
def get_sheets_name(calcObject):
    """Get sheets names in a tuple."""
    return calcObject.Sheets.ElementNames




def set_col_width(sheetObject, col, width):

    colsObject = sheetObject.getColumns()
    colsObject[col].setPropertyValue('Width', width)


def get_col_width(sheetObject, col):

    colsObject = sheetObject.getColumns()
    return colsObject[col].Width


def set_row_height(sheetObject, row, height):

    rowsObject = sheetObject.getRows()
    rowsObject[row].setPropertyValue('Height', height)


def get_row_height(sheetObject, row):

    colsObject = sheetObject.getRows()
    return colsObject[row].Height


def float_hook(value):
    """Substitute string for float.
    """
    return float(value)

def get_cell_value(sheetObject, row, col, type='formula', object_hook=None):
    """
    type='data', 'formula'
    """
    if type == 'formula':
        value = sheetObject.get_cell_by_position(col, row).getFormula()
    elif type == 'data':
        value = sheetObject.get_cell_by_position(col, row).getString()
    else:
        warnings.warn(f"type = {type} is not a valid option. Using type = 'data'.")
        value = sheetObject.get_cell_by_position(col, row).getString()

    if object_hook is not None:
        return object_hook(value)
    else:
        return value



def set_cell_value(sheetObject, row, col, value, type='formula'):
    """
    type='data', 'formula'
    """
    if type == 'formula':
        sheetObject.get_cell_by_position(col, row).setFormula(value)
    elif type == 'data':
        sheetObject.get_cell_by_position(col, row).setString(value)
    else:
        warnings.warn(f"type = {type} is not a valid option. Using type = 'data'.")
        sheetObject.get_cell_by_position(col, row).setString(value)


def copy_cell(sheet2copyFrom, sheet2pasteAt, row, col, type='formula',
              Font=1, ConditionalFormat=False, Border=False, resize=None,
              row2pasteAt=None, col2pasteAt=None, additional=None):
    """
    type='string', 'formula', None

    resize = None, 'r', 'c', 'rc' or 'cr'

    0 = ['FormatID', 'CharWeight', 'CharHeight', 'CharColor', 'CellBackColor'],
    1 = ['IsTextWrapped', 'HoriJustify', 'HoriJustifyMethod',  'VertJustify', 'VertJustifyMethod'],
    2 = [ 'CharFontName',  'CharFont', 'CellStyle'],
    3 = ['CharUnderline', 'CharCrossedOut', 'CharEmphasis', 'CharEscapement', 'CharContoured'],
    4 = ['CharPosture',  'CharPostureComplex',  'CharRelief',  'CharShadowed',  'CharStrikeout',   'CharUnderlineColor',  'CharUnderlineHasColor',]


    This function do not copy ALL the properties of a cell, because it is very
    time consuming. Instead, it copys only the most used properties. If you
    need to include additional properties, have a look at
    ``sheetObject.get_cell_by_position(0, 0)._show_attributes()`` and find the
    desired propertie. Then, include it in ``additional``.
    """
    Font = int(Font)
    if Font > 5:
        Font = 5
    elif Font <0:
        Font = 0

    if row2pasteAt is None:
        row2pasteAt = row
    if col2pasteAt is None:
        col2pasteAt = col

    # cell value
    if type is not None:
        set_cell_value(sheet2pasteAt, row=row2pasteAt, col=col2pasteAt, value=get_cell_value(sheet2copyFrom, row, col, type=type), type=type)

    # font name
    font_property_list_parsed = [['FormatID', 'CharWeight', 'CharHeight', 'CharColor', 'CellBackColor'],
                                 ['IsTextWrapped', 'HoriJustify', 'HoriJustifyMethod',  'VertJustify', 'VertJustifyMethod'],
                                 [ 'CharFontName',  'CharFont', 'CellStyle'],
                                 ['CharUnderline', 'CharCrossedOut', 'CharEmphasis', 'CharEscapement', 'CharContoured'],
                                 ['CharPosture',  'CharPostureComplex',  'CharRelief',  'CharShadowed',  'CharStrikeout',   'CharUnderlineColor',  'CharUnderlineHasColor',]
                                ]

    font_property_list = [item for sublist in font_property_list_parsed[0:Font] for item in sublist]
    for property in font_property_list:
        sheet2pasteAt.get_cell_by_position(col2pasteAt, row2pasteAt).setPropertyValue(property, getattr(sheet2copyFrom.get_cell_by_position(col, row), property))

    # conditional formating
    if ConditionalFormat:
        font_property_list = ['ConditionalFormat']
        for property in font_property_list:
            sheet2pasteAt.get_cell_by_position(col2pasteAt, row2pasteAt).setPropertyValue(property, getattr(sheet2copyFrom.get_cell_by_position(col, row), property))

    # border
    if Border:
        border_property_list = ['TableBorder', 'TableBorder2']#, 'LeftBorder', 'LeftBorder2', 'RightBorder', 'RightBorder2', 'TopBorder', 'TopBorder2', 'BottomBorder', 'BottomBorder2']
        for property in border_property_list:
            sheet2pasteAt.get_cell_by_position(col2pasteAt, row2pasteAt).setPropertyValue(property, getattr(sheet2copyFrom.get_cell_by_position(col, row), property))

    # additional
    if additional is not None:
        for property in additional:
            sheet2pasteAt.get_cell_by_position(col2pasteAt, row2pasteAt).setPropertyValue(property, getattr(sheet2copyFrom.get_cell_by_position(col, row), property))

    # col and row width
    if resize is not None:
        if resize == 'r':
            set_row_height(sheet2pasteAt, row2pasteAt, get_row_height(sheet2copyFrom, row))
        elif resize == 'c':
            set_col_width(sheet2pasteAt, col2pasteAt, get_col_width(sheet2copyFrom, col))
        elif resize == 'cr' or resize == 'rc':
            set_row_height(sheet2pasteAt, row2pasteAt, get_row_height(sheet2copyFrom, row))
            set_col_width(sheet2pasteAt, col2pasteAt, get_col_width(sheet2copyFrom, col))
        else:
            warnings.warn(f"resize = {resize} is not a valid option. Using resize = None.")


# ok
def get_cells_value(sheetObject, row_init, col_init, row_final=None, col_final=None, type='data'):
    """
    type= formula or data.
    """
    if row_final is None:
        row_final = len(sheetObject.getRowDescriptions()) + sheetObject.queryVisibleCells().Count -1
    if col_final is None:
        col_final = len(sheetObject.getColumnDescriptions()) + sheetObject.queryVisibleCells().Count -1

    sheet_data = sheetObject.get_cell_range_by_position(col_init, row_init, col_final, row_final)
    if type == 'formula':
        sheet_data = list(sheet_data.getFormulaArray())
    elif type == 'data':
        sheet_data = list(sheet_data.getDataArray())
    else:
        warnings.warn(f"type = {type} is not a valid option. Using type = 'data'.")
        sheet_data = list(sheet_data.getDataArray())

    # transform in list
    for row_number, row_data in enumerate(sheet_data):
        sheet_data[row_number] = list(row_data)

        # if one column or one row data, transform in vector
        if col_init == col_final:
            sheet_data[row_number] = row_data[0]
        # if one column or one row data, transform in vector
        if col_init == col_final:
            sheet_data[row_number] = row_data[0]
    if row_init == row_final:
        sheet_data = sheet_data[0]

    return sheet_data


def set_cells_value(sheetObject, row_init, col_init, data, type='formula'):
    """
    type=formula or data or string

    formula set formulas, but also set numbers fine. Dates and time not so much because it changes the formating (if setting date and time iwth formula you might wanna format the
    cell like date or time using copy_cells to copy formatting).

    string (data) works fine with date, time and number, but formulas are set as string. Therefore, formulas do not work.

    value (data_number) works fine for numbers ONLY.

    """

    if type == 'formula':
        for row, row_data in enumerate(data):
            sheetObject.set_columns_formula(row_init, row+col_init, row_data)
    elif type == 'data':
        for row, row_data in enumerate(data):
            sheetObject.set_columns_str(row_init, row+col_init, row_data)
    elif type == 'data_number':
        for row, row_data in enumerate(data):
            sheetObject.set_columns_value(row_init, row+col_init, row_data)
    else:
        warnings.warn(f"type = {type} is not a valid option. Using type = 'data'.")
        for row, row_data in enumerate(data):
            sheetObject.set_columns_str(row_init, row+col_init, row_data)


def copy_cells(sheet2copyFrom, sheet2pasteAt, row_init, col_init, row_final, col_final, type='formula',
              Font=0, ConditionalFormat=False, Border=False, resize=None,
              row2pasteAt=None, col2pasteAt=None, additional=None):
    """
        type='data', 'formula', 'none'
    """

    if row2pasteAt is None:
        row2pasteAt = row_init
    if col2pasteAt is None:
        col2pasteAt = col_init

    if Font>0 or ConditionalFormat is not False or Border is not False or additional is not False:
        for row_relative, row in enumerate(range(row_init, row_final)):
            for col_relative, col in enumerate(range(col_init, col_final)):
                copy_cell(sheet2copyFrom, sheet2pasteAt, row, col, type=type,
                          Font=Font, ConditionalFormat=ConditionalFormat, Border=Border, resize=None,
                          row2pasteAt=row2pasteAt+row_relative, col2pasteAt=col2pasteAt+col_relative, additional=additional)
    else:
        data = get_cells_value(sheet2copyFrom, row_init, col_init, row_final, col_final, type=type)
        set_cells_value(row2pasteAt, row2pasteAt, col2pasteAt, data, type=type)

    # col and row width
    if resize is not None:
        if resize == 'r' or resize == 'c' or resize == 'cr' or resize == 'rc':
            if 'r' in resize:
                for row_relative, row in enumerate(range(row_init, row_final)):
                    set_row_height(sheet2pasteAt, row2pasteAt+row_relative, get_row_height(sheet2copyFrom, row))
            if 'c' in resize:
                for col_relative, col in enumerate(range(col_init, col_final)):
                    set_col_width(sheet2pasteAt, col2pasteAt+col_relative, get_col_width(sheet2copyFrom, col))
        else:
            warnings.warn(f"resize = {resize} is not a valid option ('r', 'c', 'rc', 'None'). Using resize = None.")


def copy_sheet(sheet2copy, sheet2paste, type='formula',
              Font=0, ConditionalFormat=False, Border=False, resize=None, additional=None):
    """ copy_sheet.
    """
    last_col = len(sheet2copy.getColumnDescriptions()) + sheet2copy.queryVisibleCells().Count -1
    last_row = len(sheet2copy.getRowDescriptions())  + sheet2copy.queryVisibleCells().Count -1

    copy_cells(sheet2copy, sheet2paste, 0, 0, last_row, last_col, type=type, Font=Font, ConditionalFormat=ConditionalFormat, Border=Border, resize=resize, additional=None)


def get_cell_value_from_sheets(sheetObject_list, row, col, type='data'):
    """
    """
    values = []
    for sheetObject in sheetObject_list:
        values.append(get_cell_value(sheetObject, row, col, type))
    return values
