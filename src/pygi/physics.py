import numpy as np
from numpy import pi, sqrt, log, exp, sin


unit_list = ['km', 'm', 'cm', 'mm', 'µm', 'nm']


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


def beam_divergence(w0, wavelength, m2=1):
    """
    Beam divergence (radian) of a Gaussian beam.

    :param float w0: Beam waist (radius). Considered at z = 0.
    :param float wavelength: Monochromatic wavelength.
    :param float m2: M-square parameter. Default 1 (Gaussian).
    :return: theta = beam divergence.
    :rtype: float
    """
    theta = wavelength / (pi * w0 * m2)
    return theta.to('rad')


def rayleigh_length(w0, wavelength, m2=1):
    """
    Rayleigh length of a Gaussian beam.

    :param float w0: Beam waist (radius). Considered at z = 0.
    :param float wavelength: Monochromatic wavelength.
    :param float m2: M-square parameter. Default 1 (Gaussian).
    :return: zR = Rayleigh length.
    :rtype: float
    """
    z_r = pi * w0**2 / (wavelength * m2)
    return z_r


def lens_focusing(w_coll, focal_length, wavelength, m2=1):
    """
    Focusing of a Gaussian beam by a lens.

    :param float w_coll: Collimated beam size (radius).
    :param float focal_length: Focal length of lens.
    :param float wavelength: Monochromatic wavelength.
    :return: w0 = beam size at focusing distance from lens.
    :rtype: float
    """
    w0 = m2 * wavelength * focal_length / (pi * w_coll)
    return w0


def caustic(w0, z, wavelength, m2):
    """
    Calculate the beam size along the propagation axis.

    :param float w0: Beam waist (radius). Considered at z = 0.
    :param float z: Distance from waist along propagation axis.
    :param float wavelength: Monochromatic wavelength.
    :param float m2: M-square parameter. Default 1 (Gaussian).
    :return: w(z) = beam size at distance z from waist.
    :rtype: tuple
    """
    z = z.to_compact()
    z_array = np.linspace(min(0, z), max(0, z), 100)
    wz_array = beam_size(w0, z_array, wavelength, m2)

    # Workaround for numpy array to work with to_compact()
    wz_array.ito(wz_array[0].to_compact().units)
    return z_array, wz_array
