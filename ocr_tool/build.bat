@echo off
cd /d "%~dp0"

REM Remove stale spec file so PyInstaller uses fresh command-line args
del /f /q *.spec 2>nul

echo Generating PyInstaller command ...
for /f "usebackq delims=" %%i in (`conda run -n pdd python build_spec.py`) do set CMD=%%i
echo Running: %CMD%
conda run -n pdd %CMD%
if %errorlevel% equ 0 (
    echo Done! exe at dist\OCRTool.exe
) else (
    echo Failed.
)
pause
