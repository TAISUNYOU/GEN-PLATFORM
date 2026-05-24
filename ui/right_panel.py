import json
from pathlib import Path
from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QLineEdit, QGroupBox, QRadioButton, QButtonGroup,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMenu,
    QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt

PROJECTS_DIR = Path(__file__).parent.parent / "projects"


class SettingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._json_path: Optional[Path] = None
        self._loading = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        layout.addWidget(self._build_personal_group())
        layout.addWidget(self._build_project_group())
        layout.addWidget(self._build_las_group())
        layout.addWidget(self._build_extract_group())
        layout.addStretch()

    # ── group builders ──────────────────────────────────────────────────────

    def _build_group(self, title: str, fields: list) -> QGroupBox:
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        for field_data in fields:
            if isinstance(field_data, tuple) and len(field_data) == 3:
                label_text, attr, placeholder = field_data
            else:
                label_text, attr = field_data
                placeholder = None

            row = QHBoxLayout()
            row.setSpacing(8)
            lbl = QLabel(label_text)
            lbl.setFixedWidth(180)
            row.addWidget(lbl)
            edit = QLineEdit()
            if placeholder:
                edit.setPlaceholderText(placeholder)
            setattr(self, attr, edit)
            row.addWidget(edit)
            layout.addLayout(row)
        return group

    def _build_personal_group(self) -> QGroupBox:
        return self._build_group("PERSONAL", [
            ("GENPLATFORM DIRECTORY", "genplatform_dir", "/sim/...."),
            ("VIRTUOSO DIRECTORY",    "virtuoso_dir", ".../OPUS_ENV"),
            ("VERI DIRECTORY",        "veri_dir", ".../VERI"),
        ])

    def _build_project_group(self) -> QGroupBox:
        return self._build_group("PROJECT", [
            ("SIMRC",             "simrc"),
            ("LAYOUT LIBRARY",    "layout_library"),
            ("SCHEMATIC LIBRARY", "schematic_library"),
        ])

    def _build_las_group(self) -> QGroupBox:
        return self._build_group("LAS", [
            ("ICV RULE",     "icv_rule"),
            ("NXTGRD FILE",  "nxtgrd_file"),
            ("MAPPING FILE", "mapping_file"),
        ])

    def _build_extract_group(self) -> QGroupBox:
        return self._build_group("EXTRACT", [
            ("CCL", "extract_ccl"),
            ("DRV", "extract_drv"),
        ])

    # ── load / save ─────────────────────────────────────────────────────────

    def load_project(self, json_path: Path):
        self._json_path = json_path
        self._loading = True
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
            setting = data.get("SETTING", {})
            project = setting.get("PROJECT", {})
            las     = setting.get("LAS", {})
            extract = setting.get("EXTRACT", {})

            self.simrc.setText(project.get("simrc", ""))
            self.layout_library.setText(project.get("layout_library", ""))
            self.schematic_library.setText(project.get("schematic_library", ""))

            self.icv_rule.setText(las.get("icv_rule", ""))
            self.nxtgrd_file.setText(las.get("nxtgrd_file", ""))
            self.mapping_file.setText(las.get("mapping_file", ""))

            self.extract_ccl.setText(extract.get("ccl", ""))
            self.extract_drv.setText(extract.get("drv", ""))
        finally:
            self._loading = False

    def reset(self):
        self._loading = True
        try:
            self.genplatform_dir.clear()
            self.virtuoso_dir.clear()
            self.veri_dir.clear()
            self.extract_ccl.clear()
            self.extract_drv.clear()
        finally:
            self._loading = False


# ── CCL > EXTRACT tab ────────────────────────────────────────────────────────

