from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import QTest
import subprocess
import os
import sys
from getpass import getuser

"""
###################################################################################################################
								YOU NEED TO HAVE PASSWORDLESS SSH SETUP TO USE THIS
###################################################################################################################
"""

"""TO FIX:

need to add documentation!!!!!!!!!

add option for scp instead of rsync(essentially what number 14 does)

encoding issue when try running as python3 signal sends bytes instead of unicode or vice versa

change show_user_info to 'Sync Failed' if it fails instead of completed regardless

"""


class Window(QWidget):
	def __init__(self):
		super(Window, self).__init__()
		self.path()
		self.start_style()
		self.user = getuser()
		self.initui()
		self.options = None
		self.what_to_sync = []
		self.header = int()
		self.command = "rsync"
		self.custom_source_path = ""
		self.custom_dest_path = ""

	@staticmethod
	def start_style():
		# sets the window to dark mode with the fusion styling
		# from PyQt5.QtGui import * and from PyQt5.QtCore import * are needed mostly just for this to run correctly
		qApp.setStyle("Fusion")
		dark_palette = QPalette()
		dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
		dark_palette.setColor(QPalette.WindowText, Qt.white)
		dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
		dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
		dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
		dark_palette.setColor(QPalette.ToolTipText, Qt.white)
		dark_palette.setColor(QPalette.Text, Qt.white)
		dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
		dark_palette.setColor(QPalette.ButtonText, Qt.white)
		dark_palette.setColor(QPalette.BrightText, Qt.red)
		dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
		dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
		dark_palette.setColor(QPalette.HighlightedText, Qt.black)
		qApp.setPalette(dark_palette)
		qApp.setStyleSheet("QToolTip { color: #ffffff; background-color: "
		                   "#2a82da; border: 1px solid white; }")

	@staticmethod
	def path():
		abspath = os.path.abspath(__file__)
		dir_name = os.path.dirname(abspath)
		os.chdir(dir_name)

	@staticmethod
	def welcome_banner():
		return "--_--" * 30 + "\n" + " " * 100 + "SYNC_ER" + "\n" + "_-_" * 40 + "\n"

	def initui(self):
		self.setWindowTitle("Sync_er")
		self.setWindowIcon(QIcon("syncer.png"))
		self.setGeometry(150, 100, 1400, 800)
		self.setFixedSize(1400, 800)

		self.user_label = QLabel(self)
		self.user_label.setText("Using username: " + self.user)
		self.user_label.setAlignment(Qt.AlignTop)

		self.output_display = QTextEdit(self)
		self.output_display.setFixedWidth(800)
		self.output_display.setFixedHeight(750)
		self.output_display.setText(self.welcome_banner())

		self.option1 = QCheckBox("1.  Documents(linux > linux)", self)
		self.option1.stateChanged.connect(self.get_header_1)
		self.option2 = QCheckBox("2.  Downloads(linux > linux)", self)
		self.option2.stateChanged.connect(self.get_header_2)
		self.option3 = QCheckBox("3.  Custom Local Paths", self)
		self.option3.stateChanged.connect(self.get_header_3)
		self.option4 = QCheckBox("4.  Custom Remote Paths", self)
		self.option4.stateChanged.connect(self.get_header_4)

		self.dest_user_label = QLabel(self)
		self.dest_user_label.setText("Destination Username:")
		# self.dest_user.setContentsMargins(30, 0, 0, 0)

		self.dest_user_input = QLineEdit(self)
		self.dest_user_input.setFixedWidth(250)
		self.dest_user_input.setPlaceholderText("Username of other computer")

		self.dest_ip_label = QLabel(self)
		self.dest_ip_label.setText("Destination IP:")

		self.dest_ip_input = QLineEdit(self)
		self.dest_ip_input.setFixedWidth(250)
		self.dest_ip_input.setText("192.168.0.")
		self.dest_ip_input.setPlaceholderText("eg. 192.168.0.11")

		self.sync_option_label = QLabel(self)
		self.sync_option_label.setText("Syncing Options:")
		self.sync_option1 = QRadioButton("Default")
		self.sync_option1.setChecked(True)
		self.sync_option2 = QRadioButton("Compress")
		self.sync_option3 = QRadioButton("Delete")
		self.sync_option4 = QRadioButton("Enter Manually")
		self.sync_option4_input = QLineEdit(self)
		self.sync_option4_input.setFixedWidth(100)
		self.sync_option4_input.setPlaceholderText("eg. -Paiurv")

		self.show_user_info = QLabel(self)
		self.show_user_info.setAlignment(Qt.AlignCenter)

		self.sync_button = QPushButton("Sync", self)
		self.sync_button.clicked.connect(self.syncer)
		self.clear_settings_button = QPushButton("Clear Settings", self)
		self.clear_settings_button.clicked.connect(self.clear_settings)
		self.clear_display_button = QPushButton("Clear Display", self)
		self.clear_display_button.clicked.connect(self.clear_display)

		self.custom_path_src = QLineEdit(self)
		self.custom_path_src.setPlaceholderText("Custom Source Path")
		self.custom_path_dst = QLineEdit(self)
		self.custom_path_dst.setPlaceholderText("Custom Destination Path")

		h_box_paths = QHBoxLayout()
		h_box_paths.addWidget(self.custom_path_src)
		h_box_paths.addWidget(self.custom_path_dst)

		h_box_buttons = QHBoxLayout()
		h_box_buttons.setContentsMargins(20, 100, 20, 20)
		h_box_buttons.addWidget(self.sync_button)
		h_box_buttons.addWidget(self.clear_settings_button)
		h_box_buttons.addWidget(self.clear_display_button)

		grid = QGridLayout()
		grid.setSpacing(10)
		grid.setAlignment(Qt.AlignTop)
		grid.setContentsMargins(60, 60, 60, 60)
		grid.addWidget(self.dest_user_label, 0, 0)
		grid.addWidget(self.dest_user_input, 0, 1)
		grid.addWidget(self.dest_ip_label, 1, 0)
		grid.addWidget(self.dest_ip_input, 1, 1)
		grid.addWidget(self.sync_option_label, 2, 0)
		grid.addWidget(self.sync_option1, 3, 0)
		grid.addWidget(self.sync_option2, 3, 1)
		grid.addWidget(self.sync_option3, 4, 0)
		grid.addWidget(self.sync_option4, 4, 1)
		grid.addWidget(self.sync_option4_input, 5, 1)

		v_box_options = QVBoxLayout()
		v_box_options.addWidget(self.option1)
		v_box_options.addWidget(self.option2)
		v_box_options.addWidget(self.option3)
		v_box_options.addWidget(self.option4)

		v_box = QVBoxLayout()
		v_box.addWidget(self.user_label)
		v_box.addLayout(grid)
		v_box.addLayout(v_box_options)
		v_box.addLayout(h_box_paths)
		v_box.addStretch(1)
		v_box.addWidget(self.show_user_info)
		v_box.addLayout(h_box_buttons)

		h_box = QHBoxLayout()
		h_box.addLayout(v_box)
		h_box.addWidget(self.output_display)

		self.setLayout(h_box)

		# self.show()

	def get_header_1(self, state):
		if state == Qt.Checked:
			self.what_to_sync.append(1)

	def get_header_2(self, state):
		if state == Qt.Checked:
			self.what_to_sync.append(2)

	def get_header_3(self, state):
		if state == Qt.Checked:
			self.what_to_sync.append(3)

	def get_header_4(self, state):
		if state == Qt.Checked:
			self.what_to_sync.append(4)

	def get_options(self):
		if self.sync_option1.isChecked():
			self.options = "d"
		elif self.sync_option2.isChecked():
			self.options = "c"
		elif self.sync_option3.isChecked():
			self.options = "del"
		elif self.sync_option4.isChecked():
			self.options = self.sync_option4_box.text()
		return self.options

	def clear_settings(self):
		self.output_display.setText("")
		self.dest_user_input.setText("")
		self.dest_ip_input.setText("")
		self.sync_option1.setChecked(True)
		self.sync_option2.setChecked(False)
		self.sync_option3.setChecked(False)
		self.sync_option4.setChecked(False)
		self.sync_option4_input.setText("")
		self.option1.setChecked(False)
		self.option2.setChecked(False)
		self.option3.setChecked(False)
		self.option4.setChecked(False)
		self.custom_path_src.setText("")
		self.custom_path_dst.setText("")
		self.show_user_info.setText("")
		self.options = None
		self.what_to_sync[:] = []
		self.custom_source_path = ""
		self.custom_dest_path = ""

	def clear_display(self):
		self.output_display.setText("")
		self.update()

	# used to print header for what output is showing
	@pyqtSlot(int, str, str)
	def print_sync(self, header, output, errors):
		headers = {
			1: "Documents(linux > linux)", 2: "Downloads(linux > Linux)",
			3: "Custom Local Paths", 4: "Custom Remote Paths"}
		if self.output_display.toPlainText() == "":
			if len(errors) != 0:
				self.output_display.setText("#" * 75 + "\n" + " " * 50 + "Showing output for " + headers[header] +
				                            " sync" + "\n" + "#" * 75 + "\n\n" + output + "\n\n" + "~" * 10 + "ERRORS"
				                            + "~" * 10 + "\n" + str(errors))

			else:
				self.output_display.setText("#" * 75 + "\n" + " " * 50 + "Showing output for " + headers[header] +
				                            " sync" + "\n" + "#" * 75 + "\n\n" + output)
		else:
			if len(errors) != 0:
				self.output_display.append("#" * 75 + "\n" + " " * 50 + "Showing output for " + headers[header] +
				                           " sync" + "\n" + "#" * 75 + "\n\n" + output + "\n\n" + "~" * 10 + "ERRORS"
				                           + "~" * 10 + "\n" + str(errors))

			else:
				self.output_display.append("#" * 75 + "\n" + " " * 50 + "Showing output for " + headers[header] +
				                           " sync" + "\n" + "#" * 75 + "\n\n" + output)

		self.show_user_info.setText("Sync Completed!")
		self.update()

	def get_sync_info(self):
		self.get_options()
		self.dest_user = self.dest_user_input.text()
		self.dest_ip = self.dest_ip_input.text()
		self.custom_source_path = self.custom_path_src.text()
		self.custom_dest_path = self.custom_path_dst.text()

	def syncer(self):
		self.pool = QThreadPool()
		self.show_user_info.setText("Syncing...")
		self.clear_display()
		QTest.qWait(1000)
		self.get_sync_info()
		for h in self.what_to_sync:
			self.worker = SyncThatShit(h, self.command, self.options, self.user, self.dest_user, self.dest_ip,
			                           self.custom_dest_path, self.custom_source_path)
			self.worker.signals.finished.connect(self.print_sync)
			self.pool.start(self.worker)
		self.pool.waitForDone()
		self.what_to_sync[:] = []


