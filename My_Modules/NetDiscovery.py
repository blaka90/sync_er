from PyQt5.QtCore import *
from My_Modules.WorkerSignals import WorkerSignals
import nmap as nm
# from netdisco.discovery import NetworkDiscovery


class NetDiscovery(QRunnable):
    def __init__(self):
        QRunnable.__init__(self)
        self.nm = nm.PortScanner()
        # self.netdis = NetworkDiscovery()
        self.signals = WorkerSignals()
        self.hosts = []

    def run(self):
        self.nm.scan(hosts="192.168.0.1/24", arguments="-F")
        for host in self.nm.all_hosts():
            self.hosts.append(host)
        """
        self.netdis.scan()
        for dev in self.netdis.discover():
            print(dev, self.netdis.get_info(dev))
        self.netdis.stop()
        """
        self.signals.network_list.emit(self.hosts)