#! /usr/bin/python3
from os import fspath
from pathlib import Path
from shutil import copyfileobj
from tqdm.auto import tqdm  # could use from tqdm.gui import tqdm
from tqdm.utils import CallbackIOWrapper
import shutil
import os
from bcolors import bcolors
from zipfile import ZipFile
from copyimage import copyimage

class unzip:
    def unzipImage(self, fileName, tFilename, cFilename):
        desc = ''
        eFile = ''
        with ZipFile('../download/' + fileName) as zipf, tqdm(
                desc=desc, unit="B", unit_scale=True, unit_divisor=1024,
                total=sum(getattr(i, "file_size", 0) for i in zipf.infolist()),
        ) as pbar:
            for i in zipf.infolist():
                if not getattr(i, "file_size", 0):  # directory
                    zipf.extract(i)
                else:
                    with zipf.open(i) as fi, open(fspath(i.filename), "wb") as fo:
                        eFile = i.filename
                        copyfileobj(CallbackIOWrapper(pbar.update, fi), fo)
        pbar.close()
        os.rename(eFile, tFilename)
        cp = copyimage()
        print(f"{bcolors.WARNING}\n\nExtracting Boot image from Main image\n{bcolors.ENDC}")
        cp.copy_boot(tFilename, cFilename)
        #shutil.copyfile(tFilename, cFilename)
