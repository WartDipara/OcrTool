import json
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt


class ResultPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        header = QHBoxLayout()
        title = QLabel("📄  识别结果")
        title.setObjectName("title")
        self._file_indicator = QLabel("")
        self._file_indicator.setObjectName("status")
        header.addWidget(title)
        header.addWidget(self._file_indicator, 1, Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(header)

        self._text = QPlainTextEdit()
        self._text.setReadOnly(True)
        self._text.setPlaceholderText("识别完成后，结果将显示在此处...")

        layout.addWidget(self._text)

    def set_json(self, data, source_file: str = ""):
        if data is None:
            self._text.setPlainText("(无结果)")
            return
        try:
            formatted = json.dumps(data, ensure_ascii=False, indent=2)
            self._text.setPlainText(formatted)
            if source_file:
                self._file_indicator.setText(f" — {source_file}")
            else:
                self._file_indicator.setText("")
        except (TypeError, ValueError):
            self._text.setPlainText(str(data))

    def set_text(self, text: str):
        self._text.setPlainText(text)

    def get_text(self) -> str:
        return self._text.toPlainText()

    def clear(self):
        self._text.clear()
        self._file_indicator.setText("")
