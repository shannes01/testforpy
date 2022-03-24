import Constant
import paramiko
import os
import shutil
from tqdm import tqdm

class uploads:
    def progress_bar(self, *args, **kwargs):
        pbars = tqdm(*args, **kwargs)
        last = [0]  # last block transferred

        def progress_wrapper(transferred, to_be_transferred):
            pbars.total = int(to_be_transferred)
            pbars.update(int(transferred - last[0]))  # transferred subtract from last block transferred
            last[0] = transferred  # update last block transferred
            if transferred == to_be_transferred:
                pbars.close()
        return progress_wrapper, pbars

    def uploadParamikoSftp(self, localFolder, remoteLocation, doUploadImg, imgFilePath, bootImagePath):
        t = paramiko.SSHClient()
        t.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        t.connect(Constant.YumRepoHost, 22, username=Constant.YumUser, password=Constant.YumPW)
        sftp = t.open_sftp()
        #callback_progress = functools.partial(self.printProgress, imgFilePath)
        callback_progress, pbars = self.progress_bar(unit='B', unit_scale=True, miniters=1)
        if doUploadImg == True:
            try:
                os.remove(Constant.LocalBaseImage + imgFilePath)
            except:
                pass
            sftp.chdir(Constant.YumRepoBaseImageLocation)
            sftp.put(imgFilePath, imgFilePath, callback=callback_progress)
            shutil.move(imgFilePath, Constant.LocalBaseImage + imgFilePath)
            os.remove(bootImagePath)
        else:
            sftp.chdir(remoteLocation)
            sftp.put(localFolder + imgFilePath, imgFilePath, callback=callback_progress)
        t.close()
