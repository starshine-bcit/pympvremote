import traceback
import sys
from pathlib import Path

from requests import Response
from PyQt6 import QtCore

class UploadWorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    result = QtCore.pyqtSignal(Response)

class UploadWorker(QtCore.QRunnable):
    def __init__(self, fn, file: Path) -> None:
        """Initializes upload worker with a function to run, and
            file to upload.

        Args:
            fn (function): function to call when started
            file (Path): file to upload
        """        
        super(UploadWorker, self).__init__()
        self.fn = fn
        self.file = file
        self.signals = UploadWorkerSignals()
        self.setAutoDelete(True)
    
    @QtCore.pyqtSlot()
    def run(self):
        """Runs the provided function, emits result and finished if
            successfull
        """        
        try:
            result = self.fn(self.file)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            print((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


