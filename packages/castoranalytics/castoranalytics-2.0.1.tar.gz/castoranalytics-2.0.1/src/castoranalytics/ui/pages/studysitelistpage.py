import pandas as pd

from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSizePolicy,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Qt

from castoranalytics.ui.pages.basepage import BasePage
from castoranalytics.ui.components.numerictablewidgetitem import NumericTableWidgetItem
from castoranalytics.ui.utils import Label
from castoranalytics.core.logging import LogManager

LOG = LogManager()


class StudySiteListPage(BasePage):
    def __init__(self):
        super(StudySiteListPage, self).__init__(name='Study sites')
        self._study_id = None
        self._study = None
        self._study_sites = None
        self._back_button = self.init_back_button()
        self._export_to_excel_button = self.init_export_to_excel_button()
        self._study_site_list_label = self.init_study_site_list_label()
        self._table_widget = self.init_table_widget()
        self.init_page_layout()

    # INITIALIZATION

    def init_back_button(self):
        button = QPushButton('Back', self)
        button.clicked.connect(self.on_back)
        return button
    
    def init_export_to_excel_button(self):
        button = QPushButton('Export site data to Excel', self)
        button.clicked.connect(self.on_export_to_excel)
        return button

    def init_study_site_list_label(self):
        label = Label('', type=Label.HEADING1)
        return label
    
    def init_table_widget(self):
        widget = QTableWidget()
        widget.setSortingEnabled(True)
        widget.verticalHeader().setVisible(False)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        widget.itemClicked.connect(self.on_study_site_selected)
        return widget

    def init_page_layout(self):
        self.get_layout().addWidget(self._back_button)
        self.get_layout().addWidget(self._export_to_excel_button)
        self.get_layout().addWidget(self._study_site_list_label)
        self.get_layout().addWidget(self._table_widget)

    # TABLE

    def update_study_site_list_label(self, error):
        if error:
            self._study_site_list_label.setText(error)
        else:
            self._study_site_list_label.setText(f'Study sites for {self._study.get_name()}')

    # def update_table_widget(self, study_sites):
    #     self._table_widget.clearContents()
    #     self._table_widget.setRowCount(len(study_sites))
    #     self._table_widget.setColumnCount(5)
    #     self._table_widget.setHorizontalHeaderLabels(['Site code', 'Site name', 'Country code', 'Nr. records', 'Complete %'])
    #     self._table_widget.setAlternatingRowColors(True)
    #     self._table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
    #     self._table_widget.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    #     for row, study_site in enumerate(study_sites):
    #         self._table_widget.setItem(row, 0, QTableWidgetItem(study_site.get_abbreviation()))
    #         self._table_widget.setItem(row, 1, QTableWidgetItem(study_site.get_name()))
    #         self._table_widget.setItem(row, 2, QTableWidgetItem(study_site.get_country_code()))
    #         self._table_widget.setItem(row, 3, NumericTableWidgetItem(study_site.get_nr_records())) # Handles sorting correctly for numbers
    #         self._table_widget.setItem(row, 4, NumericTableWidgetItem(study_site.get_completion_percentage()))
        
    def update_table_widget(self, study_sites):
        self._table_widget.setSortingEnabled(False)
        self._table_widget.clear()
        self._table_widget.setRowCount(len(study_sites))
        self._table_widget.setColumnCount(5)
        self._table_widget.setHorizontalHeaderLabels(['Site code', 'Site name', 'Country code', 'Nr. records', 'Complete %'])
        self._table_widget.setAlternatingRowColors(True)
        self._table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._table_widget.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        for idx, study_site in enumerate(study_sites):
            self._table_widget.setItem(idx, 0, QTableWidgetItem(study_site.get_abbreviation()))
            self._table_widget.setItem(idx, 1, QTableWidgetItem(study_site.get_name()))
            self._table_widget.setItem(idx, 2, QTableWidgetItem(study_site.get_country_code()))
            self._table_widget.setItem(idx, 3, NumericTableWidgetItem(study_site.get_nr_records()))
            self._table_widget.setItem(idx, 4, NumericTableWidgetItem(study_site.get_completion_percentage()))    
        self._table_widget.setSortingEnabled(True)
        self._table_widget.viewport().update()
    
    # EVENT HANDLERS

    def on_back(self):
        self.navigate(f'/studies/{self._study_id}')

    def on_export_to_excel(self):
        if self._study_sites:
            file_path, _ = QFileDialog.getSaveFileName(self, 'Save file as...', '.', filter='Excel (.xlsx)')
            if file_path:
                if not file_path.endswith('.xlsx'):
                    QMessageBox.warning(self, 'Error', 'File must have extension .xlsx')
                    return
                data = {
                    'name': [],
                    'abbreviation': [],
                    'country_code': [],
                    'nr_records': [],
                    'completion_percentage': [],
                }
                for idx, study_site in enumerate(self._study_sites):
                    data['name'].append(study_site.get_name())
                    data['abbreviation'].append(study_site.get_abbreviation())
                    data['country_code'].append(study_site.get_country_code())
                    data['nr_records'].append(study_site.get_nr_records())
                    data['completion_percentage'].append(study_site.get_completion_percentage())
                df = pd.DataFrame(data)
                df.to_excel(file_path, index=False, engine="openpyxl")
                QMessageBox.information(self, 'Info', 'Site data successfully saved')

    def on_study_site_selected(self, item):
        # self.navigate(f'/studies/{item.data(Qt.UserRole).get_id()}')
        pass

    def on_navigate(self, params):
        self._study_site_list_label.setText('')
        self._table_widget.clearContents()
        self._study_id = params.get('study_id', None)
        if self._study_id:
            self._study = self.get_core().get_study(self._study_id)
            self.load_data('get_study_sites', self._study_id)
    
    def on_data_ready(self, study_sites, error):
        self._study_sites = study_sites
        self.update_study_site_list_label(error)
        self.update_table_widget(self._study_sites)