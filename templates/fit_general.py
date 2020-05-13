#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Just a draft."""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import copy

import manipUtils.filemanip as fmanip
import manipUtils.figmanip as figmanip
from manipUtils.arraymanip import index
import manipUtils.arraymanip as manip
from manipUtils.commomModelFunctions import fwhmLorentz, square

from scipy.optimize import curve_fit

%matplotlib qt5
# p = figmanip.getFigurePosition()
p = (1280, 39)

# %% ========================= fileList =======================================
exp_data_folder = Path('../dataTidy/0_raw')
exp_clean_folder = Path('../dataTidy/1_clean')
fit_folder = Path('../dataTidy/2_fit')

# bulk import
fileList = list((exp_clean_folder).glob('*.dat'))
fileList.sort()
fileDict = dict()
for f in fileList:
    fileDict[int(f.name.split('_')[0])] = f  # 1st number

data = dict()
for i in fileDict:
    data[i] = fmanip.loadDataDict(fileDict[i])

# %% ============================== plot ======================================
fig = plt.figure()
figmanip.setFigurePosition(p)

i = 13
plt.plot(data[i]['rshift'], data[i]['intensity'], label=fileDict[i].name)
# for j in range(len(centers)):
#     plt.text(centers[j], max(data[i]['intensity'])/2, j)

plt.legend(loc='upper right')
plt.xlabel('raman shift (cm$^{-1}$)')
plt.ylabel('intensity')

# %% ============================== data definitions ==========================
i = 13
x_total = data[i]['rshift']
y_total = data[i]['intensity']

# lorentizian guess
amplitudes = np.array([0.5, 0, 0.2, 0.3, 0.3, 0.3,   0.2,  0.1, 0.1])
centers =    np.array([424, 449, 480, 552, 610, 656, 930, 1100, 480])
widths =     np.array([40,   .01,  50,  10, 10,  10,  100,   95, 7.8])
lorentz = {i: (lambda x, A, c, w: fwhmLorentz(x, A, c, w)) for i in range(len(centers)) if i<=7}
lorentz[8] = lambda x, A, c, w: square(x, A, c, w)
# %% p_final
p_final = {'amp': [float(x) for x in amplitudes], 'center': [float(x) for x in centers], 'width': [float(x) for x in widths], 'bkg': []}

# %% ============================== plot peak numbers =========================
fig = plt.figure()
figmanip.setFigurePosition(p)
p_final['center'][0]
plt.plot(data[i]['rshift'], data[i]['intensity'], label=fileDict[i].name)

for j in range(len(centers)):
    plt.text(centers[j], max(data[i]['intensity'])/2, j)

plt.legend(loc='upper right')
plt.xlabel('raman shift (cm$^{-1}$)')
plt.ylabel('intensity')

# %% ============================= bkg ========================================
# fit definitions
lorentz_idx = []
poly_idx = [0, ]
poly_guess = [0, ]
# range2Fit = [[100, 220], [749, 760]]
range2Fit = [[749, 780]]
x2fit, y2fit = manip.extractFromData(x_total, y_total, range2Fit)

# sigma
sigma = np.ones(len(x2fit))/(10**9)
# init = index(x2fit, 50)
# final = index(x2fit, 100)
# sigma[init:final] = 1/(10**10)

# function
var_text = ''
lorentz_text = ''
poly_text = ''
for j, idx in enumerate(lorentz_idx):
    var_temp = f'a{j}, b{j}, c{j}, '
    var_text += var_temp
    lorentz_text += f'lorentz[{idx}](x, {var_temp[:-2]}) + '
for j, idx in enumerate(poly_idx):
    var_temp = f'd{j}, '
    var_text += var_temp
    poly_text += f'd{j}*x**{idx} + '
# poly_text = 'np.heaviside(111-x, 0)*(d0 + d1*x) + np.heaviside(x-111, 0)*(d0 + d1*111)  '
var_text = var_text[:-2] + ':'
lorentz_text = lorentz_text
text = lorentz_text + poly_text
function1 = eval(f'lambda x, {var_text} {text[:-2]}')

