from PySide6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QTextEdit
from PySide6.QtCore import Qt


class ProgressPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.hide()

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(120)
        self._log.setPlaceholderText("操作日志将显示在此处...")

        layout.addWidget(self._progress)
        layout.addWidget(self._log)

    def set_progress(self, current: int, total: int, message: str = ""):
        if total > 0:
            self._progress.setRange(0, total)
            self._progress.setValue(current)
            self._progress.show()
        if message:
            self._log.append(f"> {message}")
            scrollbar = self._log.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def append_log(self, message: str):
        self._log.append(f"> {message}")
        scrollbar = self._log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def reset(self):
        self._progress.setValue(0)
        self._progress.hide()
        self._log.clear()
