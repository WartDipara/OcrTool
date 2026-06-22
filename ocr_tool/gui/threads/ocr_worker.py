from PySide6.QtCore import QObject, Signal
from pathlib import Path
from core.ocr_engine import OCREngine


class OCRWorker(QObject):
    progress = Signal(int, int, str)
    finished = Signal(str, object)
    error = Signal(str, str)
    all_done = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._engine = OCREngine()

    def process(self, image_paths: list[Path], output_dir: Path):
        total = len(image_paths)
        for i, img_path in enumerate(image_paths):
            self.progress.emit(i + 1, total, f"正在识别: {img_path.name}")
            try:
                result = self._engine.predict(img_path, output_dir)
                self.finished.emit(str(img_path), result)
            except Exception as e:
                self.error.emit(str(img_path), str(e))
        self.all_done.emit()
