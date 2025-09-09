from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSizePolicy,
)
from PySide6.QtCore import Qt

from castoranalytics.ui.pages.basepage import BasePage
from castoranalytics.ui.utils import Label
from castoranalytics.core.logging import LogManager

LOG = LogManager()


class StudyListPage(BasePage):
    def __init__(self):
        super(StudyListPage, self).__init__(name='Studies')
        self._study_list_label = self.init_study_list_label()
        self._table_widget = self.init_table_widget()
        self.init_page_layout()

    # INITIALIZATION

    def init_study_list_label(self):
        label = Label('Studies', type=Label.HEADING1)
        return label

    def init_table_widget(self):
        widget = QTableWidget()
        widget.setSortingEnabled(True)
        widget.horizontalHeader().setVisible(False)
        widget.verticalHeader().setVisible(False)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        widget.itemClicked.connect(self.on_study_selected)
        return widget

    def init_page_layout(self):
        self.get_layout().addWidget(Label('Studies', type=Label.HEADING1))
        self.get_layout().addWidget(self._table_widget)

    # TABLE

    def update_study_list_label(self, studies, error):
        if error:
            self._study_list_label.setText(error)
        else:
            self._study_list_label.setText('Studies')

    def update_table_widget(self, studies):
        self._table_widget.setRowCount(len(studies))
        self._table_widget.setColumnCount(1)
        for row, study in enumerate(studies):
            item = QTableWidgetItem(study.get_name())
            item.setData(Qt.UserRole, study)
            self._table_widget.setItem(row, 0, item)
        self._table_widget.setHorizontalHeaderLabels(['Study name'])
        self._table_widget.setAlternatingRowColors(True)
        self._table_widget.sortItems(0, Qt.AscendingOrder)
        self._table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table_widget.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    # EVENT HANDLERS

    def on_study_selected(self, item):
        self.navigate(f'/studies/{item.data(Qt.UserRole).get_id()}')

    def on_data_ready(self, studies, error):
        if error:
            self._study_list_label.setText(error)
        self.update_table_widget(studies)

    def on_navigate(self, params):
        self._table_widget.clearContents()
        self.load_data('get_studies')