# building p_guess matrix
p_guess = []
err_center = 2 # percentage
err_amp =  20 # percentage
err_width =  10 # percentage
for idx in lorentz_idx:
    # amplitude
    line = [p_final['amp'][idx]-err_amp*p_final['amp'][idx]/100, p_final['amp'][idx], p_final['amp'][idx]+err_amp*p_final['amp'][idx]/100]
    p_guess.append(line)

    # center
    line = [p_final['center'][idx]-err_center*p_final['center'][idx]/100, p_final['center'][idx], p_final['center'][idx]+err_center*p_final['center'][idx]/100]
    p_guess.append(line)

    # width
    line = [0, p_final['width'][idx], p_final['width'][idx]+err_width*p_final['width'][idx]/100]
    p_guess.append(line)
for j, idx in enumerate(poly_idx):
    line = [-np.inf, poly_guess[idx], np.inf]
    p_guess.append(line)
p_guess = np.array(p_guess)
p_bound = np.array([p_guess[:, 0], p_guess[:, 2]])

# Pre allocation
p_fitted = np.zeros(len(p_guess))
p_error = np.zeros(len(p_guess))

# fit
p_fitted, pcov = curve_fit(function1, x2fit, y2fit, p_guess[:, 1], sigma=sigma, bounds=p_bound)
p_error = np.sqrt(np.diag(pcov))  # One standard deviation errors on the parameters

# warn limits
for j, idx in enumerate(lorentz_idx):
    print(f'peak: {idx}')
    for feature, idx_fitted in [('amp', j*3), ('cen', j*3+1), ('width', j*3+2)]:
        if np.isclose(p_fitted[idx_fitted], p_bound[0][idx_fitted]):
            print(f'lower bound WARNING: {feature} = {p_fitted[idx_fitted]}')
            print(f'(Bound = {p_bound[0][idx_fitted]})')
        if np.isclose(p_fitted[idx_fitted], p_bound[1][idx_fitted]):
            print(f'higher bound WARNING: {feature} = {p_fitted[idx_fitted]}')
            print(f'(Bound = {p_bound[1][idx_fitted]})')
for j, idx_fitted in enumerate(poly_idx):
    print(f'bkg: {idx_fitted}')
    if np.isclose(p_fitted[idx_fitted], p_bound[0][idx_fitted]):
        print(f'lower bound WARNING: {feature} = {p_fitted[idx_fitted]}')
        print(f'(Bound = {p_bound[0][idx_fitted]})')
    if np.isclose(p_fitted[idx_fitted], p_bound[1][idx_fitted]):
        print(f'higher bound WARNING: {feature} = {p_fitted[idx_fitted]}')
        print(f'(Bound = {p_bound[1][idx_fitted]})')

# save
p_final['bkg'] = p_fitted

# %% =========================== plot fit =====================================
fig = plt.figure()
figmanip.setFigurePosition(p)

plt.plot(x_total, y_total, color='black')
plt.plot(x2fit, y2fit, color='orange')

x_fit = np.linspace(x_total[0], x_total[-1], 5000)
y_fit = function1(x_fit, *p_fitted)
plt.plot(x_fit, y_fit, color='red')

plt.xlabel('raman shift (cm$^{-1}$)')
plt.ylabel('intensity')

# %% ======================= plot subtraction =================================
fig = plt.figure()
figmanip.setFigurePosition(p)

y_fit = function1(x_total, *p_fitted)
plt.plot(x_total, y_total-y_fit, color='black')

plt.xlabel('raman shift (cm$^{-1}$)')
plt.ylabel('intensity')

# %% ============================== fit 1 =====================================
# fit definitions
lorentz_idx = [0, 1, 2, 3, 4, 5, 6, 7, 8]
lorentz_useFit = []
# range2Fit = [[388, 476], [488, 1100]]
range2Fit = [[388, 1100], ]
x2fit, y2fit = manip.extractFromData(x_total, y_total, range2Fit)

# sigma
sigma = np.ones(len(x2fit))/(10**9)
init = index(x2fit, 403)
final = index(x2fit, 430)
sigma[init:final] = 1/(10**10)
init = index(x2fit, 520)
final = index(x2fit, 547)
sigma[init:final] = 1/(10**10)

