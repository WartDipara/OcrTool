import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from gui.app import MainWindow
from gui.styles.theme import STYLE


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setOrganizationName("OCRToolGPU")
    app.setApplicationName("OCR Tool GPU")

    app.setStyleSheet(STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
