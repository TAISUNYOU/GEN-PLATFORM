import json
from pathlib import Path
from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QGroupBox
)


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
