import os
from io import BytesIO
from tqdm import tqdm

class copyimage:
    def copy_boot(self, fileName, newName):
        file = fileName
        fsize = int(os.path.getsize(file))
        new = newName
        with open(file, 'rb') as f:
            with open(new, 'ab') as n:
                with tqdm(ncols=60, total=fsize, bar_format='{l_bar}{bar} | Remaining: {remaining}') as pbar:
                    buffer = bytearray()
                    while True:
                        buf = f.read(8192)
                        n.write(buf)
                        if len(buf) == 0:
                            break
                        buffer += buf
                        pbar.update(len(buf))
                    pbar.close()
