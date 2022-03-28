#! /usr/bin/python3
import requests
from threading import Thread
import os
import sys

from pysftp import Connection
from pychroot import Chroot

from bcolors import bcolors
from zipfile import ZipFile
from tqdm import tqdm
import subprocess
from subprocess import STDOUT, check_call
from progress.spinner import Spinner
from progress.spinner import PieSpinner
import re
import shutil
import Constant

from os import fspath
from pathlib import Path
from shutil import copyfileobj
from tqdm.auto import tqdm  # could use from tqdm.gui import tqdm
from tqdm.utils import CallbackIOWrapper
import paramiko
import functools
from unzip import unzip

state = "None"


class tools:

    def runProgress(self):
        global state
        spinner = Spinner('Processing ... ')
        while state != 'Finished':
            spinner.next()

    def runProgressLine(self):
        global state
        spinner = PieSpinner('Processing ... ')
        while state != 'Finished':
            spinner.next()

    def runUpdate(self):
        global state
        state = 'None'
        th = Thread(target=self.runProgress)
        th.start()  # open(os.devnull,"wb")
        self.runCommand('apt-get update -y')
        self.runCommand('apt-get upgrade -y')
        state = 'Finished'
        th.join()

    def runInstalls(self):
        global state
        state = 'None'
        th = Thread(target=self.runProgress)
        th.start()
        self.runCommand('apt-get install -y qemu qemu-user-static binfmt-support kpartx sshpass openssl shellinabox')
        state = 'Finished'
        th.join()

    def downloadFile(self, link_url, file_name):
        self.runCommand('rm -f ../download/*')
        r = requests.get(link_url, stream=True)
        total_size_in_bytes = int(r.headers.get('content-length', 0))
        block_size = 1024
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        with open(Constant.LocalDownload + file_name, 'wb') as f:
            for data in r.iter_content(block_size):
                progress_bar.update(len(data))
                f.write(data)
        progress_bar.close()

    def getDirPath(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        return dir_path

    def fdiskLU(self, image):
        cmd = str('fdisk -lu ' + image)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        result = proc.stdout.read().__str__()
        iter = '.img'
        parts = re.findall(r'' + iter + r'\d', result)
        disk = {}
        for p in parts:
            part = {}
            line = result.split(p)[1]
            words = re.split(r'\s+', line)
            part['Start'] = words[1]
            part['End'] = words[2]
            part['Sectors'] = words[3]
            part['Size'] = words[4]
            part['Id'] = words[5]
            part['Format'] = words[6].split('\\n')[0]
            disk[p] = part
        return disk

    def runMounts(self, bootOffset, rootOffset, rootImg, bootImg):
        self.runUmount()
        path = self.getDirPath() + "/"
        cmdRoot = 'mount -o loop,offset=' + str(rootOffset) + ' "' + path + rootImg + '" /mnt'
        cmdBoot = 'mount -o loop,offset=' + str(bootOffset) + ' "' + path + bootImg + '" /mnt/boot'
        # print(path, bootOffset, rootOffset, bootImg, rootImg, cmdRoot, cmdBoot)
        self.runCommand('mkdir -p /mnt/boot')
        self.runCommand('mkdir -p /mnt/usr/bin')
        self.runCommand(cmdRoot)
        self.runCommand(cmdBoot)
        self.runCommand('cp /usr/bin/qemu-arm-static /mnt/usr/bin/')
        # self.runCommand('mount --rbind /dev /mnt/dev')
        # self.runCommand('mount -t proc none /mnt/proc')
        # self.runCommand('mount -o bind /sys /mnt/sys')
        # self.runCommand('mount --bind /etc/resolv.conf /mnt/etc/resolv.conf')

    def doChroot(self, headless, fullp, showroom):
        with Chroot('/mnt'):
            print(f"{bcolors.OKCYAN}\n\nSet Locale and Language \n{bcolors.ENDC}")
            self.runCommandOUT('echo "LC_ALL=en_US.UTF-8" >> /etc/environment')
            self.runCommandOUT('echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen')
            self.runCommandOUT('echo "LANG=en_US.UTF-8" > /etc/locale.conf')
            self.runCommandOUT('locale-gen en_US.UTF-8')

            print(f"{bcolors.OKCYAN}\n\nChecking Network-Connections \n{bcolors.ENDC}")
            self.runCommand('ping -c 5 google.com')
            print('OK')
            print(f"{bcolors.OKCYAN}\n\nPerforming Updates & Upgrades\n{bcolors.ENDC}")
            self.runUpdate()
            print(f"{bcolors.OKCYAN}\n\nPerforming Raspi-Config\n{bcolors.ENDC}")
            self.runChrootRaspiConfig(fullp,showroom)
            print(f"{bcolors.OKCYAN}\n\nPerforming Installation Xdesktop (only for headless), chromium (only for headless), Git and Pip3\n{bcolors.ENDC}")
            self.runChrootInstalls(headless)
            print(f"{bcolors.OKCYAN}\n\nClone & Placing Client.py in the bashrc \n{bcolors.ENDC}")
            self.gitandplaceclient()
            print(f"{bcolors.OKCYAN}\n\nInstalling pre-requisites for Client\n{bcolors.ENDC}")
            self.runCommand('sudo pip3 install getmac')
            self.runCommand('sudo pip3 uninstall psutil')
            self.runCommand('sudo pip3 install psutil --no-cache')
            # self.runCommandOUT('sudo rpi-eeprom-update -d -a')

    def doWPA(self):
        with Chroot('/mnt'):
            print(f"{bcolors.OKCYAN}\n\nCopy WPA Supplicant.conf to /etc/wpa_supplicant \n{bcolors.ENDC}")
            self.runCommandOUT('cp /home/pi/sfClient/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf')  
            
        print(f"{bcolors.OKCYAN}\n\nUnmounting Rapsberry Image and remove shares\n{bcolors.ENDC}")
        self.runUmount()

    def runChrootRaspiConfig(self,fullp,showroom):
        global state
        state = 'None'
        th = Thread(target=self.runProgress)
        th.start()
        if fullp or showroom:
            self.runCommand('raspi-config nonint do_vnc 0')
            self.runCommand('raspi-config nonint do_ssh 0')
            self.runCommand('raspi-config nonint do_12c 0')
            self.runCommand('raspi-config nonint do_blanking 0')
            self.runCommandOUT('printf "duvel1je\nduvel1je\n\n" | sudo vncpasswd -weakpwd -service')
            self.runCommandOUT('mkdir -p /home/pi/websockify')
            self.runCommandOUT('git clone -c http.sslVerify=false https://root:jup1lerforce@gitlab01.rad.priv.vangenechten.com/tmukherjee/websockify /home/pi/websockify/')
            self.runCommandOUT('cd /home/pi/websockify/')
            self.runCommandOUT('ls -la /home/pi/websockify/')
            self.runCommandOUT('sudo python3 setup.py install')
            
            self.runCommandOUT('cp /home/pi/websockify/websockify-novnc.service /lib/systemd/system/websockify-novnc.service')
            self.runCommandOUT('chmod 644 /lib/systemd/system/websockify-novnc.service')

            self.runCommandOUT("echo $'Desktop=$hostname\nEncryption=AlwaysOff\nAuthentication=VncAuth\n' | sudo tee -a /etc/vnc/config.d/common.custom")
            self.runCommandOUT('sudo systemctl restart vncserver-x11-serviced.service')
            self.runCommandOUT('sudo apt install novnc -y')
            self.runCommandOUT('printf "\n\n\n\n\n\n\n" | sudo openssl req -x509 -nodes -newkey rsa:2048 -keyout /etc/ssl/novnc.pem -out /etc/ssl/novnc.pem -days 1000')
            #self.runCommandOUT('websockify --web=/usr/share/novnc/ --cert=/etc/ssl/novnc.pem 9090 localhost:5900')
            # need to convert into the service or on start
            #self.runCommandOUT('git clone http://gitlab01.rad.priv.vangenechten.com/tmukherjee/websockify/-/blob/master/websockify-novnc.service')
            
            self.runCommandOUT('systemctl daemon-reload')
            self.runCommandOUT('systemctl enable websockify-novnc.service')
            self.runCommandOUT('systemctl start websockify-novnc.service')
            # make websockify as a service and start at startup
        else:
            self.runCommand('raspi-config nonint do_ssh 0')
            self.runCommand('raspi-config nonint do_12c 0')
            self.runCommand('raspi-config nonint do_blanking 0')
        state = 'Finished'
        th.join()

    def runChrootInstalls(self, headless):
        global state
        state = 'None'
        th = Thread(target=self.runProgress)
        th.start()
        self.runCommandOUT('touch /home/pi/imgMode.txt')
        self.runCommand('apt-get install -y sshpass python3-pip git openssl shellinabox finger --fix-missing')
        self.runCommand('apt-get -y autoclean')
        self.runCommand('apt-get -y autoremove')
        #self.runCommand("sudo sed -i 's|SHELLINABOX_ARGS|#SHELLINABOX_ARGS|g' /etc/default/shellinabox")
        #self.runCommand('echo "SHELLINABOX_ARGS=\""--no-beep --disable-ssl\""" | sudo tee -a /etc/default/shellinabox')
        if headless:
            self.runCommandOUT("echo 'headless' >> /home/pi/imgMode.txt")
            print(f"{bcolors.OKCYAN}\n\nInstalling xfce4\n{bcolors.ENDC}")
            #self.runCommand('apt-get install -y xfce4 --fix-missing')
            #self.runCommand('apt-get -y autoclean')
            #self.runCommand('apt-get -y autoremove')
            print(f"{bcolors.OKCYAN}\n\nInstalling chromium\n{bcolors.ENDC}")
            #self.runCommand('apt install -y chromium --fix-missing')
            #self.runCommand('apt-get -y autoclean')
            #self.runCommand('apt-get -y autoremove')
        else:
            self.runCommandOUT("echo 'full' >> /home/pi/imgMode.txt")
        state = 'Finished'
        th.join()


    def gitandplaceclient(self):
        if not os.path.exists('/home/pi/sfClient'):
            os.makedirs('/home/pi/sfClient')
        self.runCommandOUT(
            'git clone -c http.sslVerify=false https://root:jup1lerforce@gitlab01.rad.priv.vangenechten.com/vgp-iot/smartfactory-discovery-service /home/pi/sfClient')
        #self.runCommand('touch /etc/init.d/sfclient.sh')
        #self.runCommand("echo '#!/bin/bash' >> /etc/init.d/sfclient.sh")
        #self.runCommand("echo 'python3 /home/pi/sfClient/client.py &' >> /etc/init.d/sfclient.sh")
        #self.runCommandOUT('chmod +x /etc/init.d/sfclient.sh')
        #self.runCommandOUT('chmod 755 /etc/init.d/sfclient.sh')
        #self.runCommand('update-rc.d sfclient.sh defaults')
        #self.runCommandOUT('chmod +x /home/pi/sfClient/client.py')
        #self.runCommand("echo 'nohup python3 /home/pi/sfClient/client.py &' >> /etc/profile")
        self.runCommandOUT('cp /home/pi/sfClient/shellinabox /etc/default/shellinabox')
        self.runCommandOUT('chmod 755 /etc/default/shellinabox')
        self.runCommandOUT('cp /home/pi/sfClient/sfclient.service /lib/systemd/system/sfclient.service')
        self.runCommandOUT('chmod 644 /lib/systemd/system/sfclient.service')
        self.runCommandOUT('chmod +x /home/pi/sfClient/client.py')
        self.runCommandOUT('systemctl daemon-reload')
        self.runCommandOUT('systemctl enable sfclient.service')
        self.runCommandOUT('systemctl start sfclient.service')
        
    def exitChroot(self):
        print(os.listdir("."))
        print(os.listdir(".."))

    def runUmount(self):
        self.runCommand('umount -l /mnt')
        self.runCommand('rm -rf /mnt')


    def runCommand(self, command):
        proc = subprocess.Popen(command, shell=True, stdin=None, stdout=open(os.devnull, "wb"),
                                stderr=open(os.devnull, "wb"), executable="/bin/bash")
        proc.wait()


    def runCommandOUT(self, command):
        proc = subprocess.Popen(command, shell=True, stdin=None, stdout=None,
                                stderr=None, executable="/bin/bash")
        proc.wait()


    # get the base image to the yumrepo via sftp
    def getSftp(self, filename, remoteLocation):
        global state
        state = 'None'
        th = Thread(target=self.runProgressLine)
        th.start()
        print('Get ' + filename + ' from ' + remoteLocation)
        with Connection(host=Constant.YumRepoHost, username=Constant.YumUser, password=Constant.YumPW) as sftp:
            sftp.get(remoteLocation + filename)

        state = 'Finished'
        th.join()


    # create supporting folders
    def createSupFolders(self):
        dir = os.path.dirname(Constant.LocalBaseImage)
        if not os.path.exists(dir):
            os.makedirs(dir)
            # print(dir + ' created')

        dir = os.path.dirname(Constant.LocalDownload)
        if not os.path.exists(dir):
            os.makedirs(dir)
            # print(dir + ' created')
