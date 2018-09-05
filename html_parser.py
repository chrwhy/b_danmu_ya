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

if __name__ == '__main__':
    print('Start...')
    context = ssl._create_unverified_context()
    uri = "https://live.bilibili.com/465"
    print(uri)
    doc = urllib.request.urlopen(uri, context=context)
    soup = BeautifulSoup(doc.read(),"lxml")    

    #print(soup.prettify())
    #print(soup.findAll('script'))
    #print(soup.findAll('script')[16])
    #print(len(soup.findAll('script')))    

    scripts = soup.findAll('script')
    for i in range(len(scripts)):        
        script=str(scripts[i])
        if script.find('"room_id"') >0:
            content=str(scripts[i].contents[0])
            json_part = content.split("=", 1)[1]
            data=simplejson.loads(json_part)
            print(data['roomInitRes']['data']['room_id'])
                                    
'''                                    
            script=str(scripts[i])
            #print(script)
            a = script.replace("<script>window.__NEPTUNE_IS_MY_WAIFU__=","")
            a = a.replace("</script>","")
            #print(a)
            data = simplejson.loads(a)
            print('================================')
            print(data['roomInitRes']['data']['room_id'])
            print('================================')
            #print(a)
            #<script>window.__NEPTUNE_IS_MY_WAIFU__=
            #</script>
'''                                   
