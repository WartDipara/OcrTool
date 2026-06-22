import os
import sys
import shutil
from pathlib import Path

if getattr(sys, "frozen", False):
    _exe_dir = Path(sys.argv[0]).resolve().parent
    _cache_dir = _exe_dir / "models"

    _bundled = Path(sys._MEIPASS) / "models"
    _official = _cache_dir / "official_models"
    if _bundled.is_dir() and not _official.is_dir():
        _cache_dir.mkdir(parents=True, exist_ok=True)
        for _item in _bundled.iterdir():
            _dest = _cache_dir / _item.name
            if not _dest.exists():
                if _item.is_dir():
                    shutil.copytree(_item, _dest)
                else:
                    shutil.copy2(_item, _dest)

    os.environ.setdefault("PADDLE_PDX_CACHE_HOME", str(_cache_dir))
else:
    os.environ.setdefault("PADDLE_PDX_CACHE_HOME", str(Path.home() / ".paddlex"))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from gui.app import MainWindow
from gui.styles.theme import STYLE


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setOrganizationName("OCRTool")
    app.setApplicationName("OCR Tool")

    app.setStyleSheet(STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
