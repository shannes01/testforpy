#! /usr/bin/python3
import os
from pick import pick
#from os import system, name
#import sys
from headlessprocess import headlessprocess
from fullprocess import fullprocess
from showroomprocess import showroomprocess
#from headless import headless

class startup:
    os.system('clear')

    def main(mode, source):
        # title = 'Please  select the mode'
        # options = ['Headless Mode', 'Full Mode', 'Showroom Mode', 'Exit']
        # option, index = pick(options, title, indicator='=>', default_index=0)
        if mode == 'h':
            headless.start(source)
        elif mode == 'f':
            full.start(source)
        elif mode == 's':
            showroom.start(source)
        elif mode == 3:
            quit()
        else:
            quit()

class headless:
    def start(source):
        # title = 'Headless Mode Image \n\nPlease  select the source'
        # options = ['Download from Raspberry and  Process', 'Download from Repository Server and Process', 'Back']
        # option, index = pick(options, title, indicator='=>', default_index=0)
        if source == 'i':
            headless = headlessprocess()
            headless.start(True)
        elif source == 'r':
            headless = headlessprocess()
            headless.start(False)
        #elif index == 2:
        #    startup.main()

class full:
    def start(source):
        # title = 'Full Mode Image \n\nPlease  select the source'
        # options = ['Download from Raspberry and  Process', 'Download from Repository Server and  Process', 'Back']
        # option, index = pick(options, title, indicator='=>', default_index=0)
        if source == 'i':
            fullp = fullprocess()
            fullp.start(True)
        elif source == 'r':
            fullp = fullprocess()
            fullp.start(False)
        # elif index == 2:
        #     startup.main()

class showroom:
    def start(source):
        # title = "Showroom Mode Image \n\nPlease select the source"
        # options = ['Download from Raspberry and Process', 'Download from Repository Server and Process', 'Back']
        # option, index = pick(options, title, indicator= '=>', default_index=0)
        if source == 'i':
            showroom = showroomprocess()
            showroom.start(True)
        elif source == 'r':
            showroom = showroomprocess()
            showroom.start(False)
        # elif source == 2:
        #     startup.main()
