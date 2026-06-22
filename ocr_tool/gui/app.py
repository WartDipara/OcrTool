import sys
import time
import subprocess
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QPushButton, QStatusBar, QLabel, QApplication,
)
from PySide6.QtCore import Qt, QThread, QTimer

from gui.widgets.upload_area import UploadArea
from gui.widgets.batch_list import BatchList
from gui.widgets.progress_panel import ProgressPanel
from gui.widgets.result_panel import ResultPanel
from gui.widgets.image_preview import ImagePreview
from gui.threads.ocr_worker import OCRWorker

EXE_DIR = Path(sys.argv[0]).resolve().parent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._worker_thread = None
        self._worker = None
        self._processing = False
        self._output_dir = EXE_DIR / "output"
        self._start_time = 0
        self._results: dict[str, dict] = {}

        self._build_ui()
        self._connect_signals()
        self._update_button_states()

    def _build_ui(self):
        self.setWindowTitle("OCR Tool v1.0")
        self.setMinimumSize(1000, 680)
        self.resize(1200, 800)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)

        title_bar = QHBoxLayout()
        title = QLabel("🔍  OCR Tool")
        title.setObjectName("title")
        subtitle = QLabel("图片文字识别工具")
        subtitle.setObjectName("subtitle")
        title_bar.addWidget(title)
        title_bar.addWidget(subtitle)
        title_bar.addStretch()
        main_layout.addLayout(title_bar)

        body_splitter = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        self._upload_area = UploadArea()
        left_layout.addWidget(self._upload_area)

        self._batch_list = BatchList()
        self._batch_list.setMinimumHeight(120)
        left_layout.addWidget(QLabel("文件列表（点击查看结果）"), 0)
        left_layout.addWidget(self._batch_list, 1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        self._btn_start = QPushButton("▶  开始识图")
        self._btn_view = QPushButton("📄  查看结果")
        self._btn_copy = QPushButton("📋  复制")
        self._btn_clear = QPushButton("🗑  清空")
        btn_row.addWidget(self._btn_start)
        btn_row.addWidget(self._btn_view)
        btn_row.addWidget(self._btn_copy)
        btn_row.addWidget(self._btn_clear)
        left_layout.addLayout(btn_row)

        self._progress_panel = ProgressPanel()
        left_layout.addWidget(self._progress_panel)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)

        right_splitter = QSplitter(Qt.Orientation.Vertical)

        self._result_panel = ResultPanel()
        right_splitter.addWidget(self._result_panel)

        self._preview_panel = ImagePreview()
        right_splitter.addWidget(self._preview_panel)
        right_splitter.setStretchFactor(0, 3)
        right_splitter.setStretchFactor(1, 2)

        right_layout.addWidget(right_splitter)

        body_splitter.addWidget(left)
        body_splitter.addWidget(right)
        body_splitter.setStretchFactor(0, 35)
        body_splitter.setStretchFactor(1, 65)
        main_layout.addWidget(body_splitter, 1)

        self._status = QStatusBar()
        self._status_label = QLabel("就绪")
        self._status_progress = QLabel("进度: 0/0")
        self._status_time = QLabel("耗时: --")
        self._status_chars = QLabel("文字: --")
        self._status.addWidget(self._status_label, 1)
        self._status.addPermanentWidget(self._status_progress)
        self._status.addPermanentWidget(self._status_time)
        self._status.addPermanentWidget(self._status_chars)
        self.setStatusBar(self._status)

    def _connect_signals(self):
        self._upload_area.files_selected.connect(self._on_files_selected)
        self._btn_start.clicked.connect(self._start_ocr)
        self._btn_view.clicked.connect(self._open_output_folder)
        self._btn_copy.clicked.connect(self._copy_result)
        self._btn_clear.clicked.connect(self._clear_all)
        self._batch_list.itemClicked.connect(self._on_batch_item_clicked)

    def _on_files_selected(self, files: list[Path]):
        self._batch_list.add_files(files)
        self._update_button_states()

    def _on_batch_item_clicked(self, item):
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if not file_path:
            return
        status = item.data(Qt.ItemDataRole.UserRole + 1) or ""
        name = Path(file_path).name

        if status == "done":
            result = self._results.get(file_path)
            if result:
                self._result_panel.set_json(result.get("json_data"), name)
                annotated = result.get("annotated_image")
                if annotated:
                    self._preview_panel.show_image(annotated)
                self._status_label.setText(f"查看: {name}")
        elif status == "error":
            self._progress_panel.append_log(f"[{name}] 识别失败")

    def _update_button_states(self):
        has_files = self._batch_list.count() > 0
        has_waiting = len(self._batch_list.get_files_by_status("waiting")) > 0
        has_result = bool(self._result_panel.get_text().strip())
        self._btn_start.setEnabled(has_waiting and not self._processing)
        self._btn_clear.setEnabled(has_files and not self._processing)
        self._btn_copy.setEnabled(has_result)
        self._btn_view.setEnabled(True)

    def _set_controls_enabled(self, enabled: bool):
        self._btn_start.setEnabled(enabled)
        self._btn_clear.setEnabled(enabled)
        self._upload_area.setEnabled(enabled)

    def _start_ocr(self):
        waiting = self._batch_list.get_files_by_status("waiting")
        if not waiting:
            return

        self._processing = True
        self._set_controls_enabled(False)
        self._progress_panel.reset()
        self._status_label.setText("处理中...")
        self._status_progress.setText(f"进度: 0/{len(waiting)}")
        self._start_time = time.time()

        files = [Path(f) for f in waiting]
        for f in files:
            self._batch_list.update_status(str(f), "processing")

        self._event_timer = QTimer(self)
        self._event_timer.setInterval(30)
        self._event_timer.timeout.connect(
            lambda: QApplication.processEvents()
        )
        self._event_timer.start()

        self._worker_thread = QThread()
        self._worker = OCRWorker()
        self._worker.moveToThread(self._worker_thread)

        self._worker_thread.started.connect(
            lambda: self._worker.process(files, self._output_dir)
        )
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_file_finished)
        self._worker.error.connect(self._on_file_error)
        self._worker.all_done.connect(self._on_all_done)
        self._worker.all_done.connect(self._worker_thread.quit)
        self._worker_thread.finished.connect(self._on_thread_finished)

        self._worker_thread.start()

    def _on_progress(self, current: int, total: int, message: str):
        self._progress_panel.set_progress(current, total, message)
        self._status_progress.setText(f"进度: {current}/{total}")
        if current > 0 and self._start_time > 0:
            elapsed = time.time() - self._start_time
            self._status_time.setText(f"耗时: {elapsed:.1f}s")

    def _on_file_finished(self, file_path: str, result: dict):
        self._batch_list.update_status(file_path, "done")
        self._progress_panel.append_log(f"完成: {Path(file_path).name}")
        self._results[file_path] = result

        self._result_panel.set_json(result.get("json_data"), Path(file_path).name)
        annotated = result.get("annotated_image")
        if annotated:
            self._preview_panel.show_image(annotated)

        self._update_button_states()

    def _on_file_error(self, file_path: str, error_msg: str):
        self._batch_list.update_status(file_path, "error")
        self._progress_panel.append_log(
            f"失败: {Path(file_path).name} — {error_msg}"
        )
        self._update_button_states()

    def _on_all_done(self):
        if self._event_timer:
            self._event_timer.stop()
            self._event_timer = None
        self._processing = False
        self._set_controls_enabled(True)
        self._status_label.setText("处理完成")

        all_files = self._batch_list.get_all_files()
        done = self._batch_list.get_files_by_status("done")
        err = self._batch_list.get_files_by_status("error")
        self._status_progress.setText(f"进度: {len(done)}/{len(all_files)}")
        if err:
            self._progress_panel.append_log(
                f"全部完成，成功 {len(done)} 张，失败 {len(err)} 张"
            )
        else:
            self._progress_panel.append_log("全部处理完成！")
        self._update_button_states()

    def _open_output_folder(self):
        output = self._output_dir
        output.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.Popen(["explorer", str(output.resolve())])
        except Exception as e:
            self._progress_panel.append_log(f"无法打开文件夹: {e}")

    def _copy_result(self):
        text = self._result_panel.get_text()
        if text.strip():
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self._status_label.setText("已复制到剪贴板")
            QTimer.singleShot(2000, lambda: self._status_label.setText("就绪"))

    def _clear_all(self):
        self._batch_list.clear_all()
        self._result_panel.clear()
        self._preview_panel.clear()
        self._progress_panel.reset()
        self._upload_area.reset()
        self._results.clear()
        self._status_label.setText("就绪")
        self._status_progress.setText("进度: 0/0")
        self._status_time.setText("耗时: --")
        self._status_chars.setText("文字: --")
        self._update_button_states()

    def _on_thread_finished(self):
        if self._worker:
            self._worker.deleteLater()
            self._worker = None
        if self._worker_thread:
            self._worker_thread.deleteLater()
            self._worker_thread = None

    def closeEvent(self, event):
        if self._event_timer:
            self._event_timer.stop()
            self._event_timer = None
        if self._worker_thread and self._worker_thread.isRunning():
            self._worker_thread.quit()
            self._worker_thread.wait(3000)
        event.accept()
