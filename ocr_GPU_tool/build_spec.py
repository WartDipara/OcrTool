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

try:
    pp_dist = importlib.metadata.distribution("paddlepaddle-gpu")
except importlib.metadata.PackageNotFoundError:
    pp_dist = importlib.metadata.distribution("paddlepaddle")
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

HIDDEN_IMPORTS = [
    "paddle",
    "paddlex",
    "requests",
    "requests.exceptions",
    "urllib3",
    "urllib3.util",
    "huggingface_hub",
    "certifi",
    "charset_normalizer",
    "idna",
    "PIL",
    "PIL._imaging",
]

try:
    import certifi
    CA_BUNDLE = Path(certifi.where())
    add_data.append(f"{CA_BUNDLE}{os.pathsep}{CA_BUNDLE.parent.name}")
except Exception:
    pass

# Bundle local model cache
MODEL_CACHE = Path.home() / ".paddlex"
if MODEL_CACHE.is_dir():
    add_data.append(f"{MODEL_CACHE}{os.pathsep}models")

cmd = "pyinstaller --onefile --windowed --clean --name OCRToolGPU"
cmd += " --collect-binaries PySide6"
cmd += " --collect-data PySide6.QtCore"
cmd += " --collect-all paddlex"
cmd += " --collect-all paddle"
for m in HIDDEN_IMPORTS:
    cmd += f' --hidden-import "{m}"'
for d in add_data:
    cmd += f' --add-data "{d}"'
cmd += " main.py"

print(cmd)
