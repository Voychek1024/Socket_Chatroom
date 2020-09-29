import hashlib
import math
import socket
import sys
from threading import Thread

from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QLineEdit, QListWidgetItem, QFileDialog

from chatroom import *
from login import *
from register import *


def get_md5(_str: str):
    hl = hashlib.md5()
    hl.update(_str.encode(encoding='utf-8'))
    return hl.hexdigest()


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

    def send_file(self, filename, binary):
        self.sk.sendall(bytes("5", "utf-8"))
        self.send_string_with_length(filename)
        self.send_string_with_length(binary)
        # TODO: new written file transfer pattern

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


class MyDialog(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(MyDialog, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.submit)
        self.pushButton_2.clicked.connect(self.cancel)
        self.initUi()

    def initUi(self):
        self.setWindowTitle('Register Submission')
        self.setWindowIcon(QtGui.QIcon("register.png"))

    def submit(self):
        QDialog.close(self)

    def cancel(self):
        self.lineEdit_1.clear()
        self.lineEdit_2.clear()
        self.lineEdit_3.clear()
        QDialog.close(self)


class ChatRoom(QMainWindow, Ui_Window):
    def __init__(self, parent=None):
        super(ChatRoom, self).__init__(parent)
        self.setupUi(self)

    def initUI(self):
        self.setWindowTitle("TCP Chatroom")
        self.setWindowIcon(QtGui.QIcon("chatroom.png"))
        self.show()


def get_time():
    current_time = QDateTime.currentDateTime()
    label_time = current_time.toString("yyyy-MM-dd\thh:mm:ss")
    return label_time


def append_text(_str, _color):
    color_dict = {"red": "#ff0000", "blue": "#0000ff", "black": "#000000", "teal": "#008080"}
    _content = "<span style=\" color: {};\">{}</span>".format(color_dict[_color], _str)
    return _content


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.register)
        self.pushButton_2.clicked.connect(self.login)
        self.pushButton_3.clicked.connect(self.close)
        image = QtGui.QImage(QtGui.QImageReader("login_assist.png").read())
        self.label.setPixmap(QtGui.QPixmap(image))

        self.lineEdit_2.setEchoMode(QLineEdit.Password)
        self.lineEdit_2.setStyleSheet('lineedit-password-character: 35')
        self.lineEdit_2.returnPressed.connect(self.login)

        self.dialog_window = MyDialog(self)
        self.client = ChatClient()
        self.chatroom = ChatRoom(self)
        self.initUI()

        self.chatroom.actionQuit.triggered.connect(self.quit)
        self.chatroom.pushButton.clicked.connect(self.send_message)
        self.chatroom.pushButton_2.clicked.connect(self.chatroom.lineEdit.clear)
        self.chatroom.actionFile_Transfer.triggered.connect(lambda: Thread(target=self.get_file).start())
        # TODO: [DEBUG] program stop after single transfer
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.recv_data)

        # self.vir = True

    def initUI(self):
        self.setWindowTitle("TCP Login")
        self.setWindowIcon(QtGui.QIcon("login.png"))
        self.show()

    def register(self):
        self.dialog_window.exec_()
        print(self.dialog_window.lineEdit_1.text())
        user, key, confirm = (str(self.dialog_window.lineEdit_1.text()), str(self.dialog_window.lineEdit_2.text()),
                              str(self.dialog_window.lineEdit_3.text()))
        if user == '' or key == '' or key != confirm:
            self.label_5.setText('invalid register!')
            return
        result = self.client.register_user(user, get_md5(key))
        if result == "0":
            self.label_5.setText('register successful.\nPlease Login.')
        elif result == "1":
            self.label_5.setText('register err!\nsame username.')
        elif result == "2":
            self.label_5.setText('register err!\nunknown error.')

    def login(self):
        print("Begin login sequence...")
        user, key = (str(self.lineEdit_1.text()), str(self.lineEdit_2.text()))
        key = get_md5(key)
        if user == '' or key == '':
            self.label_5.setText('invalid username or pwd!')
            return
        if self.client.check_user(user, key):
            # start main window
            # Thread(target=recv_data).start()
            print('successful login..')
            self.close()
            self.chatroom.initUI()
            self.chatroom.textBrowser.clear()
            self.chatroom.lineEdit.clear()
            Thread(target=self.recv_data).start()
            # self.timer.start(1000)
        else:
            self.label_5.setText('wrong username or pwd!')
            return

    def send_message(self):
        print("sending message..")
        content = str(self.chatroom.lineEdit.text())
        if content == "" or content == '\n':
            print("cannot send empty.")
            return
        print(content)
        self.client.send_message(content)
        self.chatroom.lineEdit.clear()

    def recv_data(self):
        while True:
            try:
                _type = self.client.recv_all_string()
                print("recv type: " + _type)
                if _type == "#!online_list#!":
                    print("receiving online list..")
                    online_list = list()
                    for n in range(self.client.recv_number()):
                        online_list.append(self.client.recv_all_string())
                    print(online_list)
                    self.chatroom.listWidget.clear()
                    for item in online_list:
                        _item = QListWidgetItem("{}".format(item))
                        self.chatroom.listWidget.addItem(_item)
                elif _type == "#!message#!":
                    print("receiving new message..")
                    user = self.client.recv_all_string()
                    content = self.client.recv_all_string()
                    time_stamp = get_time()
                    _str = user + '\t' + time_stamp
                    if user == self.lineEdit_1.text():
                        self.chatroom.textBrowser.append(append_text(_str, "teal"))
                        self.chatroom.textBrowser.append(append_text(content, "black"))
                    else:
                        self.chatroom.textBrowser.append(append_text(_str, "blue"))
                        self.chatroom.textBrowser.append(append_text(content, "black"))
                elif _type == "#!file_transfer#!":
                    print("get file...")
                    pass
            except Exception as e:
                print("client error" + str(e))
                # self.chatroom.close()
                if "WinError 10054" in str(e):
                    time_stamp = get_time()
                    self.chatroom.textBrowser.append(append_text("Service Alert\t" + time_stamp, "red"))
                    self.chatroom.textBrowser.append(append_text("You've been kicked by server!", "black"))
                    self.chatroom.lineEdit.setEnabled(False)
                break

    def get_file(self):
        """Get File Select Func Done...
        home_dir = str(Path.home())
        f_name = QFileDialog.getOpenFileName(self, 'Open file', home_dir)
        print(f_name)
        """
        # TODO：we may need another func to append bubbles to textBrowser
        #  send_message(self, filename, content), file select need another window to prevent stop responding.
        f_name = QFileDialog.getOpenFileName(self, 'Open File')
        if f_name[0]:
            file_name = f_name[0].split("/")[-1]
            with open(file_name, 'rb') as in_file:
                binary = in_file.read()
            self.client.send_file(file_name, binary.decode("utf-8"))

    def quit(self):
        print("disconnecting from socket...")
        self.client.sk.close()
        self.chatroom.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWin = MyWindow()
    myWin.show()
    sys.exit(app.exec_())
