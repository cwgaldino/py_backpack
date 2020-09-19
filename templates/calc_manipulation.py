#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Example code for manipulating libreoffice Calc."""

# standard imports
import numpy as np
from pathlib import Path

import sys
sys.path.append('/home/galdino/github/py-backpack')
import backpack.libremanip
import importlib
importlib.reload(backpack.libremanip)
from backpack.libremanip import soffice

# %%
try:
    libreoffice.terminate(ask=False)
except: pass
libreoffice = soffice(norestore=True)
calcObject = libreoffice.calc()
calcObject.insert_sheets(name='heyy', position=1)
calcObject.insert_sheets(name=['Sheet2', 'Sheet5'], position=None)
calcObject.insert_sheets(name=['Sheet3', 'Sheet4'], position=4)

calcObject.get_sheets_count()
calcObject.get_sheets_name()

calcObject.remove_sheets_by_name(['heyy', 'Sheet5'])
calcObject.remove_sheets_by_position(4) # cannot remove more than one each time!
# calcObject.remove_sheets([1, 'Sheet1']) # will raise an ERROR!
calcObject.remove_sheets('Sheet3')

sheetObject = calcObject.get_sheets_by_name('Sheet1')
sheetObject, sheetObject2 = calcObject.get_sheets_by_name(['Sheet1', 'Sheet2'])
sheetObject, sheetObject2 = calcObject.get_sheets_by_position([1, 2])
sheetObject, sheetObject2 = calcObject.get_sheets([1, 'Sheet2'])

sheetObject.set_col_width(2500, 1)
sheetObject.set_col_width(2500, 'c')
sheetObject.set_col_width(2000, [2, 'D', 'e'])
print(sheetObject.get_col_width('b'))
print(sheetObject.get_col_width([2, 'D', 'z']))

sheetObject.set_row_height(800, 1)
sheetObject.set_row_height(800, [2, 3])
print(sheetObject.get_row_height(1))
print(sheetObject.get_row_height([1, 2, 6]))

sheetObject.set_row_values(['format', 'date', 'time', 'text', 'number', 'number as string', 'formula'], row=1)
sheetObject.set_col_values(['formula', 'string', 'number'], col=1, row_start=2)
sheetObject.set_cell_value(row=2, col=2, value='01/12/2016', format='formula')
sheetObject.set_cell_value(row=3, col=2, value='01/12/2016', format='string')
sheetObject.set_cell_value(row=4, col=2, value='01/12/2016', format='number')

sheetObject.set_cell_value(row=2, col=3, value='10:56', format='formula')
sheetObject.set_cell_value(row=3, col=3, value='10:56', format='string')
sheetObject.set_cell_value(row=4, col=3, value='10:56', format='number')

sheetObject.set_cell_value(row=2, col=4, value='heyy', format='formula')
sheetObject.set_cell_value(row=3, col=4, value='heyy', format='string')
# sheetObject.set_cell_value(row=4, col=4, value='heyy', format='number')
sheetObject.set_cell_value(row=4, col=4, value='ERROR', format='string')

sheetObject.set_cell_value(row=2, col=5, value=10.53, format='formula')
sheetObject.set_cell_value(row=3, col=5, value=10.53, format='string')
sheetObject.set_cell_value(row=4, col=5, value=10.53, format='number')

sheetObject.set_cell_value(row=2, col=6, value='10.53', format='formula')
sheetObject.set_cell_value(row=3, col=6, value='10.53', format='string')
sheetObject.set_cell_value(row=4, col=6, value='10.53', format='number')

sheetObject.set_cell_value(row=2, col=7, value='=F2*2', format='formula')
sheetObject.set_cell_value(row=3, col=7, value='=F2*2', format='string')
# sheetObject.set_cell_value(row=4, col=7, value='=F2*2', format='number')
sheetObject.set_cell_value(row=4, col=7, value='ERROR', format='string')

get_as_formula = sheetObject.get_cells_value(2, 1, 4, format='formula')
get_as_string = sheetObject.get_cells_value(2, 1, 4, format='string')
get_as_number = sheetObject.get_cells_value(2, 1, 4, format='number')

print(get_as_formula)
print(get_as_string)
print(get_as_number)