# function
var_text = ''
lorentz_text = ''
for j, idx in enumerate(lorentz_idx):
    var_temp = f'a{j}, b{j}, c{j}, '
    var_text += var_temp
    lorentz_text += f'lorentz[{idx}](x, {var_temp[:-2]}) + '
for j, idx in enumerate(poly_idx):
    var_temp = f'd{j}, '
    var_text += var_temp
#     poly_text += f'd{j}*x**{idx} + '
# poly_text = 'np.heaviside(111-x, 0)*(d0 + d1*x) + np.heaviside(x-111, 0)*(d0 + d1*111)  '
var_text = var_text[:-2] + ':'
lorentz_text = lorentz_text
text = lorentz_text + poly_text
text = text[:-2]
function1 = eval(f'lambda x, {var_text} {text}')

# building p_guess matrix
p_guess = []
err_center = 20
err_amp =  1
err_width = 100
for idx in lorentz_idx:
    if idx in lorentz_useFit:
        amp = copy.deepcopy(p_final['amp'][idx])
        cen = copy.deepcopy(p_final['center'][idx])
        width = copy.deepcopy(p_final['width'][idx])
    else:
        amp = copy.deepcopy(amplitudes[idx])
        cen = copy.deepcopy(centers[idx])
        width = copy.deepcopy(widths[idx])
    # amplitude
    if amplitudes[idx]-err_amp < 0:
        line = [0, amp, amp+err_amp]
    else:
        line = [amp-err_amp, amp, amp+err_amp]
    p_guess.append(line)

    # center
    line = [cen-err_center, cen, cen+err_center]
    p_guess.append(line)

    # width
    if width-err_width < 0:
        line = [0, width, width+err_width]
    else:
        line = [width-err_width, width, width+err_width]
    p_guess.append(line)
for j, idx in enumerate(poly_idx):
    line = [-np.inf, p_final['bkg'][idx], np.inf]
    p_guess.append(line)
p_guess = np.array(p_guess)
p_bound = np.array([p_guess[:, 0], p_guess[:, 2]])

# Pre allocation
p_fitted = np.zeros(len(p_guess))
p_error = np.zeros(len(p_guess))

# fit
p_fitted, pcov = curve_fit(function1, x2fit, y2fit, p_guess[:, 1], sigma=sigma, bounds=p_bound)
p_error = np.sqrt(np.diag(pcov))  # One standard deviation errors on the parameters

# warn limits
for j, idx in enumerate(lorentz_idx):
    print(f'peak: {idx}')
    for feature, idx_fitted in [('amp', j*3), ('cen', j*3+1), ('width', j*3+2)]:
        if np.isclose(p_fitted[idx_fitted], p_bound[0][idx_fitted]):
            print(f'lower bound WARNING: {feature} = {p_fitted[idx_fitted]}')
            print(f'(Bound = {p_bound[0][idx_fitted]})')
        if np.isclose(p_fitted[idx_fitted], p_bound[1][idx_fitted]):
            print(f'higher bound WARNING: {feature} = {p_fitted[idx_fitted]}')
            print(f'(Bound = {p_bound[1][idx_fitted]})')
for j, idx_fitted in enumerate(poly_idx):
    print(f'bkg: {idx_fitted}')
    if np.isclose(p_fitted[idx_fitted], p_bound[0][idx_fitted]):
        print(f'lower bound WARNING: {feature} = {p_fitted[idx_fitted]}')
        print(f'(Bound = {p_bound[0][idx_fitted]})')
    if np.isclose(p_fitted[idx_fitted], p_bound[1][idx_fitted]):
        print(f'higher bound WARNING: {feature} = {p_fitted[idx_fitted]}')
        print(f'(Bound = {p_bound[1][idx_fitted]})')

# save
for j, idx in enumerate(lorentz_idx):
    p_final['amp'][idx] = p_fitted[j*3]
    p_final['center'][idx] = p_fitted[j*3+1]
    p_final['width'][idx] = p_fitted[j*3+2]

# %% =========================== plot fit =====================================
fig = plt.figure()
figmanip.setFigurePosition(p)

