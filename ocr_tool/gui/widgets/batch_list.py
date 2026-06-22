from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt
from pathlib import Path

STATUS_ICONS = {
    "waiting": "⏳",
    "processing": "🔄",
    "done": "✅",
    "error": "❌",
}


class BatchList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(100)

    def add_files(self, files: list[Path]):
        for f in files:
            self.add_file(f)

    def add_file(self, file: Path):
        item = QListWidgetItem(f"{STATUS_ICONS['waiting']}  {file.name}")
        item.setData(Qt.ItemDataRole.UserRole, str(file))
        item.setData(Qt.ItemDataRole.UserRole + 1, "waiting")
        self.addItem(item)

    def update_status(self, file_path: str, status: str):
        for i in range(self.count()):
            item = self.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == file_path:
                name = Path(file_path).name
                icon = STATUS_ICONS.get(status, "⏳")
                item.setText(f"{icon}  {name}")
                item.setData(Qt.ItemDataRole.UserRole + 1, status)
                if status == "processing":
                    self.setCurrentItem(item)
                break

    def get_files_by_status(self, status: str) -> list[str]:
        result = []
        for i in range(self.count()):
            item = self.item(i)
            if item.data(Qt.ItemDataRole.UserRole + 1) == status:
                result.append(item.data(Qt.ItemDataRole.UserRole))
        return result

    def get_all_files(self) -> list[str]:
        result = []
        for i in range(self.count()):
            result.append(self.item(i).data(Qt.ItemDataRole.UserRole))
        return result

    def clear_all(self):
        self.clear()
