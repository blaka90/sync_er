from PyQt5.QtCore import *
from os import path, chdir
from subprocess import Popen


class OpenCmd(QRunnable):

    def __init__(self, command):
        QRunnable.__init__(self)
        self.command = command
        self.run()

    def run(self):
        abspath = path.abspath(__file__)
        dir_name = path.dirname(abspath)
        chdir(dir_name)
        p = Popen(self.command)
        p.communicate()