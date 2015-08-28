#!/usr/bin/env python3
from email.utils import formatdate as rfc822
from datetime import datetime
import platform

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
        raise Exception("unexpected json:\n" + r)

    return r['response']['access_token']


def get_following(access_token):
    headers = {"Authorization": "Bearer " + access_token}
    r = requests.get(API_URL + "/me/following/works.json", headers=headers)
    r = r.json()

    if "response" not in r:
        raise Exception("unexpected json:\n" + r)

    return r['response']


def make_rss(works):
    def mkdate(d):
        format_string = "%Y-%m-%d %H:%M:%S %z"
        r = rfc822(datetime.strptime(d + " +0900", format_string).timestamp())
        return r

    now = rfc822(datetime.now().timestamp())
    ver = platform.python_version()

    print("<?xml version=\"1.0\"?>")
    print("<rss version=\"2.0\">")
    print("<channel>")
    print("  <title>[pixiv] フォロー新着作品</title>")
    print("  <link>http://www.pixiv.net/bookmark_new_illust.php</link>")
    print("  <pubDate>" + now + "</pubDate>")
    print("  <generator>pixivrss (Python " + ver + ")</generator>")

    for i in works:
        print("\n  <item>")
        print("    <title>" + i['title'] + " | " + i['name'] + "</title>")
        print("    <link>" + ILLUST_URL + str(item['id']) + "</link>")
        print("    <description>" + item['caption'] + "</description>")
        print("    <pubDate>" + mkdate(item['created_time']) + "</pubDate>")
        print("    <guid>" + str(item['id']) + "</guid>")
        print("  </item>")

    print("</channel>")
    print("</rss>")