class ExtractTab(QWidget):
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
        self.radio_file = QRadioButton("FILE")
        self.radio_file.setFixedWidth(RADIO_W)
        netlist_label = QLabel("NETLIST")
        netlist_label.setFixedWidth(LABEL_W)
        self.netlist_edit = QLineEdit()
        file_row.addWidget(self.radio_file)
        file_row.addWidget(netlist_label)
        file_row.addWidget(self.netlist_edit)
        layout.addLayout(file_row)

        # AUTO row
        auto_row = QHBoxLayout()
        auto_row.setSpacing(8)
        self.radio_auto = QRadioButton("AUTO")
        self.radio_auto.setFixedWidth(RADIO_W)
        cellname_label = QLabel("CELLNAME")
        cellname_label.setFixedWidth(LABEL_W)
        self.cellname_edit = QLineEdit()
        auto_row.addWidget(self.radio_auto)
        auto_row.addWidget(cellname_label)
        auto_row.addWidget(self.cellname_edit)
        layout.addLayout(auto_row)

        self._radio_group.addButton(self.radio_file)
        self._radio_group.addButton(self.radio_auto)

        self.radio_file.setChecked(True)
        self.cellname_edit.setEnabled(False)

        self.radio_file.toggled.connect(self._on_radio_toggled)

        return group

    def _on_radio_toggled(self, file_checked: bool):
        self.netlist_edit.setEnabled(file_checked)
        self.cellname_edit.setEnabled(not file_checked)

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
        self.lay_radio_file = QRadioButton("FILE")
        self.lay_radio_file.setFixedWidth(RADIO_W)
        oasis_label = QLabel("OASIS")
        oasis_label.setFixedWidth(LABEL_W)
        self.lay_oasis_edit = QLineEdit()
        file_row.addWidget(self.lay_radio_file)
        file_row.addWidget(oasis_label)
        file_row.addWidget(self.lay_oasis_edit)
        layout.addLayout(file_row)

        # AUTO row
        auto_row = QHBoxLayout()
        auto_row.setSpacing(8)
        self.lay_radio_auto = QRadioButton("AUTO")
        self.lay_radio_auto.setFixedWidth(RADIO_W)
        cellname_label = QLabel("CELLNAME")
        cellname_label.setFixedWidth(LABEL_W)
        self.lay_cellname_edit = QLineEdit()
        auto_row.addWidget(self.lay_radio_auto)
        auto_row.addWidget(cellname_label)
        auto_row.addWidget(self.lay_cellname_edit)
        layout.addLayout(auto_row)

        # LIB row
        lib_row = QHBoxLayout()
        lib_row.setSpacing(8)
        self.lay_radio_lib = QRadioButton("LIB")
        self.lay_radio_lib.setFixedWidth(RADIO_W)
        lib_label = QLabel("FROM VIRTUOSO LAYOUT LIBRARY")
        lib_row.addWidget(self.lay_radio_lib)
        lib_row.addWidget(lib_label)
        layout.addLayout(lib_row)

        self._lay_radio_group.addButton(self.lay_radio_file)
        self._lay_radio_group.addButton(self.lay_radio_auto)
        self._lay_radio_group.addButton(self.lay_radio_lib)

        self.lay_radio_file.setChecked(True)
        self.lay_cellname_edit.setEnabled(False)

        self._lay_radio_group.buttonToggled.connect(self._on_lay_radio_toggled)

        return group

    def _on_lay_radio_toggled(self, button, checked):
        if checked:
            self.lay_oasis_edit.setEnabled(self.lay_radio_file.isChecked())
            self.lay_cellname_edit.setEnabled(self.lay_radio_auto.isChecked())

    def _build_result_group(self) -> QGroupBox:
        group = QGroupBox("RESULT")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.cell_table = self._build_cell_list_table()
        layout.addWidget(self.cell_table)

        export_row = QHBoxLayout()
        export_row.setSpacing(8)
        self.export_path_edit = QLineEdit()
        self.export_btn = QPushButton("EXPORT")
        self.export_btn.clicked.connect(self._export_cell_list)
        export_row.addWidget(self.export_path_edit)
        export_row.addWidget(self.export_btn)
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
        action = menu.exec_(self.cell_table.viewport().mapToGlobal(pos))
        if action == delete_action:
            rows = sorted(
                {idx.row() for idx in self.cell_table.selectedIndexes()},
                reverse=True,
            )
            for row in rows:
                self.cell_table.removeRow(row)
        elif action == send_lvs_action:
            pass

    def _export_cell_list(self):
        path = self.export_path_edit.text().strip()
        if not path:
            return
        lines = []
        for row in range(self.cell_table.rowCount()):
            layout_val = (self.cell_table.item(row, 0) or QTableWidgetItem("")).text()
            sch_val    = (self.cell_table.item(row, 1) or QTableWidgetItem("")).text()
            lines.append(f"{layout_val} {sch_val}")
        Path(path).write_text("\n".join(lines), encoding="utf-8")

    def reset(self):
        self.radio_file.setChecked(True)
        self.netlist_edit.clear()
        self.cellname_edit.clear()

        self.lay_radio_file.setChecked(True)
        self.lay_oasis_edit.clear()
        self.lay_cellname_edit.clear()

        self.cell_table.setRowCount(0)
        for row in range(5):
            self.cell_table.insertRow(row)
            for col in range(2):
                self.cell_table.setItem(row, col, QTableWidgetItem(""))

        self.export_path_edit.clear()


