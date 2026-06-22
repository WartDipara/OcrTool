import os
from pathlib import Path
import importlib.metadata

px_dist = importlib.metadata.distribution("paddlex")
PX_SITE = Path(px_dist.locate_file("."))
PX_CONFIGS = PX_SITE / "paddlex" / "configs"

EXTRAS_OCR = [
    "beautifulsoup4", "einops", "ftfy", "imagesize", "jinja2",
    "latex2mathml", "lxml", "opencv_contrib_python", "openpyxl",
    "premailer", "pyclipper", "pypdfium2", "python_bidi", "regex",
    "safetensors", "scikit_learn", "scipy", "sentencepiece",
    "shapely", "tiktoken", "tokenizers",
]

pp_dist = importlib.metadata.distribution("paddlepaddle-gpu")
PP_SITE = Path(pp_dist.locate_file("."))
PADDLE_LIBS = PP_SITE / "paddle" / "libs"

add_data = [
    f"{PX_CONFIGS}{os.pathsep}paddlex/configs",
    f"{PADDLE_LIBS}{os.pathsep}paddle/libs",
]

for pkg in EXTRAS_OCR:
    try:
        dist = importlib.metadata.distribution(pkg)
        dinfo = Path(dist._path)
        add_data.append(f"{dinfo}{os.pathsep}{dinfo.name}")
    except importlib.metadata.PackageNotFoundError:
        pass

cmd = "pyinstaller --onefile --windowed --name OCRToolGPU"
cmd += " --collect-all PySide6"
for d in add_data:
    cmd += f' --add-data "{d}"'
cmd += " main.py"

print(cmd)
