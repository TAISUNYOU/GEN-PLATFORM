import json
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QCursor, QFont

PROJECTS_DIR = Path(__file__).parent.parent / "projects"


class LeftPanel(QWidget):
    project_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(180)
        self.setMaximumWidth(300)
        self._build_ui()
        self._load_projects()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self.select_btn = QPushButton("SELECT PROJECT")
        self.select_btn.setFixedHeight(56)
        self.select_btn.clicked.connect(self._on_select_clicked)
        layout.addWidget(self.select_btn)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.itemDoubleClicked.connect(self._on_select_clicked)
        layout.addWidget(self.tree_widget)

    def _load_projects(self):
        try:
            project_list_path = PROJECTS_DIR / "PROJECTLIST.json"
            data = json.loads(project_list_path.read_text(encoding="utf-8"))

            for tech, projects in data.items():
                tech_item = QTreeWidgetItem([tech])
                bold_font = QFont()
                bold_font.setBold(True)
                tech_item.setFont(0, bold_font)
                self.tree_widget.addTopLevelItem(tech_item)

                for _, project_file in sorted(projects.items()):
                    project_name = Path(project_file).stem
                    project_item = QTreeWidgetItem([project_name])
                    tech_item.addChild(project_item)

                tech_item.setExpanded(True)
        except Exception as e:
            print(f"Error loading projects: {e}")

    def _on_select_clicked(self):
        current = self.tree_widget.currentItem()
        if not current:
            return

        # 선택된 항목이 프로젝트인지 확인 (자식이 없음 = 프로젝트)
        if current.childCount() > 0:
            return

        name = current.text(0)

        msg = QMessageBox(self)
        msg.setWindowTitle("MOVE PROJECT")
        msg.setText(f"MOVE TO {name}?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        no_btn = msg.button(QMessageBox.No)
        def _move_cursor():
            center = no_btn.mapToGlobal(no_btn.rect().center())
            QCursor.setPos(center)
        QTimer.singleShot(0, _move_cursor)

        if msg.exec_() == QMessageBox.Yes:
            self.project_selected.emit(name)
