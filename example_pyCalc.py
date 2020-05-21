
# standard libraries
from copy import copy, deepcopy
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# backpack
import sys
sys.path.append('/home/galdino/github/py-backpack')
import backpack.filemanip as fmanip
import backpack.figmanip as figmanip
import backpack.arraymanip as amanip

sys.path.append('/home/galdino/github/pyCalc-wrapper')
import pyCalc as calc
import importlib
importlib.reload(calc)

%matplotlib qt5

# %% ==================================

# opens a new Calc instane and connects with it
calcObject = calc.connect2Calc()

# adds one sheet ('Sheet2') at position 1
calcObject.insert_sheets_new_by_name('Sheet2', 1)

# adds multiple sheets ('Sheet3' and 'Sheet4) at position 2
calcObject.insert_multisheets_new_by_name(['Sheet3', 'Sheet4'], 2)

# Get number of sheets
print(calcObject.get_sheets_count())

# Get sheet names
print(calc.get_sheets_name(calcObject))

# Remove sheets
calcObject.remove_sheets_by_name('Sheet3')

# get sheet data
sheet1 = calcObject.get_sheet_by_name('Sheet1')
sheet2 = calcObject.get_sheet_by_index(1)

# save Calc
calc.saveCalc(calcObject)

# get the location where Calc is saved
calcObject.Location

# Close Calc
calc.closeCalc(calcObject)

# kill libreoffice processes
calc.kill_libreoffice_processes()

# %% =====================================================
calcObject = calc.connect2Calc('./Untitled.ods')
sheet1 = calcObject.get_sheet_by_name('Sheet1')
sheet2copyFrom = calcObject.get_sheet_by_name('Sheet1')
sheetObject = calcObject.get_sheet_by_name('Sheet1')

calcObject2 = calc.connect2Calc('./Untitled 1.ods')
sheet1_file2 = calcObject2.get_sheet_by_name('Sheet1')
sheet2pasteAt = calcObject2.get_sheet_by_name('Sheet1')

# Sheet name
sheet2copyFrom.Name

# copy cell
row = 0
col = 1
calc.copyCell(sheet2copyFrom, sheet2pasteAt, row=row, col=col, pasteAs='formula', Font=2, ConditionalFormat=0, Border=0)

# resize cols and rows

# set and get cell value
calc.get_cell_value(sheet1_file2, row=0, col=1)
calc.set_cell_value(sheet1_file2, row=0, col=1, value='rrrrr')

# set and get value of cell ranges
xinit = 0
xfinal = 10
yinit = 1
yfinal = 10
calc.get_cells_value(sheet1, xinit, yinit, xfinal, yfinal, type='data')

data = [[1, 2, 500],
        [2, 4, '=A1'],
        [3, 6, 10]]
calc.set_cells_value(sheet1_file2, xinit=0, yinit=0, data=data, type='formula')

# copy sheet ranges
