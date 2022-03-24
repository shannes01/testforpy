#! /usr/bin/python3

import sys
from bcolors import bcolors
from startup import startup


class Imager:
    def main():
        startup.main()

    if __name__ == '__main__':
        try:
            main()
        except KeyboardInterrupt:
            sys.exit(f"{bcolors.FAIL}\n\nApplication Exited by User Interrupt{bcolors.ENDC}")
