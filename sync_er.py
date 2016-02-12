#! /usr/bin/env python

import subprocess
import os
import threading
import inspect
from optparse import OptionParser

# rsync -Paiurv /Users/blaka7/Desktop/test_rsync blaka@192.168.0.5:/Users/blaka/Desktop/

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
		self.release = False
		if options == "d":  # default
			self.options = "-Paiurv"
		elif options == "c":  # compress
			self.options = "-Paiurvz"
		elif options == "del":
			self.options = "-Paiurv --delete"
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
		print "14. Ipad MovieBox"
		print "15. Exit"
		self.ans = raw_input(">")
		self.sync_sort_source(self.ans)
		self.sync_sort_dest(self.ans)

	def sync_sort_source(self, folder):
		if self.source == "blaka":
			self.src_hdd = "MacBookHDD"
		else:
			self.src_hdd = "MacMiniHDD"

		if folder == "1":
			self.source_folder = "/Volumes/" + self.src_hdd + "/me shit/"
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
			self.source_folder = "/Users/" + self.source + "/Desktop/films/"
		elif folder == "15":
			exit(0)

	def sync_sort_dest(self, folder):
		if self.destination == "blaka":
			self.dest_hdd = "MacBookHDD"
		else:
			self.dest_hdd = "MacMiniHDD"

		if folder == "1":
			self.dest_folder = "/Volumes/" + self.dest_hdd + "/me\ shit/"
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
			self.dest_folder = "/User/Library/Artworks/*"
		elif folder == "15":
			exit(0)

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
			else:
				p = subprocess.Popen([self.command, self.options, self.source_folder, destination],
									 stdout=subprocess.PIPE)

			output = p.communicate()[0]
			exitcode = p.returncode
			if exitcode == 0:
				self.release = True
		except Exception as e:
			print "Ooops something went wrong there..." + "\n"
			print str(e) + "\n"
			# main()


def main():
	user_source = raw_input("source username: ")
	user_dest = raw_input("destination username: ")
	dest_ip = raw_input("destination ip(leave blank for local): ")
	opts = raw_input("options:\n(d)efault\n(c)ompress\n(del)ete (only deletes what is already deleted from source "
					 "folder)\nenter manually\n> ")
	while True:
		for thread in threads:
			if inspect.isclass(thread):
				poodex = int(pool.index(thread))
				pool[poodex].join()
				continue
			else:
				thread = Sync(user_source, user_dest, dest_ip, opts)
				thread.start()
				pool.append(thread)
				print "\n" + "...Syncing..." + "\n"
				print "\n" + "Would you like to sync any more?"
				sync = raw_input("y/n: ").lower()
				if sync == "y":
					print "Use same source and destination?"
					s_d = raw_input("y/n: ").lower()
					if s_d == "y":
						if thread.release:
							print output
						continue
					elif s_d == "n":
						for th in pool:
							th.join()
						main()
				else:
					print "\n"
					for th in pool:
						if th.release:
							print output
						th.join()
					exit(0)


if __name__ == "__main__":
	os.system("clear")
	print "-_-" * 25
	print " " * 25 + "WELCOME TO SYNC_ER"
	print "_-_" * 25 + "\n"
	main()
