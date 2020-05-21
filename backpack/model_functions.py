#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""Common mathematical functions and distributions."""

import numpy as np
from scipy.special import erf

def Gauss(x, A, c, w):
    r"""Gaussian distribution.

    .. math:: y(x) = A e^{-\frac{(x-c)^2}{2 w^2}}

    :param x: x value
    :param A: Amplitude
    :param c: Center
    :param w: Sigma (standard deviation)
    :return: :math:`y(x)`
    """
    return A*np.exp(-(x-c)**2/(2*w**2))


def fwhmGauss(x, A, c, w):
    r"""Gaussian distribution.

    .. math:: y(x) = A e^{-\frac{4 \ln(2) (x-c)^2}{w^2}}

    :param x: x value
    :param A: Amplitude
    :param c: Center
    :param w: FWHM
    :return: :math:`y(x)`
    """
    return A*np.exp((-4*np.log(2)*((x-c)**2))/(w**2))


def fwhmAreaGauss(x, A, c, w):
    r"""Gaussian distribution.

    .. math:: y(x) = \frac{A}{w \sqrt{\frac{\pi}{4 \ln(2)}}}  e^{-\frac{4 \ln(2) (x-c)^2}{w^2}}

    :param x: x value
    :param A: Area under the curve
    :param c: Center
    :param w: FWHM
    :return: :math:`y(x)`
    """
    return (A/(w*np.sqrt(np.pi/4*np.log(2))))*np.exp((-4*np.log(2)*((x-c)**2))/(w**2))


def Lorentz(x, A, c):
    r"""Cauchy–Lorentz distribution.

    .. math:: y(x) = \frac{1}{\pi A} \frac{A^2}{A^2 + (x-c)^2}

    :param x: x value
    :param A: Scale factor (gamma)
    :param c: Center
    :return: :math:`y(x)`
    """
    return (1/(np.pi*A))*((A**2)/(A**2 + (x-c)**2))


def fwhmLorentz(x, A, c, w):
    r"""Cauchy–Lorentz distribution.

    .. math:: y(x) = A \frac{w^2}{w^2 + 4 (x-c)^2}

    :param x: x value
    :param A: Amplitude
    :param c: Center
    :param w: FWHM
    :return: :math:`y(x)`
    """
    return A*((w**2)/(w**2 + 4* (x-c)**2))


def fwhmAreaLorentz(x, A, c, w):
    r"""Cauchy–Lorentz distribution.

    .. math:: y(x) = \frac{2A}{\pi} \frac{w}{w^2 + 4 (x-c)^2}

    :param x: x value
    :param A: Area under the curve
    :param c: Center
    :param w: FWHM
    :return: :math:`y(x)`
    """
    return ((2*A)/(np.pi))*((w)/(w**2 + 4*(x-c)**2))


def fwhmVoigt(x, A, c, w, m):
    r"""Pseudo-voigt curve.

    .. math:: y(x) = A \left[ m  \frac{w^2}{w^2 + 4 (x-c)^2}   + (1-m) e^{-\frac{4 \ln(2) (x-c)^2}{w^2}} \right]

    :param x: x value
    :param A: Amplitude
    :param c: Center
    :param w: FWHM
    :param m: Factor from 1 to 0 of the lorentzian amount
    :return: :math:`y(x)`
    """
    lorentz = fwhmLorentz(x, 1, c, w)
    gauss = fwhmGauss(x, 1, c, w)

    return A*(m*lorentz + (1-m)*gauss)


def fwhmAreaVoigt(x, A, c, w, m):
    r"""Pseudo-voigt curve.

    .. math:: y(x) = A \left[ m  \frac{2}{\pi} \frac{w}{w^2 + 4 (x-c)^2}   + (1-m) \frac{1}{w \sqrt{\frac{\pi}{4 \ln(2)}}}  e^{-\frac{4 \ln(2) (x-c)^2}{w^2}} \right]

    :param x: x value
    :param A: is the Area
    :param c: Center
    :param w: FWHM
    :param m: Factor from 1 to 0 of the lorentzian amount
    :return: :math:`y(x)`
    """
    lorentz = fwhmAreaLorentz(x, 1, c, w)
    gauss = fwhmAreaGauss(x, 1, c, w)

    return A*(m*lorentz + (1-m)*gauss)


def fwhmArctan(x, A, c, w):
    r"""Arctangent function.

    .. math:: y(x) =   \frac{A}{\np} \left[ \arctan(\frac{1}{w}(x-c)) + \frac{\pi}{2} \right]

    :param x: x value
    :param A: Amplitude
    :param c: Center
    :param w: FWHM (it will take fwhm units to go from A/4 to (3A)/4)
    :return: :math:`y(x)`
    """

    return A * (np.arctan((w**-1)*(x - c)) + (np.pi/2))/np.pi

def square(x, A, c, w):
    r"""Square step function.

    .. math::

        y(x) =   \begin{cases}
                    0, & \text{ for    $x < c-w/2$}\\
                    A, & \text{ for  }  c-w/2 < x < c+w/2\\
                    0, & \text{ for  }  x > c+w/2\\
                    \end{cases}

    :param x: x value
    :param A: Amplitude
    :param c: Center
    :param w: FWHM
    :return: :math:`y(x)`
    """
    return - np.heaviside(x-c-w/2, A)*A + np.heaviside(x-c+w/2, A)*A


def fwhmErr(x, A, c, w):
    """Error function. Integal of gaussian function calculated by ``scipy.special.erf()``.

    :param x: x value
    :param A: Amplitude
    :param c: Center
    :param w: FWHM (it will take roughly fwhm units to go from A/4 to (3A)/4)
    :return: Result y(x)
    """
    return A/2 * (erf((w**-1)/2*(x - c))+1)
