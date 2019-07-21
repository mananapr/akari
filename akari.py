import os
import sys
import requests
from bs4 import BeautifulSoup

def query_iqdb(filename):
    url = 'https://iqdb.org'
    files = {'file': (filename, open(filename, 'rb'))}
    res = requests.post(url,files=files)
    return res

def parse_result(result):
    soup = BeautifulSoup(result.text, 'html.parser')
    try:
        tables = soup.find_all('table')
        search_result = tables[1].findChildren("th")[0].get_text()
    except:
        print('Unexpected Error')
        return ['undefined']
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
            tags = tag_string.split(" ")
    return tags

def handle_flags():
    num_args = len(sys.argv)
    if num_args < 2:
        print("Not enough arguments")
        sys.exit(1)
    dirname = sys.argv[1]
    if not os.path.isdir(dirname):
        print("Invalid Path")
        sys.exit(2)
    return dirname

def main():
    dirname = handle_flags()
    count = 1
    for root, d_names, f_names in os.walk(dirname):
        for f_name in f_names:
            if(f_name[-4:] in ['.jpg','.jpeg','.png']):
                fullpath = os.path.join(root, f_name)
                print("Processing Image {}: {}".format(count, f_name))
                count = count + 1
                result = query_iqdb(fullpath)
                tags = parse_result(result)
                print(tags)
                print("-----x--x-----")

main()