plt.plot(x_total, y_total, color='black')
plt.plot(x2fit, y2fit, color='orange')

x_fit = np.linspace(x_total[0], x_total[-1], 5000)
y_fit = function1(x_fit, *p_fitted)
plt.plot(x_fit, y_fit, color='red')

# # function without square
# var_text = ''
# lorentz_text = ''
# for j, idx in enumerate(lorentz_idx):
#     if idx != 8:
#         var_temp = f'a{j}, b{j}, c{j}, '
#         var_text += var_temp
#         lorentz_text += f'lorentz[{idx}](x, {var_temp[:-2]}) + '
# for j, idx in enumerate(poly_idx):
#     var_temp = f'd{j}, '
#     var_text += var_temp
# #     poly_text += f'd{j}*x**{idx} + '
# # poly_text = 'np.heaviside(111-x, 0)*(d0 + d1*x) + np.heaviside(x-111, 0)*(d0 + d1*111)  '
# var_text = var_text[:-2] + ':'
# lorentz_text = lorentz_text
# text = lorentz_text + poly_text
# text = text[:-2]
# function2 = eval(f'lambda x, {var_text} {text}')
#
# u = 8*3
# plt.plot(x_fit, function2(x_fit, *(list(p_fitted[:u])+list(p_fitted[u+3:]))), linewidth=0.5, color='blue')

plt.xlabel('raman shift (cm$^{-1}$)')
plt.ylabel('intensity')

# %% ========================== fit final =====================================
# fit definitions
lorentz_idx =    [0, 1, 2, 3, 4, 5, 6, 7, 8]
lorentz_useFit = [0, 1, 2, 3, 4, 5, 6, 7, 8]
# range2Fit = [[388, 476], [488, 1100]]
range2Fit = [[388, 1100], ]
x2fit, y2fit = manip.extractFromData(x_total, y_total, range2Fit)

bounds_final = {'amp': dict(), 'center': dict(), 'width': dict()}
# p_final ======================
idx2 = 1
p_final['amp'][idx2]
p_final['center'][idx2]
p_final['width'][idx2]
p_final['amp'][idx2] = 0.0000001
# p_final['center'][idx2] = 450
# p_final['width'][idx2] = 10
bounds_final['amp'][idx2] = 0.0000001
# # bounds_final['center'][idx2] = 1
# # bounds_final['width'][idx2] = 4

idx2 = 2
p_final['amp'][idx2]
p_final['center'][idx2]
p_final['width'][idx2]
p_final['amp'][idx2] = 0.11
p_final['center'][idx2] = 475
p_final['width'][idx2] = 30
bounds_final['amp'][idx2] = 0.05
bounds_final['center'][idx2] = 4
bounds_final['width'][idx2] = 5
#
idx2 = 8
p_final['amp'][idx2]
p_final['center'][idx2]
p_final['width'][idx2]
p_final['amp'][idx2] = 0.28
p_final['center'][idx2] = 481
p_final['width'][idx2] = 7.8
bounds_final['amp'][idx2] = 0.02
bounds_final['center'][idx2] = 0.3
bounds_final['width'][idx2] = 0.1

# sigma
sigma = np.ones(len(x2fit))/(10**9)
init = index(x2fit, 419)
final = index(x2fit, 433)
sigma[init:final] = 1/(10**10)
init = index(x2fit, 441)
final = index(x2fit, 453)
sigma[init:final] = 1/(10**10)
init = index(x2fit, 536)
final = index(x2fit, 558)
sigma[init:final] = 1/(10**10)

# function
var_text = ''
lorentz_text = ''
for j, idx in enumerate(lorentz_idx):
    var_temp = f'a{j}, b{j}, c{j}, '
    var_text += var_temp
    lorentz_text += f'lorentz[{idx}](x, {var_temp[:-2]}) + '
for j, idx in enumerate(poly_idx):
    var_temp = f'd{j}, '
    var_text += var_temp
#     poly_text += f'd{j}*x**{idx} + '
# poly_text = 'np.heaviside(111-x, 0)*(d0 + d1*x) + np.heaviside(x-111, 0)*(d0 + d1*111)  '
var_text = var_text[:-2] + ':'
lorentz_text = lorentz_text
text = lorentz_text + poly_text
text = text[:-2]
function1 = eval(f'lambda x, {var_text} {text}')

