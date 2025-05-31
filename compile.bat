@echo off
echo Installing build dependencies...
pip install -r requirements-build.txt

echo.
echo Building AnaFis with Cython...
python build.py

echo.
echo Build complete! Press any key to exit.
pause