from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QLineEdit, QGroupBox, QRadioButton, QButtonGroup,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMenu,
    QPushButton
)
from PyQt5.QtCore import Qt


class DrvExtractTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        layout.addWidget(self._build_schematic_group())
        layout.addWidget(self._build_layout_group())
        layout.addWidget(self._build_result_group())

        self.extract_btn = QPushButton("EXTRACT")
        self.extract_btn.setFixedHeight(56)
        layout.addWidget(self.extract_btn)

    def _build_schematic_group(self) -> QGroupBox:
        group = QGroupBox("SCHEMATIC")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        self._radio_group = QButtonGroup(self)

        RADIO_W = 60
        LABEL_W = 100

        # FILE row
        file_row = QHBoxLayout()
        file_row.setSpacing(8)
        self.drv_radio_file = QRadioButton("FILE")
        self.drv_radio_file.setFixedWidth(RADIO_W)
        netlist_label = QLabel("NETLIST")
        netlist_label.setFixedWidth(LABEL_W)
        self.drv_netlist_edit = QLineEdit()
        file_row.addWidget(self.drv_radio_file)
        file_row.addWidget(netlist_label)
        file_row.addWidget(self.drv_netlist_edit)
        layout.addLayout(file_row)

        # AUTO row
        auto_row = QHBoxLayout()
        auto_row.setSpacing(8)
        self.drv_radio_auto = QRadioButton("AUTO")
        self.drv_radio_auto.setFixedWidth(RADIO_W)
        cellname_label = QLabel("CELLNAME")
        cellname_label.setFixedWidth(LABEL_W)
        self.drv_cellname_edit = QLineEdit()
        auto_row.addWidget(self.drv_radio_auto)
        auto_row.addWidget(cellname_label)
        auto_row.addWidget(self.drv_cellname_edit)
        layout.addLayout(auto_row)

        self._radio_group.addButton(self.drv_radio_file)
        self._radio_group.addButton(self.drv_radio_auto)

        self.drv_radio_file.setChecked(True)
        self.drv_cellname_edit.setEnabled(False)

        self.drv_radio_file.toggled.connect(self._on_radio_toggled)

        return group

    def _on_radio_toggled(self, file_checked: bool):
        self.drv_netlist_edit.setEnabled(file_checked)
        self.drv_cellname_edit.setEnabled(not file_checked)

    def _build_layout_group(self) -> QGroupBox:
        group = QGroupBox("LAYOUT")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)

        self._lay_radio_group = QButtonGroup(self)

        RADIO_W = 60
        LABEL_W = 100

        # FILE row
        file_row = QHBoxLayout()
        file_row.setSpacing(8)
        self.drv_lay_radio_file = QRadioButton("FILE")
        self.drv_lay_radio_file.setFixedWidth(RADIO_W)
        oasis_label = QLabel("OASIS")
        oasis_label.setFixedWidth(LABEL_W)
        self.drv_lay_oasis_edit = QLineEdit()
        file_row.addWidget(self.drv_lay_radio_file)
        file_row.addWidget(oasis_label)
        file_row.addWidget(self.drv_lay_oasis_edit)
        layout.addLayout(file_row)

        # AUTO row
        auto_row = QHBoxLayout()
        auto_row.setSpacing(8)
        self.drv_lay_radio_auto = QRadioButton("AUTO")
        self.drv_lay_radio_auto.setFixedWidth(RADIO_W)
        cellname_label = QLabel("CELLNAME")
        cellname_label.setFixedWidth(LABEL_W)
        self.drv_lay_cellname_edit = QLineEdit()
        auto_row.addWidget(self.drv_lay_radio_auto)
        auto_row.addWidget(cellname_label)
        auto_row.addWidget(self.drv_lay_cellname_edit)
        layout.addLayout(auto_row)

        # LIB row
        lib_row = QHBoxLayout()
        lib_row.setSpacing(8)
        self.drv_lay_radio_lib = QRadioButton("LIB")
        self.drv_lay_radio_lib.setFixedWidth(RADIO_W)
        lib_label = QLabel("FROM VIRTUOSO LAYOUT LIBRARY")
        lib_row.addWidget(self.drv_lay_radio_lib)
        lib_row.addWidget(lib_label)
        layout.addLayout(lib_row)

        self._lay_radio_group.addButton(self.drv_lay_radio_file)
        self._lay_radio_group.addButton(self.drv_lay_radio_auto)
        self._lay_radio_group.addButton(self.drv_lay_radio_lib)

        self.drv_lay_radio_file.setChecked(True)
        self.drv_lay_cellname_edit.setEnabled(False)

        self._lay_radio_group.buttonToggled.connect(self._on_lay_radio_toggled)

        return group

    def _on_lay_radio_toggled(self, button, checked):
        if checked:
            self.drv_lay_oasis_edit.setEnabled(self.drv_lay_radio_file.isChecked())
            self.drv_lay_cellname_edit.setEnabled(self.drv_lay_radio_auto.isChecked())

    def _build_result_group(self) -> QGroupBox:
        group = QGroupBox("RESULT")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.drv_cell_table = self._build_cell_list_table()
        layout.addWidget(self.drv_cell_table)

        export_row = QHBoxLayout()
        export_row.setSpacing(8)
        self.drv_export_path_edit = QLineEdit()
        self.drv_export_btn = QPushButton("EXPORT")
        self.drv_export_btn.clicked.connect(self._export_cell_list)
        export_row.addWidget(self.drv_export_path_edit)
        export_row.addWidget(self.drv_export_btn)
        layout.addLayout(export_row)

        return group

    def _build_cell_list_table(self) -> QTableWidget:
        table = QTableWidget(5, 2)
        table.setHorizontalHeaderLabels(["LAYOUT", "SCHEMATIC"])

        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)

        for row in range(5):
            for col in range(2):
                table.setItem(row, col, QTableWidgetItem(""))

        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self._on_cell_table_context_menu)

        return table

    def _on_cell_table_context_menu(self, pos):
        menu = QMenu(self)
        delete_action = menu.addAction("DELETE")
        send_lvs_action = menu.addAction("SEND LVS")
        action = menu.exec_(self.drv_cell_table.viewport().mapToGlobal(pos))
        if action == delete_action:
            rows = sorted(
                {idx.row() for idx in self.drv_cell_table.selectedIndexes()},
                reverse=True,
            )
            for row in rows:
                self.drv_cell_table.removeRow(row)
        elif action == send_lvs_action:
            pass

    def _export_cell_list(self):
        path = self.drv_export_path_edit.text().strip()
        if not path:
            return
        lines = []
        for row in range(self.drv_cell_table.rowCount()):
            layout_val = (self.drv_cell_table.item(row, 0) or QTableWidgetItem("")).text()
            sch_val    = (self.drv_cell_table.item(row, 1) or QTableWidgetItem("")).text()
            lines.append(f"{layout_val} {sch_val}")
        Path(path).write_text("\n".join(lines), encoding="utf-8")

    def reset(self):
        self.drv_radio_file.setChecked(True)
        self.drv_netlist_edit.clear()
        self.drv_cellname_edit.clear()

        self.drv_lay_radio_file.setChecked(True)
        self.drv_lay_oasis_edit.clear()
        self.drv_lay_cellname_edit.clear()

        self.drv_cell_table.setRowCount(0)
        for row in range(5):
            self.drv_cell_table.insertRow(row)
            for col in range(2):
                self.drv_cell_table.setItem(row, col, QTableWidgetItem(""))

        self.drv_export_path_edit.clear()


class DrvLasTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addStretch()

    def reset(self):
        pass


class DrvRunTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addStretch()

    def reset(self):
        pass


class DrvTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.sub_tabs = QTabWidget()
        self.extract_tab = DrvExtractTab()
        self.las_tab = DrvLasTab()
        self.run_tab = DrvRunTab()
        self.sub_tabs.addTab(self.extract_tab, "EXTRACT")
        self.sub_tabs.addTab(self.las_tab, "LAS")
        self.sub_tabs.addTab(self.run_tab, "RUN")

        layout.addWidget(self.sub_tabs)

    def reset(self):
        self.extract_tab.reset()
        self.las_tab.reset()
        self.run_tab.reset()
