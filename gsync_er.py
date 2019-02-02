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

version = 1.4

"""
TO FIX:

encoding issue when try running as python3 signal sends bytes instead of unicode

TO ADD:

add option for scp instead of rsync(essentially what number 14 does)
this could be a toggle with rsync and scp after username label

add option to find ip address from username giving(has to be on network...possibly with nmap?)
or save ip address of username and try it when that username is used...enter manual otherwise until saved

add button which opens new small window that can add multiple custom remote/local paths?

may have to make fullscreen if adding more features or going to get crowded

try make compatible with windows and mac:
	Documents option maps to os dependent path documents, same for downloads etc
	including adding all the standards...pictures music videos etc
"""


# the main window
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
		self.custom_local_source_path = ""
		self.custom_local_dest_path = ""
		self.custom_remote_source_path = ""
		self.custom_remote_dest_path = ""
		self.user_and_dest_okay = True
		self.custom_source_and_dest_okay = True

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
	def path():  # change into current working dirctory wherever program is ran from
		abspath = os.path.abspath(__file__)
		dir_name = os.path.dirname(abspath)
		os.chdir(dir_name)

	@staticmethod
	def welcome_banner():  # nostalgia from my cli version
		return "--_--" * 30 + "\n" + " " * 100 + "SYNC_ER" + "\n" + "_-_" * 40 + "\n"

	# initilize the user interface
	def initui(self):
		# set the name, icon and size of main window
		self.setWindowTitle("Sync_er")
		self.setWindowIcon(QIcon("syncer.png"))
		self.setGeometry(150, 100, 1400, 800)
		self.setFixedSize(1400, 800)

		# label for showing the users username
		self.user_label = QLabel(self)
		self.user_label.setText("Using username: " + self.user)
		self.user_label.setAlignment(Qt.AlignTop)

		# not used as a textedit, but used to display output from syncs
		self.output_display = QTextEdit(self)
		self.output_display.setFixedWidth(800)
		self.output_display.setFixedHeight(750)
		self.output_display.setText(self.welcome_banner())

		# the options the user has to sync with (should be adding more later)
		self.option1 = QCheckBox("1.  Documents(linux > linux)", self)
		self.option1.stateChanged.connect(self.get_header_1)
		self.option2 = QCheckBox("2.  Downloads(linux > linux)", self)
		self.option2.stateChanged.connect(self.get_header_2)
		self.option3 = QCheckBox("3.  Custom Local Paths", self)
		self.option3.stateChanged.connect(self.get_header_3)
		self.option4 = QCheckBox("4.  Custom Remote Paths", self)
		self.option4.stateChanged.connect(self.get_header_4)

		# label for destination username
		self.dest_user_label = QLabel(self)
		self.dest_user_label.setText("Destination Username:")

		# user input box for the destination usenname
		self.dest_user_input = QLineEdit(self)
		self.dest_user_input.setFixedWidth(250)
		self.dest_user_input.setPlaceholderText("Username of other computer")

		# label for destination ip address
		self.dest_ip_label = QLabel(self)
		self.dest_ip_label.setText("Destination IP:")

		# user input box for destination ip address
		self.dest_ip_input = QLineEdit(self)
		self.dest_ip_input.setFixedWidth(250)
		self.dest_ip_input.setText("192.168.0.")  # I'm lazy
		self.dest_ip_input.setPlaceholderText("eg. 192.168.0.11")

		# label for different options/flags used for sync
		self.sync_option_label = QLabel(self)
		self.sync_option_label.setText("Syncing Options:")
		# this is the default, standard rsync option
		self.sync_option1 = QRadioButton("Default")
		self.sync_option1.setChecked(True)
		# option to compress the files for syncing(best used for large syncs)
		self.sync_option2 = QRadioButton("Compress")
		# option to delete destination path before sync(removes unwanted files already on destination)
		self.sync_option3 = QRadioButton("Delete")
		# manually specify syncing options(probably only used in rare cases)
		self.sync_option4 = QRadioButton("Enter Manually")
		self.sync_option4.toggled.connect(self.check_option)
		# user input box for manual options/flags
		self.sync_option4_input = QLineEdit(self)
		self.sync_option4_input.setFixedWidth(100)
		self.sync_option4_input.setPlaceholderText("eg. -Paiurv")
		self.sync_option4_input.setDisabled(True)

		# label used to show the user some feedback in many instances
		self.show_user_info = QLabel(self)
		self.show_user_info.setAlignment(Qt.AlignCenter)

		# sync button, starts the process of syncing all user input
		self.sync_button = QPushButton("Sync", self)
		self.sync_button.clicked.connect(self.syncer)
		# button to clear all user input
		self.clear_settings_button = QPushButton("Clear Settings", self)
		self.clear_settings_button.clicked.connect(self.clear_settings)
		# button to clear the display  only
		self.clear_display_button = QPushButton("Clear Display", self)
		self.clear_display_button.clicked.connect(self.clear_display)

		# user input box for the source of remote syncs
		self.custom_remote_path_src = QLineEdit(self)
		self.custom_remote_path_src.setPlaceholderText("Custom Remote Source Path")
		self.custom_remote_path_src.setDisabled(True)
		# user input box for the destination of remote syncs
		self.custom_remote_path_dst = QLineEdit(self)
		self.custom_remote_path_dst.setPlaceholderText("Custom Remote Destination Path")
		self.custom_remote_path_dst.setDisabled(True)

		# user input box for the source of local syncs
		self.custom_local_path_src = QLineEdit(self)
		self.custom_local_path_src.setPlaceholderText("Custom Local Source Path")
		self.custom_local_path_src.setDisabled(True)
		# user input box for the destination of local syncs
		self.custom_local_path_dst = QLineEdit(self)
		self.custom_local_path_dst.setPlaceholderText("Custom Local Destination Path")
		self.custom_local_path_dst.setDisabled(True)

		# horizontal layout for custom remote user path input boxes
		h_box_remote_paths = QHBoxLayout()
		h_box_remote_paths.addWidget(self.custom_remote_path_src)
		h_box_remote_paths.addWidget(self.custom_remote_path_dst)

		# horizontal layout for custom local user path input boxes
		h_box_local_paths = QHBoxLayout()
		h_box_local_paths.addWidget(self.custom_local_path_src)
		h_box_local_paths.addWidget(self.custom_local_path_dst)

		# horizontal layout for buttons at bottom of ui
		h_box_buttons = QHBoxLayout()
		h_box_buttons.setContentsMargins(20, 100, 20, 20)
		h_box_buttons.addWidget(self.sync_button)
		h_box_buttons.addWidget(self.clear_settings_button)
		h_box_buttons.addWidget(self.clear_display_button)

		# grid layout for most of the user input and options
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

		# vertical layout for the actual syncing options
		v_box_options = QVBoxLayout()
		v_box_options.addWidget(self.option1)
		v_box_options.addWidget(self.option2)
		v_box_options.addWidget(self.option3)
		v_box_options.addLayout(h_box_local_paths)
		v_box_options.addWidget(self.option4)
		v_box_options.addLayout(h_box_remote_paths)

		# layout for the left hand side of ui layouts
		v_box = QVBoxLayout()
		v_box.addWidget(self.user_label)
		v_box.addLayout(grid)
		v_box.addLayout(v_box_options)
		v_box.addStretch(1)
		v_box.addWidget(self.show_user_info)
		v_box.addLayout(h_box_buttons)

		# horizontal layout to split user input on left and display on right
		h_box = QHBoxLayout()
		h_box.addLayout(v_box)
		h_box.addWidget(self.output_display)

		# set the layout
		self.setLayout(h_box)

	def check_option(self, enabled):
		if enabled:
			self.sync_option4_input.setDisabled(False)
		else:
			self.sync_option4_input.setDisabled(True)

	# if any checkbox is ticked, add to or remove from what_to_sync list
	def get_header_1(self, state):
		if state == Qt.Checked:
			self.what_to_sync.append(1)
		else:
			self.what_to_sync.remove(1)

	def get_header_2(self, state):
		if state == Qt.Checked:
			self.what_to_sync.append(2)
		else:
			self.what_to_sync.remove(2)

	def get_header_3(self, state):
		if state == Qt.Checked:
			self.what_to_sync.append(3)
			self.custom_local_path_src.setDisabled(False)
			self.custom_local_path_dst.setDisabled(False)
		else:
			self.what_to_sync.remove(3)
			self.custom_local_path_src.setDisabled(True)
			self.custom_local_path_dst.setDisabled(True)

	def get_header_4(self, state):
		if state == Qt.Checked:
			self.what_to_sync.append(4)
			self.custom_remote_path_src.setDisabled(False)
			self.custom_remote_path_dst.setDisabled(False)
		else:
			self.what_to_sync.remove(4)
			self.custom_remote_path_src.setDisabled(True)
			self.custom_remote_path_dst.setDisabled(True)

	# sets the correct option/flag from user input and returns option for use in sync
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

	# resets all settings and user input/options when clear setting button is pressed
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
		self.custom_remote_path_src.setText("")
		self.custom_remote_path_dst.setText("")
		self.custom_local_path_src.setText("")
		self.custom_local_path_dst.setText("")
		self.show_user_info.setText("")
		self.options = None
		self.custom_local_source_path = ""
		self.custom_local_dest_path = ""
		self.custom_remote_source_path = ""
		self.custom_remote_dest_path = ""

	# clears the output display only when clear display button is pressed
	def clear_display(self):
		self.output_display.setText("")
		self.update()

	# used to print to display what output is showing after sync is complete
	@pyqtSlot(int, str, str)
	def print_sync(self, header, output, errors):
		# show what sync option/header was used for corresponding output and then display it
		headers = {
			1: "Documents(linux > linux)", 2: "Downloads(linux > Linux)",
			3: "Custom Local Paths", 4: "Custom Remote Paths"}
		# if only 1 sync option is getting used this will run
		if self.output_display.toPlainText() == "":
			if len(errors) != 0:
				self.output_display.setText("#" * 79 + "\n" + " " * 60 + "Showing output for " + headers[header] +
				                            " sync" + "\n" + "#" * 79 + "\n\n" + output + "\n\n" + "~" * 93 + "\n"
				                            + " " * 100 + "ERRORS" + "\n" + "~" * 93 + "\n\n" + str(errors))
				self.show_user_info.setText("Sync Completed!\nbut...\n Errors have occured!")

			else:
				self.output_display.setText("#" * 79 + "\n" + " " * 60 + "Showing output for " + headers[header] +
				                            " sync" + "\n" + "#" * 79 + "\n\n" + output)
				self.show_user_info.setText("Sync Completed!")
		# if multiple syncs are getting run it will append the ouputs together for display
		else:
			if len(errors) != 0:
				self.output_display.append("#" * 79 + "\n" + " " * 60 + "Showing output for " + headers[header] +
				                           " sync" + "\n" + "#" * 79 + "\n\n" + output + "\n\n" + "~" * 93 + "\n"
				                           + " " * 100 + "ERRORS" + "\n" + "~" * 93 + "\n\n" + str(errors))
				self.show_user_info.setText("Sync Completed!\nbut...\n Errors have occured!")

			else:
				self.output_display.append("#" * 79 + "\n" + " " * 60 + "Showing output for " + headers[header] +
				                           " sync" + "\n" + "#" * 79 + "\n\n" + output)
				self.show_user_info.setText("Sync Completed!")

		self.update()

	# grab all the information from user inputs needed for the sync
	def get_sync_info(self):
		self.get_options()
		self.dest_user = str(self.dest_user_input.text())
		self.dest_ip = str(self.dest_ip_input.text())
		self.custom_local_source_path = str(self.custom_local_path_src.text())
		self.custom_local_dest_path = str(self.custom_local_path_dst.text())
		self.custom_remote_source_path = str(self.custom_remote_path_src.text())
		self.custom_remote_dest_path = str(self.custom_remote_path_dst.text())
		# used later for if the user doesn't specify certain details when trying to sync
		if (not self.dest_user) or (not self.dest_ip):
			self.user_and_dest_okay = False
		if (not self.custom_source_path) or (not self.custom_dest_path):
			self.custom_source_and_dest_okay = False

	# called when the sync button is pressed
	def syncer(self):
		# make sure user has ticked atleast 1 of the sync options, return if not
		if not self.what_to_sync:
			self.show_user_info.setText("Please choose options to begin syncing")
			QTest.qWait(3000)
			self.show_user_info.setText("")
			self.update()
			return

		# create pool for threads if multiple syncs in one go
		self.pool = QThreadPool()
		self.get_sync_info()  # pull all user input/options ready for sync
		self.clear_display()  # essionally just removes welcome_banner at this point
		# all remote options
		to_check = [1, 2, 4]

		# loop through sync options ticked
		for h in self.what_to_sync:
			# if sync is remote make sure all user inputs required are filled
			if h in to_check:
				if not self.custom_source_and_dest_okay:  # make sure custom paths have user input
					self.show_user_info.setText("Please input custom paths before syncing")
					QTest.qWait(3000)
					self.show_user_info.setText("")
					self.update()
					self.custom_source_and_dest_okay = True
					return
				if not self.user_and_dest_okay:  # make sure username and ip address have user input
					self.show_user_info.setText("Please input username or ip address before syncing")
					QTest.qWait(3000)
					self.show_user_info.setText("")
					self.update()
					self.user_and_dest_okay = True
					return
			# local sync only, make sure custom paths have user input
			elif h == 3:
				if not self.custom_source_and_dest_okay:
					self.show_user_info.setText("Please input custom paths before syncing")
					QTest.qWait(3000)
					self.show_user_info.setText("")
					self.update()
					self.custom_source_and_dest_okay = True
					return
			# if all user input is filled in start the sync
			self.show_user_info.setText("Syncing...")  # give the user feedback
			QTest.qWait(1000)
			# creates the sync object, passing it all required input for sync
			self.worker = SyncThatShit(h, self.command, self.options, self.user, self.dest_user, self.dest_ip,
			                           self.custom_local_dest_path, self.custom_local_source_path,
			                           self.custom_remote_dest_path, self.custom_remote_source_path)
			# signal for when thread is complete, output ready for display
			self.worker.signals.finished.connect(self.print_sync)
			# start the thread/sync
			self.pool.start(self.worker)
		# wait for all syncs to complete
		self.pool.waitForDone()


