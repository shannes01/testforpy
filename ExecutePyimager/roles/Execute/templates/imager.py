#! /usr/bin/python3

import sys, getopt
from bcolors import bcolors
from startup import startup


class Imager:
    def main(mode, source):
        startup.main(mode, source)

    if __name__ == '__main__':
        mode = 'h'
        source = 'i'
        print(f"Arguments count: {len(sys.argv)}")
        mode = sys.argv[1]
        source = sys.argv[2]
        try:
            main(mode, source)
        except KeyboardInterrupt:
            sys.exit(f"{bcolors.FAIL}\n\nApplication Exited by User Interrupt{bcolors.ENDC}")
