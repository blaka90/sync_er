from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


# class for opening/showing a file browser to choose path instead of typing it manually
class MyFileBrowser(QWidget):

    def __init__(self, os_type):
        QWidget.__init__(self)
        self.view = QTreeView()  # for displaying the FileSystemModel in a TreeView
        self.sig = BrowserSignal()  # signal for passing data back to main window
        self.setWindowTitle("Custom Path File Manager")
        self.path = ""
        self.get_path(os_type)
        self.file_path = ""
        self.model = QFileSystemModel()  # the file file system model creation
        self.model.setRootPath(QDir.rootPath())  # we want to start from root
        self.setGeometry(320, 200, 1000, 600)
        self.view.setModel(self.model)  # puts the file system model into the tree view
        self.view.setRootIndex(self.model.index(self.path))  # set the indexes
        self.view.setSortingEnabled(True)  # give the option to sort on header click
        self.view.setColumnWidth(0, 610)
        self.view.sortByColumn(0, Qt.AscendingOrder)
        self.open_button = QPushButton("Open", self)  # pushed when file path is chosen and sends signal
        self.open_button.clicked.connect(self.return_path)
        self.open_button.setFixedWidth(200)
        self.open_button.setStyleSheet("background-color: blue; color: black")

        self.v_box = QVBoxLayout()
        self.v_box.addWidget(self.view)
        self.v_box.addWidget(self.open_button, alignment=Qt.AlignCenter)
        self.setLayout(self.v_box)
        self.show()

    def get_path(self, type_os):
        if type_os == "linux":
            self.path = "/"
        elif type_os == "mac":
            self.path = "/"
        elif type_os == "windows":
            self.path = "C:\\"
        else:
            print("Failed to set os root dir for FileSystemModel")

    # when filepath is chosen and open button is pressed return path to correlating input box in main window and close
    def return_path(self):
        fp = self.view.selectedIndexes()[0]
        self.file_path = self.model.filePath(fp)
        self.sig.return_data.emit(self.file_path)
        self.close()


# used for MyFileBrowser to return path through signal
class BrowserSignal(QObject):
    return_data = pyqtSignal(str)
