import configparser
import os
import sys
import json
import argparse
from string import Template

import requests
from pathlib import Path
from shutil import copyfile
from bs4 import BeautifulSoup
from argparse import Namespace as argNs
from akari import danbooru_helper, db
import re

'''
    Option is a class to collect and pass user's options

    function parse(self,argument: argns) is used to parse args to Option
'''


class Option:
    rename: bool = False
    version: bool = False
    gui: bool = False
    force: bool = False
    proxy: dict = {}
    format: str
    general_lim: int

    def __init__(self, argument: argNs):
        if argument is None:
            print("Illegal Parameters for Option Init")
            sys.exit(2)
        self.rename = argument.rename
        self.version = argument.version
        self.gui = argument.gui
        self.force = argument.force


image_extensions = ['.jpg', '.jpeg', '.png', '.gif']

# Directory for storing the database file
data_dir = str(Path.home()) + '/.config/akari'

tag_db = db.tag_database()

"""
    Submits the search form at https://iqdb.org
"""


def query_iqdb(filename):
    url = 'https://iqdb.org'
    files = {'file': (filename, open(filename, 'rb'))}
    res = requests.post(url, files=files)
    return res


"""
    Updates the tag count in the database
"""


def update_tags(tags, db):
    for tag in tags:
        if tag in db['akari-tags']:
            db['akari-tags'][tag] = db['akari-tags'][tag] + 1
        else:
            db['akari-tags'][tag] = 1


"""
    Writes the dictionary `db` to the database file
"""


def commit_changes(db):
    with open(data_dir + '/db.json', 'w') as outfile:
        json.dump(db, outfile)


"""
    Parses the response from `query_iqdb` function
    Returns a list of tags
"""


def parse_result(result):
    soup = BeautifulSoup(result.text, 'html.parser')
    try:
        tables = soup.find_all('table')
        search_result = tables[1].findChildren("th")[0].get_text()
    except:
        return ['server-error']
    tags = []
    if search_result == 'No relevant matches':
        print('No Match Found')
        tags.append('undefined')
    else:
        print('Match Found')
        alt_string = tables[1].findChildren("img")[0]['alt']
        tag_string_index = alt_string.find('Tags:')
        if tag_string_index == -1:
            tags.append('undefined')
        else:
            tag_string = alt_string[tag_string_index + 6:]
            tag_string = tag_string.lower()
            tag_string_formatted = ''.join(c for c in tag_string if c not in ',')
            tags = list(set(tag_string_formatted.split(" ")))
    return tags


"""
    Find the anime characters and return the list of them
    Using danbooru_helper to retrieve tag's category from Danbooru
    and save it to the database
    
    :parameter
        - tags: list : a list of tags
        - proxy: proxy option for user's to set, formatted in 
                proxies = {
                    'http': '127.0.0.1:6666',
                    'https': '127.0.0.1:6666',
                }
            default is None
            
    :return
        - tag_with_category: a dict
            - key: category_name: str
            - value: a list of tags  
"""


def categorize_tags(tags, proxies=None):
    tag_with_category = {
        "general": [],
        "artist": [],
        "copyright": [],
        "character": [],
        "meta": [],
    }
    try:
        for _, tag in enumerate(tags):
            tag_category = danbooru_helper.search_tag_category(tag, proxy=proxies)
            tag_with_category[tag_category].append(tag)
            tag_db.add_tag(tag, tag_category)

        return tag_with_category
    except ValueError as val_err:
        print(str(val_err))
        sys.exit(2)
    except NotImplementedError as err:
        print(f"Sorry :( \n{str(err)}\n. Please give me the issue on the github.")
        sys.exit(2)


"""
    Generate new_name formatted in the settings and return newname
    Use `re.findall(r"{(\w+)}", strs)` to find all placeholder
"""


def newname_generator(tag_dict: dict, image_path: str, option: Option):
    placeholders = re.findall(r"{(\w+)}", option.format)
    new_name = ""
    sub_dict=dict()
    for i, placeholder in enumerate(placeholders):
        if i == 0:
            for j, tag in enumerate(tag_dict[placeholder]):
                if j == 0:
                    new_name = new_name+tag
                    continue
                elif len(new_name + ';' + tag) >= 256:
                    break
                else:
                    new_name = new_name+";"+tag
            sub_dict[placeholder]=new_name
            new_name=""
        else:
            for j, g_tag in enumerate(tag_dict[placeholder]):  # g_tag aka general tag
                if len(new_name + ';' + g_tag) >= 256 or j > option.general_lim:
                    break
                if j == 0:
                    new_name = new_name + g_tag
                else:
                    new_name = new_name + ';' + g_tag
            sub_dict[placeholder]=new_name
            new_name=""

    template = Template(option.format)
    print(sub_dict)
    print(option.format)
    return template.safe_substitute(sub_dict)



"""
    Scans `dirname` directory for images and adds their paths in db
    Then adds tags for those images by calling `query_iqdb` and `parse_result`
    Finally it updates the tags and writes the changes to the database file
    
    Use the format of "{char}+{general}(limit:4)"
"""


