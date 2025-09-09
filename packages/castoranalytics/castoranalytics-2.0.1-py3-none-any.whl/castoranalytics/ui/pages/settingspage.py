from PySide6.QtWidgets import (
    QPushButton,
    QFormLayout,
    QLineEdit,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)

import castoranalytics.ui.constants as constants

from castoranalytics.ui.pages.basepage import BasePage
from castoranalytics.ui.utils import Label


class SettingsPage(BasePage):
    def __init__(self):
        super(SettingsPage, self).__init__(name='Settings')
        self._back_button = self.init_back_button()
        self._save_button = self.init_save_button()
        self._client_id_field = self.init_client_id_field()
        self._client_secret_field = self.init_client_secret_field()
        self._token_url_field = self.init_token_url_field()
        self._api_base_url_field = self.init_api_base_url_field()
        self._api_settings_form = self.init_api_settings_form(
            self._client_id_field, self._client_secret_field, self._token_url_field, self._api_base_url_field
        )
        self._license_key_field = self.init_license_key_field()
        self._license_key_form = self.init_license_key_form(self._license_key_field)
        self.init_page_layout()

    # INITIALIZATION

    def init_back_button(self):
        button = QPushButton('Back', self)
        button.clicked.connect(self.on_back)
        return button
    
    def init_save_button(self):
        button = QPushButton('Save settings', self)
        button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        button.clicked.connect(self.on_save)
        return button
    
    def init_client_id_field(self):
        return QLineEdit(self.get_setting(constants.CASTOR_ANALYTICS_SETTINGS_KEY_CLIENT_ID))
    
    def init_client_secret_field(self):
        return QLineEdit(self.get_setting(constants.CASTOR_ANALYTICS_SETTINGS_KEY_CLIENT_SECRET))
    
    def init_token_url_field(self):
        return QLineEdit(self.get_setting(
            constants.CASTOR_ANALYTICS_SETTINGS_KEY_TOKEN_URL, default=constants.CASTOR_ANALYTICS_SETTINGS_KEY_TOKEN_URL_DEFAULT))
    
    def init_api_base_url_field(self):
        return QLineEdit(self.get_setting(
            constants.CASTOR_ANALYTICS_SETTINGS_KEY_API_BASE_URL, default=constants.CASTOR_ANALYTICS_SETTINGS_KEY_API_BASE_URL_DEFAULT))
    
    def init_license_key_field(self):
        return QLineEdit(self.get_setting(
            constants.CASTOR_ANALYTICS_SETTINGS_KEY_LICENSE_KEY))
    
    def init_api_settings_form(self, client_id_field, client_secret_field, token_url_field, api_base_url_field):
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow) # needed on MacOS
        form.addRow(constants.CASTOR_ANALYTICS_SETTINGS_KEY_CLIENT_ID_NAME, client_id_field)
        form.addRow(constants.CASTOR_ANALYTICS_SETTINGS_KEY_CLIENT_SECRET_NAME, client_secret_field)
        form.addRow(constants.CASTOR_ANALYTICS_SETTINGS_KEY_TOKEN_URL_NAME, token_url_field)
        form.addRow(constants.CASTOR_ANALYTICS_SETTINGS_KEY_API_BASE_URL_NAME, api_base_url_field)
        layout = QVBoxLayout()
        layout.addWidget(Label(constants.CASTOR_ANALYTICS_API_SETTINGS_TITLE, type=Label.HEADING1))
        layout.addLayout(form)
        return layout
    
    def init_license_key_form(self, license_key_field):
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow) # needed on MacOS
        form.addRow(constants.CASTOR_ANALYTICS_SETTINGS_KEY_LICENSE_KEY_NAME, license_key_field)
        layout = QVBoxLayout()
        layout.addWidget(Label(constants.CASTOR_ANALYTICS_LICENSE_KEY_SETTINGS_TITLE, type=Label.HEADING1))
        layout.addLayout(form)
        return layout
    
    def init_page_layout(self):
        self.get_layout().addWidget(self._back_button)
        self.get_layout().addLayout(self._api_settings_form)
        # self.get_layout().addLayout(self._license_key_form)
        self.get_layout().addItem(QSpacerItem(0, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.get_layout().addWidget(self._save_button)

    # EVENT HANDLERS

    def on_back(self):
        self.back()

    def on_save(self):
        client_id = self._client_id_field.text()
        client_secret = self._client_secret_field.text()
        token_url = self._token_url_field.text()
        api_base_url = self._api_base_url_field.text()
        self._settings.setValue(constants.CASTOR_ANALYTICS_SETTINGS_KEY_CLIENT_ID, client_id)
        self._settings.setValue(constants.CASTOR_ANALYTICS_SETTINGS_KEY_CLIENT_SECRET, client_secret)
        self._settings.setValue(constants.CASTOR_ANALYTICS_SETTINGS_KEY_TOKEN_URL, token_url)
        self._settings.setValue(constants.CASTOR_ANALYTICS_SETTINGS_KEY_API_BASE_URL, api_base_url)
        self.get_core().set_api_credentials(client_id, client_secret, token_url, api_base_url)
        self.back()

    def on_navigate(self, params):
        pass