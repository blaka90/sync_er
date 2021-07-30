from __future__ import unicode_literals
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import QTest
import subprocess
import os
import sys
from Crypto.PublicKey import RSA
from getpass import getuser
import netifaces as ni
import paramiko
from scp import SCPClient, SCPException
from functools import partial
import nmap as nm
import socket

'''
###################################################################################################################
    THIS PROGRAM WILL GENERATE A PASSWORDLESS RSA KEY PAIR(IF NONE EXISTS) & SETUP PASSWORDLESS SSH CONNECTIONS
###################################################################################################################
'''

__author__ = "blaka90"
__version__ = "0.7.6"


# the main window
class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        # self.nd = NetDiscovery()
        # self.nd.signals.network_list.connect(self.get_network_list)
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
        self.try_passphrase = False
        self.append = False
        self.finish_er = []
        self.available_hosts = None
        # create pool for threads if multiple syncs in one go
        self.pool = QThreadPool()
        self.pool.setMaxThreadCount(8)

    @staticmethod
    def start_style():
        # sets the window to dark mode with the fusion styling
        # from PyQt5.QtGui import * and from PyQt5.QtCore import * are needed mostly just for this to run correctly
        qApp.setStyle("Oxygen")
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
            return "--_--" * 38 + "\n" + " " * 115 + "SYNC_ER" + "\n" + "_-_" * 53 + "\n"

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
        self.statusbar.setStyleSheet("color:" + color)
        self.statusbar.showMessage(message, time)

    # initilize the user interface
    def init_ui(self):
        """all below code is (roughly) in decending visual order"""

        # set the name, icon and size of main window
        self.setWindowTitle("Sync_er")
        self.setWindowIcon(QIcon("resources/syncer.png"))
        self.setGeometry(150, 100, 1450, 800)
        self.setFixedSize(1450, 800)
        # self.setStyleSheet("background-color: black")

        """right side of gui"""
        # not used as a textedit, but used to display output from syncs
        self.output_display = QTextEdit(self)
        self.output_display.setFixedWidth(800)
        self.output_display.setFixedHeight(750)
        self.output_display.setCursorWidth(0)
        self.output_display.setText(self.welcome_banner())
        if "blaka" in self.user:
            self.output_display.setStyleSheet("background-image: url(resources/output_display.jpeg); color: lightblue")

        # loadingbar gif for syncs
        self.loading_bar = QLabel(self)
        self.movie = QMovie("resources/loading.gif")
        self.loading_bar.setMovie(self.movie)
        self.loading_bar.setFixedWidth(570)
        self.loading_bar.setAlignment(Qt.AlignCenter)

        """left side of gui"""

        # label for showing the users username
        self.user_label = QLabel(self)
        self.user_label.setText("Username: " + self.user)
        self.user_label.setAlignment(Qt.AlignTop)
        self.user_label.setStyleSheet('color: black')

        # label for showing the users IP Address
        self.user_ip_label = QLabel(self)
        self.user_ip_label.setText("IP Address: " + self.user_ip)
        self.user_ip_label.setAlignment(Qt.AlignTop)
        self.user_ip_label.setStyleSheet('color: black')

        # button for changing command to rsync (default)
        self.rsync_button = QPushButton("Rsync")
        self.rsync_button.setCheckable(True)
        self.rsync_button.setStyleSheet('background-color: blue; color: green')
        self.rsync_button.setFixedWidth(100)
        self.rsync_button.clicked.connect(self.rsync_command)
        # button for changing command to scp
        self.scp_button = QPushButton("Scp")
        self.scp_button.setCheckable(True)
        self.scp_button.setStyleSheet('background-color: blue; color: darkred')
        self.scp_button.setFixedWidth(100)
        self.scp_button.clicked.connect(self.scp_command)

        # hides the output window
        self.hide_op = QCheckBox("Hide Display", self)
        self.hide_op.stateChanged.connect(self.hide_output)
        self.hide_op.setFixedWidth(120)
        self.hide_op.setStyleSheet("color: black")

        # label for section Destination options
        self.system_label_dest = QLabel(self)
        self.system_label_dest.setText("Destination Options")
        self.system_label_dest.setStyleSheet("color: gray")
        self.system_label_dest.setAlignment(Qt.AlignCenter)

        # label for destination username
        self.dest_user_label = QLabel(self)
        self.dest_user_label.setText("Destination Username:")

        # user input box for the destination usenname
        self.dest_user_input = QLineEdit(self)
        self.dest_user_input.setFixedWidth(220)
        self.dest_user_input.setPlaceholderText("Username of other computer")

        # experimental lazy way of getting saved ip's
        self.find_dest_info_button = QPushButton("Find")
        self.find_dest_info_button.setFixedWidth(60)
        self.find_dest_info_button.clicked.connect(self.find_ips)
        # self.find_dest_info_button.setStyleSheet("background-color: blue; color: black")

        # label for destination ip address
        self.dest_ip_label = QLabel(self)
        self.dest_ip_label.setText("Destination IP:")

        # user input box for destination ip address
        self.dest_ip_input = QLineEdit(self)
        self.dest_ip_input.setFixedWidth(220)
        # self.dest_ip_input.setText("192.168.0.")  # I'm lazy      ----may remove this coz find button
        self.dest_ip_input.setPlaceholderText("eg. 192.168.0.11")

        # easier way of getting saved ip's
        self.get_added_button = QPushButton("choose")
        self.get_added_button.setFixedWidth(60)
        self.get_added_button.clicked.connect(self.get_added_user)
        # self.get_added_button.setStyleSheet("background-color: blue; color: black")

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

        # only shows if ssh is not already setup from this system
        self.gen_ssh_keys_button = QPushButton("Generate SSH Keygen")
        self.gen_ssh_keys_button.clicked.connect(self.run_keygen)
        # self.gen_ssh_keys_button.setStyleSheet("background-color: blue; color: black")

        self.add_user = QPushButton("Add New Destination")
        self.add_user.clicked.connect(self.run_add_user)
        # self.add_user.setStyleSheet("background-color: darkblue; color: black")

        # label for section flags used for syncs
        self.system_label_flag_options = QLabel(self)
        self.system_label_flag_options.setText("Flag Options")
        self.system_label_flag_options.setAlignment(Qt.AlignCenter)
        self.system_label_flag_options.setStyleSheet("color: gray")
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

        # label for section syncing options
        self.system_label_sync_options = QLabel(self)
        self.system_label_sync_options.setText("Sync_ing Options")
        self.system_label_sync_options.setAlignment(Qt.AlignCenter)
        self.system_label_sync_options.setStyleSheet("color: gray")

        # the options the user has to sync with (should be adding more later)
        self.option1 = QCheckBox("  Desktop", self)
        self.option1.stateChanged.connect(partial(self.get_header, header=1))
        self.option2 = QCheckBox("  Documents", self)
        self.option2.stateChanged.connect(partial(self.get_header, header=2))
        self.option3 = QCheckBox("  Downloads", self)
        self.option3.stateChanged.connect(partial(self.get_header, header=3))
        self.option4 = QCheckBox("  Music", self)
        self.option4.stateChanged.connect(partial(self.get_header, header=4))
        self.option5 = QCheckBox("  Pictures", self)
        self.option5.stateChanged.connect(partial(self.get_header, header=5))
        self.option6 = QCheckBox("  Videos", self)
        self.option6.stateChanged.connect(partial(self.get_header, header=6))
        self.option7 = QCheckBox("  Custom Local Paths", self)
        self.option7.stateChanged.connect(partial(self.get_header, header=7))
        self.option8 = QCheckBox("  Custom Remote Paths", self)
        self.option8.stateChanged.connect(partial(self.get_header, header=8))

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
        self.sync_button.setFixedWidth(250)
        self.sync_button.setFixedHeight(50)
        self.sync_button.setStyleSheet("font-size: 20px; color: black")
        # button to clear all user input
        self.clear_settings_button = QPushButton("Clear Settings", self)
        self.clear_settings_button.clicked.connect(self.clear_settings)
        self.clear_settings_button.setFixedWidth(150)
        self.clear_settings_button.setFixedHeight(25)
        # self.clear_settings_button.setStyleSheet("background-color: blue; color: black")
        # button to clear the display  only
        self.clear_display_button = QPushButton("Clear Display", self)
        self.clear_display_button.clicked.connect(self.clear_display)
        self.clear_display_button.setFixedWidth(150)
        self.clear_display_button.setFixedHeight(25)
        # self.clear_display_button.setStyleSheet("background-color: blue; color: black")

        # should have used QMainWindow but am here now -_-
        self.statusbar = QStatusBar(self)

        """start of layouts"""

        # layout for left top row
        top_row1 = QHBoxLayout()
        top_row1.addWidget(self.user_label)
        top_row1.addWidget(self.rsync_button)
        top_row1.addWidget(self.scp_button)

        top_row2 = QHBoxLayout()
        top_row2.addWidget(self.user_ip_label)
        # top_row2.setAlignment(Qt.AlignRight)
        top_row2.addWidget(self.hide_op)

        # ride side of bottom buttons
        clear_buttons = QVBoxLayout()
        clear_buttons.addWidget(self.clear_display_button)
        clear_buttons.addWidget(self.clear_settings_button)
        clear_buttons.setAlignment(Qt.AlignRight)

        # horizontal layout for buttons at bottom of ui
        h_box_buttons = QHBoxLayout()
        h_box_buttons.setContentsMargins(100, 20, 20, 20)
        h_box_buttons.addWidget(self.sync_button)
        h_box_buttons.addLayout(clear_buttons)
        # h_box_buttons.addWidget(self.clear_settings_button)
        # h_box_buttons.addWidget(self.clear_display_button)

        # horizontal layout for os radio buttons inside destination_grid layout
        h_box_os_buttons = QHBoxLayout()
        # h_box_os_buttons.setContentsMargins(50, 0, 0, 0)
        h_box_os_buttons.addWidget(self.dest_os_linux)
        h_box_os_buttons.addWidget(self.dest_os_windows)
        h_box_os_buttons.addWidget(self.dest_os_mac)

        # destination_grid layout for most of the user input and options
        destination_grid = QGridLayout()
        destination_grid.setSpacing(20)
        destination_grid.setAlignment(Qt.AlignTop)
        destination_grid.setContentsMargins(60, 10, 30, 20)
        destination_grid.addWidget(self.dest_user_label, 0, 0)
        destination_grid.addWidget(self.dest_user_input, 0, 1)
        destination_grid.addWidget(self.find_dest_info_button, 0, 2)
        destination_grid.addWidget(self.dest_ip_label, 1, 0)
        destination_grid.addWidget(self.dest_ip_input, 1, 1)
        destination_grid.addWidget(self.get_added_button, 1, 2)
        destination_grid.addWidget(self.dest_os_label, 2, 0)
        destination_grid.addLayout(h_box_os_buttons, 2, 1)
        if not self.has_ssh_keygen():
            destination_grid.addWidget(self.gen_ssh_keys_button, 3, 0)
        destination_grid.addWidget(self.add_user, 3, 1)

        flag_options_grid = QGridLayout()
        flag_options_grid.setContentsMargins(50, 10, 50, 20)
        flag_options_grid.addWidget(self.sync_option1, 0, 0)
        flag_options_grid.addWidget(self.sync_option2, 0, 1)
        flag_options_grid.addWidget(self.sync_option3, 0, 2)
        flag_options_grid.addWidget(self.sync_option4, 0, 3)
        flag_options_grid.addWidget(self.sync_option4_input, 1, 3)

        sync_options_grid = QGridLayout()
        sync_options_grid.setContentsMargins(0, 10, 0, 10)
        sync_options_grid.addWidget(self.option1, 0, 0)
        sync_options_grid.addWidget(self.option2, 1, 0)
        sync_options_grid.addWidget(self.option3, 2, 0)
        sync_options_grid.addWidget(self.option4, 0, 2)
        sync_options_grid.addWidget(self.option5, 1, 2)
        sync_options_grid.addWidget(self.option6, 2, 2)
        sync_options_grid.addWidget(self.option7, 3, 0)
        sync_options_grid.addWidget(self.custom_local_path_src, 4, 0)
        sync_options_grid.addWidget(self.custom_local_path_src_button, 4, 1)
        sync_options_grid.addWidget(self.custom_local_path_dst, 4, 2)
        sync_options_grid.addWidget(self.custom_local_path_dst_button, 4, 3)
        sync_options_grid.addWidget(self.option8, 5, 0)
        sync_options_grid.addWidget(self.custom_remote_path_src, 6, 0)
        sync_options_grid.addWidget(self.custom_remote_path_src_button, 6, 1)
        sync_options_grid.addWidget(self.custom_remote_path_dst, 6, 2)
        sync_options_grid.addWidget(self.custom_remote_path_dst_button, 6, 3)

        # layout for the left hand side of ui layouts
        v_box_left = QVBoxLayout()
        v_box_left.addLayout(top_row1)
        v_box_left.addLayout(top_row2)
        v_box_left.addSpacing(10)
        v_box_left.addWidget(self.system_label_dest)
        v_box_left.addLayout(destination_grid)
        v_box_left.addWidget(self.system_label_flag_options)
        v_box_left.addLayout(flag_options_grid)
        v_box_left.addWidget(self.system_label_sync_options)
        v_box_left.addLayout(sync_options_grid)
        v_box_left.addStretch(1)
        # v_box_left.addWidget(self.show_user_info)
        v_box_left.addWidget(self.loading_bar)
        v_box_left.addLayout(h_box_buttons)

        # vertical layout for output_display and progressbar
        v_box_right = QVBoxLayout()
        v_box_right.addWidget(self.output_display)
        # v_box_right.addWidget(self.loading_bar)

        # horizontal layout to split user input on left and display on right
        h_box = QHBoxLayout()
        h_box.addLayout(v_box_left)
        h_box.addLayout(v_box_right)

        v = QVBoxLayout()
        v.addLayout(h_box)
        v.addWidget(self.statusbar)

        # this is out of place but breaks scp_command on startup on windows otherwise!-_-
        # sets the right command for os
        if self.operating_system == "linux":
            self.rsync_button.setChecked(True)
            self.rsync_command()
        elif self.operating_system == "mac":
            self.rsync_button.setChecked(True)
            self.rsync_command()
        elif self.operating_system == "windows":
            self.scp_button.setChecked(True)
            self.scp_command()

        # set the layout
        self.setLayout(v)

    def hide_output(self, state):
        if state == Qt.Checked:
            self.output_display.hide()
            self.setFixedSize(644, 800)
        else:
            self.output_display.show()
            self.setFixedSize(1450, 800)

    # checks if user has generated ssh keygen before and shows button to generate if not
    def has_ssh_keygen(self):
        if self.operating_system == "linux":
            self.ssh_path = "/home/{}/.ssh/".format(self.user)
        elif self.operating_system == "mac:":
            self.ssh_path = "/Users/{}/.ssh/".format(self.user)
        elif self.operating_system == "windows":
            self.ssh_path = "C:/Users/{}/.ssh/".format(self.user)
        else:
            print("Failed to set ssh path")
        if os.path.exists(self.ssh_path):
            if os.path.isfile(self.ssh_path + "id_rsa"):
                if os.path.isfile("resources/syncer_keygen.txt"):
                    self.try_passphrase = False
                else:
                    self.try_passphrase = True
                return True
            else:
                self.show_info_color("yellow", "It appears this is you're first run...Click 'Generate SSH Keygen' "
                                               "to get started!", 15000)
                return False
        else:
            os.mkdir(self.ssh_path, 0o700)
            self.show_info_color("yellow", "It appears this is you're first run...Click 'Generate SSH Keygen' "
                                           "to get started!", 15000)
            return False

    def check_for_saved_ips(self):
        if not os.path.isfile("resources/" + self.user + "_saved_ips.txt"):
            with open("resources/" + self.user + "_saved_ips.txt", "w") as f:
                f.close()

    def run_add_user(self):
        self.check_for_saved_ips()
        self.get_sync_info()
        if self.dest_user_input.text() == "":
            self.show_info_color("red", "Please fill out all Destination Info", 3000)
            return
        if self.dest_ip_input.text() == "":
            self.show_info_color("red", "Please fill Destination Ip Address", 3000)
            return
        if self.dest_operating_system == "":
            self.show_info_color("red", "Please select Destination OS", 3000)
            return

        self.show_info_color("yellow", "Trying to save User data", 10000)

        to_save = self.dest_user + " " + self.dest_ip + " " + self.dest_operating_system + "\n"

        ask_pass, ok_pressed = QInputDialog.getText(self, "Adding New User", "Destination Password: ",
                                                    QLineEdit.Password, "")
        if ok_pressed:
            pex_pass = ask_pass
        else:
            self.show_info_color("red", "Adding New User Cancelled!", 5000)
            return

        if self.dest_operating_system == "linux":
            dest_ssh_path = "/home/{}/.ssh/".format(self.dest_user)
        elif self.dest_operating_system == "mac:":
            dest_ssh_path = "/Users/{}/.ssh/".format(self.dest_user)
        elif self.dest_operating_system == "windows":
            dest_ssh_path = "C:/Users/{}/.ssh/".format(self.dest_user)
        else:
            self.show_info_color("darkred", "Failed to gather data", 5000)
            return

        path_pub = self.ssh_path + "id_rsa.pub"
        path_priv = self.ssh_path + "id_rsa"
        known_hosts = self.ssh_path + "known_hosts"
        auth_keys = dest_ssh_path + "authorized_keys"

        if not os.path.isfile(known_hosts):
            f = open(known_hosts, "a+")
            f.close()
            os.chmod(known_hosts, 0o644)
        else:
            self.r_known_hosts(known_hosts)

        key = open(os.path.expanduser(path_pub)).read()
        shell = paramiko.SSHClient()
        shell.load_host_keys(known_hosts)
        shell.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file(path_priv)
        try:
            if self.try_passphrase:
                have_passphrase = QMessageBox.question(self, 'SSH Keys Passphrase', "Have you got a Passphrase on the "
                                                                                    "SSH Public/Private Keys?",
                                                       QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if have_passphrase == QMessageBox.Yes:
                    passphrase, ok_pressed = QInputDialog.getText(self, "SSH Keys Passphrase", "Enter Passphrase: ",
                                                                  QLineEdit.Password, "")
                    if ok_pressed and passphrase != '':
                        shell.connect(self.dest_ip, username=self.dest_user, password=pex_pass,
                                      pkey=pkey, passphrase=passphrase)
                else:
                    shell.connect(self.dest_ip, username=self.dest_user, password=pex_pass, pkey=pkey)

            else:
                shell.connect(self.dest_ip, username=self.dest_user, password=pex_pass)
            shell.exec_command('mkdir -p {}'.format(self.ssh_path))
            shell.exec_command('echo "{0}" >> {1}'.format(key, auth_keys))
            shell.exec_command('chmod 644 {}'.format(auth_keys))
            shell.exec_command('chmod 700 {}'.format(self.ssh_path))
            # shell.get_host_keys().save("known_hosts")
            shell.close()
            self.show_info_color("green", "Successfully Transfered ssh keys!", 4000)
        except paramiko.ssh_exception.NoValidConnectionsError as e:
            print(str(e))
            self.show_info_color("red", "Failed to Transfer ssh keys!", 5000)

        if self.append:
            with open("resources/" + self.user + "_saved_ips.txt", "a+") as f:
                f.write(to_save)
                f.close()
                self.show_info_color("green", "successfully saved User data!", 5000)
        else:
            with open("resources/" + self.user + "_saved_ips.txt", "r") as f:
                fr = f.readlines()
                f.close()
            with open("resources/" + self.user + "_saved_ips.txt", "w") as f:
                for line in fr:
                    if line.startswith(self.dest_user):
                        if line != to_save:
                            f.write(to_save)
                        else:
                            f.write(line)
                    else:
                        f.write(line)
                f.close()
                self.show_info_color("green", "Updated saved user data!", 5000)

    def r_known_hosts(self, kh):
        ip = ""
        with open("resources/" + self.user + "_saved_ips.txt", "r") as f:
            fr = f.readlines()
            f.close()
            for line in fr:
                if line.startswith(self.dest_user):
                    ip = line.split()
        if ip != "":
            with open(kh, "r") as f:
                kh_file = f.readlines()
                f.close()
            with open(kh, "w") as f:
                for line in kh_file:
                    if line.startswith(ip[1]):
                        continue
                    else:
                        f.write(line)
                f.close()
                self.append = False
                return self.append
        else:
            self.append = True
            return self.append

    # no calls to this(keeping for testing until evrything is bulletproof!!)
    def fail_safe(self):
        self.show_info_color("yellow", "Trying a different method", 5000)
        if self.operating_system == "linux":
            op_cmd = OpenCmd(["gnome-terminal", "-e", "'python3' 'ssh_install.py'"])
            return op_cmd
        elif self.operating_system == "windows":
            self.show_info_color("gray", "A command prompt should have opened...follow the instructions", 10000)
            QTest.qWait(1000)
            op_cmd = OpenCmd(["cmd.exe", "start", "cmd.exe", "/k", "python ssh_install.py"])
            return op_cmd
        else:
            print("Not implemented yet")

    def run_keygen(self):
        if self.operating_system == "linux":
            priv_keypath = "/home/{}/.ssh/id_rsa".format(self.user)
            pub_keypath = "/home/{}/.ssh/id_rsa.pub".format(self.user)
        elif self.operating_system == "mac:":
            priv_keypath = "/Users/{}/.ssh/id_rsa".format(self.user)
            pub_keypath = "/Users/{}/.ssh/id_rsa.pub".format(self.user)
        elif self.operating_system == "windows":
            priv_keypath = "C:/Users/{}/.ssh/id_rsa".format(self.user)
            pub_keypath = "C:/Users/{}/.ssh/id_rsa.pub".format(self.user)
        else:
            self.show_info_color("darkred", "Failed to set keygen path", 5000)
            return
        try:
            key = RSA.generate(2048)
            f = open(priv_keypath, "wb")
            f.write(key.exportKey('PEM'))
            f.close()
            os.chmod(priv_keypath, 0o600)

            pubkey = key.publickey()
            f = open(pub_keypath, "wb")
            f.write(pubkey.exportKey('OpenSSH'))
            f.close()
            os.chmod(pub_keypath, 0o644)

            self.show_info_color("green", "Successfully Created ssh keys!", 4000)
            self.gen_ssh_keys_button.hide()
            QTest.qWait(3000)
            self.show_info_color("yellow", "Press 'Add New Destination' Button to add a new user and "
                                           "begin Sync_ing with!", 10000)
            syncer_keygen = open("resources/syncer_keygen.txt", "a+")
            syncer_keygen.write("True")
            syncer_keygen.close()
        except RSA.error:
            self.show_info_color("red", "Failed to Create ssh keys!", 5000)

    # if user has added new destination, can get all user info without typing it
    def get_added_user(self):
        with open("resources/" + self.user + "_saved_ips.txt", 'r+') as f:
            lines = f.readlines()
            f.seek(0)
            f.writelines(line for line in lines if line.strip())
            f.truncate()
            f.close()
        try:
            # check for user in saved_ips list and set in dest_ip_input
            saved_ips = open("resources/" + self.user + "_saved_ips.txt", "r")
            saved_ips_lines = saved_ips.readlines()
            saved_ips.close()
        except FileNotFoundError:
            self.show_info_color("red", "You must use 'Add New Destination' button at least "
                                        "once for this Feature to work!", 5000)
            return
        try:
            num_lines = len(saved_ips_lines)
            if num_lines == 0:
                self.show_info_color("red", "No users seem to be added?", 5000)
            users = []
            for line in saved_ips_lines:
                u_data = line.split()
                users.append(u_data[0])

            user, okpressed = QInputDialog.getItem(self, "Load User Info", "Saved Users:", users, 0, False)
            if okpressed and user:

                for line in saved_ips_lines:
                    ndest_data = line.split()
                    if user == ndest_data[0]:
                        self.dest_user_input.setText(ndest_data[0])
                        self.dest_ip_input.setText(ndest_data[1])
                        if ndest_data[2] == "linux":
                            self.dest_os_linux.setChecked(True)
                        elif ndest_data[2] == "mac":
                            self.dest_os_mac.setChecked(True)
                        elif ndest_data[2] == "windows":
                            self.dest_os_windows.setChecked(True)
                        return
                    else:
                        continue
        except IndexError:
            self.show_info_color("red", "It appears user data is broken!", 10000)
            self.output_display.setText("\tOpen saved_ips.txt  and  make sure it looks like:\n\n"
                                        "USER IP OS\n\n\tor if multiple:\n\nUSER IP OS\nUSER IP OS\nUSER IP OS\n\n"
                                        "\texample:\n\nadam 192.168.0.24 windows\n\n\tor if multiple:"
                                        "\n\nadam 192.168.0.24 windows\nbob 192.168.0.67 mac\ndebra 192.168.0.52 linux"
                                        "\n\nmake sure there is a space in between USER and IP and OS"
                                        "\n\n\nIf you are still seeing this message after trying to fix you didn't "
                                        "leave spaces\n\n     space  space\nUSER  ^  IP  ^  OS\n\n"
                                        "or:\n if any (USER IP OS) is missing and you have already added new destiantion"
                                        " and it was working before just add it back\n\nelse:\n"
                                        "delete that line altogether and try adding new destination again")

    # if user has entered and connected to destination before, can get the ip without typing it
    def get_saved_ip(self):
        if self.dest_user_input.text() == "":
            self.show_info_color("red", "You must specify Username to find Destination user's info!", 5000)
            return
        else:  # pull the data from ui
            self.get_sync_info()
        try:
            # check for user in saved_ips list and set in dest_ip_input
            saved_ips = open("resources/" + self.user + "_saved_ips.txt", "r")
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
                    self.show_info_color("red", "Information is not saved for this User!", 5000)
                    self.dest_ip_input.setText("")
                else:
                    continue
        except FileNotFoundError:
            self.show_info_color("red", "Destination Username and IP must have been entered at "
                                        "least once for this Feature to work!", 5000)

    def get_network_list(self, nl):
        self.available_hosts = nl
        return self.available_hosts

    # if user has entered and connected to destination before, can get the ip without typing it
    def find_ips(self):
        print(self.available_hosts)

    # get which radio button is pressed for destination OS
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
                self.show_info_color("red", "This Option only works if destination Username has been input...\t"
                                            "**EXPERIMENTAL**", 3000)
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
            self.show_info_color("red", "RSYNC OPTION IS NOT AVAILABLE ON WINDOWS\t...\t"
                                        "*this option will run but is not advised*\t...\t"
                                        "if you have actaully managed install rsync in windows ignore this", 8000)
        self.command = "rsync"
        self.rsync_button.setStyleSheet('background-color: green; color: black')
        self.scp_button.setStyleSheet('background-color: darkred; color: black')
        self.scp_button.setChecked(False)

    # button to enable scp command instead of rsync
    def scp_command(self):
        self.command = "scp"
        self.scp_button.setStyleSheet('background-color: green; color: black')
        self.rsync_button.setStyleSheet('background-color: darkred; color: black')
        self.rsync_button.setChecked(False)
        self.show_info_color("yellow", "!!! WARNING !!!\t\tScp option only copies the folder to destination\t"
                                       "to copy only the contents of a folder use Rsync!\t"
                                       "*Applies to all options", 10000)

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
            if header == 7:
                self.custom_local_path_src.setDisabled(False)
                self.custom_local_path_dst.setDisabled(False)
                self.custom_local_path_src_button.setDisabled(False)
                self.custom_local_path_dst_button.setDisabled(False)
            if header == 8:
                self.custom_remote_path_src.setDisabled(False)
                self.custom_remote_path_dst.setDisabled(False)
                self.custom_remote_path_src_button.setDisabled(False)
                self.custom_remote_path_dst_button.setDisabled(False)
        else:
            self.what_to_sync.remove(header)
            if header == 7:
                self.custom_local_path_src.setDisabled(True)
                self.custom_local_path_dst.setDisabled(True)
                self.custom_local_path_src_button.setDisabled(True)
                self.custom_local_path_dst_button.setDisabled(True)
            if header == 8:
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
        self.option5.setChecked(False)
        self.option6.setChecked(False)
        self.option7.setChecked(False)
        self.option8.setChecked(False)
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
        self.sync_button.setStyleSheet("font-size: 20px; background-color: green; color: black")
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
            1: "Desktop", 2: "Documents", 3: "Downloads", 4: "Music", 5: "Pictures", 6: "Videos",
            7: "Custom Local Paths", 8: "Custom Remote Paths"}
        # if only 1 sync option is getting used this will run
        if self.output_display.toPlainText() == "":
            if len(errors) != 0:
                self.output_display.setText("#" * 77 + "\n" + " " * 60 + "Showing output for " + headers[header]
                                            + " sync" + "\n" + "#" * 77 + "\n\n" + output + "\n\n" + "~" * 91 + "\n"
                                            + " " * 100 + "ERRORS" + "\n" + "~" * 91 + "\n\n" + errors)

            else:
                self.output_display.setText("#" * 77 + "\n" + " " * 60 + "Showing output for " + headers[header]
                                            + " sync" + "\n" + "#" * 77 + "\n\n" + output)

        # if multiple syncs are getting run it will append the ouputs together for display
        else:
            if len(errors) != 0:
                self.output_display.append("#" * 77 + "\n" + " " * 60 + "Showing output for " + headers[header]
                                           + " sync" + "\n" + "#" * 77 + "\n\n" + output + "\n\n" + "~" * 91 + "\n"
                                           + " " * 100 + "ERRORS" + "\n" + "~" * 91 + "\n\n" + errors)

            else:
                self.output_display.append("#" * 77 + "\n" + " " * 60 + "Showing output for " + headers[header]
                                           + " sync" + "\n" + "#" * 77 + "\n\n" + output)

        self.output_display.verticalScrollBar().setValue(self.output_display.verticalScrollBar().maximum())

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
        self.get_sync_info()  # pull all user input/options ready for sync
        self.clear_display()  # essionally just removes welcome_banner at this point
        # all remote options
        to_check = [1, 2, 3, 4, 5, 6]

        # add all ticked sync's to finish_er so it can pop each one when done and show completed
        self.finish_er = []
        for head in self.what_to_sync:
            self.finish_er.append(head)

        self.show_info_color("white", "Syncing...", 1000000000)  # give the user feedback

        # loop through sync options ticked
        for h in self.what_to_sync:
            # local sync only, make sure custom paths have user input
            if 7 in self.what_to_sync:
                if not self.custom_local_source_and_dest_okay:
                    self.show_info_color("red", "Please input custom paths before syncing", 3000)
                    self.custom_local_source_and_dest_okay = True
                    return
            if 8 in self.what_to_sync:
                if not self.custom_remote_source_and_dest_okay:  # make sure custom paths have user input
                    self.show_info_color("red", "Please input custom paths before syncing", 3000)
                    self.custom_remote_source_and_dest_okay = True
                    return
                if not self.user_and_dest_okay:  # make sure username and ip address have user input
                    self.show_info_color("red", "Please input username or ip address before syncing", 3000)
                    self.user_and_dest_okay = True
                    return
                if self.dest_operating_system == "":
                    self.show_info_color("red", "Please choose Destination Operating System type", 3000)
                    return
            # if sync is remote make sure all user inputs required are filled
            if h in to_check:
                if not self.user_and_dest_okay:  # make sure username and ip address have user input
                    self.show_info_color("red", "Please input username or ip address before syncing", 3000)
                    self.user_and_dest_okay = True
                    return
                if self.dest_operating_system == "":
                    self.show_info_color("red", "Please choose Destination Operating System type", 3000)
                    return

            # if all user input is filled in start the sync
            self.sync_button.setStyleSheet("font-size: 20px; background-color: red; color: black")
            self.update_progress(True)

            # creates the sync object, passing it all required input for sync
            self.worker = SyncThatShit(h, self.command, self.options, self.user, self.dest_user, self.dest_ip,
                                       self.custom_local_dest_path, self.custom_local_source_path,
                                       self.custom_remote_dest_path, self.custom_remote_source_path,
                                       self.operating_system, self.dest_operating_system, self.ssh_path)
            # signal to let show_user_info know if any errors occured changing color and user feedback
            self.worker.signals.sync_errors.connect(self.was_there_errors)
            # signal for when thread is complete, output ready for display
            self.worker.signals.finished.connect(self.print_sync)
            # signal to show all syncing's are complete
            self.worker.signals.display_finish.connect(self.sync_complete)
            # start the thread/sync
            self.pool.start(self.worker)

    # wait for all syncs to complete
    def sync_complete(self, head):
        self.finish_er.remove(head)
        if not self.finish_er:
            self.update_progress(False)
            if self.any_errors:
                self.show_info_color("yellow", "Sync Completed!\tBut...\r Errors have occured!", 8000)
            else:
                self.show_info_color("green", "Sync Completed!", 8000)
            self.any_errors = False
            self.sync_button.setStyleSheet("font-size: 20px; color: black")


