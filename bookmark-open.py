#! /usr/bin/env python3

import os
import json
import argparse
import subprocess

# Chrome command line switches
# https://peter.sh/experiments/chromium-command-line-switches/

MAC_HOME = os.path.expanduser('~')
MAC_CHROME_PATH = f"{MAC_HOME}/Library/Application Support/Google/Chrome"

CHROME_BASE_PATH = \
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

PROG_DESCRIPTION = \
"""
Given a json list file of objects with "url", 
open all of them in a new chrome window
"""

def main():
    parser = argparse.ArgumentParser(prog="bookmark-open.py",
        description=PROG_DESCRIPTION)
    parser.add_argument('file', type=str,
        help="path to json file with url list")
    parser.add_argument('-i', '--incognito', dest='incognito',
        type=bool, default=True,
        help="if set, open all urls in incognito (default)")
    parser.add_argument('-u', '--user', dest='user',
        default='work',
        help="if set, open all urls in user mode")

    args = parser.parse_args()

    # load chrome local state
    with open(f"{MAC_CHROME_PATH}/Local State", 'r') as f:
        state = json.load(f)

    # read available chrome profiles
    profiles = state['profile']['info_cache']

    # select the profile to get bookmarks from
    prof = None
    if args.user:
        profs = [(k, v['name'], v['user_name']) for k, v in profiles.items()]
        for key, name, email in profs:
            if name == args.user or email == args.user:
                prof = key
                break
        else:
            raise Exception(f"profile not found: {args.user}")

    elif state['profile']['last_used']:
        prof = state['profile']['last_used']
    else:
        prof = "Default"

    if not os.path.exists(args.file):
        print(f"File does not exist: {args.file}")
        exit(1)
    elif os.path.isdir(args.file):
        print(f"{args.file} is a directory!")
        exit(1)

    try:
        with open(args.file, 'r') as file:
            bookmarks = json.load(file)
    except:
        print(f"Couldn't read file: {args.file}")
        exit(1)

    if type(bookmarks) != list:
        print(f"File in wrong format: {args.file}")
        exit(1)
    
    chrome_args = [CHROME_BASE_PATH]

    # select profile to open with
    chrome_args.append(f'--profile-directory={prof}')

    # ensure a new window is opened
    chrome_args.append('--new-window')

    # check if open in incognito
    if args.incognito:
        chrome_args.append('--incognito')

    print(' '.join(chrome_args))

    urls = []
    for b in bookmarks:
        if 'url' in b:
            print(b['url'])
            urls.append(b['url'])

    if not urls:
        print(f"No URLs found in file: {args.file}")
        exit(1)

    chrome_args += urls

    # run chrome as subprocess
    subprocess.run(chrome_args)

if __name__ == "__main__":
    main()