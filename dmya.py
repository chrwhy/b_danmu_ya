# coding: utf-8
import random
import _thread
import time
import requests
import struct
import simplejson
import socket
import logging
import zlib
import msg_parser

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
fp = logging.FileHandler('danmu-man.log', encoding='utf-8')
fs = logging.StreamHandler()
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT, handlers=[fp, fs])


def http_get_request(url):
    s = requests.session()
    response = s.get(url)
    return response.text


class DanmuYa:

    def __init__(self, room_id, u_id=0):
        self.running = False
        self.room_id = room_id
        self.api_room_detail_url = 'https://api.live.bilibili.com/room/v1/Danmu/getConf?room_id={}'.format(room_id)
        self.dm_host = None
        self.token = None
        self.socket_client = self.set_up()
        self._uid = u_id or int(100000000000000.0 + 200000000000000.0 * random.random())
        self.magic = 16
        self.ver = 1
        self.into_room = 7
        self.package_type = 1
        self.max_data_length = 65495

    def set_up(self):
        logging.debug(self.api_room_detail_url)
        room_detail_str = http_get_request(self.api_room_detail_url)
        logging.debug(room_detail_str)
        room_detail = simplejson.loads(room_detail_str)
        self.dm_host = room_detail['data']['host']
        self.token = room_detail['data']['token']
        logging.debug(self.dm_host)

        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((self.dm_host, 2243))
        self.running = True
        return conn

    def _heartbeat(self, socket_client):
        while self.running:
            try:
                heartbeat_pack = struct.pack('!IHHII', 16, 16, 1, 2, 1)
                socket_client.send(heartbeat_pack + "".encode('utf-8'))
                logging.info('Client ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤')
                time.sleep(30)
            except ConnectionAbortedError:
                logging.error("ConnectionAbortedError error: ", exc_info=True)
                self.running = False
                break

        logging.warning("Running status: %s", self.running)
        logging.warning('Heartbeat stopped...')

    def _pack_socket_data(self, data_length, data):
        _data = data.encode('utf-8')
        _send_bytes = struct.pack('!IHHII', data_length, self.magic, self.ver, self.into_room, self.package_type)
        return _send_bytes + _data

    def _recv_data(self, expect):
        left = expect
        data = bytes()
        while left > 0:
            try:
                delta = self.socket_client.recv(left)
                if len(delta) < 1:
                    pass
                    logging.warning('BROKEN')
                    return None
                data += delta
                left = left - len(delta)
            except:
                return None
        return data

    def _break_msg(self, msg_bytes):
        claimed_len, magic, ver, message_type, package_type = struct.unpack('!IHHII', msg_bytes[0:16])
        splitted_msg = msg_bytes[16:claimed_len]
        splitted_msg_json_str = splitted_msg.decode('utf-8')
        if claimed_len == len(msg_bytes):
            msg_parser.parse_danmu(splitted_msg_json_str)
            #print(splitted_msg_json_str)
            return
        else:
            self._break_msg(msg_bytes[claimed_len:])

    def _danmu_event_loop(self):
        while True:
            try:
                pre_data = self._recv_data(16)
                if pre_data is None:
                    logging.warning('Connection broken')
                    break

                claimed_len, magic, ver, message_type, package_type = struct.unpack('!IHHII', pre_data)
                if message_type == 8:
                    init_pack = self._recv_data(claimed_len - 16)
                    logging.info('Init. pack received %s', init_pack.decode())
                    continue
                if message_type != 5 and message_type != 3:
                    logging.warning('unknown message type: %s, going to stop...', str(message_type))
                    break
                if package_type != 0 and package_type != 1:
                    logging.warning('unknown package_type: %s', str(package_type))

                if claimed_len == 20:
                    logging.info('Bilibili ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤ ❤')
                    danmu_msg_package = self._recv_data(claimed_len - 16)
                    if pre_data is None:
                        logging.warning('Connection broken, going to stop...')
                        self.stop()
                        break
                    online = struct.unpack('!l', danmu_msg_package)
                    logging.info('人气值: ' + str(online[0]) + '\n')
                    continue
            except struct.error:
                logging.error('pre_data: ' + pre_data.decode('utf-8'), exc_info=True)
                logging.error('pre_data_len: ' + str(len(pre_data)), exc_info=True)
                continue
            except:
                logging.error("Unexpected error: ", exc_info=True)
                self.stop()
                break

            try:
                danmu_msg_package = self._recv_data(claimed_len - 16)
                if danmu_msg_package is None:
                    logging.warning('Connection broken')
                    break

                #logging.debug('Version No. %s', ver)
                if ver == 2:
                    deflated_msg_package = zlib.decompress(danmu_msg_package)
                    self._break_msg(deflated_msg_package)
                else:
                    danmu_msg_json = danmu_msg_package.decode('utf-8')
            except simplejson.JSONDecodeError:
                logging.error("Unexpected error: ", exc_info=True)
                logging.error('Original json: %s', danmu_msg_json)
            except UnicodeDecodeError:
                logging.error("Unexpected error:", exc_info=True)
                logging.error(danmu_msg_package)
            except:
                logging.error("Unexpected error:", exc_info=True)
                logging.error("Going to stop...")
                return

    def stop(self):
        logging.warning("stop called.")
        self.running = False
        if self.socket_client:
            self.socket_client.close()

    def start(self):
        logging.info('%s DanmuYa Go...', self.room_id)
        _thread.start_new_thread(self._heartbeat, (self.socket_client,))

        init_data = simplejson.dumps({"roomid": self.room_id, "uid": self._uid})
        total_length = 16 + len(init_data)
        data = self._pack_socket_data(total_length, init_data)
        self.socket_client.send(data)
        _thread.start_new_thread(self._danmu_event_loop, ())


if __name__ == '__main__':
    dmj = DanmuYa(47867)
    dmj.start()
    while dmj.running:
        time.sleep(5)
