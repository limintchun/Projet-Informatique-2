"""
NOM : Li
PRÉNOM : Min-Tchun
SECTION : B1-INFO
MATRICULE : 000590125
"""

# Par manque d'organisation, je n'ai pas su adapter l'inteface graphique pour la phase 4 et 5

from PySide6.QtCore import Qt, QRectF
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QGraphicsScene, QGraphicsView, \
    QInputDialog, QErrorMessage, QWidget, QFileDialog
from PySide6.QtGui import QImage, QColor, QPixmap
from encoding import Decoder, Encoder


class ImageWindow(QMainWindow):
    def __init__(self):
        super(ImageWindow, self).__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('ULBMP Viewer')
        self.setGeometry(100, 100, 800, 600)

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)

        self.load_button = QPushButton('Load Image', self)
        self.load_button.clicked.connect(self.load_image)

        self.save_button = QPushButton('Save Image', self)
        self.save_button.clicked.connect(self.save_image)
        self.save_button.setEnabled(False)

        layout = QVBoxLayout()
        layout.addWidget(self.load_button)
        layout.addWidget(self.view)
        layout.addWidget(self.save_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def load_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("ULBMP files (*.ulbmp)")

        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]

            try:
                img = Decoder.load_from(file_path)

                width, height = img.get_width(), img.get_height()
                image = QImage(width, height, QImage.Format_RGB32)

                for y in range(height):
                    for x in range(width):
                        pixel = img[x, y]
                        r, g, b = pixel.get_red(), pixel.get_green(), pixel.get_blue()
                        color = QColor(r, g, b)
                        image.setPixel(x, y, color.rgb())

                self.scene.clear()

                pixmap = QPixmap.fromImage(image)
                self.scene.addPixmap(pixmap)

                self.view.setScene(self.scene)

                # Ajuster dynamiquement la taille du canevas (scène) en fonction de la taille de l'image
                self.scene.setSceneRect(0, 0, width, height)

                self.view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

                self.save_button.setEnabled(True)
            except Exception as e:
                error_dialog = QErrorMessage(self)
                error_dialog.showMessage(f"Error loading image: {str(e)}")

    def save_image(self):
        try:
            # Get the ULBMP version to use
            version, ok = QInputDialog.getInt(self, 'Enter ULBMP version', 'Enter ULBMP version:', 1, 1, 4)
            if not ok:
                return

            # Get the file path to save the image
            file_path, _ = QFileDialog.getSaveFileName(self, 'Save Image', '', 'ULBMP files (*.ulbmp)')
            if not file_path:
                return

            # Use the save_to method of the Encoder class to save the image
            encoder = Encoder(Decoder.load_from(file_path), version)
            encoder.save_to(file_path)

            # Inform the user about the successful save
            self.statusBar().showMessage(f"Image saved as {file_path}", 2000)

        except Exception as e:
            error_dialog = QErrorMessage(self)
            error_dialog.showMessage(f"Error saving image: {str(e)}")