# ── CCL > RUN tab ────────────────────────────────────────────────────────────

class _RatioTable(QTableWidget):
    """QTableWidget that keeps column widths at fixed ratios on resize."""
    def __init__(self, rows: int, cols: int, ratios: list):
        super().__init__(rows, cols)
        self._ratios = ratios
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self.viewport().width()
        for i, r in enumerate(self._ratios):
            self.setColumnWidth(i, int(w * r))


class RunTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        layout.addWidget(self._build_input_group())
        layout.addWidget(self._build_run_result_group())

        self.check_ccl_btn = QPushButton("CHECK CCL")
        self.check_ccl_btn.setFixedHeight(56)
        self.check_ccl_btn.clicked.connect(self._on_check_ccl)
        layout.addWidget(self.check_ccl_btn)

    def _build_input_group(self) -> QGroupBox:
        group = QGroupBox("INPUT")
        group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self._run_radio_group = QButtonGroup(self)

        RADIO_W = 90

        # 라디오 묶음 + GET 버튼 병렬 배치
        outer_row = QHBoxLayout()
        outer_row.setSpacing(8)

        radio_layout = QVBoxLayout()
        radio_layout.setSpacing(8)

        # AUTO row
        auto_row = QHBoxLayout()
        auto_row.setSpacing(8)
        self.run_radio_auto = QRadioButton("AUTO")
        self.run_radio_auto.setFixedWidth(RADIO_W)
        auto_row.addWidget(self.run_radio_auto)
        auto_row.addWidget(QLabel("FROM EXTRACT TAB"))
        radio_layout.addLayout(auto_row)

        # FILE row
        file_row = QHBoxLayout()
        file_row.setSpacing(8)
        self.run_radio_file = QRadioButton("FILE")
        self.run_radio_file.setFixedWidth(RADIO_W)
        cell_list_label = QLabel("CELL LIST")
        cell_list_label.setFixedWidth(100)
        self.run_file_cell_list_edit = QLineEdit()
        file_row.addWidget(self.run_radio_file)
        file_row.addWidget(cell_list_label)
        file_row.addWidget(self.run_file_cell_list_edit)
        radio_layout.addLayout(file_row)

        # CELL row
        cell_row = QHBoxLayout()
        cell_row.setSpacing(8)
        self.run_radio_cell = QRadioButton("CELL")
        self.run_radio_cell.setFixedWidth(RADIO_W)
        lay_label = QLabel("LAYOUT NAME")
        lay_label.setFixedWidth(100)
        self.run_layout_name_edit = QLineEdit()
        sch_label = QLabel("SCHEMATIC NAME")
        sch_label.setFixedWidth(120)
        self.run_sch_name_edit = QLineEdit()
        cell_row.addWidget(self.run_radio_cell)
        cell_row.addWidget(lay_label)
        cell_row.addWidget(self.run_layout_name_edit)
        cell_row.addWidget(sch_label)
        cell_row.addWidget(self.run_sch_name_edit)
        radio_layout.addLayout(cell_row)

        outer_row.addLayout(radio_layout)

        # GET 버튼 (라디오 묶음과 병렬 배치)
        self.run_get_btn = QPushButton("GET")
        self.run_get_btn.setFixedWidth(60)
        self.run_get_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        outer_row.addWidget(self.run_get_btn)

        layout.addLayout(outer_row)

        self._run_radio_group.addButton(self.run_radio_auto)
        self._run_radio_group.addButton(self.run_radio_file)
        self._run_radio_group.addButton(self.run_radio_cell)

        self.run_radio_auto.setChecked(True)
        self.run_file_cell_list_edit.setEnabled(False)
        self.run_layout_name_edit.setEnabled(False)
        self.run_sch_name_edit.setEnabled(False)

        self._run_radio_group.buttonToggled.connect(self._on_run_radio_toggled)

        return group

    def _on_run_radio_toggled(self, button, checked):
        if checked:
            file_checked = self.run_radio_file.isChecked()
            cell_checked = self.run_radio_cell.isChecked()
            self.run_file_cell_list_edit.setEnabled(file_checked)
            self.run_layout_name_edit.setEnabled(cell_checked)
            self.run_sch_name_edit.setEnabled(cell_checked)

    def _build_run_result_group(self) -> QGroupBox:
        group = QGroupBox("RESULT")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        self.run_table = self._build_run_cell_table()
        layout.addWidget(self.run_table)

        export_row = QHBoxLayout()
        export_row.setSpacing(8)
        self.run_export_path_edit = QLineEdit()
        self.run_export_btn = QPushButton("EXPORT")
        self.run_export_btn.clicked.connect(self._run_export_cell_list)
        export_row.addWidget(self.run_export_path_edit)
        export_row.addWidget(self.run_export_btn)
        layout.addLayout(export_row)

        return group

    def _build_run_cell_table(self) -> _RatioTable:
        table = _RatioTable(5, 3, [0.4, 0.4, 0.2])
        table.setHorizontalHeaderLabels(["LAYOUT", "SCHEMATIC", "RESULT"])

        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.ExtendedSelection)

        for row in range(5):
            for col in range(3):
                table.setItem(row, col, QTableWidgetItem(""))

        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self._on_run_table_context_menu)

        return table

    def _on_run_table_context_menu(self, pos):
        menu = QMenu(self)
        delete_action = menu.addAction("DELETE")
        open_result_action = menu.addAction("OPEN RESULT")
        action = menu.exec_(self.run_table.viewport().mapToGlobal(pos))
        if action == delete_action:
            rows = sorted(
                {idx.row() for idx in self.run_table.selectedIndexes()},
                reverse=True,
            )
            for row in rows:
                self.run_table.removeRow(row)
        elif action == open_result_action:
            pass

    def _run_export_cell_list(self):
        path = self.run_export_path_edit.text().strip()
        if not path:
            return
        lines = []
        for row in range(self.run_table.rowCount()):
            cells = [
                (self.run_table.item(row, col) or QTableWidgetItem("")).text()
                for col in range(self.run_table.columnCount())
            ]
            lines.append(" ".join(cells))
        Path(path).write_text("\n".join(lines), encoding="utf-8")

    def _on_check_ccl(self):
        pass

    def reset(self):
        self.run_radio_auto.setChecked(True)
        self.run_file_cell_list_edit.clear()
        self.run_layout_name_edit.clear()
        self.run_sch_name_edit.clear()

        self.run_table.setRowCount(0)
        for row in range(5):
            self.run_table.insertRow(row)
            for col in range(3):
                self.run_table.setItem(row, col, QTableWidgetItem(""))

        self.run_export_path_edit.clear()


