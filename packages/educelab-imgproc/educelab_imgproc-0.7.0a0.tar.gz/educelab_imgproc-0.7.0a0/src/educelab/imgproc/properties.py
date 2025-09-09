import numpy as np


def dynamic_range(t):
    """Returns the dynamic range (minimum and maximum supported value) for the
    provided pixel type. If an array is provided, returns the dynamic range of
    the array's dtype.

    :param t: Array or dtype
    :return: min, max
    """
    if isinstance(t, np.ndarray):
        dtype = t.dtype
    elif t in (np.uint8, np.uint16, np.float32, np.float64):
        dtype = t
    else:
        raise ValueError(f'Unsupported input type: {t}')

    if dtype == np.uint8:
        return 0, 255
    elif dtype == np.uint16:
        return 0, 65535
    elif dtype in (np.float32, np.float64):
        return 0., 1.
    else:
        raise ValueError(f'Unsupported dtype: {t}')
