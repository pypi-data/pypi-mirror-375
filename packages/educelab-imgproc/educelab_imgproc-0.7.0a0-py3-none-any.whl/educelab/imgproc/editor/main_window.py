import logging
import time
from pathlib import Path

import PySide6QtAds as ads
import numpy as np
from PIL import Image
from PySide6.QtCore import (QStandardPaths, QSettings, Signal, QThreadPool)
from PySide6.QtGui import QAction, QKeySequence, QCloseEvent, Qt, QKeyEvent
from PySide6.QtWidgets import (QMainWindow, QFileDialog)
from PySide6QtAds import CDockManager, CDockWidget
from educelab.imgproc import clip, as_dtype
from educelab.imgproc.editor.cards import CardListWidget
from educelab.imgproc.editor.widgets import (ImageViewer, IndicatorWidget)
from educelab.imgproc.editor.workers import ProcessImageRunnable


class MainWindow(QMainWindow):
    raw_image = None
    edit_image = None
    _show_raw = False
    _last_update: int = None

    pipelineSubmitted = Signal(object)

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        settings = QSettings()

        # File picker
        self._file_picker = QFileDialog()
        home_dir = QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
        file_dir = settings.value('main/file_dir', home_dir, type=str)
        self._file_picker.setDirectory(file_dir)

        # File menu
        self.file_menu = self.menuBar().addMenu(' &File')
        open_action = QAction('&Open', self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.setStatusTip('Open image file')
        open_action.triggered.connect(self._on_open_file)
        self.file_menu.addAction(open_action)

        # save_action = QAction('&Save As', self)
        # save_action.setShortcut(QKeySequence.SaveAs)
        # save_action.setStatusTip('Save image file')
        # save_action.triggered.connect(self._on_save_file)
        # self.file_menu.addAction(save_action)

        exit_action = QAction('&Exit', self)
        exit_action.setStatusTip('Closes the program')
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)

        # View menu
        self.view_menu = self.menuBar().addMenu('&View')
        sidebar_menu = self.view_menu.addMenu('&Sidebars')

        # Dock manager
        self.dock_mgr = CDockManager(self)

        # Viewer
        self.image_viewer = ImageViewer(self)
        central_dock_widget = ads.CDockWidget('Viewer')
        central_dock_widget.setWidget(self.image_viewer)
        central_dock_area = self.dock_mgr.setCentralWidget(central_dock_widget)
        central_dock_area.setAllowedAreas(ads.DockWidgetArea.OuterDockAreas)

        # Adjustments list
        self.proc_list = CardListWidget(self)
        proc_list_dock = CDockWidget('Adjustments')
        proc_list_dock.setWidget(self.proc_list)
        proc_list_dock.setMinimumSizeHintMode(
            ads.CDockWidget.MinimumSizeHintFromDockWidget)
        proc_list_dock.setMinimumSize(self.proc_list.minimumSize())
        self.dock_mgr.addDockWidget(ads.DockWidgetArea.RightDockWidgetArea,
                                    proc_list_dock)
        sidebar_menu.addAction(proc_list_dock.toggleViewAction())
        self.proc_list.settingsChanged.connect(self._on_settings_changed)

        # Status bar
        self.indicator = IndicatorWidget()
        self.statusBar().addPermanentWidget(self.indicator)

        self._load_settings()

    def __del__(self):
        # clear running jobs
        QThreadPool.globalInstance().clear()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Space and self._show_raw is False:
            logger = logging.getLogger('ImgProc')
            logger.debug('switching to raw image')
            self._show_raw = True
            self.image_viewer.set_image(self.raw_image)
        super(MainWindow, self).keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Space and self._show_raw is True:
            logger = logging.getLogger('ImgProc')
            logger.debug('switching to edited image')
            self._show_raw = False
            self.image_viewer.set_image(self.edit_image)
        super(MainWindow, self).keyPressEvent(event)

    def closeEvent(self, event: QCloseEvent):
        self._save_settings()
        event.accept()

    def _save_settings(self):
        settings = QSettings()

        # Save window size and pos
        settings.setValue('main/geometry', self.saveGeometry())
        settings.setValue('main/state', self.saveState())
        settings.setValue('main/dock/geometry', self.dock_mgr.saveGeometry())
        settings.setValue('main/dock/state', self.dock_mgr.saveState())

    def _load_settings(self):
        settings = QSettings()

        # Window settings
        if settings.contains('main/geometry'):
            self.restoreGeometry(settings.value('main/geometry'))
        if settings.contains('main/state'):
            self.restoreState(settings.value('main/state'))
        if settings.contains('main/dock/geometry'):
            self.dock_mgr.restoreGeometry(settings.value('main/dock/geometry'))
        if settings.contains('main/dock/state'):
            self.dock_mgr.restoreState(settings.value('main/dock/state'))

    def _on_open_file(self):
        settings = QSettings()
        logger = logging.getLogger('ImgProc')

        self._file_picker.setFileMode(QFileDialog.ExistingFile)
        if self._file_picker.exec():
            file_path = self._file_picker.selectedFiles()[0]
            settings.setValue('main/file_dir', str(Path(file_path).parent))

            # Test for LAB
            img = Image.open(file_path)
            if img.mode == 'LAB':
                self.raw_image = np.array(img.convert(mode='RGB'))
                logger.warning(
                    f'Image converted to RGB from LAB: {str(Path(file_path).name)}')
                self.statusBar().showMessage(
                    'WARNING: Image converted to RGB from LAB', 10000)
            else:
                self.raw_image = np.array(img)
            self.edit_image = self.raw_image
            img.close()

            # clear running jobs
            QThreadPool.globalInstance().clear()

            # update image
            self._last_update = time.time_ns()
            self.image_viewer.set_image(self.raw_image, refit=True)
            self._on_settings_changed()

    def _on_settings_changed(self):
        logger = logging.getLogger('ImgProc')
        ts = time.time_ns()
        pipeline = [c.apply_function for c in self.proc_list.cards()]
        if self.raw_image is None:
            return
        if len(pipeline) == 0:
            logger.debug('skipping pipeline')
            self._on_pipeline_complete((self.raw_image, ts))
            return

        def apply_fn(img):
            in_dtype = img.dtype
            img = as_dtype(img, np.float32)
            for p in pipeline:
                img = clip(p(img), 0., 1.)
            img = as_dtype(img, in_dtype)
            return img

        logger.debug('submitting pipeline')
        worker = ProcessImageRunnable(self.raw_image.copy(), apply_fn, ts)
        worker.setAutoDelete(True)
        worker.signals.pipelineComplete.connect(self._on_pipeline_complete)
        QThreadPool.globalInstance().start(worker)
        self.indicator.set_running()

    def _on_pipeline_complete(self, result):
        img, ts = result
        logger = logging.getLogger('ImgProc')
        logger.debug('update received')
        if self._last_update is not None and ts <= self._last_update:
            logger.debug(f'ignoring update with old ts={ts}')
            return
        if img is not None:
            self._last_update = ts
            self.edit_image = img
            self.indicator.set_ready()
            if not self._show_raw:
                self.image_viewer.set_image(img)
