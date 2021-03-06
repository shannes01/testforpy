#! /usr/bin/python3
from datetime import datetime
import sys
import json
from bcolors import bcolors
from tools import tools
import Constant
from uploads import uploads
from unzip import unzip


# link_full = https://downloads.raspberrypi.org/raspios_arm64/images/raspios_arm64-2021-04-09/2021-03-04-raspios-buster-arm64.zip
# link_headless = https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2021-05-28/2021-05-07-raspios-buster-arm64-lite.zip
# link_showroom = 'https://downloads.raspberrypi.org/raspios_arm64/images/raspios_arm64-2021-05-28/2021-05-07-raspios-buster-arm64.zip'
#class Constant(object):
#    pass

class showroomprocess:
    def start(self, rasbian):
        tool = tools()

        print(f"{bcolors.WARNING}\nCreate supporting directories\n\n{bcolors.ENDC}")
        tool.createSupFolders()

        print(f"{bcolors.WARNING}Showroom Mode \n\nUpdate and Upgrade System -- Skipping\n\n{bcolors.ENDC}")
        #tool.runUpdate()

        print(f"{bcolors.WARNING}\n\nInstall necessary tools\n\n{bcolors.ENDC}")
        tool.runInstalls()

        #Set download vars
        print(f"{bcolors.WARNING}\n\nDownloading Raspbian\n\n{bcolors.ENDC}")
        #link = 'https://downloads.raspberrypi.org/raspios_arm64/images/raspios_arm64-2021-05-28/2021-05-07-raspios-buster-arm64.zip'
        link = Constant.RaspianShowroomImage
        fileName = 'smartfactory_showroom.zip'
        targetName = 'smartfactory_showroom_'+ datetime.today().strftime("%Y-%m-%d")+'.img'
        copyName = 'smartfactory_showroom_boot_'+ datetime.today().strftime("%Y-%m-%d")+'.img'
        upload = uploads()

        if rasbian == True:
            #Download Raspian zip
            tool.downloadFile(link, fileName)
            print(f"{bcolors.WARNING}\nDownload completed{bcolors.ENDC}")
            print(f"{bcolors.WARNING}\nUnzipping the Image\n{bcolors.ENDC}")
            # Store the Raspian image on Yumrepo.
            print(f"{bcolors.WARNING}\nStoring file to Yum Repo Server\n{bcolors.ENDC}")
            upload.uploadParamikoSftp(Constant.LocalDownload, Constant.YumRepoRaspianLocation, False, fileName, '')
        else:
            tool.downloadFile(Constant.raspianYumLinkShowroom, fileName)
            print(f"{bcolors.WARNING}\nDownload from yumrepo completed{bcolors.ENDC}")
            print(f"{bcolors.WARNING}\nUnzipping the Image\n{bcolors.ENDC}")


        #Unzip the Raspian image
        print(f"{bcolors.WARNING}\n\nUnzipping the Image\n{bcolors.ENDC}")
        unz = unzip()
        unz.unzipImage(fileName, targetName, copyName)
        print(f"{bcolors.WARNING}\nImage is now inflated as " + targetName + "\n")
        print(f"{bcolors.WARNING}\nRunning Fdisk -lu to Determine Image Partitions\n{bcolors.ENDC}")

        disks = tool.fdiskLU(targetName)
        strdisk = str(json.dumps(disks))
        jdisk = json.loads(strdisk)
        print("Partition 1 : Start Sector : -", jdisk[".img1"]["Start"])
        print("Partition 2 : Start Sector : -", jdisk[".img2"]["Start"])
        startPart1 = int(jdisk[".img1"]["Start"]) * 512
        startPart2 = int(jdisk[".img2"]["Start"]) * 512
        # print(startPart1, startPart2)

        print(f"{bcolors.OKCYAN}\nMounting Sector for Root Partition{bcolors.ENDC}")
        tool.runMounts(startPart1, startPart2, targetName, copyName)

        print(f"{bcolors.OKCYAN}\nMounting Finished\n\nChrooting on Mounted Image and running Updates\n{bcolors.ENDC}")
        tool.doChroot(False,False,True)

        print(f"{bcolors.WARNING}\nExit Chroot\n{bcolors.ENDC}")

        print(f"{bcolors.OKCYAN}\nwpa_supplicant.conf\n\nGet wifi details from GIT\n{bcolors.ENDC}")
        tool.doWPA()

        print(f"{bcolors.WARNING}\nSending file to Yum Repo Server\n{bcolors.ENDC}")
        upload.uploadParamikoSftp(Constant.LocalBaseImage, Constant.YumRepoBaseImageLocation, True, targetName,
                                  copyName)

        print(f"{bcolors.WARNING}\nShowroom mode finished processing\n{bcolors.ENDC}")
        sys.exit("Finished")