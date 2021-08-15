from PyQt5.QtCore import *
import subprocess
import paramiko
import os
from scp import SCPClient, SCPException
from My_Modules.WorkerSignals import WorkerSignals


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

            with open("resources/process_pids", "a") as f:
                f.write(str(p.pid) + "\n")
                f.close()

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