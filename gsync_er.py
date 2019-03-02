from __future__ import unicode_literals
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import QTest
import subprocess
import os
import sys
from getpass import getuser, getpass
import netifaces as ni
import paramiko
from scp import SCPClient
from functools import partial

'''
###################################################################################################################
								YOU NEED TO HAVE PASSWORDLESS SSH SETUP TO USE THIS
###################################################################################################################
'''
__author__ = "blaka90"
__version__ = "1.6.4"

'''
TO FIX:

test default documents sync(even linux>linux) with scp...make sure syncs and doesn't just add folder to folder

can't uncheck dest_os_* in clear settings

self.run_keygen() needs sorting for if running on different os and even diff linux distro
	
JUST TESTED ON WINDOWS WITH PYTHON 3.7.2:
	-installed openssh from settings-apps-manage option feautures-Openssh client/Openssh server
		-need to test ssh_install.py winodws


TO ADD:

possibly a way to change saved_ips incase ip changes(maybe implement in test_n_save) 

display how to use guide on output display???  (paths, generate keygen shit and that)

add more default syncing options
	
'''


# the main window
class Window(QWidget):
	def __init__(self):
		super(Window, self).__init__()
		self.user_ip = ""
		self.get_local_ip()
		self.path()
		self.start_style()
		self.user = getuser()
		self.operating_system = ""
		self.dest_operating_system = ""
		self.get_os()
		self.init_ui()
		self.options = None
		self.what_to_sync = []
		self.header = int()
		self.any_errors = False
		self.command = "rsync"
		self.custom_local_source_path = ""
		self.custom_local_dest_path = ""
		self.custom_remote_source_path = ""
		self.custom_remote_dest_path = ""
		self.user_and_dest_okay = True
		self.custom_remote_source_and_dest_okay = True
		self.custom_local_source_and_dest_okay = True

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

	def welcome_banner(self):  # nostalgia from my cli version
		if "blaka" in self.user:
			return "--_--" * 30 + "\n" + " " * 100 + "SYNC_ER" + "\n" + "_-_" * 40 + "\n"

	def get_os(self):
		if "linux" in sys.platform.lower():
			self.operating_system = "linux"
		elif sys.platform.lower().startswith("win"):
			self.operating_system = "windows"
		elif "darwin" in sys.platform.lower():
			self.operating_system = "mac"
		else:
			print("Failed to determine Operating System")

	def get_local_ip(self):
		inters = ni.interfaces()
		for inter in inters:
			try:
				ip = ni.ifaddresses(inter)[ni.AF_INET][0]['addr']
				if ip.startswith("192"):
					self.user_ip = ip
					return self.user_ip
			except (KeyError, ValueError) as er:
				print("Failed to get User IP Address")
				print(er)

	# used to show different color and duration for user feedback for show_user_info label
	def show_info_color(self, color, message, time):
		self.show_user_info.setStyleSheet("color:" + color)
		self.show_user_info.setText(message)
		QTest.qWait(time)
		self.show_user_info.setStyleSheet("color:white")
		self.show_user_info.setText("")

	# initilize the user interface
	def init_ui(self):
		"""all below code is (roughly) in decending visual order"""

		# set the name, icon and size of main window
		self.setWindowTitle("Sync_er")
		self.setWindowIcon(QIcon("syncer.png"))
		self.setGeometry(150, 100, 1400, 800)
		self.setFixedSize(1400, 800)

		"""right side of gui"""
		# not used as a textedit, but used to display output from syncs
		self.output_display = QTextEdit(self)
		self.output_display.setFixedWidth(800)
		self.output_display.setFixedHeight(750)
		self.output_display.setText(self.welcome_banner())

		# progressbar for syncs
		self.loading_bar = QLabel(self)
		self.movie = QMovie("loading.gif")
		self.loading_bar.setMovie(self.movie)
		self.loading_bar.setFixedWidth(800)
		self.loading_bar.setAlignment(Qt.AlignCenter)

		"""left side of gui"""

		# label for showing the users username
		self.user_label = QLabel(self)
		self.user_label.setText("Your Username: " + self.user)
		self.user_label.setAlignment(Qt.AlignTop)
		self.user_label.setStyleSheet('color: gray')

		# label for showing the users IP Address
		self.user_ip_label = QLabel(self)
		self.user_ip_label.setText("Your IP Address: " + self.user_ip)
		self.user_ip_label.setAlignment(Qt.AlignTop)
		self.user_ip_label.setStyleSheet('color: gray')

		# button for changing command to rsync (default)
		self.rsync_button = QPushButton("Rsync")
		self.rsync_button.setCheckable(True)
		self.rsync_button.setStyleSheet('color: green')
		self.rsync_button.setFixedWidth(100)
		self.rsync_button.clicked.connect(self.rsync_command)
		# button for changing command to scp
		self.scp_button = QPushButton("Scp")
		self.scp_button.setCheckable(True)
		self.scp_button.setStyleSheet('color: darkred')
		self.scp_button.setFixedWidth(100)
		self.scp_button.clicked.connect(self.scp_command)

		if self.operating_system == "linux":
			self.rsync_button.setChecked(True)
			self.rsync_command()
		elif self.operating_system == "mac":
			self.rsync_button.setChecked(True)
			self.rsync_command()
		elif self.operating_system == "windows":
			self.scp_button.setChecked(True)
			self.scp_command()

		# label for destination username
		self.dest_user_label = QLabel(self)
		self.dest_user_label.setText("Destination Username:")

		# user input box for the destination usenname
		self.dest_user_input = QLineEdit(self)
		self.dest_user_input.setFixedWidth(220)
		self.dest_user_input.setPlaceholderText("Username of other computer")

		# label for destination ip address
		self.dest_ip_label = QLabel(self)
		self.dest_ip_label.setText("Destination IP:")

		# user input box for destination ip address
		self.dest_ip_input = QLineEdit(self)
		self.dest_ip_input.setFixedWidth(220)
		# self.dest_ip_input.setText("192.168.0.")  # I'm lazy      ----may remove this coz find button
		self.dest_ip_input.setPlaceholderText("eg. 192.168.0.11")

		# experimental lazy way of getting saved ip's
		self.find_dest_info_button = QPushButton("Find")
		self.find_dest_info_button.setFixedWidth(60)
		self.find_dest_info_button.clicked.connect(self.get_saved_ip)

		# get the os type of destination and later try change path accordingly
		self.dest_os_label = QLabel(self)
		self.dest_os_label.setText("Destination OS:")
		# radio buttons to specify destination OS type
		self.dest_os_linux = QRadioButton("Linux")
		# linux default (linuxmasterrace)
		# self.dest_os_linux.setChecked(True)
		self.dest_os_windows = QRadioButton("Windows")
		self.dest_os_mac = QRadioButton("Mac")
		# group just these os radio buttons together
		self.os_radio_group = QButtonGroup(self)
		self.os_radio_group.addButton(self.dest_os_linux, 0)
		self.os_radio_group.addButton(self.dest_os_windows, 2)
		self.os_radio_group.addButton(self.dest_os_mac, 1)

		self.create_ssh_button = QPushButton("Generate ssh keygen/passwordless")
		self.create_ssh_button.clicked.connect(self.run_keygen)
		"""
		# group just these sync option radio buttons together
		self.sync_radio_group = QButtonGroup(self)
		self.sync_radio_group.addButton(self.sync_option1)
		self.sync_radio_group.addButton(self.sync_option2)
		self.sync_radio_group.addButton(self.sync_option3)
		self.sync_radio_group.addButton(self.sync_option4)
		"""
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

		# the options the user has to sync with (should be adding more later)
		self.option1 = QCheckBox("1.  Documents (Linux > Linux)", self)
		self.option1.stateChanged.connect(partial(self.get_header, header=1))
		self.option2 = QCheckBox("2.  Downloads (Linux > Linux)", self)
		self.option2.stateChanged.connect(partial(self.get_header, header=2))
		self.option3 = QCheckBox("3.  Custom Local Paths", self)
		self.option3.stateChanged.connect(partial(self.get_header, header=3))
		self.option4 = QCheckBox("4.  Custom Remote Paths", self)
		self.option4.stateChanged.connect(partial(self.get_header, header=4))

		# user input box for the source of local syncs
		self.custom_local_path_src = QLineEdit(self)
		self.custom_local_path_src.setPlaceholderText("Type Full Source Path   or    press -->")
		self.custom_local_path_src.setDisabled(True)
		# user input box for the destination of local syncs
		self.custom_local_path_dst = QLineEdit(self)
		self.custom_local_path_dst.setPlaceholderText("Type Full Destination Path   or      -->")
		self.custom_local_path_dst.setDisabled(True)

		# user input box for the source of remote syncs
		self.custom_remote_path_src = QLineEdit(self)
		self.custom_remote_path_src.setPlaceholderText("Type Full Source Path   or    press -->")
		self.custom_remote_path_src.setDisabled(True)
		# user input box for the destination of remote syncs
		self.custom_remote_path_dst = QLineEdit(self)
		self.custom_remote_path_dst.setPlaceholderText("Type Full Destination Path   or      -->")
		self.custom_remote_path_dst.setDisabled(True)

		# button to open the file browser for local source path
		self.custom_local_path_src_button = QPushButton("...", self)
		self.custom_local_path_src_button.setFixedWidth(20)
		self.custom_local_path_src_button.clicked.connect(partial(self.get_browser, custom_path="local_source"))
		self.custom_local_path_src_button.setDisabled(True)
		# button to open the file browser fro local destination path
		self.custom_local_path_dst_button = QPushButton("...", self)
		self.custom_local_path_dst_button.setFixedWidth(20)
		self.custom_local_path_dst_button.clicked.connect(partial(self.get_browser, custom_path="local_dest"))
		self.custom_local_path_dst_button.setDisabled(True)
		# button to open the file browser for remote source path
		self.custom_remote_path_src_button = QPushButton("...", self)
		self.custom_remote_path_src_button.setFixedWidth(20)
		self.custom_remote_path_src_button.clicked.connect(partial(self.get_browser, custom_path="remote_source"))
		self.custom_remote_path_src_button.setDisabled(True)
		# button to open the file browser for remote destination path
		self.custom_remote_path_dst_button = QPushButton("...", self)
		self.custom_remote_path_dst_button.setFixedWidth(20)
		self.custom_remote_path_dst_button.clicked.connect(partial(self.get_browser, custom_path="remote_dest"))
		self.custom_remote_path_dst_button.setDisabled(True)

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

		"""start of layouts"""

		# layout for left top row
		top_row = QHBoxLayout()
		top_row.addWidget(self.user_label)
		top_row.addWidget(self.rsync_button)
		top_row.addWidget(self.scp_button)

		# horizontal layout for custom remote user path input boxes
		h_box_remote_paths = QHBoxLayout()
		h_box_remote_paths.addWidget(self.custom_remote_path_src)
		h_box_remote_paths.addWidget(self.custom_remote_path_src_button)
		h_box_remote_paths.addWidget(self.custom_remote_path_dst)
		h_box_remote_paths.addWidget(self.custom_remote_path_dst_button)

		# horizontal layout for custom local user path input boxes
		h_box_local_paths = QHBoxLayout()
		h_box_local_paths.addWidget(self.custom_local_path_src)
		h_box_local_paths.addWidget(self.custom_local_path_src_button)
		h_box_local_paths.addWidget(self.custom_local_path_dst)
		h_box_local_paths.addWidget(self.custom_local_path_dst_button)

		# horizontal layout for buttons at bottom of ui
		h_box_buttons = QHBoxLayout()
		h_box_buttons.setContentsMargins(20, 100, 20, 20)
		h_box_buttons.addWidget(self.sync_button)
		h_box_buttons.addWidget(self.clear_settings_button)
		h_box_buttons.addWidget(self.clear_display_button)

		# horizontal layout for os radio buttons inside grid layout
		h_box_os_buttons = QHBoxLayout()
		# h_box_os_buttons.setContentsMargins(50, 0, 0, 0)
		h_box_os_buttons.addWidget(self.dest_os_linux)
		h_box_os_buttons.addWidget(self.dest_os_windows)
		h_box_os_buttons.addWidget(self.dest_os_mac)

		# grid layout for most of the user input and options
		grid = QGridLayout()
		grid.setSpacing(10)
		grid.setAlignment(Qt.AlignTop)
		grid.setContentsMargins(60, 60, 30, 60)
		grid.addWidget(self.dest_user_label, 0, 0)
		grid.addWidget(self.dest_user_input, 0, 1)
		grid.addWidget(self.find_dest_info_button, 0, 2)
		grid.addWidget(self.dest_ip_label, 1, 0)
		grid.addWidget(self.dest_ip_input, 1, 1)
		grid.addWidget(self.dest_os_label, 2, 0)
		grid.addLayout(h_box_os_buttons, 2, 1)
		if not self.has_ssh_keygen():
			grid.addWidget(self.create_ssh_button, 3, 1)
		grid.addWidget(self.sync_option_label, 4, 0)
		grid.addWidget(self.sync_option1, 5, 0)
		grid.addWidget(self.sync_option2, 5, 1)
		grid.addWidget(self.sync_option3, 6, 0)
		grid.addWidget(self.sync_option4, 6, 1)
		grid.addWidget(self.sync_option4_input, 7, 1)

		# vertical layout for the radio buttons syncing options
		v_box_options = QVBoxLayout()
		v_box_options.addWidget(self.option1)
		v_box_options.addWidget(self.option2)
		v_box_options.addWidget(self.option3)
		v_box_options.addLayout(h_box_local_paths)
		v_box_options.addWidget(self.option4)
		v_box_options.addLayout(h_box_remote_paths)

		# layout for the left hand side of ui layouts
		v_box = QVBoxLayout()
		v_box.addLayout(top_row)
		v_box.addWidget(self.user_ip_label)
		v_box.addLayout(grid)
		v_box.addLayout(v_box_options)
		v_box.addStretch(1)
		v_box.addWidget(self.show_user_info)
		v_box.addLayout(h_box_buttons)

		# vertical layout for output_display and progressbar
		v_box_right = QVBoxLayout()
		v_box_right.addWidget(self.output_display)
		v_box_right.addWidget(self.loading_bar)

		# horizontal layout to split user input on left and display on right
		h_box = QHBoxLayout()
		h_box.addLayout(v_box)
		h_box.addLayout(v_box_right)
		# h_box.addWidget(self.output_display)

		# set the layout
		self.setLayout(h_box)

	# checks if user has generated ssh keygen before and shows button to generate if not
	def has_ssh_keygen(self):
		check_path = ""
		if self.operating_system == "linux":
			check_path = "/home/{}/.ssh/".format(self.user)
		elif self.operating_system == "mac:":
			check_path = "/Users/{}/.ssh/".format(self.user)
		elif self.operating_system == "windows":
			check_path = "C:/Users/{}/.ssh/".format(self.user)
		else:
			print("Failed to set ssh path")
		if os.path.exists(check_path):
			if os.path.isfile(check_path + "id_rsa.pub"):
				return True
			else:
				return False
		else:
			return False

	def run_keygen(self):
		if self.operating_system == "linux":
			p = subprocess.Popen(["gnome-terminal", "-e", "'python3' 'ssh_install.py'"])
			out, err = p.communicate()
			self.output_display.setText(out + err)
		else:
			print("Not implemented yet")

	"""
	def run_keygen(self):
		self.get_sync_info()
		if self.dest_user_input.text() == "":
			self.show_info_color("red", "Please fill out all destination Info", 3000)
			return
		if self.dest_ip_input.text() == "":
			self.show_info_color("red", "Please fill out all destination Info", 3000)
			return
		if self.dest_operating_system == "":
			return
		if self.operating_system == "mac:":
			command = "ssh-gen"
		else:
			command = "ssh-keygen"

		self.show_info_color("white", "Please type a new password to encrypt your ssh keys\n"
		                              "into the terminal", 0)
		'''
		text, okpressed = QInputDialog.getText(self, "SSH Password", "Password:", QLineEdit.Password, "")
		if okpressed and text != '':
			text = text.encode()'''

		p = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
		                     stdin=subprocess.PIPE)

		outp, err = p.communicate(input=b"\n")

		if outp and not err:
			self.show_info_color("green", "Successfully Created ssh keys!", 5000)
			self.run_passwordless()
		else:
			self.show_info_color("red", "Failed to create ssh keys!", 5000)
			self.output_display.setText("errors:{}".format(err.decode()))

	def run_passwordless(self):
		ssh_path = ""
		if self.operating_system == "linux":
			ssh_path = "/home/{}/.ssh/".format(self.user)
		elif self.operating_system == "mac:":
			ssh_path = "/Users/{}/.ssh/".format(self.user)
		elif self.operating_system == "windows":
			ssh_path = "C:/Users/{}/.ssh/".format(self.user)
		os.chdir(ssh_path)
		command = "ssh-copy-id -i id_rsa.pub " + self.dest_user + "@" + self.dest_ip
		p = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
		                     stdin=subprocess.PIPE)

		outp, err = p.communicate()

		if outp and not err:
			self.show_info_color("green", "Successfully Transfered ssh keys!", 5000)
			self.test_n_save()
		else:
			self.show_info_color("red", "Failed to Transfer ssh keys!", 5000)
			self.output_display.setText("errors:{}".format(err.decode()))
		"""

	# check if user and ip are already saved and save if not
	def test_n_save(self):
		# self.show_info_color("yellow", "Trying to save User data", 3000)
		to_save = self.dest_user + " " + self.dest_ip + " " + self.dest_operating_system + "\n"
		try:
			saved_ips = open("saved_ips.txt", "r")
			for line in saved_ips.readlines():
				if line == to_save:
					saved_ips.close()
					# self.show_info_color("darkred", "User already saved!", 3000)
					return

		except FileNotFoundError:
			self.show_info_color("darkred", "Failed to load Previous user data", 5000)

		# make sure the destination is online(exists)
		if self.operating_system == "windows":
			response = os.system("ping -n 1 " + self.dest_ip)
		else:
			response = os.system("ping -c 1 " + self.dest_ip)

		# and then check the response...
		if response == 0:
			# if valid destination save to saved_ips.txt list
			with open("saved_ips.txt", "a+") as f:
				f.write(to_save)
				f.close()
				self.show_info_color("green", "successfully saved User data!", 3000)

	# if user has entered connected to destination before, can get the ip without typing it
	def get_saved_ip(self):
		if self.dest_user_input.text() == "":
			self.show_info_color("darkred", "You must specify Username to find Destination user's info!", 5000)
			return
		else:  # pull the data from ui
			self.get_sync_info()
		try:
			# check for user in saved_ips list and set in dest_ip_input
			saved_ips = open("saved_ips.txt", "r")
			saved_ips_lines = saved_ips.readlines()
			saved_ips.close()
			num_lines = len(saved_ips_lines)
			num = 0
			for line in saved_ips_lines:
				ndest_data = line.split()
				num += 1
				if self.dest_user == ndest_data[0]:
					self.dest_ip_input.setText(ndest_data[1])
					if ndest_data[2] == "linux":
						self.dest_os_linux.setChecked(True)
					elif ndest_data[2] == "mac":
						self.dest_os_mac.setChecked(True)
					elif ndest_data[2] == "windows":
						self.dest_os_windows.setChecked(True)
					return
				elif num == num_lines:
					self.show_info_color("darkred", "User information is not saved for this User!", 5000)
					self.dest_ip_input.setText("")
				else:
					continue
		except FileNotFoundError:
			self.show_info_color("darkred", "Destination Username and IP must have been entered at "
			                                "least once \nfor this Feature to work!", 5000)

	def get_dest_os(self):
		if self.dest_os_linux.isChecked():
			self.dest_operating_system = "linux"
		elif self.dest_os_mac.isChecked():
			self.dest_operating_system = "mac"
		elif self.dest_os_windows.isChecked():
			self.dest_operating_system = "windows"

		return self.dest_operating_system

	# create file manager object for local/remote source/destination and capture data
	def get_browser(self, custom_path):
		if custom_path == "remote_dest":
			if self.dest_user_input.text() == "":
				self.show_info_color("red", "This Option only works if destination Username has been input\n"
				                            "EXPERIMENTAL", 3000)
				return
			else:
				self.brow = MyFileBrowser(self.operating_system)
				self.brow.sig.return_data.connect(partial(self.get_browser_recv, custom_path=custom_path))
		else:
			self.brow = MyFileBrowser(self.operating_system)
			self.brow.sig.return_data.connect(partial(self.get_browser_recv, custom_path=custom_path))

	# receive data from file manager object signal and set to local/remote source/destination input
	def get_browser_recv(self, data, custom_path):
		if os.path.isfile(data):
			if custom_path == "local_source":
				self.custom_local_path_src.setText(data)
			elif custom_path == "local_dest":
				self.custom_local_path_dst.setText(data)
			elif custom_path == "remote_source":
				self.custom_remote_path_src.setText(data)
			elif custom_path == "remote_dest":
				new_data = data.replace(self.user, self.dest_user_input.text())
				self.custom_remote_path_dst.setText(new_data)

		else:
			ndata = data + "/"
			if custom_path == "local_source":
				self.custom_local_path_src.setText(ndata)
			elif custom_path == "local_dest":
				self.custom_local_path_dst.setText(ndata)
			elif custom_path == "remote_source":
				self.custom_remote_path_src.setText(ndata)
			# experimental-get remote user path and try just swapping usernames given paths should be same bar username
			elif custom_path == "remote_dest":
				new_data = ndata.replace(self.user, self.dest_user_input.text())
				self.custom_remote_path_dst.setText(new_data)

	# (on by default) button to enable rsync command instead of scp
	def rsync_command(self):
		if self.operating_system == "windows":
			self.show_info_color("darkred", "RSYNC OPTION IS NOT AVAILABLE ON WINDOWS\n...\n"
			                                "*this option will run but is not advised*\n...\n"
			                                "if you have actaully managed install rsync in windows ignore this\n", 8000)
		self.command = "rsync"
		self.rsync_button.setStyleSheet('color: green')
		self.scp_button.setStyleSheet('color: darkred')
		self.scp_button.setChecked(False)

	# button to enable scp command instead of rsync
	def scp_command(self):
		self.command = "scp"
		self.scp_button.setStyleSheet('color: green')
		self.rsync_button.setStyleSheet('color: darkred')
		self.rsync_button.setChecked(False)

	# disables input for custom option/flag if unchecked...vice versa
	def check_option(self, enabled):
		if enabled:
			self.sync_option4_input.setDisabled(False)
		else:
			self.sync_option4_input.setDisabled(True)

	# if any checkbox is ticked, add to or remove from what_to_sync list
	def get_header(self, state, header):
		if state == Qt.Checked:
			self.what_to_sync.append(header)
			# Disable input unless tick box is checked
			if header == 3:
				self.custom_local_path_src.setDisabled(False)
				self.custom_local_path_dst.setDisabled(False)
				self.custom_local_path_src_button.setDisabled(False)
				self.custom_local_path_dst_button.setDisabled(False)
			if header == 4:
				self.custom_remote_path_src.setDisabled(False)
				self.custom_remote_path_dst.setDisabled(False)
				self.custom_remote_path_src_button.setDisabled(False)
				self.custom_remote_path_dst_button.setDisabled(False)
		else:
			self.what_to_sync.remove(header)
			if header == 3:
				self.custom_local_path_src.setDisabled(True)
				self.custom_local_path_dst.setDisabled(True)
				self.custom_local_path_src_button.setDisabled(True)
				self.custom_local_path_dst_button.setDisabled(True)
			if header == 4:
				self.custom_remote_path_src.setDisabled(True)
				self.custom_remote_path_dst.setDisabled(True)
				self.custom_remote_path_src_button.setDisabled(True)
				self.custom_remote_path_dst_button.setDisabled(True)

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
		self.dest_os_linux.setChecked(False)
		self.dest_os_linux.show()
		self.dest_os_mac.setChecked(False)
		self.dest_os_windows.setChecked(False)
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
		self.show_user_info.setStyleSheet("color: white")
		self.options = None
		self.custom_local_source_path = ""
		self.custom_local_dest_path = ""
		self.custom_remote_source_path = ""
		self.custom_remote_dest_path = ""
		self.any_errors = False
		if self.operating_system == "linux":
			self.rsync_button.setChecked(True)
			self.rsync_command()
		elif self.operating_system == "mac":
			self.rsync_button.setChecked(True)
			self.rsync_command()
		elif self.operating_system == "windows":
			self.scp_button.setChecked(True)
			self.scp_command()

	# clears the output display only when clear display button is pressed
	def clear_display(self):
		self.output_display.setText("")
		self.update()

	# used as a flag to display correct user feedback if errors in sync
	def was_there_errors(self, err):
		self.any_errors = err

	def update_progress(self, switch):
		if switch:
			self.movie.start()
			self.loading_bar.show()
		else:
			self.movie.stop()
			self.loading_bar.hide()

	# used to print to display what output is showing after sync is complete
	@pyqtSlot(int, str, str)  # DO I EVEN NEED THIS SINCE I CONNECT THE SIGNAL ANYWAY?
	def print_sync(self, header, output, errors):
		# show what sync option/header was used for corresponding output and then display it
		headers = {
			1: "Documents (Linux > Linux)", 2: "Downloads (Linux > Linux)",
			3: "Custom Local Paths", 4: "Custom Remote Paths"}
		# if only 1 sync option is getting used this will run
		if self.output_display.toPlainText() == "":
			if len(errors) != 0:
				self.output_display.setText("#" * 77 + "\n" + " " * 60 + "Showing output for " + headers[header] +
				                            " sync" + "\n" + "#" * 77 + "\n\n" + output + "\n\n" + "~" * 91 + "\n"
				                            + " " * 100 + "ERRORS" + "\n" + "~" * 91 + "\n\n" + errors)

			else:
				self.output_display.setText("#" * 77 + "\n" + " " * 60 + "Showing output for " + headers[header] +
				                            " sync" + "\n" + "#" * 77 + "\n\n" + output)

		# if multiple syncs are getting run it will append the ouputs together for display
		else:
			if len(errors) != 0:
				self.output_display.append("#" * 77 + "\n" + " " * 60 + "Showing output for " + headers[header] +
				                           " sync" + "\n" + "#" * 77 + "\n\n" + output + "\n\n" + "~" * 91 + "\n"
				                           + " " * 100 + "ERRORS" + "\n" + "~" * 91 + "\n\n" + errors)

			else:
				self.output_display.append("#" * 77 + "\n" + " " * 60 + "Showing output for " + headers[header] +
				                           " sync" + "\n" + "#" * 77 + "\n\n" + output)

		self.update()

	# grab all the information from user inputs needed for the sync
	def get_sync_info(self):
		self.get_options()
		self.get_dest_os()
		self.dest_user = str(self.dest_user_input.text())
		self.dest_ip = str(self.dest_ip_input.text())
		self.custom_local_source_path = str(self.custom_local_path_src.text())
		self.custom_local_dest_path = str(self.custom_local_path_dst.text())
		self.custom_remote_source_path = str(self.custom_remote_path_src.text())
		self.custom_remote_dest_path = str(self.custom_remote_path_dst.text())
		# used later for if the user doesn't specify certain details when trying to sync
		if (not self.dest_user) or (not self.dest_ip):
			self.user_and_dest_okay = False
		else:
			self.user_and_dest_okay = True
		if (not self.custom_remote_source_path) or (not self.custom_remote_dest_path):
			self.custom_remote_source_and_dest_okay = False
		else:
			self.custom_remote_source_and_dest_okay = True
		if (not self.custom_local_source_path) or (not self.custom_local_dest_path):
			self.custom_local_source_and_dest_okay = False
		else:
			self.custom_local_source_and_dest_okay = True
		self.update()

	# called when the sync button is pressed
	def syncer(self):
		# make sure user has ticked atleast 1 of the sync options, return if not
		if not self.what_to_sync:
			self.show_info_color("red", "Please choose options to begin syncing", 3000)
			return

		# create pool for threads if multiple syncs in one go
		self.pool = QThreadPool()
		self.get_sync_info()  # pull all user input/options ready for sync
		self.clear_display()  # essionally just removes welcome_banner at this point
		# all remote options
		to_check = [1, 2]

		# loop through sync options ticked
		for h in self.what_to_sync:
			# if sync is remote make sure all user inputs required are filled
			if h in to_check:
				if not self.user_and_dest_okay:  # make sure username and ip address have user input
					self.show_info_color("darkred", "Please input username or ip address before syncing", 3000)
					self.user_and_dest_okay = True
					return
				if self.dest_operating_system == "":
					self.show_info_color("darkred", "Please choose Destination Operating System type", 3000)
					return
			# local sync only, make sure custom paths have user input
			elif h == 3:
				if not self.custom_local_source_and_dest_okay:
					self.show_info_color("darkred", "Please input custom paths before syncing", 3000)
					self.custom_local_source_and_dest_okay = True
					return
			elif h == 4:
				if not self.custom_remote_source_and_dest_okay:  # make sure custom paths have user input
					self.show_info_color("darkred", "Please input custom paths before syncing", 3000)
					self.custom_remote_source_and_dest_okay = True
					return
				if not self.user_and_dest_okay:  # make sure username and ip address have user input
					self.show_info_color("darkred", "Please input username or ip address before syncing", 3000)
					self.user_and_dest_okay = True
					return
				if self.dest_operating_system == "":
					self.show_info_color("darkred", "Please choose Destination Operating System type", 3000)
					return
			self.test_n_save()
			# if all user input is filled in start the sync
			self.show_user_info.setText("Syncing...")  # give the user feedback
			self.update_progress(True)
			QTest.qWait(1000)
			# creates the sync object, passing it all required input for sync
			self.worker = SyncThatShit(h, self.command, self.options, self.user, self.dest_user, self.dest_ip,
			                           self.custom_local_dest_path, self.custom_local_source_path,
			                           self.custom_remote_dest_path, self.custom_remote_source_path,
			                           self.operating_system, self.dest_operating_system)
			# signal to let show_user_info know if any errors occured changing color and user feedback
			self.worker.signals.sync_errors.connect(self.was_there_errors)
			# signal for when thread is complete, output ready for display
			self.worker.signals.finished.connect(self.print_sync)
			# start the thread/sync
			self.pool.start(self.worker)
		# wait for all syncs to complete
		self.pool.waitForDone()
		self.update_progress(False)
		self.sync_complete()

	def sync_complete(self):
		QTest.qWait(100)
		if self.any_errors:
			self.show_info_color("yellow", "Sync Completed!\nbut...\n Errors have occured!", 8000)
		else:
			self.show_info_color("green", "Sync Completed!", 8000)
		self.any_errors = False


