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
import parser

PRINT_JSON = False


def print_json(json_data):
    if PRINT_JSON:
        print('☘ ☘ Json format☘ ☘')
        print(json_data)
        print('\n')


def _heartbeat(self):
    while True:
        time.sleep(30)
        # heartbeat_pack = struct.pack('!IHHII', length, magic_num, version, msg_type, data_exchange_pack)
        heartbeat_pack = struct.pack('!IHHII', 16, 16, 1, 2, 1)
        self.socket_client.send(heartbeat_pack + "".encode('utf-8'))
        print('Client ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤\n')
        # \u2665


class DMJBot(object):
    def __init__(self, room_id, u_id=0):
        self.room_id = room_id
        self.api_room_detail_url = 'https://api.live.bilibili.com/api/player?id=cid:{}'.format(room_id)
        self.dm_host = None
        self.socket_client = self._set_up()
        self._uid = u_id or int(100000000000000.0 + 200000000000000.0 * random.random())
        self.magic = 16
        self.ver = 1
        self.into_room = 7
        self.package_type = 1
        self.max_data_length = 65495

    def _set_up(self):
        room_detail_xml_string = self._http_get_request(self.api_room_detail_url)
        xml_string = ('<root>' + room_detail_xml_string.strip() + '</root>').encode('utf-8')
        root = xml.dom.minidom.parseString(xml_string).documentElement
        dm_server = root.getElementsByTagName('dm_server')
        self.dm_host = dm_server[0].firstChild.data
        # self.dm_host = '120.92.112.150'

        # tcp_socket return
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((self.dm_host, 2243))
        print(self.dm_host)
        return s

    def _http_get_request(self, url):
        s = requests.session()
        response = s.get(url)
        return response.text

    def _pack_socket_data(self, data_length, data):
        _data = data.encode('utf-8')
        _send_bytes = struct.pack('!IHHII', data_length, self.magic, self.ver, self.into_room, self.package_type)
        return _send_bytes + _data

    def read_data(self, expect):
        left = expect
        data = bytes()
        while left > 0:
            delta = self.socket_client.recv(left)
            if len(delta) < 1:
                print('BROKEN')
                return None
            data += delta
            left = expect - len(delta)
        return data

    def _start(self):
        _thread.start_new_thread(_heartbeat, (self,))
        # 是JSON 前面要补16字节数据
        _dmj_data = simplejson.dumps({
            "roomid": self.room_id,
            "uid": self._uid,
        }, separators=(',', ':'))
        total_length = 16 + len(_dmj_data)
        data = self._pack_socket_data(total_length, _dmj_data)
        self.socket_client.send(data)
        # 会断是因为心跳问题，需要30秒内发送心跳
        # 这里先接收确认进入房间的信息
        self.socket_client.recv(16)

        while True:
            pre_data = self.read_data(16)

            try:
                claimed_len, magic, ver, message_type, package_type = struct.unpack('!IHHII', pre_data)
                if claimed_len == 20:
                    print('Bilibili ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤')
                    danmu_msg_package = self.socket_client.recv(claimed_len - 16)
                    online = struct.unpack('!l', danmu_msg_package)
                    print('人气值: ' + str(online[0]) + '\n')
                    continue
            except struct.error:
                print('pre_data: ' + pre_data.decode('utf-8'))
                print('pre_data_len: ' + str(len(pre_data)))
                continue
            except:
                print("Unexpected error:", sys.exc_info()[0])
                continue

            try:
                danmu_msg_package = self.read_data((claimed_len - 16))
                danmu_msg_json = danmu_msg_package.decode('utf-8')
                print_json(danmu_msg_json)
                json_data = simplejson.loads(danmu_msg_json)
                danmu_brief = parser.parse_danmu(danmu_msg_json)
            except simplejson.JSONDecodeError:
                print('json error: ' + danmu_msg_json + '\n\n')
                # continue
            except UnicodeDecodeError:
                print('UnicodeDecodeError***************************')
                print(danmu_msg_package)
                print('UnicodeDecodeError***************************\n\n')
                # continue
            except:
                print("Unexpected error:", sys.exc_info()[0])


if __name__ == '__main__':
    print(sys.argv)
    print('https://api.live.bilibili.com/api/player?id=cid:{}'.format(139))
    # Diffir Live
    # room_id=5565763
    room_id = 1029
    dmj = DMJBot(room_id)
    dmj._start()
