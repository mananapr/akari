#!/usr/bin/env python3

import sys
from akari.gui import init_gui
from akari.__init__ import __version__
from akari.utils import handle_flags, loadDB, scan_diretory

def main():
    dirname = handle_flags()
    if dirname == -2:
        print("akari version {}".format(__version__))
        sys.exit(0)
    if dirname == -1:
        init_gui()
    else:
        db = loadDB()
        scan_diretory(dirname, db)
        sys.exit(0)

if __name__ == '__main__':
    main()
