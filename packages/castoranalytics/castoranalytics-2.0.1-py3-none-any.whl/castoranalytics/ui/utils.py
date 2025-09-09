import os
import sys

from PySide6.QtWidgets import (
    QWidget, 
    QLabel, 
    QVBoxLayout, 
    QHBoxLayout, 
    QFrame,
)
from PySide6.QtCore import (
    Qt, 
    QEvent,
    QObject,
    QCoreApplication,
    QSettings,
)


class Settings(QSettings):
    def __init__(self):
        super(Settings, self).__init__(QSettings.IniFormat, QSettings.UserScope, 'com.rbeesoft', 'castoranalytics')

    def get(self, name, default=None):
        value = self.value(name)
        if value is None or value == '':
            return default
        return value

    def set(self, name, value):
        self.setValue(name, value)


class FunctionEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, func, *args, **kwargs):
        super().__init__(FunctionEvent.EVENT_TYPE)
        self.func = func
        self.args = args
        self.kwargs = kwargs


def is_macos():
    return sys.platform.startswith('darwin')


class EventDispatcher(QObject):
    def event(self, event):
        if isinstance(event, FunctionEvent):
            event.func(*event.args, **event.kwargs)
            return True
        return super().event(event)


_dispatcher = EventDispatcher()


def to_main_thread(func):
    def wrapper(*args, **kwargs):
        QCoreApplication.postEvent(_dispatcher, FunctionEvent(func, *args, **kwargs))
    return wrapper


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    return os.path.join(base_path, relative_path)


class BusyOverlay(QWidget):
    def __init__(self, parent=None, message="Loading..."):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)
        self.setStyleSheet("""
            background-color: rgba(0, 0, 0, 128);
        """)
        box = QFrame(self)
        box.setStyleSheet("""
            background-color: rgba(256, 256, 256, 200);
            color: white;
            border-radius: 10px;
            padding: 15px;
        """)
        box.setFrameShape(QFrame.StyledPanel)
        label = QLabel(message, box)
        label.setStyleSheet("font-size: 16px;")
        label.setAlignment(Qt.AlignCenter)
        box_layout = QVBoxLayout(box)
        box_layout.addWidget(label)
        main_layout = QHBoxLayout(self)
        main_layout.addStretch()
        vbox = QVBoxLayout()
        vbox.addStretch()
        vbox.addWidget(box, alignment=Qt.AlignCenter)
        vbox.addStretch()
        main_layout.addLayout(vbox)
        main_layout.addStretch()
        self.setLayout(main_layout)
        if parent:
            parent.installEventFilter(self)
        self.hide()

    def show_overlay(self):
        if self.parent():
            self.resize(self.parent().size())
        self.show()
        self.raise_()

    def hide_overlay(self):
        self.hide()

    def eventFilter(self, obj, event):
        if obj == self.parent() and event.type() == QEvent.Resize:
            self.resize(self.parent().size())
        return super().eventFilter(obj, event)
    

class Label(QLabel):
    HEADING1 = 1
    HEADING2 = 2
    HEADING3 = 3

    def __init__(self, text, type=None, style=''):
        super(Label, self).__init__(text)
        if type == self.HEADING1:
            style = f'font-size: 18px; font-weight: bold; color: darkslateblue; {style}'
        elif type == self.HEADING2:
            style = f'font-size: 16px; font-weight: bold; color: darkslateblue; {style}'
        elif type == self.HEADING3:
            style = f'font-size: 14px; font-weight: bold; color: darkslateblue; {style}'
        else:
            style = f'font-size: 12px; color: slateblue; {style}'
        self.setStyleSheet(style)