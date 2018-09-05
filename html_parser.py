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
import bs4
from bs4 import BeautifulSoup

print(bs4.__file__)

if __name__ == '__main__':
    print('Start')
    uri = "https://live.bilibili.com/465"
    xx = urllib.request.urlopen(uri)
    soup = BeautifulSoup(xx.read(),"lxml")    
    #print(soup.prettify())
    #print(soup.findAll('script'))
    #print(soup.findAll('script')[16])
    #print(len(soup.findAll('script')))    
    scripts = soup.findAll('script')
    for i in range(len(scripts)):        
        script=str(scripts[i])
        if script.find('"room_id"') >0:
            b=scripts[i].contents[0]
            #print(str(b))                       
            #b = b.replace("window.__NEPTUNE_IS_MY_WAIFU__=","")
            x = str(b).split("=", 1)[1]
            data=simplejson.loads(x)
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