class NetDiscovery(QRunnable):
    def __init__(self):
        QRunnable.__init__(self)
        self.ps = nm.PortScanner()
        self.signals = WorkerSignals()
        self.hosts = []
        self.hosts_up()

    def hosts_up(self):
        self.ps.scan(hosts="192.168.0.1/24", arguments="-F")  # was -O with sudo=True
        hosts_list = [(x, self.ps[x]['status']['state']) for x in self.ps.all_hosts()]
        for host, status in hosts_list:
            try:
                hn = socket.gethostbyaddr(host)
                self.hosts.append(host)
            except socket.herror:
                print(hn)
        self.signals.network_list.emit(self.hosts)


class OpenCmd(QRunnable):

    def __init__(self, command):
        QRunnable.__init__(self)
        self.command = command
        self.run()

    def run(self):
        abspath = os.path.abspath(__file__)
        dir_name = os.path.dirname(abspath)
        os.chdir(dir_name)
        p = subprocess.Popen(self.command)
        p.communicate()


# object used for signals when finished to start printing to display
class WorkerSignals(QObject):
    finished = pyqtSignal(int, str, str)
    # used to let show_user_info if any errors occured for coloring and feedback
    sync_errors = pyqtSignal(bool)
    display_finish = pyqtSignal(int)
    network_list = pyqtSignal(list)


