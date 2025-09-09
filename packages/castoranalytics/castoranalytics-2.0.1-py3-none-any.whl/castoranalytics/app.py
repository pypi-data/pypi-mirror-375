import sys

from PySide6 import QtWidgets

from castoranalytics.ui.mainwindow import MainWindow
from castoranalytics.ui.bootstrap import BOOTSTRAP_CSS


def main():
    QtWidgets.QApplication.setApplicationName('Castor Analytics')
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(BOOTSTRAP_CSS)
    main_window = MainWindow()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()