# ── CCL tab ──────────────────────────────────────────────────────────────────

class CclTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.sub_tabs = QTabWidget()
        self.extract_tab = ExtractTab()
        self.run_tab = RunTab()
        self.sub_tabs.addTab(self.extract_tab, "EXTRACT")
        self.sub_tabs.addTab(self.run_tab, "RUN")

        layout.addWidget(self.sub_tabs)

    def reset(self):
        self.extract_tab.reset()
        self.run_tab.reset()


# ── DRV > EXTRACT tab ───────────────────────────────────────────────────────

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


# ── DRV > LAS tab ───────────────────────────────────────────────────────────

class DrvLasTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addStretch()

    def reset(self):
        pass


# ── DRV > RUN tab ───────────────────────────────────────────────────────────

class DrvRunTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.addStretch()

    def reset(self):
        pass


# ── DRV tab ──────────────────────────────────────────────────────────────────

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


# ── RightPanel ───────────────────────────────────────────────────────────────

class RightPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self.title_label = QLabel("프로젝트를 선택하세요")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.title_label)

        self.setting_tab = SettingTab()
        self.ccl_tab = CclTab()
        self.drv_tab = DrvTab()

        self.tabs = QTabWidget()
        self.tabs.addTab(self.setting_tab, "SETTING")
        self.tabs.addTab(self.ccl_tab, "CCL")
        self.tabs.addTab(self.drv_tab, "DRV")

        layout.addWidget(self.tabs)

    def load_project(self, project_name: str):
        self.setting_tab.reset()
        self.ccl_tab.reset()
        self.drv_tab.reset()
        self.title_label.setText(project_name)
        json_path = PROJECTS_DIR / f"{project_name}.json"
        if json_path.exists():
            self.setting_tab.load_project(json_path)
