from PySide6.QtWidgets import (
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSizePolicy,
)
from PySide6.QtCore import Qt

import castoranalytics.ui.constants as constants

from castoranalytics.ui.pages.basepage import BasePage
from castoranalytics.ui.utils import Label
from castoranalytics.core.logging import LogManager

LOG = LogManager()


class StudyPage(BasePage):
    def __init__(self):
        super(StudyPage, self).__init__(name='Study')
        self._study_id = None
        self._back_button = self.init_back_button()
        self._study_name_label = self.init_study_name_label()
        self._table_widget = self.init_table_widget()
        self._sites_warning_label = self.init_sites_warning_label()
        self._show_sites_button = self.init_show_sites_button()
        self.init_page_layout()

    # INITIALIZATION

    def init_back_button(self):
        button = QPushButton('Back', self)
        button.clicked.connect(self.on_back)
        return button
    
    def init_table_widget(self):
        widget = QTableWidget()
        widget.setSelectionMode(QTableWidget.NoSelection)
        widget.horizontalHeader().setVisible(False)
        widget.verticalHeader().setVisible(False)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        widget.setFocusPolicy(Qt.NoFocus)
        return widget
    
    def init_study_name_label(self):
        label = Label('', type=Label.HEADING1)
        return label
    
    def init_sites_warning_label(self):
        label = Label(constants.CASTOR_ANALYTICS_STUDY_SITES_WARNING, type=Label.HEADING1, style='color: red;')
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        label.setContentsMargins(0, 0, 0, 20)
        label.setVisible(False)
        return label
    
    def init_show_sites_button(self):
        button = QPushButton('Get sites', self)
        button.clicked.connect(self.on_show_sites)
        button.setVisible(False)
        return button

    def init_page_layout(self):
        self.get_layout().addWidget(self._back_button)
        self.get_layout().addWidget(self._study_name_label)
        self.get_layout().addWidget(self._table_widget)
        self.get_layout().addWidget(self._sites_warning_label)
        self.get_layout().addWidget(self._show_sites_button)

    # TABLE

    def update_study_name_label(self, study, error):
        if error:
            self._study_name_label.setText(error)
            return
        self._study_name_label.setText(study.get_name())

    def update_table_widget(self, study):
        self._table_widget.setRowCount(5)
        self._table_widget.setColumnCount(2)
        self._table_widget.setItem(0, 0, QTableWidgetItem('Study ID'))
        self._table_widget.setItem(0, 1, QTableWidgetItem(study.get_id()))
        self._table_widget.setItem(1, 0, QTableWidgetItem('Number of sites'))
        self._table_widget.setItem(1, 1, QTableWidgetItem(str(study.get_nr_sites())))
        self._table_widget.setItem(2, 0, QTableWidgetItem('Number of participants'))
        self._table_widget.setItem(2, 1, QTableWidgetItem(str(study.get_nr_participants())))
        self._table_widget.setItem(3, 0, QTableWidgetItem('Number of fields'))
        self._table_widget.setItem(3, 1, QTableWidgetItem(str(study.get_nr_fields())))
        self._table_widget.setItem(4, 0, QTableWidgetItem('Created on'))
        self._table_widget.setItem(4, 1, QTableWidgetItem(str(study.get_created_on())))
        self._table_widget.setAlternatingRowColors(True)
        self._table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table_widget.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def show_sites_button(self, study):
        if study.get_nr_sites() > 10:
            self._sites_warning_label.setVisible(True)
        self._show_sites_button.setVisible(True)
        
    # EVENT HANDLERS

    def on_back(self):
        self.navigate(f'/studies')

    def on_show_sites(self):
        self.navigate(f'/studies/{self._study_id}/sites')

    def on_navigate(self, params):
        self._study_name_label.setText('')
        self._table_widget.clearContents()
        self._sites_warning_label.setVisible(False)
        self._show_sites_button.setVisible(False)
        self._study_id = params.get('study_id', None)
        if self._study_id:
            self.load_data('get_study', self._study_id)

    def on_data_ready(self, study, error):
        self.update_study_name_label(study, error)
        self.update_table_widget(study)
        self.show_sites_button(study)