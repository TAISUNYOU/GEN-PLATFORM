from pathlib import Path
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QLineEdit, QGroupBox, QRadioButton, QButtonGroup,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMenu,
    QPushButton, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt


class ExtractTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.genplatform_dir = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        layout.addWidget(self._build_schematic_group())
        layout.addWidget(self._build_layout_group())
        layout.addWidget(self._build_result_group())

        self.extract_btn = QPushButton("EXTRACT")
        self.extract_btn.setFixedHeight(56)
        self.extract_btn.clicked.connect(self._extract_cells)
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

    # ── Extract Logic ───────────────────────────────────────────────────────

    def _validate_folder_paths(self) -> bool:
        """Step 1: 폴더 경로 유효성검사 및 생성"""
        try:
            # 1. GENPLATFORM 경로 검증
            if not self.genplatform_dir:
                QMessageBox.warning(self, "Error", "GENPLATFORM DIRECTORY가 설정되지 않았습니다.")
                return False

            genplatform_path = Path(self.genplatform_dir)
            if not genplatform_path.exists():
                QMessageBox.warning(self, "Error", f"GENPLATFORM DIRECTORY가 존재하지 않습니다:\n{self.genplatform_dir}")
                return False

            # 2. CCL 폴더 생성 (없으면)
            ccl_path = genplatform_path / "CCL"
            ccl_path.mkdir(parents=True, exist_ok=True)

            # 3. EXTRACT 폴더 생성 (없으면)
            extract_path = ccl_path / "EXTRACT"
            extract_path.mkdir(parents=True, exist_ok=True)

            return True

        except Exception as e:
            QMessageBox.critical(self, "Error", f"폴더 검증 중 오류 발생:\n{str(e)}")
            return False

    def _process_schematic(self):
        """Step 2: SCHEMATIC 입력처리"""
        pass

    def _process_layout(self):
        """Step 3: LAYOUT 입력처리"""
        pass

    def _perform_extract(self):
        """Step 4: SCHEMATIC, LAYOUT 입력 정보를 바탕으로 EXTRACT"""
        pass

    def _extract_cells(self):
        """메인 Extract 함수"""
        # Step 1: 폴더 경로 유효성검사
        if not self._validate_folder_paths():
            return

        # Step 2: SCHEMATIC 입력처리
        self._process_schematic()

        # Step 3: LAYOUT 입력처리
        self._process_layout()

        # Step 4: EXTRACT 실행
        self._perform_extract()

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
