import logging

from PySide6.QtCore import QObject, Signal, QRunnable


class ProcessImageSignals(QObject):
    workerWaiting = Signal()
    workerInProgress = Signal()
    workerError = Signal()
    pipelineComplete = Signal(object)


class ProcessImageRunnable(QRunnable):
    def __init__(self, image, apply_fn, ts):
        super(ProcessImageRunnable, self).__init__()
        self.image = image
        self.apply_fn = apply_fn
        self.ts = ts
        self.signals = ProcessImageSignals()

    def run(self):
        try:
            image = self.apply_fn(self.image)
            self.signals.pipelineComplete.emit((image, self.ts))
        except Exception as e:
            logger = logging.getLogger('ImgProc')
            logger.exception('Error applying processing pipeline')


class ProcessImageWorker(QObject):
    workerWaiting = Signal()
    workerInProgress = Signal()
    workerError = Signal()

    pipelineComplete = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def process(self, process_tuple):
        try:
            self.workerInProgress.emit()
            image, apply_fn, ts = process_tuple
            image = apply_fn(image)
            self.pipelineComplete.emit((image, ts))
            self.workerWaiting.emit()
        except Exception as e:
            logger = logging.getLogger('ImgProc')
            logger.exception('Error applying processing pipeline')
            self.workerError.emit()
