# **_sync_er_**

## Cross Platform Gui wrapper for **_RSYNC_** and **_SCP_**

tested with:
- python2.7
- python3.6

Supports:
- Linux(Fully Tested)
- MacOS(Partial Testing)
- Windows(SCP Only)

Requirements:
- python-nmap
- Crypto
- scp
- paramiko
- netifaces
- pyqt5

### Uses:

&nbsp; &nbsp; Linux and Mac users should use rsync as it is the preferred

&nbsp; &nbsp; Windows users scp is your only option as of now(unless you can get rsync working with cygwin)
  
&nbsp; &nbsp; rsync copies either a single file to destination or all contents of folder(no folder) to destination
  
&nbsp; &nbsp; scp copies either a single file to destination or the folder(with contents) to destination

## Linux Installation:
1. Download sync_er-master.zip and unzip or git clone https://github.com/blaka90/sync_er.git
2. Copy sync_er to wherever you want to install (i personally use /opt/)(requires sudo)
   `cp -r sync_er-master/ /your/install/path/`
3. move into where ever you choose to install
   `cd /your/install/path/sync_er-master/`
4. run `pip3 install -r requirements.txt` 
    or for python2.7 `pip install -r requirments.txt`