def scan_directory(dirname, db, options: Option):
    image_paths = []
    count = 1

    for root, d_names, f_names in os.walk(dirname):
        for f_name in f_names:
            if f_name[-4:] in image_extensions:
                fullpath = os.path.join(root, f_name)
                image_paths.append(fullpath)

    num_of_images = len(image_paths)
    for image in image_paths:
        filename = os.path.basename(os.path.normpath(image))
        print("Processing Image {} of {}: {}".format(count, num_of_images, filename))
        count = count + 1
        if options.force is False and image in db and db[image] != ['server-error']:
            print('Already exits in DB. Skipping...')
        else:
            result = query_iqdb(image)
            tags = parse_result(result)

            if options.rename:
                if tags[0] != "undefined" and tags[0] != "server-error":
                    _, extension_name = os.path.splitext(os.path.normpath(image))
                    new_name = os.path.dirname(os.path.normpath(image))
                    print(new_name)
                    tag_dict = categorize_tags(tags, proxies=options.proxy)

                    if tag_dict is not None:
                        new_name = newname_generator(tag_dict, new_name, options)
                        new_name = os.path.join(os.path.dirname(os.path.normpath(image)),new_name)
                    else:
                        for i in range(len(tags)):
                            if i == 0:
                                new_name = os.path.join(new_name, tags[i])
                            else:
                                if len(new_name + '_' + tags[i]) >= 256:
                                    break
                                new_name = new_name + '_' + tags[i]
                    new_name_count = 1
                    if os.path.isfile(new_name + extension_name):
                        while os.path.isfile(new_name + str(f"({new_name_count})") + extension_name):
                            new_name_count = new_name_count + 1
                        new_name = os.path.normpath(
                            new_name + str("({count})").format(count=new_name_count) + extension_name)
                    else:
                        new_name = os.path.normpath(new_name + extension_name)
                    os.rename(src=image, dst=new_name)
                    print(f"renaming {image} to {new_name}")
                    image = new_name

            db[image] = tags
            update_tags(tags, db)
            commit_changes(db)
            print(tags)

        print("-----x--x-----")


"""
    Initialises the db dictionary.
    Looks for the database file in the data directory and creates one if it doesn't exists
    It looks for missing files in the database and then finally returns the updated db dictionary
"""


def loadDB():
    db = {}
    db['akari-tags'] = {}
    misplaced_files = []
    tags_to_remove = []
    db_location = data_dir + '/db.json'

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    if os.path.isfile(db_location):
        copyfile(db_location, db_location + '.backup')
        with open(db_location) as json_db:
            db = json.load(json_db)

    for key in db:
        if key == 'akari-tags':
            continue
        if not os.path.isfile(key):
            misplaced_files.append(key)
    for file in misplaced_files:
        for tag in db[file]:
            db['akari-tags'][tag] = db['akari-tags'][tag] - 1
            if db['akari-tags'][tag] == 0:
                tags_to_remove.append(tag)
        db.pop(file, None)
        print('{} misplaced'.format(file))
    for tag in tags_to_remove:
        db['akari-tags'].pop(tag, None)
        print('{} tag removed'.format(tag))

    commit_changes(db)
    return db


'''
    read config from ~/.config/akari/settings.conf
'''


def read_config(option: Option):
    config = configparser.ConfigParser()
    config_path = os.path.join(Path.home(), ".config", "akari", "settings.conf")
    # If no configuration file detected, Create one
    if not os.path.isfile(config_path):
        config["Common"] = {
            "format": "${char}+${general}",
            "general_num_limit": "5"
        }
        with open(config_path, 'w') as configFile:
            config.write(configFile)
    else:
        config.read(config_path)
    option.format = config["Common"]["format"]
    option.general_lim = int(config["Common"]["general_num_limit"])
    common_conf = config["Common"]
    if common_conf.get("http_proxy") is not None or common_conf.get("https_proxy") is not None:
        option.proxy["http"] = common_conf.get("http_proxy")
        option.proxy["https"] = common_conf.get("https_proxy")
    else:
        option.proxy = None


"""
    Handles the command line arguments
    :returns
        option: Option : parse the command line option
        dirname: str   : the absolute path to the working directory
    Exits otherwise
    
"""


def handle_flags():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--scan', metavar='/path/to/dir', required=True, help='Scan directory for new images',
                        default=None)
    parser.add_argument('-g', '--gui', help='Start the GUI', action='store_true')
    parser.add_argument('-v', '--version', help='Displays the version', action='store_true')
    parser.add_argument('-r', '--rename', help='Rename the image if tags are detected', action="store_true")
    parser.add_argument('-f', '--force', help='force akari to identify the image', action='store_true')
    parser.add_argument('--http_proxy', help='HTTP proxy for accessing website(Danbooru) (e.g.: 127.0.0.1:1234)',
                        default="")
    parser.add_argument('--https_proxy', help='HTTPS proxy for accessing website(Danbooru) (e.g.: 127.0.0.1:1234)',
                        default="")
    args = parser.parse_args()
    dirname = args.scan

    if args.version:
        return Option(args), None
    if args.gui:
        return Option(args), None
    if dirname is None:
        parser.print_help(sys.stderr)
        sys.exit(2)
    if not os.path.isdir(dirname):
        print("Invalid Path")
        parser.print_help(sys.stderr)
        sys.exit(2)
    option = Option(args)
    read_config(option)
    return option, dirname
