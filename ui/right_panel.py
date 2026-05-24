from pathlib import Path
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel
from PyQt5.QtCore import Qt

from ui.tab_setting import SettingTab
from ui.tab_ccl import CclTab
from ui.tab_drv import DrvTab

PROJECTS_DIR = Path(__file__).parent.parent / "projects"


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
            # ExtractTab에 GENPLATFORM DIRECTORY 전달
            genplatform_dir = self.setting_tab.genplatform_dir.text().strip()
            self.ccl_tab.extract_tab.genplatform_dir = genplatform_dir
