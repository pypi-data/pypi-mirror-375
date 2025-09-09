from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)
from PySide6.QtCore import Qt

import castoranalytics.ui.constants as constants

from castoranalytics.core import Core
from castoranalytics.core.logging import LogManager
from castoranalytics.ui.utils import to_main_thread, BusyOverlay, Settings

LOG = LogManager()


class BasePage(QWidget):
    def __init__(self, name):
        super(BasePage, self).__init__()
        self._name = name
        self._settings = Settings()
        self._busy_overlay = BusyOverlay(self)
        self._router = None
        self._core = self.init_core()
        self._error_label = self.init_error_label()
        self._page_layout = self.init_page_layout_internal(self._error_label)
        self.setLayout(self._page_layout)

    def init_error_label(self):
        label = QLabel()
        if not self.get_core().ready():
            label.setText(constants.CASTOR_ANALYTICS_API_SETTINGS_ERROR_MESSAGE)
        return label
    
    def init_page_layout_internal(self, error_label):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(error_label)
        return layout

    def init_core(self):
        self._core = Core(
            self.get_setting(constants.CASTOR_ANALYTICS_SETTINGS_KEY_CLIENT_ID, None),
            self.get_setting(constants.CASTOR_ANALYTICS_SETTINGS_KEY_CLIENT_SECRET, None),
            self.get_setting(constants.CASTOR_ANALYTICS_SETTINGS_KEY_TOKEN_URL, None),
            self.get_setting(constants.CASTOR_ANALYTICS_SETTINGS_KEY_API_BASE_URL, None),
        )
        return self._core
    
    def get_core(self):
        return self._core

    def get_layout(self):
        return self._page_layout
    
    def load_data(self, func_name, *args, **kwargs):
        func_name = func_name if func_name.endswith('_async') else func_name + '_async'
        try:
            if self.get_core().ready():
                func = getattr(self.get_core(), func_name)
                self._busy_overlay.show_overlay()
                func(to_main_thread(self.on_data_ready_internal), *args, **kwargs)
                self._error_label.setText('')
            else:
                self._error_label.setText(constants.CASTOR_ANALYTICS_API_SETTINGS_ERROR_MESSAGE)
        except Exception as e:
            self._busy_overlay.hide_overlay()
            LOG.error(e)

    def on_data_ready_internal(self, result, error):
        self.on_data_ready(result, error)
        self._busy_overlay.hide_overlay()

    def on_data_ready(self, result, error):
        raise NotImplementedError()

    def set_router(self, router):
        self._router = router

    def back(self):
        if self._router:
            self._router.back()

    def navigate(self, path):
        if self._router:
            self._router.navigate(path)

    def get_setting(self, name, default=None):
        return self._settings.get(name, default)
    
    def set_setting(self, name, value):
        self._settings.set(name, value)

    def on_navigate(self, params):
        raise NotImplementedError()