# object used for signals when finished to start printing to display
class WorkerSignals(QObject):
	finished = pyqtSignal(int, str, str)


# object for running the sync commands
class SyncThatShit(QRunnable):
	# all user input passed to it from main window ui
	def __init__(self, header, command, options, user, dest_user, dest_ip, custom_local_dest_path,
	             custom_local_source_path, custom_remote_dest_path, custom_remote_source_path):
		QRunnable.__init__(self)
		self.header = header
		self.command = command
		self.options = options
		self.delete = False
		self.user = user
		self.dest_user = dest_user
		self.dest_ip = dest_ip
		self.custom_local_dest_path = custom_local_dest_path
		self.custom_local_source_path = custom_local_source_path
		self.custom_remote_dest_path = custom_remote_dest_path
		self.custom_remote_source_path = custom_remote_source_path
		self.source_path = ""
		self.dest_path = ""
		self.destination = ""
		self.output = ""
		self.errors = None
		self.signals = WorkerSignals()
		self.sync_sort()

	# automatically gets run as thread
	def run(self):

		try:  # used for remote options
			self.destination = self.dest_user + "@" + self.dest_ip + ":" + self.dest_path

			# obsolete from cli version(will be updated to usuable option tho)
			# ipad = self.destination + "@" + self.destination_ip + ":" + self.dest_path

			# command for local syncs
			if self.header == 3:
				p = subprocess.Popen([self.command, self.options, self.source_path, self.dest_path],
				                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)

			# obsolete from cli verion(will be updated to usuable option tho)
			elif self.header == 14:
				# p = subprocess.Popen(["scp", ipad, self.source_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				pass

			# command for remote syncs
			else:
				if self.delete:
					p = subprocess.Popen([self.command, self.options, self.source_path, self.destination, "--delete"],
					                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				else:
					p = subprocess.Popen([self.command, self.options, self.source_path, self.destination],
					                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)

			# get command output and errors for use to display in ui
			self.output, self.errors = p.communicate()
			# signal connected to print_sync, displaying the outputs of syncs
			self.signals.finished.emit(self.header, self.output, self.errors)
		# this will not be visible at all in this gui version (FIX THIS)
		except Exception as e:
			print("Ooops something went wrong there..." + "\n" + str(e))

	# sets the paths of the sync depending on what sync option/header is used
	def sync_sort(self):
		# set the option/flag
		if self.options == "d":  # default
			self.options = "-Paiurv"
		elif self.options == "c":  # compress
			self.options = "-Paiurvz"
		elif self.options == "del":  # delete outdated
			self.options = "-Paiurv"
			self.delete = True

		# sets if self.option1 is ticked
		if self.header == 1:
			self.source_path = "/home/" + self.user + "/Documents/"
			self.dest_path = "/home/" + self.dest_user + "/Documents/"

		# sets if self.option2 is ticked
		elif self.header == 2:
			self.source_path = "/home/" + self.user + "/Downloads/"
			self.dest_path = "/home/" + self.dest_user + "/Downloads/"

		# sets if self.option3 is ticked
		elif self.header == 3:
			self.source_path = self.custom_local_source_path
			self.dest_path = self.custom_local_dest_path

		# sets if self.option4 is ticked
		elif self.header == 4:
			self.source_path = self.custom_remote_source_path
			self.dest_path = self.custom_remote_dest_path

		# obsolete from cli version(will be updated to usuable option tho)
		elif self.header == 14:
			# self.source_path = "/Users/" + self.source + "/Desktop/films/"
			# self.dest_path = "/User/Library/Artworks/*"
			pass


def main():
	# create the application
	app = QApplication(sys.argv)
	# inintilze the window object
	window = Window()
	# show the window
	window.show()
	sys.exit(app.exec_())


if __name__ == "__main__":
	main()
