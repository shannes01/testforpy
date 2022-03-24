#! /usr/bin/python3
import os
from pick import pick
#from os import system, name
#import sys
from headlessprocess import headlessprocess
from fullprocess import fullprocess
#from headless import headless

class startup:
    os.system('clear')

    def main():
        title = 'Please  select the mode'
        options = ['Headless Mode', 'Full Mode', 'Exit']
        option, index = pick(options, title, indicator='=>', default_index=0)
        if index == 0:
            headless.start()
        elif index == 1:
            full.start()
        elif index == 2:
            quit()
        else:
            print("Invalid options")

class headless:
    def start():
        title = 'Headless Mode Image \n\nPlease  select the source'
        options = ['Download from Raspberry and  Process', 'Download from Repository Server and Process', 'Back']
        option, index = pick(options, title, indicator='=>', default_index=0)
        if index == 0:
            headless = headlessprocess()
            headless.start(True)
        elif index == 1:
            headless = headlessprocess()
            headless.start(False)
        elif index == 2:
            startup.main()

class full:
    def start():
        title = 'Full Mode Image \n\nPlease  select the source'
        options = ['Download from Raspberry and  Process', 'Download from Repository Server and  Process', 'Back']
        option, index = pick(options, title, indicator='=>', default_index=0)
        if index == 0:
            fullp = fullprocess()
            fullp.start(True)
        elif index == 1:
            fullp = fullprocess()
            fullp.start(False)
        elif index == 2:
            startup.main()

