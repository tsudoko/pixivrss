#!/usr/bin/env python3

# This work is subject to the CC0 1.0 Universal (CC0 1.0) Public Domain
# Dedication license. Its contents can be found in the LICENSE file or at:
# http://creativecommons.org/publicdomain/zero/1.0/

from datetime import datetime
from email.utils import formatdate as rfc822
from html import escape
import argparse
import getpass
import os.path
import platform
import sys

import requests

CLIENT_ID = "bYGKuGVw91e0NMfPGp44euvGt59s"
CLIENT_SECRET = "HP3RmkgAmEGro0gn1x9ioawQE8WMfvLXDz3ZqxpK"

API_URL = "https://public-api.secure.pixiv.net/v1"
ILLUST_URL = "http://www.pixiv.net/member_illust.php?mode=medium&illust_id="


def get_access_token(username, password):
    auth = {
        "username": username,
        "password": password,
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    r = requests.post("https://oauth.secure.pixiv.net/auth/token", data=auth)
    r = r.json()

    if "response" not in r or "access_token" not in r['response']:
        raise Exception("unexpected json:\n" + str(r))

    return r['response']['access_token']


def get_following(access_token):
    headers = {"Authorization": "Bearer " + access_token}
    r = requests.get(API_URL + "/me/following/works.json", headers=headers)
    r = r.json()

    if "response" not in r:
        raise Exception("unexpected json:\n" + str(r))

    return r['response']


def make_rss(works):
    def mkdate(d):
        format_string = "%Y-%m-%d %H:%M:%S"
        r = rfc822(datetime.strptime(d, format_string).timestamp())
        return r

    now = rfc822(datetime.now().timestamp())
    ver = platform.python_version()

    print("<?xml version=\"1.0\"?>")
    print("<rss version=\"2.0\">")
    print("<channel>")
    print("  <title>[pixiv] フォロー新着作品</title>")
    print("  <link>http://www.pixiv.net/bookmark_new_illust.php</link>")
    print("  <pubDate>" + now + "</pubDate>")
    print("  <description />")
    print("  <generator>pixivrss (Python " + ver + ")</generator>")

    for i in works:
        title = "「%s」/「%s」" % (i['title'], i['user']['name'])

        print("\n  <item>")
        print("    <title>" + escape(title) + "</title>")
        print("    <link>" + escape(ILLUST_URL + str(i['id'])) + "</link>")
        if i['caption']:
            caption = escape(i['caption']).replace("\r\n", "<br />")
            print("    <description>" + caption + "</description>")
        print("    <pubDate>" + mkdate(i['created_time']) + "</pubDate>")
        print("    <guid>" + escape(ILLUST_URL + str(i['id'])) + "</guid>")
        print("  </item>")

    print("</channel>")
    print("</rss>")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username")
    parser.add_argument("-p", "--password")
    parser.add_argument("-n", "--unattended", action="store_true", help="don't ask for credentials")
    parser.add_argument("-t", "--token", help="use the API token instead of username/password; it's generated after logging in through the API and is usually valid for an hour")

    args = parser.parse_args()

    if not args.unattended and not args.token:
        if not args.username:
            args.username = input("Pixiv ID: ")
        if not args.password:
            args.password = getpass.getpass("Password: ")

    if not ((args.username and args.password) or args.token):
        raise Exception("not enough credentials")

    if not args.token:
        args.token = get_access_token(args.username, args.password)

    make_rss(get_following(args.token))

if __name__ == "__main__":
    main()
