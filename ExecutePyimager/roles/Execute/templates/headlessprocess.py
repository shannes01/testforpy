#! /usr/bin/python3
from datetime import datetime
import json
import sys

import Constant
from bcolors import bcolors
from tools import tools
from unzip import unzip
from uploads import uploads


# link_full = https://downloads.raspberrypi.org/raspios_arm64/images/raspios_arm64-2021-04-09/2021-03-04-raspios-buster-arm64.zip
# link_headless = https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2021-05-28/2021-05-07-raspios-buster-arm64-lite.zip
# link_showroom = 'https://downloads.raspberrypi.org/raspios_arm64/images/raspios_arm64-2021-05-28/2021-05-07-raspios-buster-arm64.zip'
class headlessprocess:
    def start(self, rasbian):
        tool = tools()

        print(f"{bcolors.WARNING}\nCreate supporting directories\n\n{bcolors.ENDC}")
        tool.createSupFolders()

        print(f"{bcolors.WARNING}Headless Mode \n\nUpdate and Upgrade System -- Skipping\n\n{bcolors.ENDC}")
        #tool.runUpdate()

        print(f"{bcolors.WARNING}\n\nInstall necessary tools\n\n{bcolors.ENDC}")
        tool.runInstalls()

        print(f"{bcolors.WARNING}\n\nDownloading Raspbian\n\n{bcolors.ENDC}")
        #link = 'https://downloads.raspberrypi.org/raspios_lite_arm64/images/raspios_lite_arm64-2021-04-09/2021-03-04-raspios-buster-arm64-lite.zip'
        link = Constant.RaspianHeadlessImage
        fileName = 'smartfactory_headless.zip'
        targetName = 'smartfactory_headless_'+ datetime.today().strftime("%Y-%m-%d")+'.img'
        copyName = 'smartfactory_headless_boot_'+ datetime.today().strftime("%Y-%m-%d")+'.img'
        upload = uploads()

        if rasbian == True:
            tool.downloadFile(link, fileName)
            print(f"{bcolors.WARNING}\nDownload Raspian completed{bcolors.ENDC}")
            # Store the Raspian image on Yumrepo.
            print(f"{bcolors.WARNING}\nStoring file to Yum Repo Server\n{bcolors.ENDC}")
            upload.uploadParamikoSftp(Constant.LocalDownload, Constant.YumRepoRaspianLocation, False, fileName, '')
        else:
            tool.downloadFile(Constant.raspianYumLinkHeadless, fileName)

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
        tool.doChroot(True,False,False)

        print(f"{bcolors.WARNING}\nExit Chroot\n{bcolors.ENDC}")

        print(f"{bcolors.WARNING}\nSending img files from local to Yum Repo Server\n{bcolors.ENDC}")
        #upload.uploadParamikoSftp(Constant.LocalBaseImage, Constant.YumRepoBaseImageLocation, True, targetName,
                                  #copyName)

        print(f"{bcolors.WARNING}\nHeadless mode finished processing\n{bcolors.ENDC}")
        sys.exit("Finished")