# object for running the sync commands
class SyncThatShit(QRunnable):
    # all user input passed to it from main window ui
    def __init__(self, header, command, options, user, dest_user, dest_ip, custom_local_dest_path,
                 custom_local_source_path, custom_remote_dest_path, custom_remote_source_path, user_os, dest_os, ssh_path):
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
        self.ssh_path = ssh_path
        self.source_path = ""
        self.dest_path = ""
        self.destination = ""
        self.output = ""
        self.errors = ""
        self.para_scp = False
        self.signals = WorkerSignals()
        self.sync_sort()

    def run(self):
        # self.proc = QProcess()
        # self.proc_command = ""
        try:  # used for remote options
            self.destination = self.dest_user + "@" + self.dest_ip + ":" + self.dest_path

            # command for local syncs
            if self.header == 7:
                if self.command == 'scp':
                    self.options = '-rv'
                    if (self.dest_os == "windows") or (self.user_os == "windows"):
                        self.scp_copy()
                    elif os.path.isfile(self.source_path):
                        # self.proc_command = self.command + " " + self.source_path + " " + self.dest_path
                        p = subprocess.Popen([self.command, self.source_path, self.dest_path],
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    else:
                        # self.proc_command = self.command + " " + self.options + " " + self.source_path + " " + self.dest_path
                        p = subprocess.Popen([self.command, self.options, self.source_path, self.dest_path],
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    # self.proc_command = self.command + " " + self.options + " " + self.source_path + " " + self.dest_path
                    p = subprocess.Popen([self.command, self.options, self.source_path, self.dest_path],
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # command for remote syncs
            else:
                if self.command == "rsync":
                    if self.delete:
                        # self.proc_command = self.command + " " + self.options + " " + self.source_path + \
                        #                                             " " + self.destination + " --delete"
                        p = subprocess.Popen(
                            [self.command, self.options, self.source_path, self.destination, "--delete"],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    else:
                        # self.proc_command = self.command + " " + self.options + " " + self.source_path + \
                        #                                             " " + self.destination
                        p = subprocess.Popen([self.command, self.options, self.source_path, self.destination],
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                else:
                    if (self.dest_os == "windows") or (self.user_os == "windows"):
                        self.scp_copy()
                    else:
                        self.options = '-rv'
                        # self.scp_copy()
                        p = subprocess.Popen([self.command, self.options, self.source_path, self.destination],
                                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        # self.proc_command = self.command + " " + self.options + " " + self.source_path + \
                        #                                             " " + self.destination

            # # run the process wait for it to finish and store the output
            # self.proc.start(self.proc_command)
            # self.proc.waitForFinished()
            # # self.proc.finished.emit()
            # self.output = self.proc.readAllStandardOutput()
            # self.errors = self.proc.readAllStandardError()
            # self.proc.close()
            # # get command output and errors for use to display in ui
            # self.output = str(self.output, "utf-8")
            # self.errors = str(self.errors, "utf-8")

            # get scp output and then clean up scp output
            if self.para_scp:
                self.get_scp_output()
            elif self.command == "scp":
                self.output, self.errors = p.communicate()
                self.output = self.output.decode()
                self.errors = self.errors.decode()
                self.get_scp_output()
            else:
                # get command output and errors for use to display in ui
                self.output, self.errors = p.communicate()
                self.output = self.output.decode()
                self.errors = self.errors.decode()

            # signal connected to print_sync, displaying the outputs of syncs
            if self.errors != "":
                self.signals.sync_errors.emit(True)
            self.signals.finished.emit(self.header, self.output, self.errors)
            self.signals.display_finish.emit(self.header)
        # display stderr
        except Exception as e:
            err = "Ooops something went wrong there..." + "\n" + str(e)
            self.signals.finished.emit(self.header, self.output, err)
            self.signals.display_finish.emit(self.header)

    def scp_copy(self):
        self.para_scp = True
        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys(self.ssh_path + 'known_hosts')
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            pkey = paramiko.RSAKey.from_private_key_file(self.ssh_path + 'id_rsa')
            client.connect(hostname=self.dest_ip, username=self.dest_user, pkey=pkey)
            with SCPClient(client.get_transport()) as scp:
                if os.path.isfile(self.source_path):
                    scp.put(self.source_path, self.dest_path)
                else:
                    scp.put(self.source_path, remote_path=self.dest_path, recursive=True)

            # scp.get(self.dest_path, self.source_path)
            scp.close()
            client.close()
        except SCPException as e:
            print(e)

    # sets the paths of the sync depending on what sync option/header is used
    def sync_sort(self):
        sp = ""
        dp = ""
        # set the option/flag
        if self.options == "d":  # default
            self.options = "-Paiurv"
        elif self.options == "c":  # compress
            self.options = "-Paiurvz"
        elif self.options == "del":  # delete destination dir before copying
            self.options = "-Paiurv"
            self.delete = True

        # force scp if windows is involved
        if self.dest_os == "windows":
            if self.user_os != "windows":
                self.command = "scp"

        if self.user_os == "linux":
            sp = "/home/" + self.user
        elif self.user_os == "mac":
            sp = "/Users/" + self.user
        elif self.user_os == "windows":
            sp = "C:/Users/" + self.user

        if self.dest_os == "linux":
            dp = "/home/" + self.dest_user
        elif self.dest_os == "mac":
            dp = "/Users/" + self.dest_user
        elif self.dest_os == "windows":
            dp = "C:/Users/" + self.dest_user

        if self.header == 1:
            self.source_path = sp + "/Desktop/"
            self.dest_path = dp + "/Desktop/"
        elif self.header == 2:
            self.source_path = sp + "/Documents/"
            self.dest_path = dp + "/Documents/"
        elif self.header == 3:
            self.source_path = sp + "/Downloads/"
            self.dest_path = dp + "/Downloads/"
        elif self.header == 4:
            self.source_path = sp + "/Music/"
            self.dest_path = dp + "/Music/"
        elif self.header == 5:
            self.source_path = sp + "/Pictures/"
            self.dest_path = dp + "/Pictures/"
        elif self.header == 6:
            self.source_path = sp + "/Videos/"
            self.dest_path = dp + "/Videos/"

        # sets if self.option7 is ticked
        if self.header == 7:
            self.source_path = self.custom_local_source_path
            self.dest_path = self.custom_local_dest_path

        # sets if self.option8 is ticked
        if self.header == 8:
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
