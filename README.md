# **_sync_er_**



## Cross Platform Gui wrapper for **_RSYNC_** and **_SCP_**


(STILL IN ALPHA)

**_USE AT YOUR OWN RISK_**

tested with:
- python2.7
- python3.6

Supports:
- Linux(On-going Testing)
- MacOS(Partial Testing)
- Windows(SCP Only)

Requirements:
- ~~python-nmap~~
- Crypto
- scp
- paramiko
- netifaces
- pyqt5

### Uses:
Linux default: rsync

MacOS default: rsync

Windows default: scp

&nbsp; &nbsp; Linux and Mac users should use rsync as it is the preferred

&nbsp; &nbsp; Windows users scp is your only option as of now(unless you can get rsync working with cygwin)
  
&nbsp; &nbsp; rsync copies either a single file to destination or all contents of folder(no folder) to destination
  
&nbsp; &nbsp; scp copies either a single file to destination or the folder(with contents) to destination

## Linux Installation:
1. Download sync_er-master.zip and unzip or git clone https://github.com/blaka90/sync_er.git
2. Copy sync_er to wherever you want to install `cp -r sync_er-master/ /your/install/path/`
   - (i personally use /opt/)(requires sudo)
3. move into where ever you choose to install `cd /your/install/path/sync_er-master/`
4. run `pip3 install -r requirements.txt` or for python2.7 `pip install -r requirments.txt`
5. now you can either just run `python3 /path/to/sync_er.py` to use
   - or
6. go into `sync_er-master/resources/` and edit `sync_er.desktop` to make an Application Menu Entry
   - on lines `Exec=python3 /path/to/sync_er/sync_er.py` and `Icon=/path/to/sync_er/resources/syncer.png`
   - change `/path/to` to where you installed the sync_er-master/ folder
7. now `cp sync_er.desktop ~/.local/share/applications/`
8. sync_er should now be in your application menu

## ~~MacOS Installation~~:
todo
## ~~Windows Installation~~:
1. Go to _settings_ then _apps_, then click _manage optional features_
2. scroll down to Openssh client & Openssh server and click install on both(if they not already installed)

**_finish this_**

### SCREENSHOTS:

![normal](https://user-images.githubusercontent.com/8757090/55292194-575c7400-53df-11e9-9cf8-915a57a8722e.png)

better with background? (user choose their own?)
![image_sync_er](https://user-images.githubusercontent.com/8757090/55291857-aa342c80-53db-11e9-9479-6f78d3742023.png)

![load_user](https://user-images.githubusercontent.com/8757090/55292196-63e0cc80-53df-11e9-9501-77d210e7a1d5.png)

![file_browser](https://user-images.githubusercontent.com/8757090/55292198-6e9b6180-53df-11e9-901d-58c480552474.png)

![sync_ing](https://user-images.githubusercontent.com/8757090/55292199-72c77f00-53df-11e9-958f-cb461f260f72.png)

![completed](https://user-images.githubusercontent.com/8757090/55292200-74914280-53df-11e9-89ce-b4381b7ff313.png)
