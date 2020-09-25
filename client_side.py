import hashlib
import socket
import math
from time import sleep
from threading import Thread


class ChatClient:
    def __init__(self):
        print("Initializing Client..")
        self.sk = socket.socket()
        self.sk.connect(('localhost', 18000))

    def check_user(self, user, key):
        self.sk.sendall(bytes("1", "utf-8"))
        self.send_string_with_length(user)
        self.send_string_with_length(key)
        check_result = self.recv_string_with_length(1)
        return check_result == "1"

    def register_user(self, user, key):
        self.sk.sendall(bytes("2", "utf-8"))
        self.send_string_with_length(user)
        self.send_string_with_length(key)
        return self.recv_string_with_length(1)

    def send_message(self, message):
        self.sk.sendall(bytes("3", "utf-8"))
        self.send_string_with_length(message)

    def send_string_with_length(self, content):
        self.sk.sendall(bytes(content, encoding='utf-8').__len__().to_bytes(4, byteorder='big'))
        self.sk.sendall(bytes(content, encoding='utf-8'))

    def recv_string_with_length(self, _len):
        return str(self.sk.recv(_len), 'utf-8')

    def send_number(self, index):
        self.sk.sendall(int(index).to_bytes(4, byteorder='big'))

    def recv_number(self):
        return int.from_bytes(self.sk.recv(4), byteorder='big')

    def recv_all_string(self):
        length = int.from_bytes(self.sk.recv(4), byteorder='big')
        b_size = 3 * 1024
        times = math.ceil(length / b_size)
        content = ""
        for i in range(times):
            if i == times - 1:
                seg_b = self.sk.recv(length % b_size)
            else:
                seg_b = self.sk.recv(b_size)
            content += str(seg_b, encoding='utf-8')
        return content


def get_md5(_str: str):
    hl = hashlib.md5()
    hl.update(_str.encode(encoding='utf-8'))
    return hl.hexdigest()


def send_message(message):
    print("sending message..")
    content = message
    if content == "" or content == '\n':
        print("cannot send empty.")
        return
    print(content)
    client.send_message(content)


def close_sk():
    print('disconnecting socket..')
    client.sk.close()


def login():
    print("login sequence..")
    user, key = ("python", "123456")
    key = get_md5(key)
    if user == '' or key == '':
        print('invalid username or pwd!')
        return
    if client.check_user(user, key):
        # start main window
        Thread(target=recv_data).start()
        pass
    else:
        print('invalid username or pwd!!')
        return


def register_submit():
    print("Initializing register..")
    user, key, confirm = ("", "", "")
    if user == '' or key == '' or key != confirm:
        print('invalid register！')
        return
    result = client.register_user(user, get_md5(key))
    if result == "0":
        print('register successful..')
    elif result == "1":
        print('same username.')
    elif result == "2":
        print('unknown error.')


def recv_data():
    sleep(1)
    while True:
        try:
            # 首先获取数据类型
            _type = client.recv_all_string()
            print("recv type: " + _type)
            if _type == "#!onlinelist#!":
                print("receiving online list..")
                online_list = list()
                for n in range(client.recv_number()):
                    online_list.append(client.recv_all_string())
                # main_frame.refresh_friends(online_list)
                print(online_list)
            elif _type == "#!message#!":
                print("receiving new message..")
                user = client.recv_all_string()
                print("user: " + user)
                content = client.recv_all_string()
                print("message: " + content)
                # main_frame.recv_message(user, content)
        except Exception as e:
            print("client error" + str(e))
            break


if __name__ == '__main__':
    client = ChatClient()
    login()
