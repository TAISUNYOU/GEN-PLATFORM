import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QGroupBox       { font-weight: 600; }
        QTabBar::tab              { font-weight: 600; padding: 8px 18px; min-width: 70px; }
        QTabBar::tab:selected     { background: #4A90D9; color: white; }
        QTabBar::tab:!selected    { background: #D0D0D0; color: #444; }
        QPushButton     { font-weight: 600; }
    """)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