class WorkerSignals(QObject):
	finished = pyqtSignal(int, str, str)


class SyncThatShit(QRunnable):

	def __init__(self, header, command, options, user, dest_user, dest_ip, custom_dest_path, custom_source_path):
		QRunnable.__init__(self)
		self.header = header
		self.command = command
		self.options = options
		self.delete = False
		self.user = user
		self.dest_user = dest_user
		self.dest_ip = dest_ip
		self.custom_dest_path = custom_dest_path
		self.custom_source_path = custom_source_path
		self.source_path = ""
		self.dest_path = ""
		self.destination = ""
		self.output = ""
		self.errors = None
		self.signals = WorkerSignals()
		self.sync_sort()

	def run(self):
		try:
			self.destination = self.dest_user + "@" + self.dest_ip + ":" + self.dest_path
			# ipad = self.destination + "@" + self.destination_ip + ":" + self.dest_path
			if self.header == 3:
				p = subprocess.Popen([self.command, self.options, self.source_path, self.dest_path],
				                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			elif self.header == 14:
				# p = subprocess.Popen(["scp", ipad, self.source_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				pass
			else:
				if self.delete:
					p = subprocess.Popen([self.command, self.options, self.source_path, self.destination, "--delete"],
					                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				else:
					p = subprocess.Popen([self.command, self.options, self.source_path, self.destination],
					                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)

			self.output, self.errors = p.communicate()
			self.signals.finished.emit(self.header, self.output, self.errors)
		except Exception as e:
			print("Ooops something went wrong there..." + "\n" + str(e))

	# sets the source destination of the sync
	def sync_sort(self):
		if self.options == "d":  # default
			self.options = "-Paiurv"
		elif self.options == "c":  # compress
			self.options = "-Paiurvz"
		elif self.options == "del":  # delete outdated
			self.options = "-Paiurv"
			self.delete = True

		if self.header == 1:
			self.source_path = "/home/" + self.user + "/Documents/"
			self.dest_path = "/home/" + self.dest_user + "/Documents/"

		elif self.header == 2:
			self.source_path = "/home/" + self.user + "/Downloads/"
			self.dest_path = "/home/" + self.dest_user + "/Downloads/"

		elif self.header == 3:
			self.source_path = self.custom_source_path
			self.dest_path = self.custom_dest_path

		elif self.header == 4:
			self.source_path = self.custom_source_path
			self.dest_path = self.custom_dest_path

		elif self.header == 14:
			# self.source_path = "/Users/" + self.source + "/Desktop/films/"
			# self.dest_path = "/User/Library/Artworks/*"
			pass


def main():
	app = QApplication(sys.argv)  # create the application
	window = Window()
	window.show()
	sys.exit(app.exec_())


if __name__ == "__main__":
	main()
