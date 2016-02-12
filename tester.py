import subprocess
import os
import threading
import inspect

# rsync -Paiurv /Users/blaka7/Desktop/test_rsync blaka@192.168.0.5:/Users/blaka/Desktop/


threads = ["thread1", "thread2", "thread3", "thread4", "thread5"]
pool = []


class Sync(threading.Thread):

	def __init__(self, user_source, user_destination, destination_ip, options):
		os.chdir("/")
		self.source = user_source
		self.destination = user_destination
		self.destination_ip = destination_ip
		self.source_folder = ""
		self.dest_folder = ""
		self.command = "rsync"
		self.ans = ""
		self.src_hdd = ""
		self.dest_hdd = ""
		if options == "default":
			self.options = "-Paiurv"
		elif options == "compress":
			self.options = "-Paiurvz"
		else:
			self.options = options
		self.what_to_sync()
		threading.Thread.__init__(self, target=self.sync_that_shit)

	def what_to_sync(self):
		print "What would you like to sync?" + "\n"
		print "1.  Full Hard Drive"
		print "2.  Books"
		print "3.  Iso's and Dmg's"
		print "4.  VM's"
		print "5.  Programming"
		print "6.  Games"
		print "7.  Pic's n Video's"
		print "8.  Cloud Books"
		print "9.  Documents"
		print "10. Bash Scripts"
		print "11. Downloads"
		print "12. Custom Paths"
		print "13. Custom Remote Paths"
		print "14. Exit"
		self.ans = raw_input(">")
		self.sync_sort_source(self.ans)
		self.sync_sort_dest(self.ans)

	def sync_sort_source(self, folder):
		if self.source == "blaka":
			self.src_hdd = "MacBookHDD"
		else:
			self.src_hdd = "MacMiniHDD"

		if folder == "1":
			self.source_folder = "/Volumes/" + self.src_hdd + "/"
		elif folder == ("2" or "8"):
			self.source_folder = "/Volumes/" + self.src_hdd + "/me shit/Books/"
		elif folder == "3":
			self.source_folder = "/Volumes/" + self.src_hdd + "/me shit/iso n dmgs/"
			print "\n" + "Please wait...this could take a while"
		elif folder == "4":
			self.source_folder = "/Volumes/" + self.src_hdd + "/me shit/VMS/"
			print "\n" + "Please wait...this could take a while"
		elif folder == "5":
			self.source_folder = "/Volumes/" + self.src_hdd + "/me shit/programming/"
		elif folder == "6":
			self.source_folder = "/Volumes/" + self.src_hdd + "/me shit/GAMES/"
			print "\n" + "Please wait...this could take a while"
		elif folder == "7":
			self.source_folder = "/Volumes/" + self.src_hdd + "/me shit/pics n videos/"
		elif folder == "9":
			self.source_folder = "/Users/" + self.source + "/Documents/"
		elif folder == "10":
			self.source_folder = "/Users/" + self.source + "/Desktop/bash scripts/"
		elif folder == "11":
			self.source_folder = "/Users/" + self.source + "/Downloads/"
		elif folder == "12":
			self.source_folder = raw_input("Source Folder: ")
		elif folder == "13":
			self.source_folder = raw_input("Source Folder(R): ")
		elif folder == "14":
			exit(0)

	def sync_sort_dest(self, folder):
		if self.destination == "blaka":
			self.dest_hdd = "MacBookHDD"
		else:
			self.dest_hdd = "MacMiniHDD"

		if folder == "1":
			self.dest_folder = "/Volumes/" + self.dest_hdd + "/"
		elif folder == "2":
			self.dest_folder = "/Volumes/" + self.dest_hdd + "/me\ shit/Books/"
		elif folder == "3":
			self.dest_folder = "/Volumes/" + self.dest_hdd + "/me\ shit/iso\ n\ dmgs/"
		elif folder == "4":
			self.dest_folder = "/Volumes/" + self.dest_hdd + "/me\ shit/VMS/"
		elif folder == "5":
			self.dest_folder = "/Volumes/" + self.dest_hdd + "/me\ shit/programming/"
		elif folder == "6":
			self.dest_folder = "/Volumes/" + self.dest_hdd + "/me\ shit/GAMES/"
		elif folder == "7":
			self.dest_folder = "/Volumes/" + self.dest_hdd + "/me\ shit/pics\ n\ videos/"
		elif folder == "8":
			self.dest_folder = "/Users/" + self.destination + "/Google\ Drive/Books/"
		elif folder == "9":
			self.dest_folder = "/Users/" + self.destination + "/Documents/"
		elif folder == "10":
			self.dest_folder = "/Users/" + self.destination + "/Desktop/bash\ scripts/"
		elif folder == "11":
			self.dest_folder = "/Users/" + self.destination + "/Downloads/"
		elif folder == "12":
			self.dest_folder = raw_input("Destination Folder: ")
		elif folder == "13":
			self.dest_folder = raw_input("Destination Folder(R): ")
		elif folder == "14":
			exit(0)

	def sync_that_shit(self):
		try:
			destination = self.destination + "@" + self.destination_ip + ":" + self.dest_folder
			if self.ans == ("8" or "12"):
				p = subprocess.Popen([self.command, self.options, self.source_folder, self.dest_folder], stdout=subprocess.PIPE)
			else:
				p = subprocess.Popen([self.command, self.options, self.source_folder, destination], stdout=subprocess.PIPE)

			output = p.communicate()[0]
			print output
		except Exception as e:
			print "Ooops something went wrong there..." + "\n"
			print str(e) + "\n"
			main()


def main():
	user_source = raw_input("source username: ")
	user_dest = raw_input("destination username: ")
	dest_ip = raw_input("destination ip(leave blank for local): ")
	opts = raw_input("options(default/compress/or enter manually): ")
	while True:
		for thread in threads:
			if inspect.isclass(thread):
				continue
			else:
				thread = Sync(user_source, user_dest, dest_ip, opts)
				thread.start()
				pool.append(thread)
				print "\n" + "Would you like to sync any more?"
				sync = raw_input("y/n: ").lower()
				if sync == "y":
					print "Use same source and destination?"
					s_d = raw_input("y/n: ").lower()
					if s_d == "y":
						continue
					elif s_d == "n":
						for th in pool:
							th.join()
						main()
				else:
					for th in pool:
						th.join()
					exit(0)


if __name__ == "__main__":
	print "-_-" * 30
	print " " * 30 + "WELCOME TO SYNC_ER"
	print "_-_" * 30 + "\n"
	main()