# set as formula unless date and time or if formulas must by writen as string (formula is nor evaluates)
# get as string

# set as string if date or time (numbers saved as string will be read as strings no matter what)
# get as string

# get as formula only if you need the non-evaluated string of a formula (number are read as strings)

# set and get as number only if other formats yield errors (format=formula will typically work fine for numbers)

# fake data
x = np.array([0,1,2,3,4,5,6,7,8,9,10])
y = x**2
y2 = x**3
y3 = x**4
data = np.zeros((len(x), 4))
data[:, 0] = x
data[:, 1] = y
data[:, 2] = y2
data[:, 3] = y3

# sending to sheet
sheetObject.set_row_values(['x', 'x**2', 'x**3', 'x**4'], row=6)

sheetObject.set_col_values(data[:, 0], 1, 7)
sheetObject.set_col_values(data[:, 1], 'b', 7)
sheetObject.set_cells_value(data[:, 2:], row_start=7, col_start=3)
dataFromSheet = sheetObject.get_cells_value(row_start=7, col_stop=4)
print(dataFromSheet)
dataFromSheet = np.array(dataFromSheet)
print(dataFromSheet)

# it also works with lists
data_aslist = data.tolist()
sheetObject.set_row_values(data=['x', 'x**2', 'x**3', 'x**4'], row=6, col_start='F')
sheetObject.set_cells_value(data=data_aslist, row_start=7, col_start='F')

# cell properties
sheetObject.list_cell_properties()

# some properties can easily
color = int('0xffff00', 16)  # yellow
sheetObject.set_cell_property(property='CellBackColor', value=color, row=1, col=1)
colorObject, _ = sheetObject.get_cell_property('CellBackColor', 1, 1)
print(colorObject)

sheetObject.list_cell_properties(filter='border')

# some properties are tricky to change programatically
borderObject, subparameters = sheetObject.get_cell_property('BottomBorder', 2, 2)
# borderObject is a complex object
print(subparameters)
print(borderObject.Color)
print(borderObject.LineStyle)
print(borderObject.LineWidth)
borderObject.Color = int('0x301dde', 16)
borderObject.LineStyle = 2
borderObject.LineWidth = 100
sheetObject.set_cell_property(property='BottomBorder', value=borderObject, row=2, col=2)

# set many cells at once
sheetObject.set_cells_properties(property='CellBackColor', value=color, row_start=6, col_start=1, row_stop=6, col_stop='I')
colorObject, _ = sheetObject.get_cells_properties(property='CellBackColor', row_start=6, col_start=1, row_stop=6, col_stop='I')

# copy cell formatting
p_obj = sheetObject.get_cell_formating(row=1, col=1, extra=None)
sheetObject.set_cell_formating(p_obj, row=3, col=4, extra=None)

# copy to another sheet
sheet2, = calcObject.get_sheets('Sheet2')
p_obj = sheetObject.get_cell_formating(row=1, col=1, extra=None)
sheet2.set_cell_formating(p_obj, row=3, col=4, extra=None)
p_obj = sheet2.get_cell_formating(row=3, col=4, extra=None)
sheet2.set_cell_formating(p_obj, row=1, col=2, extra=None)

# copy whole formatting
object_formating = sheetObject.get_cells_formatting(row_start=1, col_start=1, extra=None)
sheet2.set_cells_formatting(object_formating, row_start=1, col_start=1, extra=None)
sheet2.set_cell_formating(object_formating[0][0], row=1, col=1, extra=None)

# copy values to another sheet
data = sheetObject.get_cells_value()
sheet2.set_cells_value(data)

# copy cell size
cols = np.arange(1, sheetObject.get_last_col()+1)
col_widths = sheetObject.get_col_width(cols)
for idx, _ in enumerate(cols):
    sheet2.set_col_width(col_widths[idx], col=cols[idx])
rows = np.arange(1, sheetObject.get_last_row()+1)
row_height = sheetObject.get_row_height(rows)
for idx, _ in enumerate(rows):
    sheet2.set_row_height(row_height[idx], row=rows[idx])

# save
calcObject.save('example')

# saving again does not require filename
calcObject.save()
