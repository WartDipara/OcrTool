import json
from pathlib import Path


class OCREngine:
    def __init__(self):
        self._ocr = None

    def _ensure_initialized(self):
        if self._ocr is None:
            from paddleocr import PaddleOCR
            self._ocr = PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                enable_mkldnn=False,
            )

    def predict(self, image_path: Path, output_dir: Path) -> dict:
        self._ensure_initialized()
        output_dir.mkdir(parents=True, exist_ok=True)

        stem = image_path.stem

        result = self._ocr.predict(str(image_path))

        json_paths = []
        img_paths = []

        for res in result:
            res.save_to_json(str(output_dir))
            res.save_to_img(str(output_dir))
            expected_json = output_dir / f"{stem}_res.json"
            expected_img = output_dir / f"{stem}_ocr_res_img.png"
            if expected_json.exists():
                json_paths.append(expected_json)
            if expected_img.exists():
                img_paths.append(expected_img)

        json_data = None
        if json_paths:
            with open(json_paths[-1], "r", encoding="utf-8") as f:
                json_data = json.load(f)

        return {
            "json_data": json_data,
            "json_path": json_paths[-1] if json_paths else None,
            "annotated_image": img_paths[-1] if img_paths else None,
        }
