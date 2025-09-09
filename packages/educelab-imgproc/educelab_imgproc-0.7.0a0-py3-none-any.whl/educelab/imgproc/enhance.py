from collections.abc import Sequence
from typing import Union

import numpy as np
from skimage import exposure
from scipy.interpolate import CubicSpline

List2F = Sequence[float, float, ...]

clahe = exposure.equalize_adapthist
"""Contrast limited adaptive histogram equalization (CLAHE).

See: `skimage.exposure.equalize_adapthist() <https://scikit-image.org/docs/stable/api/skimage.exposure.html#skimage.exposure.equalize_adapthist>`_
"""

clip = np.clip
"""Clip image values to a range."""


def curves(image, x, y=None, **kwargs):
    """Cubic spline curves enhancement, aka Photoshop Curves.

    Constructs and applies a cubic spline intensity transfer function to the
    input image.

    :param image: Input image
    :param x: If shape (n,), the spline knot positions in the input intensity
           domain (a.k.a. the independent variables). If shape (n, 2), then
           a list of pairs defining the spline knot positions in both the input
           and output domains.
    :param y: If provided, an array_like of shape (n,) corresponding to spline
           knot positions in the output intensity range (a.k.a. the dependent
           variables). Required if x has shape (n,).
    :param kwargs: Extra kwargs passed to
           `scipy.interpolate.CubicSpline() <https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.CubicSpline.html>`_.
    :return: The enhanced image.
    """
    if not isinstance(x, np.ndarray):
        x = np.array(x)

    if x.ndim == 0 or x.ndim > 2:
        raise ValueError('x must be of shape (n,) or (n, 2)')

    if y is None:
        if x.shape[-1] != 2:
            raise ValueError('missing y of shape (n,) or x of shape (n, 2)')
        y = x[..., 1]
        x = x[..., 0]
    else:
        y = np.array(y)
        if x.ndim != 1 or y.ndim != 1:
            raise ValueError('x and y must be of shape (n,)')
        elif x.shape != y.shape:
            raise ValueError('x and y do not have the same length n')

    # default kwargs
    defaults = {'bc_type': 'natural'}
    kwargs = defaults | kwargs

    return CubicSpline(x, y, **kwargs)(image)


def stretch(image, a_min, a_max, **kwargs):
    """Linearly rescale the provided min/max range to the dynamic range of the
    image.
    """
    return exposure.rescale_intensity(image, in_range=(a_min, a_max), **kwargs)


def stretch_percentile(image, min_perc, max_perc, **kwargs):
    """Linearly rescale the provided percentile range to the dynamic range of
    the image.
    """
    min_val = np.percentile(image, min_perc)
    max_val = np.percentile(image, max_perc)
    return exposure.rescale_intensity(image, in_range=(min_val, max_val), **kwargs)


def stretch_binned_percentile(image, percent: Union[float, List2F, None] = None,
                              bins=256, **kwargs):
    """Alternative version of
    :func:`~educelab.imgproc.enhance.stretch_percentile` that uses percentiles
    calculated from intensity binning.
    """
    if percent is None:
        percent = (.35, .35)
    elif isinstance(percent, float):
        percent = (percent, percent)
    elif isinstance(percent, tuple):
        pass
    else:
        raise ValueError(
            f'unsupported type {type(percent)}, must be '
            f'[float, Sequence[float, float], None]')

    # calculate histogram
    hist, edges = np.histogram(image, bins=bins)

    # find the lower and upper bins which saturate clip_% pixels low and high
    threshold = int(image.size * percent[0] / 200.)
    c = (np.cumsum(hist) < threshold).argmin()
    threshold = int(image.size * percent[1] / 200.)
    d = bins - 1 - (np.cumsum(hist[::-1]) < threshold).argmin()

    # convert the bin to a low and high pixel value
    c = edges[0] + c * (edges[1] - edges[0])
    d = edges[0] + d * (edges[1] - edges[0])

    # rescale and return
    return exposure.rescale_intensity(image, in_range=(c, d), **kwargs)