# building p_guess matrix
p_guess = []
err_amp =  2
err_center = 4
err_width = 10
for idx in lorentz_idx:
    if idx in lorentz_useFit:
        amp = copy.deepcopy(p_final['amp'][idx])
        cen = copy.deepcopy(p_final['center'][idx])
        width = copy.deepcopy(p_final['width'][idx])
    else:
        amp = copy.deepcopy(amplitudes[idx])
        cen = copy.deepcopy(centers[idx])
        width = copy.deepcopy(widths[idx])
    # amplitude bounds
    if idx in bounds_final['amp']:
        line = [amp-bounds_final['amp'][idx], amp, amp+bounds_final['amp'][idx]]
    else:
        if amp-err_amp < 0:
            line = [0, amp, amp+err_amp]
        else:
            line = [amp-err_amp, amp, amp+err_amp]
    p_guess.append(line)

    # center bounds
    if idx in bounds_final['center']:
        line = [cen-bounds_final['center'][idx], cen, cen+bounds_final['center'][idx]]
    else:
        line = [cen-err_center, cen, cen+err_center]
    p_guess.append(line)

    # width bounds
    if idx in bounds_final['width']:
        line = [width-bounds_final['width'][idx], width, width+bounds_final['width'][idx]]
    else:
        if width-err_width < 0:
            line = [0, width, width+err_width]
        else:
            line = [width-err_width, width, width+err_width]
    p_guess.append(line)
for j, idx in enumerate(poly_idx):
    line = [-np.inf, p_final['bkg'][idx], np.inf]
    p_guess.append(line)
p_guess = np.array(p_guess)
p_bound = np.array([p_guess[:, 0], p_guess[:, 2]])

# Pre allocation
p_fitted = np.zeros(len(p_guess))
p_error = np.zeros(len(p_guess))

# fit
p_fitted, pcov = curve_fit(function1, x2fit, y2fit, p_guess[:, 1], sigma=sigma, bounds=p_bound)
p_error = np.sqrt(np.diag(pcov))  # One standard deviation errors on the parameters

# warn limits
for j, idx in enumerate(lorentz_idx):
    print(f'peak: {idx}')
    for feature, idx_fitted in [('amp', j*3), ('cen', j*3+1), ('width', j*3+2)]:
        if np.isclose(p_fitted[idx_fitted], p_bound[0][idx_fitted]):
            print(f'lower bound WARNING: {feature} = {p_fitted[idx_fitted]}')
            print(f'(Bound = {p_bound[0][idx_fitted]})')
        if np.isclose(p_fitted[idx_fitted], p_bound[1][idx_fitted]):
            print(f'higher bound WARNING: {feature} = {p_fitted[idx_fitted]}')
            print(f'(Bound = {p_bound[1][idx_fitted]})')
for j, idx_fitted in enumerate(poly_idx):
    print(f'bkg: {idx_fitted}')
    if np.isclose(p_fitted[idx_fitted], p_bound[0][idx_fitted]):
        print(f'lower bound WARNING: {feature} = {p_fitted[idx_fitted]}')
        print(f'(Bound = {p_bound[0][idx_fitted]})')
    if np.isclose(p_fitted[idx_fitted], p_bound[1][idx_fitted]):
        print(f'higher bound WARNING: {feature} = {p_fitted[idx_fitted]}')
        print(f'(Bound = {p_bound[1][idx_fitted]})')

# save
for j, idx in enumerate(lorentz_idx):
    p_final['amp'][idx] = copy.copy(p_fitted[j*3])
    p_final['center'][idx] = copy.copy(p_fitted[j*3+1])
    p_final['width'][idx] = copy.copy(p_fitted[j*3+2])
for j in range(len(p_final['bkg'])):
    p_final['bkg'][j] = copy.copy(p_fitted[-len(p_final['bkg'])+j])


# %% =========================== plot fit =====================================
fig = plt.figure()
figmanip.setFigurePosition(p)
init =  360
final = 1100

