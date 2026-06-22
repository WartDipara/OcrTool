from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QColor, QPainter, QPen, QBrush
from pathlib import Path


VALID_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
DROP_HIGHLIGHT = """
    UploadArea#card {
        background-color: #1e2a45;
        border: 2px dashed #7c3aed;
        border-radius: 10px;
    }
"""
DROP_NORMAL = """
    UploadArea#card {
        background-color: #16213e;
        border: 2px dashed #2a2a4a;
        border-radius: 10px;
    }
"""


class UploadArea(QWidget):
    files_selected = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._build_ui()

    def _build_ui(self):
        self.setMinimumHeight(140)
        self.setObjectName("card")
        self.setStyleSheet(DROP_NORMAL)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)

        self._icon_label = QLabel("📁")
        self._icon_label.setStyleSheet("font-size: 32px; background: transparent;")
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._text_label = QLabel("拖拽图片到此处\n或点击下方按钮上传")
        self._text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._text_label.setObjectName("subtitle")

        self._btn = QPushButton("选择图片 (jpg/png/webp)")
        self._btn.setObjectName("btnSmall")
        self._btn.clicked.connect(self._on_browse)

        self._file_label = QLabel("")
        self._file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._file_label.setObjectName("status")
        self._file_label.setWordWrap(True)
        self._file_label.hide()

        layout.addWidget(self._icon_label)
        layout.addWidget(self._text_label)
        layout.addWidget(self._btn, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._file_label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            valid = any(
                Path(u.toLocalFile()).suffix.lower() in VALID_EXTENSIONS
                for u in urls if u.isLocalFile()
            )
            if valid:
                event.acceptProposedAction()
                self.setStyleSheet(DROP_HIGHLIGHT)

    def dragLeaveEvent(self, event):
        self.setStyleSheet(DROP_NORMAL)

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet(DROP_NORMAL)

        urls = event.mimeData().urls()
        files = []
        for u in urls:
            if u.isLocalFile():
                p = Path(u.toLocalFile())
                if p.suffix.lower() in VALID_EXTENSIONS:
                    files.append(p)

        if files:
            self._show_selected(files)
            self.files_selected.emit(files)

    def _on_browse(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.webp);;所有文件 (*.*)",
        )
        if paths:
            files = [Path(p) for p in paths]
            self._show_selected(files)
            self.files_selected.emit(files)

    def _show_selected(self, files: list[Path]):
        n = len(files)
        if n == 1:
            self._file_label.setText(f"已选择: {files[0].name}")
        else:
            self._file_label.setText(f"已选择 {n} 张图片")
        self._file_label.show()
        self._icon_label.hide()
        self._text_label.hide()

    def reset(self):
        self._file_label.hide()
        self._icon_label.show()
        self._text_label.show()
        self.setStyleSheet(DROP_NORMAL)
