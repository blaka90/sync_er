import subprocess
import sys
from getpass import getuser

# mac needs to homebrew install ssh-copy-id for this to work


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
	os = input("\nDestination OS (l)inux/(m)ac/(w)indows: ")
	if os == "l":
		dos = "linux"
	elif os == "m":
		dos = "mac"
	elif os == "w":
		dos = "windows"
	else:
		print("Invalid option try again\noptions:\n(l)inux\n(m)ac\n(w)indows\n")
		get_dos()
	return dos


def run_passwordless():
	this_user = getuser()

	user = input("\nDestination Username: ")
	ip = input("\nDestination IP: ")
	dos = get_dos()

	if get_os() == "linux":
		ssh_path = "/home/{}/.ssh/id_rsa.pub".format(this_user)
		command = "ssh-copy-id"
		option = "-i"
		dest = user + "@" + ip
		p = subprocess.Popen([command, option, ssh_path, dest])
		p.communicate()
	elif get_os() == "mac:":
		ssh_path = "/Users/{}/.ssh/id_rsa.pub".format(this_user)
		command = "ssh-copy-id"
		option = "-i"
		dest = user + "@" + ip
		p = subprocess.Popen([command, option, ssh_path, dest])
		p.communicate()
	elif get_os() == "windows":
		ssh_path = "C:/Users/{}/.ssh/id_rsa.pub".format(this_user)
		command = "scp"
		dest = user + "@" + ip + ":/home/" + user + "/.ssh/authorized_keys"
		p = subprocess.Popen([command, ssh_path, dest])
		p.communicate()

	to_save = user + " " + ip + " " + dos + "\n"
	with open("saved_ips.txt", "a+") as f:
		f.write(to_save)
		f.close()
		print("\n\nSuccessfully saved user!")


def main():
	if get_os() == "mac":
		command = "ssh-gen"
	else:
		command = "ssh-keygen"

	p = subprocess.Popen([command])
	p.communicate()
	run_passwordless()


if __name__ == "__main__":
	main()


