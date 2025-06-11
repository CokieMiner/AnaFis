# AnaFis Distribution Guide

## Executable Information

- **File**: `AnaFis.exe`
- **Size**: ~24 MB
- **Type**: Standalone Windows executable
- **Python Version**: 3.13.3
- **PyInstaller Version**: 6.13.0

## Distribution Contents

The `dist\AnaFis\` directory contains:
- `AnaFis.exe` - Main executable file
- `_internal\` - Directory with bundled dependencies and libraries

## System Requirements

- **Operating System**: Windows 10/11 (64-bit)
- **Memory**: 512 MB RAM minimum, 1 GB recommended
- **Disk Space**: 50 MB free space
- **Dependencies**: None (all bundled)

## Installation

1. Copy the entire `AnaFis` folder to the desired location
2. Run `AnaFis.exe` directly - no installation required
3. The application will create user preferences in your user directory

## Features Included

- ✅ Curve Fitting with multiple mathematical models
- ✅ Uncertainty Propagation calculations
- ✅ Data import/export (Excel, CSV, JSON)
- ✅ Graph plotting and export
- ✅ Multi-language support (Portuguese/English)
- ✅ Settings and preferences system
- ✅ Complete GUI interface

## Known Issues

- First startup may take a few seconds as libraries are loaded
- Some antivirus software may flag the executable (false positive)

## Build Information

Built with PyInstaller using the following key dependencies:
- NumPy (numerical computing)
- SciPy (scientific computing)
- Matplotlib (plotting)
- Pandas (data manipulation)
- SymPy (symbolic mathematics)
- Tkinter (GUI framework)

## Troubleshooting

### Application won't start
- Ensure you're running the exe from within the AnaFis folder
- Check that `_internal` directory is present alongside the exe
- Try running from command prompt to see error messages

### Antivirus warnings
- The executable is safe - warnings are due to PyInstaller bundling
- Add the folder to antivirus exceptions if needed

### Performance issues
- Ensure adequate RAM (1GB+)
- Close other heavy applications
- First startup is slower due to library initialization

## Distribution

This is a portable application that can be:
- Copied to USB drives
- Shared as a ZIP file
- Distributed without Python installation requirements
- Run from any Windows computer without setup

Built on: June 11, 2025
