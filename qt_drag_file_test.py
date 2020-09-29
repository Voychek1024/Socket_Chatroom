import sys

from PyQt5.QtWidgets import QLineEdit, QApplication


class FileEdit(QLineEdit):
    def __init__(self, parent=None):
        super(FileEdit, self).__init__(parent)
        self.setDragEnabled(True)

    def dragEnterEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def dropEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            # for some reason, this doubles up the intro slash
            filepath = str(urls[0].path())[1:]
            self.setText(filepath)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Oxygen')
    myWin = FileEdit()
    myWin.show()
    sys.exit(app.exec_())
