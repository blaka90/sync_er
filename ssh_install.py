import subprocess
import sys
from getpass import getuser
import os

# mac needs to homebrew install ssh-copy-id for this to work

this_user = getuser()


def get_os():
	operating_system = ""
	if "linux" in sys.platform.lower():
		operating_system = "linux"
	elif sys.platform.lower().startswith("win"):
		operating_system = "windows"
	elif "darwin" in sys.platform.lower():
		operating_system = "mac"
	else:
		print("Failed to determine Operating System")
	return operating_system


def get_dos():
	dos = ""
	os = input("\nDestination OS\n\n(L)inux\n(M)ac\n(W)indows\n(L/M/W)?: ")
	if os.lower() == "l":
		dos = "linux"
	elif os.lower() == "m":
		dos = "mac"
	elif os.lower() == "w":
		dos = "windows"
	else:
		print("Invalid option try again\noptions:\n(L)inux\n(M)ac\n(W)indows\n")
		get_dos()
	return dos


def run_passwordless():

	user = input("\nDestination Username: ")
	ip = input("\nDestination IP: ")
	dos = get_dos()

	if get_os() == "linux":
		ssh_path = "/home/{}/.ssh/id_rsa.pub".format(this_user)
		command = "ssh-copy-id"
		option = "-i"
		dest = user + "@" + ip
		p = subprocess.Popen([command, option, ssh_path, dest])
		out, err = p.communicate()
	elif get_os() == "mac:":
		ssh_path = "/Users/{}/.ssh/id_rsa.pub".format(this_user)
		command = "ssh-copy-id"
		option = "-i"
		dest = user + "@" + ip
		p = subprocess.Popen([command, option, ssh_path, dest])
		out, err = p.communicate()
	elif get_os() == "windows":
		ssh_path = "C:/Users/{}/.ssh/id_rsa.pub".format(this_user)
		command = "scp"
		dest = user + "@" + ip + ":/home/" + user + "/.ssh/authorized_keys"
		p = subprocess.Popen([command, ssh_path, dest])
		out, err = p.communicate()
	else:
		print("Failed to run_passwordless")
		return sys.exit(6)
	if out:
		to_save = user + " " + ip + " " + dos + "\n"
		with open("saved_ips.txt", "a+") as f:
			f.write(to_save)
			f.close()
			print("\n\nSuccessfully saved user!")
			print("\n\nYou may close this command prompt now!\n\n")
			sys.exit(0)
	else:
		print("error:\n" + str(err))
		print("\n\nFailed to save user!\n\n")
		print("\n\nYou may close this command prompt now!\n\n")
		sys.exit(7)


def main():
	just_passwordless = False
	command = ""
	if get_os() == "linux":
		ssh_path = "/home/{}/.ssh/id_rsa.pub".format(this_user)
		command = "ssh-keygen"
		if os.path.isfile(ssh_path):
			just_passwordless = True
	elif get_os() == "mac:":
		ssh_path = "/Users/{}/.ssh/id_rsa.pub".format(this_user)
		command = "ssh-gen"
		if os.path.isfile(ssh_path):
			just_passwordless = True
	elif get_os() == "windows":
		ssh_path = "C:/Users/{}/.ssh/id_rsa.pub".format(this_user)
		command = "ssh-keygen"
		if os.path.isfile(ssh_path):
			just_passwordless = True

	if not just_passwordless:
		p = subprocess.Popen([command])
		p.communicate()
		ans = input("Add New Destination now? (y/n): ")
		if ans.lower() == "y":
			run_passwordless()
		else:
			sys.exit(9)
	else:
		run_passwordless()


if __name__ == "__main__":
	main()


