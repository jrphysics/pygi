import numpy as np
from numpy import pi, sqrt, log, exp, sin


unit_list = ['m', 'cm', 'mm', 'um', 'nm']


def beam_size(w0, z, wavelength, m2=1):
    """
    Beam size (radius) along propagation axis.

    :param float w0: Beam waist (radius). Considered at z = 0.
    :param float z: Distance from waist along propagation axis.
    :param float wavelength: Monochromatic wavelength.
    :param float m2: M-square parameter. Default 1 (Gaussian).
    :return: w(z) = beam size at distance z from waist.
    :rtype: float
    """
    wz = w0 * sqrt(1 + (m2 * wavelength * z / (pi * w0**2))**2)
    return wz


def lens_focusing(w_coll, focal_length, wavelength):
    """
    Focusing of a Gaussian beam by a lens.

    :param float w_coll: Collimated beam size (radius).
    :param float focal_length: Focal length of lens.
    :param float wavelength: Monochromatic wavelength.
    :return: w0 = beam size at distance z from waist.
    :rtype: float
    """
    w0 = wavelength * focal_length / (pi * w_coll)
    return w0


def unit(unit_string):
    """
    Convert units to SI.

    :param str unit_string: Unit string (e.g. 'cm', 'nm', 'um', 'm').
    :return: Conversion factor to SI.
    :rtype: float
    """
    unit_dict = {
        'm': 1,
        'cm': 1E-2,
        'mm': 1E-3,
        'um': 1E-6,
        'nm': 1E-9
    }
    return unit_dict[unit_string]
