import sys
import socket
from threading import Thread
import math

from PyQt5.QtCore import QTimer, QTime, Qt, QDateTime
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QSystemTrayIcon, QMenu, QAction, QStyle, qApp, \
    QTableWidgetItem, QTableWidget, QListWidget, QListWidgetItem, QLabel, QMessageBox

from server_ui import *

online_conn = list()
user_conn = dict()


def check_user(user, key):
    myWin.textBrowser.append(append_text("login[user:{},key:{}]".format(user, key), "black"))
    with open("server\\data\\user.txt", 'r', encoding='utf-8') as user_data:
        lines = user_data.readlines()
        for line in lines:
            row = line.strip().split('\t')
            _user = row[0]
            _key = row[1]
            if _user == user and _key == key:
                return True
        return False


def add_user(user, key):
    try:
        myWin.textBrowser.append(append_text("register[user:{},key:{}]".format(user, key), "black"))
        with open("server\\data\\user.txt", 'r', encoding='utf-8') as user_data:
            lines = user_data.readlines()
            for line in lines:
                _user = line.strip().split('\t')[0]
                if _user == user:
                    return "1"

        with open("server\\data\\user.txt", 'a', encoding='utf-8') as user_data:
            row = user + '\t' + key + '\n'
            user_data.write(row)
        return "0"
    except Exception as e:
        myWin.textBrowser.append(append_text("appending user data err: {}".format(str(e)), "black"))
        return "2"


def get_user_conn(_user):
    for key, value in user_conn.items():
        if _user == value:
            return key


def send_string_with_length(_conn, content):
    _conn.sendall(bytes(content, encoding='utf-8').__len__().to_bytes(4, byteorder='big'))
    _conn.sendall(bytes(content, encoding='utf-8'))


def recv_string_with_length(_conn, _len):
    return str(_conn.recv(_len), 'utf-8')


def send_number(_conn, index):
    _conn.sendall(int(index).to_bytes(4, byteorder='big'))


def recv_number(_conn):
    return int.from_bytes(_conn.recv(4), byteorder='big')


def recv_all_string(_conn):
    length = int.from_bytes(_conn.recv(4), byteorder='big')
    b_size = 3 * 1024
    times = math.ceil(length / b_size)
    content = ""
    for i in range(times):
        if i == times - 1:
            seg_b = _conn.recv(length % b_size)
        else:
            seg_b = _conn.recv(b_size)
        content += str(seg_b, encoding='utf-8')
    return content


def handle_online_list(_conn):
    myWin.update_online_list()
    for con in online_conn:
        send_string_with_length(con, "#!online_list#!")
        send_number(con, online_conn.__len__())
        for c in online_conn:
            send_string_with_length(con, user_conn[c])
    return True


def handle_login(_conn):
    user = recv_all_string(_conn)
    key = recv_all_string(_conn)
    check_result = check_user(user, key)
    if check_result:
        _conn.sendall(bytes("1", "utf-8"))
        user_conn[_conn] = user
        online_conn.append(_conn)
        handle_online_list(_conn)
    else:
        _conn.sendall(bytes("0", "utf-8"))
    return True


def handle_register(_conn):
    user = recv_all_string(_conn)
    key = recv_all_string(_conn)
    _conn.sendall(bytes(add_user(user, key), "utf-8"))
    return True


def kick_user(user):
    try:
        _conn = get_user_conn(user).close()
        user_conn.pop(_conn)
        online_conn.remove(_conn)
        handle_online_list(_conn)
    except Exception as e:
        myWin.textBrowser.append(append_text("failed to kick user:{} due to:{}".format(user, str(e)), "black"))


def handle_message(_conn):
    content = recv_all_string(_conn)
    for c in online_conn:
        send_string_with_length(c, "#!message#!")
        send_string_with_length(c, user_conn[_conn])
        send_string_with_length(c, content)
    return True


def handle(_conn, addr):
    try:
        while True:
            _type = str(_conn.recv(1), "utf-8")
            _goon = True
            if _type == "1":
                myWin.textBrowser.append(append_text("handling login..", "black"))
                _goon = handle_login(_conn)
            elif _type == "2":
                myWin.textBrowser.append(append_text("handling register..", "black"))
                _goon = handle_register(_conn)
            elif _type == "3":
                myWin.textBrowser.append(append_text("handling message..", "black"))
                _goon = handle_message(_conn)
            elif _type == "4":
                myWin.textBrowser.append(append_text("refreshing online list..", "black"))
                _goon = handle_online_list(_conn)
                myWin.update_online_list()
            if not _goon:
                break
    except Exception as e:
        myWin.textBrowser.append(append_text("conn shut down due to:{}".format(str(e)), "black"))
    finally:
        try:
            _conn.close()
            online_conn.remove(_conn)
            user_conn.pop(_conn)
            handle_online_list(_conn)
        except Exception as e:
            myWin.textBrowser.append(append_text("conn shut down due to:{}".format(str(e)), "black"))


class Server:
    def __init__(self):
        print("Initializing server..")
        self.sk = socket.socket()
        self.sk.bind(('localhost', 18000))
        self.sk.listen(5)
        print("listening...")
        Thread(target=self.listen).start()

    def listen(self):
        try:
            while True:
                conn, addr = self.sk.accept()
                Thread(target=handle, args=(conn, addr)).start()
        except Exception as e:
            print("server err:{}".format(str(e)))


def append_text(_str, _color):
    color_dict = {"red": "#ff0000", "blue": "#0000ff", "black": "#000000", "teal": "#008080"}
    _content = "<span style=\" color: {};\">{}</span>".format(color_dict[_color], _str)
    return _content


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.textBrowser.clear()
        self.textBrowser.append(append_text("Initializing server...", "black"))

        self.initUI()
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        show_action = QAction("Show", self)
        hide_action = QAction("Hide", self)
        quit_action = QAction("Quit", self)
        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hid)

        """Need to fix bugs of tray remaining"""
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        self.actionMinimize.triggered.connect(self.hid)
        self.actionQuit.triggered.connect(qApp.quit)

        timer = QTimer(self)
        timer.timeout.connect(self.show_time)
        timer.start(200)

        # self.listWidget.clear()
        self.listWidget.itemDoubleClicked.connect(self.kick_user)

        self.server = Server()

    def initUI(self):
        self.setWindowTitle("TCP Chatroom server")
        self.setWindowIcon(QtGui.QIcon("server_2.png"))
        self.show()

    def hid(self):
        self.hide()
        self.tray_icon.showMessage(
            "TCP Chatroom server",
            "Application minimized to Tray.",
            QSystemTrayIcon.Information,
            2000
        )

    def show_time(self):
        current_time = QDateTime.currentDateTime()
        label_time = current_time.toString("yyyy-MM-dd(ddd)\nhh:mm:ss AP")
        self.label_2.setText(label_time)

    @QtCore.pyqtSlot(QListWidgetItem)
    def kick_user(self, item):
        reply = QMessageBox.question(self, 'Confirmation',
                                     "Kicking user '{}'?".format(item.text()),
                                     QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No
                                     )
        if reply == QMessageBox.Yes:
            self.listWidget.takeItem(self.listWidget.currentRow())
            # do kicking!
            kick_user(item.text())

    def update_online_list(self):
        self.listWidget.clear()
        for c in online_conn:
            _item = QListWidgetItem("{}".format(user_conn[c]))
            self.listWidget.addItem(_item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Oxygen')
    myWin = MainWindow()
    myWin.show()
    sys.exit(app.exec_())
