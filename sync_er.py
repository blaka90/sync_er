#! /usr/bin/env python

import subprocess
import os
import threading
import inspect
from optparse import OptionParser


'''---------------THIS WILL NOT WORK ON ANY OTHER MACHINES BAR MINE, NOR IS IT MEANT TOO----------- '''


"""
	need to put all documentation in!

	14. is a working progress(soon as i bastard find .ssh/authorized_keys on ipad)

	8. also is a bit dodgy for the time being just do local custom paths(12) for now

	add command line option parser but if none just uses original program
"""


# just a reminder for how to use option parser(example from another project)
"""
 parser = OptionParser(usage='usage: %prog [options] <ssh-server>[:<server-port>]',
						  version='%prog 1.0', description=HELP)
	parser.add_option('-p', '--remote-port', action='store', type='int', dest='port',
					  default=DEFAULT_PORT,
					  help='port on server to forward (default: %d)' % DEFAULT_PORT)
	options, args = parser.parse_args()

	if len(args) != 1:
		parser.error('Incorrect number of arguments.')
	if options.remote is None:
		parser.error('Remote address required (-r).')

	g_verbose = options.verbose
	server_host, server_port = get_host_port(args[0], SSH_PORT)
	remote_host, remote_port = get_host_port(options.remote, SSH_PORT)
	return options, (server_host, server_port), (remote_host, remote_port)


def main():
	options, server, remote = parse_options()
"""

# should probably use threadings Pool class but until then this will do
threads = ["thread1", "thread2", "thread3", "thread4", "thread5"]
pool = []


# the class for each threaded sync
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
		self.header = 0
		self.output = ""
		self.release = False
		if options == "d":  # default
			self.options = "-Paiurv"
		elif options == "c":  # compress
			self.options = "-Paiurvz"
		elif options == "del":  # delete outdated
			self.options = "-Paiurv --delete"
		else:
			self.options = options
		self.what_to_sync()
		threading.Thread.__init__(self, target=self.sync_that_shit)

	# used to print header for what output is showing
	def print_sync(self):
		headers = {
			1: "Full Hard Drive", 2: "Books", 3: "Iso's and Dmg's", 4: "VM's", 5: "Programming", 6: "Games",
			7: "Pic's n Video's", 8: "Cloud Books", 9: "Documents", 10: "Bash Scripts", 11: "Downloads",
			12: "Custom Paths", 13: "Custom Remote Paths", 14: "Ipad MovieBox"}
		print "#" * 75
		print " " * 15 + "Showing output for " + headers[self.header] + " sync\n"
		print "#" * 75

	# runs after each object is created
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
		print "14. Ipad MovieBox"
		print "15. Exit"
		self.ans = raw_input(">")
		self.sync_sort(self.ans)

	# sets the source destination of the sync
	def sync_sort(self, folder):
		if self.source == "blaka":
			self.src_hdd = "MacBookHDD"
		else:
			self.src_hdd = "MacMiniHDD"

		if self.destination == "blaka":
			self.dest_hdd = "MacBookHDD"
		else:
			self.dest_hdd = "MacMiniHDD"

		if folder == "1":
			self.source_folder = "/Volumes/" + self.src_hdd + "/me shit/"
			self.dest_folder = "/Volumes/" + self.dest_hdd + "/me\ shit/"
			self.header = 1

		elif folder == "2":
			self.source_folder = "/Volumes/" + self.src_hdd + "/me shit/Books/"
			self.dest_folder = "/Volumes/" + self.dest_hdd + "/me\ shit/Books/"
			self.header = 2

		elif folder == "3":
			self.source_folder = "/Volumes/" + self.src_hdd + "/me shit/iso n dmgs/"
			self.dest_folder = "/Volumes/" + self.dest_hdd + "/me\ shit/iso\ n\ dmgs/"
			self.header = 3
			print "\n" + "Please wait...this could take a while"

		elif folder == "4":
			self.source_folder = "/Volumes/" + self.src_hdd + "/me shit/VMS/"
			self.dest_folder = "/Volumes/" + self.dest_hdd + "/me\ shit/VMS/"
			self.header = 4
			print "\n" + "Please wait...this could take a while"

		elif folder == "5":
			self.source_folder = "/Volumes/" + self.src_hdd + "/me shit/programming/"
			self.dest_folder = "/Volumes/" + self.dest_hdd + "/me\ shit/programming/"
			self.header = 5

		elif folder == "6":
			self.source_folder = "/Volumes/" + self.src_hdd + "/me shit/GAMES/"
			self.dest_folder = "/Volumes/" + self.dest_hdd + "/me\ shit/GAMES/"
			self.header = 6
			print "\n" + "Please wait...this could take a while"

		elif folder == "7":
			self.source_folder = "/Volumes/" + self.src_hdd + "/me shit/pics n videos/"
			self.dest_folder = "/Volumes/" + self.dest_hdd + "/me\ shit/pics\ n\ videos/"
			self.header = 7

		elif folder == "8":
			self.source_folder = "/Volumes/" + self.src_hdd + "/me shit/Books/"
			self.dest_folder = "/Users/" + self.destination + "/Google\ Drive/Books/"
			self.header = 8

		elif folder == "9":
			self.source_folder = "/Users/" + self.source + "/Documents/"
			self.dest_folder = "/Users/" + self.destination + "/Documents/"
			self.header = 9

		elif folder == "10":
			self.source_folder = "/Users/" + self.source + "/Desktop/bash scripts/"
			self.dest_folder = "/Users/" + self.destination + "/Desktop/bash\ scripts/"
			self.header = 10

		elif folder == "11":
			self.source_folder = "/Users/" + self.source + "/Downloads/"
			self.dest_folder = "/Users/" + self.destination + "/Downloads/"
			self.header = 11

		elif folder == "12":
			self.source_folder = raw_input("Source Folder: ")
			self.dest_folder = raw_input("Destination Folder: ")
			self.header = 12

		elif folder == "13":
			self.source_folder = raw_input("Source Folder(R): ")
			self.dest_folder = raw_input("Destination Folder(R): ")
			self.header = 13

		elif folder == "14":
			self.source_folder = "/Users/" + self.source + "/Desktop/films/"
			self.dest_folder = "/User/Library/Artworks/*"
			self.header = 14

		elif folder == "15":
			print "#" * 25 + "EXITING" + "#" * 25
			exit(0)

	# depending on what options are used, sets the right command
	def sync_that_shit(self):
		global output
		try:
			destination = self.destination + "@" + self.destination_ip + ":" + self.dest_folder
			ipad = self.destination + "@" + self.destination_ip + ":" + self.dest_folder
			if self.ans == ("8" or "12"):
				p = subprocess.Popen([self.command, self.options, self.source_folder, self.dest_folder],
									 stdout=subprocess.PIPE)
			elif self.ans == "14":
				p = subprocess.Popen(["scp", ipad, self.source_folder], stdout=subprocess.PIPE)
			elif self.ans == "5":
				exclude = "--exclude=InfiniteSkills - Learning Python Programming/"
				p = subprocess.Popen([self.command, self.options, exclude, self.source_folder, destination],
									 stdout=subprocess.PIPE)
			else:
				p = subprocess.Popen([self.command, self.options, self.source_folder, destination],
									 stdout=subprocess.PIPE)

			p.wait()
			self.output = p.communicate()[0]
			exitcode = p.returncode
			# used to release output so their isn't output showing when user input is happening
			if exitcode == 0:
				self.release = True
		except Exception as e:
			print "Ooops something went wrong there..." + "\n"
			print str(e) + "\n"
			# main()


