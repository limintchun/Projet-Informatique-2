"""
NOM : Li
PRÉNOM : Min-tchun
SECTION : B1-INFO
MATRICULE : 000590125
"""

from window import ImageWindow
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication([])
    window = ImageWindow()
    window.show()
    app.exec()
