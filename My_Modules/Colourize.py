from PyQt5.QtCore import *
from PyQt5.QtTest import QTest
from random import choice
from My_Modules.WorkerSignals import WorkerSignals


class Colourize(QRunnable):
	def __init__(self):
		QRunnable.__init__(self)
		self.colours = ["red", "green", "blue", "yellow", "orange", "purple", "pink", "black", "white", "brown"]
		self.signals = WorkerSignals()

	def run(self):
			while True:
				self.signals.colours.emit(choice(self.colours))
				QTest.qWait(500)
