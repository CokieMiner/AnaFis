@echo off
REM Build script for AnaFis executable
echo Building AnaFis executable...

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build the executable
python -m PyInstaller --onefile --windowed --icon=app_files/utils/icon.ico --name="AnaFis" run.py

REM Check if build was successful
if exist "dist\AnaFis.exe" (
    echo.
    echo ================================
    echo Build completed successfully!
    echo ================================
    echo.
    echo Executable location: dist\AnaFis.exe
    echo.
    echo You can now run the application by double-clicking:
    echo %cd%\dist\AnaFis.exe
    echo.
    echo Or copy the 'dist\AnaFis.exe' file to another location.
    echo.
) else (
    echo.
    echo ================================
    echo Build failed!
    echo ================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause
