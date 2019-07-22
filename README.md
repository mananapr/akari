# akari
akari is a work in progress python program to manage anime artwork. currently it uses [iqdb](https://iqdb.org) to reverse-search images and fetch appropriate tags.

## Requirements
- requests
- BeautifulSoup 4
- PyQt5

## Installation
For user installation, simply run:

    pip3 install --user akari
    
Then add `$HOME/.local/bin` to your `$PATH`:

    echo PATH=\"\$PATH:\$HOME/.local/bin\" >> $HOME/.bashrc
    source $HOME/.bashrc

Alternatively, you can do a system wide installtion:

    sudo pip3 install akari

## Usage
    usage: akari [-h] [-s /path/to/dir] [-g]

    optional arguments:
      -h, --help            show this help message and exit
      -s /path/to/dir, --scan /path/to/dir
                            Scan directory for new images
      -g, --gui             Start the GUI
      -v, --version         Displays the version


[TODO](https://github.com/mananapr/akari/issues/1)