# object used for signals when finished to start printing to display
class WorkerSignals(QObject):
	finished = pyqtSignal(int, str, str)
	# used to let show_user_info if any errors occured for coloring and feedback
	sync_errors = pyqtSignal(bool)


# object for running the sync commands
class SyncThatShit(QRunnable):
	# all user input passed to it from main window ui
	def __init__(self, header, command, options, user, dest_user, dest_ip, custom_local_dest_path,
	             custom_local_source_path, custom_remote_dest_path, custom_remote_source_path, user_os, dest_os):
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
		self.user_os = user_os
		self.dest_os = dest_os
		self.source_path = ""
		self.dest_path = ""
		self.destination = ""
		self.output = ""
		self.errors = ""
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
				if self.command == "rsync":
					if self.delete:
						p = subprocess.Popen(
							[self.command, self.options, self.source_path, self.destination, "--delete"],
							stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					else:
						p = subprocess.Popen([self.command, self.options, self.source_path, self.destination],
						                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)

				else:
					p = subprocess.Popen([self.command, "-rv", self.source_path, self.destination],
					                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					# self.scp_copy()

			"""
			if self.command == "scp":
				# self.output = self.output.decode()
				# self.errors = self.errors.decode()
				self.get_scp_output()
			else:"""
			# get command output and errors for use to display in ui
			self.output, self.errors = p.communicate()
			self.output = self.output.decode()
			self.errors = self.errors.decode()
			# get scp output and then clean up scp output
			if self.command == "scp":
				self.get_scp_output()
			# signal connected to print_sync, displaying the outputs of syncs
			if self.errors != "":
				self.signals.sync_errors.emit(True)
			self.signals.finished.emit(self.header, self.output, self.errors)
		# display stderr
		except Exception as e:
			err = "Ooops something went wrong there..." + "\n" + str(e)
			self.signals.finished.emit(self.header, self.output, err)

	def scp_copy(self):
		hostname = self.dest_ip
		port = 22
		try:
			client = paramiko.SSHClient()
			client.load_system_host_keys()
			client.connect(hostname=hostname, port=port, username=self.dest_user)
			with SCPClient(client.get_transport()) as scp:
				if os.path.isfile(self.source_path):
					scp.put(self.source_path, self.dest_path)
				else:
					scp.put(self.source_path, recursive=True, remote_path=self.dest_path)
			# scp.get(self.dest_path, self.source_path)
			scp.close()
			client.close()
		except Exception as e:
			print(e)
			self.password = getpass()
			client = paramiko.SSHClient()
			client.load_system_host_keys()
			client.connect(hostname=hostname, port=port, username=self.dest_user, passphrase=self.password)
			with SCPClient(client.get_transport()) as scp:
				if os.path.isfile(self.source_path):
					scp.put(self.source_path, self.dest_path)
				else:
					scp.put(self.source_path, recursive=True, remote_path=self.dest_path)
			# scp.get(self.dest_path, self.source_path)
			scp.close()
			client.close()

	# sets the paths of the sync depending on what sync option/header is used
	def sync_sort(self):
		# force scp if windows is involved
		if self.dest_os == "windows":
			if self.user_os != "windows":
				self.command = "scp"
		# set the option/flag
		if self.options == "d":  # default
			self.options = "-Paiurv"
		elif self.options == "c":  # compress
			self.options = "-Paiurvz"
		elif self.options == "del":  # delete destination dir before copying
			self.options = "-Paiurv"
			self.delete = True

		# sets if self.option1 is ticked
		if self.header == 1:
			if self.user_os == "linux":
				self.source_path = "/home/" + self.user + "/Documents/"
			elif self.user_os == "mac":
				self.source_path = "/Users/" + self.user + "/Documents/"
			elif self.user_os == "windows":
				self.source_path = "C:/Users/" + self.user + "/Documents/"

			if self.dest_os == "linux":
				self.dest_path = "/home/" + self.dest_user + "/Documents/"
			elif self.dest_os == "mac":
				self.dest_path = "/Users/" + self.dest_user + "/Documents/"
			elif self.dest_os == "windows":
				self.dest_path = "C:/Users/" + self.dest_user + "/Documents/"

		# sets if self.option2 is ticked
		elif self.header == 2:
			if self.user_os == "linux":
				self.source_path = "/home/" + self.user + "/Downloads/"
			elif self.user_os == "mac":
				self.source_path = "/Users/" + self.user + "/Downloads/"
			elif self.user_os == "windows":
				self.source_path = "C:/Users/" + self.user + "/Downloads/"

			if self.dest_os == "linux":
				self.dest_path = "/home/" + self.dest_user + "/Downloads/"
			elif self.dest_os == "mac":
				self.dest_path = "/Users/" + self.dest_user + "/Downloads/"
			elif self.dest_os == "windows":
				self.dest_path = "C:/Users/" + self.dest_user + "/Downloads/"

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

	# scp is weird with output so this frankenstein will have to do for now
	def get_scp_output(self):
		out_buff = ""
		err_buff = ""
		for line in self.errors.splitlines():
			if line.startswith("Executing"):
				out_buff += line + "\n"
			elif line.startswith("OpenSSH"):
				out_buff += line + "\n\n"
			elif line.startswith("Entering"):
				out_buff += line + "\n"
			elif line.startswith("Sink"):
				out_buff += line + "\n"
			elif line.startswith("Sending"):
				out_buff += line + "\n"
			elif line.startswith("Transferred"):
				out_buff += "\n" + line + "\n"
			elif line.startswith("Bytes"):
				out_buff += line
			elif line.startswith("ssh"):
				err_buff += line + "\n"
			elif line.startswith("lost"):
				err_buff += line + "\n"
			else:
				continue
		self.output = out_buff
		self.errors = err_buff


# used for MyFileBrowser to return path through signal
class BrowserSignal(QObject):
	return_data = pyqtSignal(str)


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
