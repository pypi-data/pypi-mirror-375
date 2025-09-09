from functools import partial

import numpy as np
from skimage import exposure

from educelab.imgproc.conversion import as_dtype
from educelab.imgproc.properties import dynamic_range


def flatfield_correction(image, lf, df=None):
    """Apply `flatfield correction <https://en.wikipedia.org/wiki/Flat-field_correction>`_
    to an image.

    :param image: Input image.
    :type image: ArrayLike
    :param lf: Light-field image.
    :type lf: ArrayLike
    :param df: Dark-field image. If :code:`None`, an empty dark field will be
               used.
    :type df: ArrayLike | None
    :return: Flatfield-corrected image.
    :rtype: ArrayLike
    """
    # generate an empty darkfield
    if df is None:
        i_min, _ = dynamic_range(image.dtype)
        df = np.full_like(image, i_min)

    # work in float32 if not already a float
    if image.dtype not in (np.float32, np.float64):
        image = as_dtype(image, np.float32)
    if lf.dtype not in (np.float32, np.float64):
        lf = as_dtype(lf, np.float32)
    if df.dtype not in (np.float32, np.float64):
        df = as_dtype(df, np.float32)

    # apply flatfields
    fd_diff = lf - df
    return (image - df) * np.mean(fd_diff) / fd_diff


gamma_correction = exposure.adjust_gamma
"""Apply gamma correction to an image.

See: `skimage.exposure.adjust_gamma() <https://scikit-image.org/docs/stable/api/skimage.exposure.html#skimage.exposure.adjust_gamma>`_
"""

normalize = partial(exposure.rescale_intensity, out_range=(0., 1.))
"""Rescale an image's effective dynamic range (min and max values) to the 
range [0, 1]."""
