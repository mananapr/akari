import os
import sys
import json
import argparse
import requests
from pathlib import Path
from shutil import copyfile
from bs4 import BeautifulSoup

image_extensions = ['.jpg','.jpeg','.png','.gif']
data_dir = str(Path.home()) + '/.config/akari'

def query_iqdb(filename):
    url = 'https://iqdb.org'
    files = {'file': (filename, open(filename, 'rb'))}
    res = requests.post(url,files=files)
    return res

def update_tags(tags, db):
    for tag in tags:
        if tag in db['akari-tags']:
            db['akari-tags'][tag] = db['akari-tags'][tag] + 1
        else:
            db['akari-tags'][tag] = 1

def commit_changes(db):
    with open(data_dir+'/db.json', 'w') as outfile:
        json.dump(db, outfile)

def parse_result(result):
    soup = BeautifulSoup(result.text, 'html.parser')
    try:
        tables = soup.find_all('table')
        search_result = tables[1].findChildren("th")[0].get_text()
    except:
        print('Unexpected Error')
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
            tag_string = alt_string[tag_string_index+6:]
            tag_string = tag_string.lower()
            tag_string_formatted  = ''.join(c for c in tag_string if c not in ',')
            tags = list(set(tag_string_formatted.split(" ")))
    return tags

def scan_diretory(dirname, db):
    image_paths = []
    count = 1
    for root, d_names, f_names in os.walk(dirname):
        for f_name in f_names:
            if(f_name[-4:] in image_extensions):
                fullpath = os.path.join(root, f_name)
                image_paths.append(fullpath)
    num_of_images = len(image_paths)
    for image in image_paths:
        filename = os.path.basename(os.path.normpath(image))
        print("Processing Image {} of {}: {}".format(count, num_of_images, filename))
        count = count + 1
        if image in db and db[image] != ['server-error']:
            print('Already exits in DB. Skipping...')
        else:
            result = query_iqdb(image)
            tags = parse_result(result)
            db[image] = tags
            update_tags(tags, db)
            commit_changes(db)
            print(tags)
        print("-----x--x-----")

def loadDB():
    db = {}
    db['akari-tags'] = {}
    misplaced_files = []
    tags_to_remove = []
    db_location = data_dir + '/db.json'

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    if os.path.isfile(db_location):
        copyfile(db_location,db_location+'.backup')
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

def handle_flags():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s','--scan',metavar='/path/to/dir',help='Scan directory for new images',default=None)
    parser.add_argument('-g','--gui',help='Start the GUI',action='store_true')
    parser.add_argument('-v','--version',help='Displays the version',action='store_true')
    args = parser.parse_args()
    dirname = args.scan

    if args.version == True:
        return -2
    if args.gui == True:
        return -1
    if dirname is None:
        parser.print_help(sys.stderr)
        sys.exit(2)
    if not os.path.isdir(dirname):
        print("Invalid Path")
        parser.print_help(sys.stderr)
        sys.exit(2)

    return dirname
