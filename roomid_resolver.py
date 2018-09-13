# coding: utf-8
import random
import sys
import _thread
import time
import requests
import xml.dom.minidom
import struct
import simplejson
import socket
import urllib
import ssl
import bs4
from bs4 import BeautifulSoup

'''
B站直播房间号有两套, 一个是浏览器地址中的域名后面紧跟的那部分数字, 这个貌似是B站的房间短号, 给一些知名主播或者是自留的一些直播频道的房间号, 方便记忆传播
e.g. https://live.bilibili.com/388  388为房间短号, 其实它真正的房间号是5096, 弹幕丫获取弹幕的时候是需要5096这个房间号的, 这个应该才是B站直播房间后台的唯一标识

roomid_resolver 目的就是避免每次需要抓取弹幕的时候需要在浏览器控制台手动去找 roomid, 这program 本质上是获取HTML后找出其中的 room_id

'''


def resolve_room_id(url_room_id):
    print('resolve_room_id enter...')
    context = ssl._create_unverified_context()
    # uri = "https://live.bilibili.com/465"
    uri = "https://live.bilibili.com/" + url_room_id
    print(uri)
    doc = urllib.request.urlopen(uri, context=context)
    soup = BeautifulSoup(doc.read(), "lxml")

    # print(soup.prettify())
    # print(soup.findAll('script'))
    # print(soup.findAll('script')[16])
    # print(len(soup.findAll('script')))

    scripts = soup.findAll('script')
    for i in range(len(scripts)):
        script = str(scripts[i])
        if script.find('"room_id"') > 0:
            content = str(scripts[i].contents[0])
            json_part = content.split("=", 1)[1]
            data = simplejson.loads(json_part)
            room_id = data['roomInitRes']['data']['room_id']
            print(room_id)
            return room_id

    return None


if __name__ == '__main__':
    resolve_room_id('388')
