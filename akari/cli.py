#!/usr/bin/env python3

import sys
from akari.gui import init_gui
from akari.__init__ import __version__
from akari.utils import handle_flags, loadDB, scan_diretory, Option

def main():
    # handle_flags() returns -2 if -v flag is passed
    options, dirname = handle_flags()
    if options.version:
        print("akari version {}".format(__version__))
        sys.exit(0)
    # handle_flags() returns -1 if -g flag is passed
    if options.gui:
        init_gui()
    # handle_flags() returns path to directory otherwise
    else:
        db = loadDB()
        scan_diretory(dirname, db, options)
        sys.exit(0)

if __name__ == '__main__':
    main()
