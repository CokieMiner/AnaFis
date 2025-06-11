@echo off
echo AnaFis Build Diagnostic Script
echo ================================
echo.

echo 1. Checking Python installation...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found in PATH
    goto :end
)
echo.

echo 2. Checking PyInstaller installation...
python -m PyInstaller --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PyInstaller not installed
    echo Install with: pip install pyinstaller
    goto :end
)
echo.

echo 3. Checking required files...
if not exist "run.py" (
    echo ERROR: run.py not found
    goto :end
)
echo ✓ run.py found

if not exist "app_files\utils\icon.ico" (
    echo ERROR: icon.ico not found
    goto :end
)
echo ✓ icon.ico found

if not exist "AnaFis_onedir.spec" (
    echo ERROR: AnaFis_onedir.spec not found
    goto :end
)
echo ✓ AnaFis_onedir.spec found
echo.

echo 4. Testing simple PyInstaller build...
echo Building with simple spec file...
python -m PyInstaller AnaFis_onedir.spec
echo Simple build exit code: %ERRORLEVEL%
echo.

echo 5. Checking results...
if exist "dist\AnaFis\AnaFis.exe" (
    echo ✓ SUCCESS: Executable created at dist\AnaFis\AnaFis.exe
    echo File size:
    dir "dist\AnaFis\AnaFis.exe" | find "AnaFis.exe"
) else (
    echo ✗ FAILED: No executable found
    if exist "dist" (
        echo Dist folder contents:
        dir dist /s
    )
)

:end
echo.
pause