from castoranalytics.ui.utils import is_macos


# Window settings
CASTOR_ANALYTICS_WINDOW_TITLE = 'Castor Analytics'
CASTOR_ANALYTICS_WINDOW_W = 1024
CASTOR_ANALYTICS_WINDOW_H = 600

# Resources
CASTOR_ANALYTICS_RESOURCES_DIR = 'castoranalytics/ui/resources'
CASTOR_ANALYTICS_RESOURCES_IMAGES_DIR = 'castoranalytics/ui/resources/images'
CASTOR_ANALYTICS_RESOURCES_IMAGES_ICONS_DIR = 'castoranalytics/resources/ui/images/icons'
CASTOR_ANALYTICS_RESOURCES_ICON = 'castoranalytics.icns' if is_macos() else 'castoranalytics.ico'
CASTOR_ANALYTICS_RESOURCES_BACKGROUND_IMAGE = 'home.png'
CASTOR_ANALYTICS_RESOURCES_BACKGROUND_IMAGE_OPACITY = 0.25

# API Settings
CASTOR_ANALYTICS_API_SETTINGS_TITLE = 'API settings'
CASTOR_ANALYTICS_API_SETTINGS_ERROR_MESSAGE = 'It looks like your API settings are incomplete. Please go to settings.'
CASTOR_ANALYTICS_SETTINGS_KEY_CLIENT_ID = 'castoranalytics.client_id'
CASTOR_ANALYTICS_SETTINGS_KEY_CLIENT_ID_NAME = 'API client ID'
CASTOR_ANALYTICS_SETTINGS_KEY_CLIENT_SECRET = 'castoranalytics.client_secret'
CASTOR_ANALYTICS_SETTINGS_KEY_CLIENT_SECRET_NAME = 'API client secret'
CASTOR_ANALYTICS_SETTINGS_KEY_TOKEN_URL = 'castoranalytics.token_url'
CASTOR_ANALYTICS_SETTINGS_KEY_TOKEN_URL_NAME = 'API token URL'
CASTOR_ANALYTICS_SETTINGS_KEY_TOKEN_URL_DEFAULT = 'https://data.castoredc.com/oauth/token'
CASTOR_ANALYTICS_SETTINGS_KEY_API_BASE_URL = 'castoranalytics.api_base_url'
CASTOR_ANALYTICS_SETTINGS_KEY_API_BASE_URL_NAME = 'API base URL'
CASTOR_ANALYTICS_SETTINGS_KEY_API_BASE_URL_DEFAULT = 'https://data.castoredc.com/api'

# License key settings
CASTOR_ANALYTICS_LICENSE_KEY_SETTINGS_TITLE = 'License key'
CASTOR_ANALYTICS_LICENSE_KEY_SETTINGS_ERROR_MESSAGE = 'It looks like you have not set the license key. Please go to settings.'
CASTOR_ANALYTICS_SETTINGS_KEY_LICENSE_KEY = 'castoranalytics.license_key'
CASTOR_ANALYTICS_SETTINGS_KEY_LICENSE_KEY_NAME = 'License key'

# Studies and sites
CASTOR_ANALYTICS_STUDY_SITES_WARNING_MAX = 10
CASTOR_ANALYTICS_STUDY_SITES_WARNING = f'Your study has >{CASTOR_ANALYTICS_STUDY_SITES_WARNING_MAX} sites. Loading these for the first time will take a few minutes'