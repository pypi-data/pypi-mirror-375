import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

import numpy as np
from PySide6.QtCore import QStandardPaths
from PySide6.QtGui import QImage

from educelab.imgproc.conversion import as_dtype
from educelab.imgproc.properties import dynamic_range


def ndarray_to_qimage(image: np.ndarray) -> QImage:
    if image.ndim > 3:
        raise ValueError(f'unsupported image dimension: {image.ndim}')

    if image.ndim == 2:
        image = image[..., np.newaxis]
    cns = image.shape[-1]
    _, max_x = dynamic_range(image)

    if cns == 1:
        image = np.concatenate((image, image, image), axis=-1)
        pix_fmt = QImage.Format.Format_RGB888
    elif cns == 2:
        a = image[..., 1:2]
        y = (image[..., 0] * (a / max_x)).astype(image.dtype)
        image = np.concatenate((y, y, y, a), axis=-1)
        pix_fmt = QImage.Format.Format_ARGB32
    elif cns == 3:
        # a = np.zeros_like(image[..., 0:1])
        # image = np.concatenate((image, a), axis=-1)
        pix_fmt = QImage.Format.Format_RGB888
    elif cns == 4:
        image[:3] /= image[..., 3:4]
        pix_fmt = QImage.Format.Format_ARGB32
    else:
        raise ValueError(f'unsupported number of channels: {cns}')

    if image.dtype != np.uint8:
        image = as_dtype(image, np.uint8)

    image = QImage(image.data, image.shape[1], image.shape[0], image.strides[0],
                   pix_fmt)

    return image


class ApplicationLogFilter(logging.Filter):
    allowed_names = ['ImgProc', 'educelab']

    def filter(self, record):
        for a in self.allowed_names:
            if a in record.name:
                return True
        return False


def setup_logging(log_level=logging.INFO):
    app_dir = QStandardPaths.writableLocation(
        QStandardPaths.AppLocalDataLocation)
    log_dir = Path(app_dir) / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'ImgProc_log.txt'

    # Formats
    date_format = '%Y-%m-%d %H:%M:%S UTC'
    line_format = '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'

    # Setup formatter
    logger_frmt = logging.Formatter(fmt=line_format, datefmt=date_format)
    logger_frmt.converter = time.gmtime

    # Setup log filter
    log_filter = ApplicationLogFilter()

    # Setup handlers
    handlers = []

    stderr_hndl = logging.StreamHandler()
    stderr_hndl.setLevel(log_level)
    stderr_hndl.setFormatter(logger_frmt)
    stderr_hndl.addFilter(log_filter)
    handlers.append(stderr_hndl)

    file_hndl = RotatingFileHandler(filename=log_file,
                                    maxBytes=5000000,
                                    backupCount=10)
    file_hndl.setLevel(log_level)
    file_hndl.setFormatter(logger_frmt)
    file_hndl.addFilter(log_filter)
    handlers.append(file_hndl)

    # noinspection PyArgumentList
    logging.basicConfig(format=line_format, level=log_level,
                        datefmt=date_format, handlers=handlers)
