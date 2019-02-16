import os
import subprocess
import sys
from getpass import getuser


def get_os():
	if "linux" in sys.platform.lower():
		operating_system = "linux"
	elif sys.platform.lower().startswith("win"):
		operating_system = "windows"
	elif "darwin" in sys.platform.lower():
		operating_system = "mac"
	return operating_system


def run_passwordless(user, ip):
	ssh_path = ""
	command = ""
	if get_os() == "linux":
		ssh_path = "/home/{}/.ssh/".format(getuser())
		command = "ssh-copy-id -i id_rsa.pub " + user + "@" + ip
	elif get_os() == "mac:":
		ssh_path = "/Users/{}/.ssh/".format(getuser())
		command = "ssh-copy-id -i id_rsa.pub " + user + "@" + ip
	elif get_os() == "windows":
		ssh_path = "C:/Users/{}/.ssh/".format(getuser())
		command = "scp id_rsa.pub " + user + "@" + ip + ":/home/" + user + "/.ssh/authorized_keys"
	os.chdir(ssh_path)
	p = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
	                     stdin=subprocess.PIPE)

	outp, err = p.communicate()

	if outp and not err:
		print("Successfully Transfered ssh keys!")
	else:
		print("Failed to Transfer ssh keys!")


def main():
	if get_os() == "mac":
		command = "ssh-gen"
	else:
		command = "ssh-keygen"

	p = subprocess.Popen([command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
		                    stdin=subprocess.PIPE)

	outp, err = p.communicate()

	if outp and not err:
		print("Successfully created ssh keys!\n")
		user = input("Destination Username: ")
		ip = input("Destination IP: ")
		run_passwordless(user, ip)
	elif outp and err:
		user = input("Destination Username: ")
		ip = input("Destination IP: ")
		run_passwordless(user, ip)
	else:
		print("Failed to create ssh keys!")


