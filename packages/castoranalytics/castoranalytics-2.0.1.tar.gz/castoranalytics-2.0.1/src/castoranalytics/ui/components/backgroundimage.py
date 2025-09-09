import os

from PySide6.QtWidgets import (
    QLabel,
    QSizePolicy
)
from PySide6.QtGui import (
    QPixmap,
    QPainter, 
    QColor,
)
from PySide6.QtCore import Qt

import castoranalytics.ui.constants as constants
from castoranalytics.ui.utils import resource_path


class BackgroundImage(QLabel):
    def __init__(self):
        super(BackgroundImage, self).__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setScaledContents(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        image_path = resource_path(os.path.join(
            constants.CASTOR_ANALYTICS_RESOURCES_IMAGES_DIR, constants.CASTOR_ANALYTICS_RESOURCES_BACKGROUND_IMAGE))
        self.setPixmap(self.apply_opacity_to_pixmap(QPixmap(image_path), constants.CASTOR_ANALYTICS_RESOURCES_BACKGROUND_IMAGE_OPACITY))
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True) # should not handle events!
        self._background_image_pixmap = None

    def rescale(self):
        if self._background_image_pixmap is not None:
            scaled_pixmap = self._background_image_pixmap.scaled(
                self.size(), aspectMode=Qt.AspectRatioMode.IgnoreAspectRatio, mode=Qt.TransformationMode.SmoothTransformation)
            self.setPixmap(
                self.apply_opacity_to_pixmap(
                    scaled_pixmap, constants.CASTOR_ANALYTICS_RESOURCES_BACKGROUND_IMAGE_OPACITY))

    def apply_opacity_to_pixmap(self, pixmap, opacity):
        transparent_pixmap = QPixmap(pixmap.size())
        transparent_pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(transparent_pixmap)
        painter.setOpacity(opacity)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        return transparent_pixmap