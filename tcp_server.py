import sys

from PyQt5.QtCore import QTimer, QTime, Qt, QDateTime
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QSystemTrayIcon, QMenu, QAction, QStyle, qApp, \
    QTableWidgetItem, QTableWidget, QListWidget, QListWidgetItem, QLabel, QMessageBox

from server_ui import *

online_conn = list()
user_conn = dict()


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
        """
        self.sk = socket.socket()
        self.sk.bind(('localhost', 18000))
        self.sk.listen(10)
        self.server_log += "socket listening..."
        self.server_log_ct += 1
        self.conn, self.addr = self.sk.accept()
        Thread(target=self.handle, args=(self.conn, self.addr)).start()
        """

    def initUI(self):
        self.setWindowTitle("TCP Chatroom server")
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
            self.server_log += 'kicked user "{}"'.format(item.text())
            self.listWidget.takeItem(self.listWidget.currentRow())
            self.server_log_ct += 1
            # do kicking!


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Oxygen')
    myWin = MainWindow()
    myWin.show()
    sys.exit(app.exec_())
