#! /usr/bin/env python3

import json
import os 
import argparse

MAC_HOME = os.path.expanduser('~')
MAC_CHROME_PATH = f"{MAC_HOME}/Library/Application Support/Google/Chrome"
# MAC_BOOKMARKS_PATH = f"{MAC_CHROME_PATH}/Default/Bookmarks"

prog_description = \
"""
Gets a list of urls from a Chrome Bookmarks folder.
"""

def main():
    # get command line arguments
    # expects a url of the form "chrome://bookmarks/?id={bkmk id}"
    parser = argparse.ArgumentParser(prog="bookmark-export.py",
        description=prog_description)
    parser.add_argument('path', type=str, nargs='?',
        help="Chrome Bookmarks folder path")
    parser.add_argument('-o', dest='out_dir', nargs='?',
        const='.', default=None,
        help="Save url list to path if specified, else to current directory")
    parser.add_argument('--simple', dest="simple", 
        action='store_true', default=False,
        help="If set, only list titles and urls")
    parser.add_argument('--profile', dest='profile', default=None,
        help="provide the profile name that owns the bookmarks")

    args = parser.parse_args()

    # load chrome local state
    with open(f"{MAC_CHROME_PATH}/Local State", 'r') as f:
        state = json.load(f)

    # read available chrome profiles
    profiles = state['profile']['info_cache']

    # select the profile to get bookmarks from
    prof = None
    if args.profile:
        profs = [(k, v['name'], v['user_name']) for k, v in profiles.items()]
        for key, name, email in profs:
            if name == args.profile or email == args.profile:
                prof = key
                break
        else:
            raise Exception(f"profile not found: {args.profile}")

    elif state['profile']['last_used']:
        prof = state['profile']['last_used']
    else:
        prof = "Default"

    bookmark_path = f"{MAC_CHROME_PATH}/{prof}/Bookmarks"

    # load bookmarks from file
    with open(bookmark_path, 'r') as file:
        bookmarks = json.load(file)

    result = bookmarks['roots']

    # search for folder name in bookmarks
    # if no folder name given, print all
    # if folder not found, terminate
    if args.path:
        searchlist = args.path.split('/')

        base = searchlist.pop(0)
        if base in ['Bookmarks Bar', 'bar', '']:
            d = result['bookmark_bar']['children']
        elif base in ['Other Bookmarks', 'other']:
            d = result['other']['children']
        else:
            print(f"Base folder not found: {base}")
            exit()

        while searchlist:
            dname = searchlist.pop(0)
            for v in d:
                if type(v) == dict and v['name'] == dname:
                    if v['type'] == 'folder':
                        d = v['children']
                    elif v['type'] == 'url':
                        d = [v]
                    break
            else:
                print(f"folder not found: {dname}")
                exit(1)

        result = d

    if args.simple:
        for i in range(len(result)):
            result[i] = {
                'name': result[i]['name'],
                'url': result[i]['url']
            }

    # print or save
    if args.out_dir:
        with open(args.out_dir, 'w') as file:
            json.dump(result, file, indent=2)
    else:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()