idx = (index(x_total, init), index(x_total, final))
plt.plot(x_total[idx[0]:idx[1]], y_total[idx[0]:idx[1]], color='black')
idx = (index(x2fit, init), index(x_total, final))
plt.plot(x2fit[idx[0]:idx[1]], y2fit[idx[0]:idx[1]], color='orange')

x_fit = np.linspace(x_total[0], x_total[-1], 5000)
y_fit = function1(x_fit, *p_fitted)
idx = (index(x_fit, init), index(x_fit, final))
plt.plot(x_fit[idx[0]:idx[1]], y_fit[idx[0]:idx[1]], color='red')

# # function without square
var_text = ''
lorentz_text = ''
for j, idx in enumerate(lorentz_idx):
    if idx != 8:
        var_temp = f'a{j}, b{j}, c{j}, '
        var_text += var_temp
        lorentz_text += f'lorentz[{idx}](x, {var_temp[:-2]}) + '
for j, idx in enumerate(poly_idx):
    var_temp = f'd{j}, '
    var_text += var_temp
#     poly_text += f'd{j}*x**{idx} + '
# poly_text = 'np.heaviside(111-x, 0)*(d0 + d1*x) + np.heaviside(x-111, 0)*(d0 + d1*111)  '
var_text = var_text[:-2] + ':'
lorentz_text = lorentz_text
text = lorentz_text + poly_text
text = text[:-2]
function2 = eval(f'lambda x, {var_text} {text}')

u = 8*3
idx = (index(x_fit, init), index(x_fit, final))
plt.plot(x_fit[idx[0]:idx[1]], function2(x_fit[idx[0]:idx[1]], *(list(p_fitted[:u])+list(p_fitted[u+3:]))), linewidth=0.5, color='blue')


plt.xlabel('raman shift (cm$^{-1}$)')
plt.ylabel('intensity')

# %% ======================== save final parameters ===========================
fmanip.saveDict(p_final, fit_folder/(fileDict[i].name[:-4] + '.par'), checkOverwrite=False)

# %% =========================== save curve ===================================
peaks = dict()
peaks['x'] = copy.deepcopy(x_total)
peaks['signal'] = y_total
peaks['peaks'] = np.zeros(len(y_total))
for idx in range(len(p_final['amp'])):
    peaks[idx] = lorentz[idx](x_total, p_final['amp'][idx], p_final['center'][idx], p_final['width'][idx])
    peaks['peaks'] += lorentz[idx](x_total, p_final['amp'][idx], p_final['center'][idx], p_final['width'][idx])

# bkg
bkg_final = poly_text[:-2].replace('x', 'x_total')
for j, idx in enumerate(poly_idx):
    d = 'd' + str(j)
    bkg_final = bkg_final.replace(d, str(p_final['bkg'][j]))
peaks['bkg'] = eval(bkg_final)

fmanip.saveDataDict(peaks, fit_folder/(fileDict[i].name[:-4] + '.curve'), checkOverwrite=False)

# %% ============================ plot final fit ==============================
# bkg
fig = plt.figure()
figmanip.setFigurePosition(p)

plt.plot(peaks['x'], peaks['signal'], color='black')
plt.plot(peaks['x'], peaks['bkg'], color='red')

plt.title(fileDict[i].name + ': background fit')
plt.xlabel('raman shift (cm$^{-1}$)')
plt.ylabel('intensity')

plt.savefig(fit_folder/(fileDict[i].name[:-4] + '.bkg.pdf'))

# peaks
fig = plt.figure()
figmanip.setFigurePosition(p)

plt.plot(peaks['x'], peaks['signal'] - peaks['bkg'], color='black')
plt.plot(peaks['x'], peaks['peaks'], color='red')

for idx in range(len(p_final['amp'])):
    plt.plot(peaks['x'], peaks[idx], linewidth=.5, color='red')

plt.title(fileDict[i].name + ': peak fit')
plt.xlabel('raman shift (cm$^{-1}$)')
plt.ylabel('intensity')

plt.savefig(fit_folder/(fileDict[i].name[:-4] + '.peaks.pdf'))
# figmanip.saveFigsInPDF(fit_folder, fileDict[i].name)
