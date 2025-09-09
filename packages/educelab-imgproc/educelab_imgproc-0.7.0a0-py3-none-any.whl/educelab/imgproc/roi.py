import re
from dataclasses import dataclass

_SHAPE_REGEX = r"(?P<w>\d+)x(?P<h>\d+)"
_ORIGIN_REGEX = r"\+(?P<x>\d+)\+(?P<y>\d+)"
_ROI_REGEX = _SHAPE_REGEX + _ORIGIN_REGEX
_SHAPE_REGEX = re.compile(_SHAPE_REGEX)
_ORIGIN_REGEX = re.compile(_ORIGIN_REGEX)
_ROI_REGEX = re.compile(_ROI_REGEX)


def parse_roi_params(roi_str: str):
    """ Parse an image region-of-interest string of the form :code:`WxH+X+Y`.

    :param roi_str: ROI string
    :return: ROI dataclass
    """
    # ROI return value
    @dataclass
    class ROI:
        x: int = None
        y: int = None
        w: int = None
        h: int = None

        def __str__(self):
            return f'(x:{self.x}, y:{self.y}, w:{self.w}, h:{self.h})'

    # Parse the ROI parameters
    match = _ROI_REGEX.match(roi_str)
    if not match:
        raise ValueError(f'cannot parse ROI from str: {roi_str}')

    # Convert to ints
    roi = ROI()
    for key, value in match.groupdict():
        roi.__dict__[key] = int(value)

    # Return ROI commands
    return roi
