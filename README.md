# AnaFis - Physics Data Analysis

## Overview

AnaFis is a comprehensive physics data analysis application with a modern graphical interface designed for researchers, students, and professionals working with experimental data. The application provides powerful tools for curve fitting and uncertainty propagation with real-time visualization capabilities.

## Installation

AnaFis requires Python 3.8 or newer.

### Option 1: Install using setup.py (Recommended)

Clone or download the repository and run:

```bash
python setup.py install
```

Or for development installation:

```bash
pip install -e .
```

### Option 2: Manual dependency installation

If you prefer to install dependencies manually:

```bash
pip install numpy scipy sympy matplotlib pandas
```

**Note:** `tkinter` comes pre-installed with Python and doesn't need to be installed separately.

## Running the Application

### After installation with setup.py:
If you installed using `python setup.py install`, you can run:

```bash
anafis
```

### Running from source:
To start AnaFis from the source directory, run:

```bash
python run.py
```

The application will show a splash screen while loading and then open the main interface.

## Main Features

### Core Functionality
- **Curve Fitting**: Advanced curve fitting with user-defined functions and built-in models
- **Uncertainty Propagation**: Calculate uncertainty propagation for arbitrary formulas using symbolic mathematics
- **Multi-language Support**: Interface available in Portuguese and English
- **Real-time Visualization**: Interactive plots that update in real-time during fitting

### Interface Features
- **Tabbed Interface**: Work with multiple analyses simultaneously
- **Language Switching**: Change interface language on-the-fly without restarting
- **Modern UI**: Clean, intuitive interface built with tkinter
- **Export Capabilities**: Export graphs in various formats (PNG, PDF, SVG)

### Advanced Tools
- **Custom Functions**: Define and use custom mathematical models for fitting
- **Parameter Estimation**: Advanced parameter estimation with uncertainty calculation
- **Data Import**: Support for CSV and tab-separated text files
- **History Management**: Keep track of previous analyses and results

## Data File Format

AnaFis supports tab-separated .csv or .txt files with the following column structure:

```
x    σx    y    σy
```

**Example data file:**
```
1.0  0.1   2.0  0.2
2.0  0.1   4.1  0.2
3.0  0.1   6.2  0.2
4.0  0.1   7.9  0.2
```

**Column descriptions:**
- `x`: Independent variable values
- `σx`: Uncertainty (standard deviation) in x
- `y`: Dependent variable values  
- `σy`: Uncertainty (standard deviation) in y

## Usage Guide

### Curve Fitting Module
1. **Load Data**: Use the "Load Data" button to import your data file
2. **Select Model**: Choose from predefined models or define a custom function
3. **Set Parameters**: Provide initial parameter estimates
4. **Perform Fit**: Click "Fit" to execute the curve fitting algorithm
5. **Analyze Results**: View fit parameters, uncertainties, and goodness-of-fit statistics
6. **Export**: Save plots and results in your preferred format

### Uncertainty Calculator Module
1. **Define Formula**: Enter your mathematical expression using symbolic notation
2. **Add Variables**: Specify variables with their values and uncertainties
3. **Calculate**: The application will compute uncertainty propagation using partial derivatives
4. **View Results**: See the final result with calculated uncertainty
5. **Formula Visualization**: View LaTeX-rendered formulas for better understanding

## Supported Mathematical Functions

The application supports standard mathematical functions including:
- Basic operations: `+`, `-`, `*`, `/`, `**` 
- Trigonometric: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`
- Logarithmic: `log`, `ln`, `exp`
- Hyperbolic: `sinh`, `cosh`, `tanh`
- Constants: `pi`, `e`

## Language Support

AnaFis supports both Portuguese and English interfaces. You can switch languages using the dropdown in the main toolbar. The language change applies to all interface elements and updates all open tabs immediately.

## Troubleshooting

### Common Issues
- **Fit does not converge**: Try different initial parameter values or verify data quality
- **Large fitting errors**: Review uncertainty values and model appropriateness  
- **Missing tkinter**: Install via your OS package manager or ensure it's included in Python installation
- **Import errors**: Verify all dependencies are installed with correct versions

### Performance Tips
- For large datasets, consider data preprocessing or sampling
- Complex custom functions may require longer computation time
- Save your work frequently when working with large analyses

## System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.8 or newer
- **Memory**: Minimum 4GB RAM recommended
- **Storage**: At least 100MB free space for installation

## Roadmap

### Upcoming Features
- **Complete Settings Integration**: Full theme support with light/dark/auto modes
- **Excel-like Tables**: Spreadsheet-style data entry and editing capabilities  
- **Equation Solving Module**: Symbolic and numerical equation solver
- **Enhanced Data Visualization**: 3D plotting, advanced customization options
- **File Management**: Project files, recent files menu, auto-save functionality

See [TODO.md](TODO.md) for the complete development roadmap and feature planning.

## Contributing

AnaFis is open for contributions. Please feel free to submit issues, feature requests, or pull requests to improve the application.

## License

This project is available under open source licensing terms. See the license file for details.