def main():  # the main loop
	user_source = raw_input("source username: ")
	user_dest = raw_input("destination username: ")
	dest_ip = raw_input("destination ip(leave blank for local): ")
	opts = raw_input("options:\n(d)efault\n(c)ompress\n(del)ete (only deletes what is already deleted from source "
					 "folder)\nenter manually\n> ")
	print "\n"
	# the programs main loop for initiating a sync thread
	while True:
		for thread in threads:
			if inspect.isclass(thread):  # my version of threading.Pool
				poodex = int(pool.index(thread))  # (max 5)
				pool[poodex].join()  
				continue
			else:
				# the actual object creation
				thread = Sync(user_source, user_dest, dest_ip, opts)
				thread.start()
				pool.append(thread)  # add it to the pool
				print "\n" + "...Syncing..." + "\n"
				print "\n" + "Would you like to sync any more?"
				sync = raw_input("y/n: ").lower()  # can only do up to 5 continuous syncs to date
				if sync == "y":
					print "Use same source and destination?"
					s_d = raw_input("y/n: ").lower()
					if s_d == "y":  # makes a new thread sync object
						print "\n"
						continue
					elif s_d == "n":  # holds the output and starts the main loop over
						for th in pool:
							th.join()
						main()
				else:
					print "\n"
					for th in pool:  # releases all the outputs for each sync then exits
						if th.release:
							th.print_sync()
							print th.output
						th.join()
					exit(0)


if __name__ == "__main__":
	os.system("clear")
	# welcome banner
	print "-_-" * 26
	print " " * 35 + "SYNC_ER"
	print "_-_" * 26 + "\n"
	main()
