from PyQt5.QtCore import *


# object used for signals when finished to start printing to display
class WorkerSignals(QObject):
    finished = pyqtSignal(int, str, str)
    # used to let show_user_info if any errors occured for coloring and feedback
    sync_errors = pyqtSignal(bool)
    display_finish = pyqtSignal(int)
    network_list = pyqtSignal(list)
    colours = pyqtSignal(str)
