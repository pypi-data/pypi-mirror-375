import numpy as np

from educelab.imgproc.properties import dynamic_range


def as_dtype(image, dtype) -> np.ndarray:
    """Convert an image to a specific fundamental dtype. Automatically performs
    dynamic range adjustment.

    :param image: Input image.
    :type image: ArrayLike
    :param dtype: Output dtype.
    :type dtype: :py:class:`numpy.dtype`
    :return: Converted image.
    :rtype: ArrayLike
    """
    if image.dtype == dtype:
        return image

    in_min, in_max = (float(x) for x in dynamic_range(image))
    out_min, out_max = (float(x) for x in dynamic_range(dtype))

    if image.dtype in (np.float32, np.float64):
        image = np.clip(image, a_min=0., a_max=1.)

    image = out_min + (image - in_min) * (out_max - out_min) / (in_max - in_min)
    return image.astype(dtype)


def uint_to_dtype(image, bpc: int, dtype=np.float32) -> np.ndarray:
    """Convert an uint image with an effective bit depth :code:`bpc` to a
    specific fundamental dtype. Unlike :py:func:`as_dtype`, this function allows
    you to specify the input's *effective* bit depth independent of the
    array's dtype. This is useful when working with 10-/12-/14-bit raw images
    which are stored in an uint16 pixel type.

    :param image: Input image.
    :type image: ArrayLike
    :param bpc: Effective bit depth.
    :type bpc: int
    :param dtype: Output dtype.
    :type dtype: :py:class:`numpy.dtype`
    :return: Converted image.
    :rtype: ArrayLike
    """

    image = image / (2 ** bpc - 1)
    return as_dtype(image, dtype)
