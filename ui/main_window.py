from PyQt5.QtWidgets import QMainWindow, QSplitter, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt
from ui.left_panel import LeftPanel
from ui.right_panel import RightPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GEN-Platform v1.0")
        self.resize(1200, 900)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)

        self.left_panel = LeftPanel()
        self.right_panel = RightPanel()

        splitter.addWidget(self.left_panel)
        splitter.addWidget(self.right_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([220, 980])

        layout.addWidget(splitter)

        self.left_panel.project_selected.connect(self.right_panel.load_project)

        first_tech = self.left_panel.tree_widget.topLevelItem(0)
        if first_tech and first_tech.childCount() > 0:
            first_project = first_tech.child(0)
            self.left_panel.tree_widget.setCurrentItem(first_project)
            self.right_panel.load_project(first_project.text(0))
