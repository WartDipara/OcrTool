from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from pathlib import Path


class ImagePreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._image_path = None
        self._build_ui()

    def _build_ui(self):
        self.setMinimumWidth(280)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._label = QLabel("图片预览")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setObjectName("subtitle")
        self._label.setMinimumHeight(200)
        self._label.setStyleSheet("""
            QLabel {
                background-color: #0f3460;
                border: 1px solid #2a2a4a;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        self._label.setScaledContents(False)

        layout.addWidget(self._label)

    def show_image(self, image_path: Path | str):
        self._image_path = Path(image_path)
        if not self._image_path.exists():
            self._label.setText(f"图片不存在\n{self._image_path.name}")
            return

        pixmap = QPixmap(str(self._image_path))
        if pixmap.isNull():
            self._label.setText(f"无法加载图片\n{self._image_path.name}")
            return

        scaled = pixmap.scaled(
            self._label.size() - QPixmap(8, 8).size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._label.setPixmap(scaled)

    def clear(self):
        self._label.setPixmap(QPixmap())
        self._label.setText("图片预览")
        self._image_path = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._image_path and self._label.pixmap() and not self._label.pixmap().isNull():
            pixmap = QPixmap(str(self._image_path))
            scaled = pixmap.scaled(
                self._label.size() - QPixmap(8, 8).size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._label.setPixmap(scaled)
