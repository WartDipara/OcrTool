@echo off
cd /d "%~dp0"
echo Generating PyInstaller command ...
for /f "usebackq delims=" %%i in (`conda run -n pdd-gpu python build_spec.py`) do set CMD=%%i
echo Running: %CMD%
conda run -n pdd-gpu %CMD%
if %errorlevel% equ 0 (
    echo Done! exe at dist\OCRToolGPU.exe
) else (
    echo Failed.
)
pause
