from typing import Union

import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (QPixmap, QMouseEvent, QImage, QWheelEvent, QPainter,
                           QColor)
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import (QFrame, QGraphicsView, QGraphicsScene, QLabel,
                               QSlider, QSizePolicy, QVBoxLayout, QWidget)

from educelab.imgproc.editor.util import ndarray_to_qimage


class ZoomGraphicsView(QGraphicsView):
    def __init__(self, parent=None, zooming=True):
        super(ZoomGraphicsView, self).__init__(parent)
        self._zoom_enabled = zooming
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def enable_zoom(self, enabled: bool):
        self._zoom_enabled = enabled

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self._zoom_enabled:
            angle = event.angleDelta().y()
            factor = pow(1.0015, angle)
            self.scale(factor, factor)


class ImageViewer(QFrame):
    _viewport = None
    _scene = None
    _pix_map_item = None

    def __init__(self, parent=None):
        super(ImageViewer, self).__init__(parent)

        self._viewport = ZoomGraphicsView()
        self._viewport.setViewport(QOpenGLWidget())
        self._viewport.setRenderHint(
            QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        self._viewport.setDragMode(QGraphicsView.ScrollHandDrag)
        self._zoomable = True

        self._scene = QGraphicsScene(self._viewport)
        self._viewport.setScene(self._scene)

        self._pix_map_item = self._scene.addPixmap(QPixmap())

        layout = QVBoxLayout()
        layout.addWidget(self._viewport)
        self.setLayout(layout)

        self.setSizePolicy(QSizePolicy.MinimumExpanding,
                           QSizePolicy.MinimumExpanding)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self.zoom_fit()

    def set_image(self, image: Union[QImage, np.ndarray], refit=False):
        if isinstance(image, np.ndarray):
            image = ndarray_to_qimage(image)

        if refit:
            self._scene.removeItem(self._pix_map_item)
            self._pix_map_item = self._scene.addPixmap(QPixmap.fromImage(image))
            self._pix_map_item.setTransformationMode(Qt.SmoothTransformation)
            self._pix_map_item.setOffset(-image.width() / 2,
                                         -image.height() / 2)
            self.zoom_fit()
        else:
            self._pix_map_item.setPixmap(QPixmap.fromImage(image))

    def enable_zoom(self, enabled: bool):
        self._viewport.enable_zoom(enabled)
        self._zoomable = enabled

    def zoom_fit(self):
        bg = self._viewport.items()[0]
        self._viewport.fitInView(bg, Qt.KeepAspectRatio)


class IndicatorWidget(QLabel):
    def __init__(self, parent=None):
        super(IndicatorWidget, self).__init__(parent=parent)
        self.setMinimumSize(10, 10)
        self.setMaximumSize(10, 10)
        self.set_ready()

    def set_ready(self):
        self.setStyleSheet(
            'QLabel{border-radius:5px;background-color:limegreen}')

    def set_running(self):
        self.setStyleSheet('QLabel{border-radius:5px;background-color:#d47500}')

    def set_error(self):
        self.setStyleSheet('QLabel{border-radius:5px;background-color:Red}')

    def set_color(self, color: QColor):
        c = color.name()
        self.setStyleSheet(f'QLabel{{border-radius:5px;background-color:{c}}}')


class IntSlider(QSlider):
    """https://stackoverflow.com/a/61439160"""
    intValuePreview = Signal(int)
    intValueChanged = Signal(int)
    _last_val = None

    def __init__(self, *args, **kargs):
        super(IntSlider, self).__init__(*args, **kargs)
        self.sliderPressed.connect(self._on_press)
        self.sliderReleased.connect(self._on_release)
        self.valueChanged.connect(self._on_value_changed)

    def _on_press(self):
        self._last_val = self.value()

    def _on_release(self):
        old_val = self._last_val
        new_val = self.value()
        self._last_val = None
        if old_val is not None and new_val != self._last_val:
            self._on_value_changed()

    def _on_value_changed(self):
        if self._last_val is not None:
            self.intValuePreview.emit(self.value())
        else:
            self.intValuePreview.emit(self.value())
            self.intValueChanged.emit(self.value())


class DoubleSlider(QSlider):
    """https://stackoverflow.com/a/61439160"""
    doubleValuePreview = Signal(float)
    doubleValueChanged = Signal(float)
    _last_val = None

    def __init__(self, *args, **kargs):
        super(DoubleSlider, self).__init__(*args, **kargs)
        self._min = 0
        self._max = 99
        self.interval = 1
        self.setTickInterval(1)
        self.sliderPressed.connect(self._on_press)
        self.sliderReleased.connect(self._on_release)
        self.valueChanged.connect(self._on_value_changed)

    def _on_press(self):
        self._last_val = self.value()

    def _on_release(self):
        old_val = self._last_val
        new_val = self.value()
        self._last_val = None
        if old_val is not None and new_val != self._last_val:
            self._on_value_changed()

    def _on_value_changed(self):
        if self._last_val is not None:
            self.doubleValuePreview.emit(self.value())
        else:
            self.doubleValuePreview.emit(self.value())
            self.doubleValueChanged.emit(self.value())

    def setValue(self, value):
        index = round((value - self._min) / self.interval)
        return super(DoubleSlider, self).setValue(index)

    def value(self):
        return self.index * self.interval + self._min

    @property
    def index(self):
        return super(DoubleSlider, self).value()

    def setIndex(self, index):
        return super(DoubleSlider, self).setValue(index)

    def setMinimum(self, value):
        self._min = value
        self._range_adjusted()

    def setMaximum(self, value):
        self._max = value
        self._range_adjusted()

    def setRange(self, min_val, max_val):
        self._min = min_val
        self._max = max_val
        self._range_adjusted()

    def setInterval(self, value):
        # To avoid division by zero
        if not value:
            raise ValueError('Interval of zero specified')
        self.interval = value
        self._range_adjusted()

    def _range_adjusted(self):
        number_of_steps = int((self._max - self._min) / self.interval)
        super(DoubleSlider, self).setMaximum(number_of_steps)


class LabeledIntSlider(QWidget):
    valueChanged = Signal(int)
    intValuePreview = Signal(int)
    intValueChanged = Signal(int)

    slider: IntSlider = None

    def __init__(self, orientation: Qt.Orientation = None, parent=None):
        super(LabeledIntSlider, self).__init__(parent=None)
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.slider = IntSlider()
        if orientation is not None:
            self.slider.setOrientation(orientation)
        self.layout().addWidget(self.slider)
        self.slider.valueChanged.connect(self.valueChanged.emit)
        self.slider.intValuePreview.connect(self.intValuePreview.emit)
        self.slider.intValueChanged.connect(self.intValueChanged.emit)

        val_label = QLabel()
        self.layout().addWidget(val_label)
        val_label.setAlignment(Qt.AlignHCenter)
        val_label.setText(str(self.slider.value()))
        self.slider.intValuePreview.connect(lambda v: val_label.setText(f'{v}'))

    def value(self):
        return self.slider.value()


class LabeledDoubleSlider(QWidget):
    valueChanged = Signal(int)
    doubleValuePreview = Signal(float)
    doubleValueChanged = Signal(float)

    slider: DoubleSlider = None

    def __init__(self, orientation: Qt.Orientation = None, parent=None):
        super(LabeledDoubleSlider, self).__init__(parent=None)
        self.setLayout(QVBoxLayout())
        self.layout().setSpacing(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.slider = DoubleSlider()
        if orientation is not None:
            self.slider.setOrientation(orientation)
        self.layout().addWidget(self.slider)
        self.slider.valueChanged.connect(self.valueChanged.emit)
        self.slider.doubleValuePreview.connect(self.doubleValuePreview.emit)
        self.slider.doubleValueChanged.connect(self.doubleValueChanged.emit)

        val_label = QLabel()
        self.layout().addWidget(val_label)
        val_label.setAlignment(Qt.AlignHCenter)
        val_label.setText(str(self.slider.value()))
        self.slider.doubleValuePreview.connect(
            lambda v: val_label.setText(f'{v:.03g}'))

    def value(self):
        return self.slider.value()
