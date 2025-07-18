import os
import sys

os.environ["QT_API"] = "PySide6"

from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    
    # set application styles/theme
    # app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()