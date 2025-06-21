# AnaFis - Physics Data Analysis

## Overview

AnaFis is a comprehensive physics data analysis application with a modern graphical interface designed for researchers, students, and professionals working with experimental data. The application provides powerful tools for curve fitting and uncertainty propagation with real-time visualization capabilities.

**Recent Updates (v10):**
- 🎨 **Vista theme as default** - Modern, consistent UI across all components
- 🛠️ **Enhanced stability** - Fixed threading issues and memory leaks
- ⚡ **Performance optimizations** - Background loading
- 🧹 **Code quality improvements** - Comprehensive cleanup, better error handling

## Installation

**🐍 Python 3.8+ Required**

### Virtual Environment Installation (Recommended)

AnaFis should be installed in a virtual environment to avoid dependency conflicts and ensure a clean installation.

#### Step 1: Create and Activate Virtual Environment

**Windows:**
```cmd
# Create virtual environment
python -m venv anafis-env

# Activate virtual environment
anafis-env\Scripts\activate
```

**macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv anafis-env

# Activate virtual environment
source anafis-env/bin/activate
```

#### Step 2: Install Dependencies

With the virtual environment activated:

```bash
# Upgrade pip first
pip install --upgrade pip

# Install AnaFis dependencies
pip install -r requirements.txt
```

#### Step 3: Run AnaFis

```bash
python run.py
```

### Alternative: Development Installation

For developers who want to modify the code:

```bash
# After activating virtual environment
pip install -e .
```

**Note:** `tkinter` comes pre-installed with Python and doesn't need to be installed separately.

## Running the Application

### From Virtual Environment

After activating your virtual environment:

```bash
python run.py
```

The application will show a splash screen with startup progress and timing information, then open the main interface.

### Startup Performance

AnaFis features optimized startup with:
- **Background module loading** for faster initial display
- **Timing metrics** displayed during startup
- **Resource optimization** for reduced memory usage

## Main Features

### Core Functionality
- **Curve Fitting**: Advanced curve fitting with ODR (Orthogonal Distance Regression)
- **Uncertainty Propagation**: Calculate uncertainty propagation using symbolic mathematics
- **Multi-language Support**: Portuguese and English with runtime switching
- **Real-time Visualization**: Interactive plots with residuals analysis

### Enhanced Interface (v1.0)
- **Vista Theme**: Modern, consistent theme across all components
- **Tabbed Interface**: Work with multiple analyses simultaneously  
- **Settings System**: Comprehensive preferences management
- **Error Handling**: Robust error recovery and user feedback

### Advanced Tools
- **Custom Functions**: Define mathematical models with parameter estimation
- **History Management**: Track and restore previous analyses
- **Data Export**: Multiple formats (PNG, PDF, SVG) with configurable options
- **Plugin System**: Extensible architecture for custom functionality

### Performance Features
- **Background Loading**: Non-blocking module initialization
- **Memory Management**: Automatic cleanup and resource optimization
- **Threading Safety**: Proper matplotlib integration without GUI warnings
- **Session Limiting**: Prevents system overload from too many restored tabs

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

### Virtual Environment Issues
- **Environment not found**: Ensure you created the environment with `python -m venv anafis-env`
- **Activation fails**: Check you're using the correct activation command for your OS
- **Dependencies missing**: Verify virtual environment is activated before installing requirements

### Common Runtime Issues
- **Fit does not converge**: Try different initial parameter values or verify data quality
- **Large fitting errors**: Review uncertainty values and model appropriateness  
- **Startup errors**: Check all dependencies are installed in the virtual environment

### Performance Tips
- For large datasets, consider data preprocessing or sampling
- Complex custom functions may require longer computation time
- The application automatically limits session restoration to 10 tabs for optimal performance
- Use the timing information displayed at startup to monitor performance

## Virtual Environment Management

### Deactivating Environment
```bash
deactivate
```

### Updating Dependencies
```bash
# With virtual environment activated
pip install --upgrade -r requirements.txt
```

### Removing Environment
```bash
# Deactivate first, then remove folder
deactivate
rm -rf anafis-env  # Linux/macOS
rmdir /s anafis-env  # Windows
```

## Building Executable (Optional)

If you want to create a standalone executable after setting up the virtual environment:

### Prerequisites
```bash
# With virtual environment activated
pip install pyinstaller
```

### Build Process
1. Use the provided build scripts:
   ```cmd
   # Windows Batch
   build_exe.bat
   
   # PowerShell
   .\build_exe.ps1
   ```

2. Or build manually:
   ```bash
   python -m PyInstaller --clean AnaFis.spec
   ```

3. The executable will be created in `dist\AnaFis\AnaFis.exe`

### Build Configuration
- The `AnaFis.spec` file contains all build settings
- Includes all necessary dependencies and data files
- Optimized for size and performance
- Creates a portable distribution

**Note:** Building executables is optional. The recommended approach is to use the virtual environment installation.

## System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.8 or newer
- **Memory**: Minimum 4GB RAM recommended
- **Storage**: At least 200MB free space for virtual environment and dependencies
- **Display**: 1024x768 minimum resolution recommended

## Dependencies

AnaFis requires the following Python packages (automatically installed with `requirements.txt`):

```
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.5.0
sympy>=1.8.0
pandas>=1.3.0
```


## Roadmap

### Next Release (v11)
- **Excel-like Tables**: Spreadsheet-style data entry and editing capabilities  
- **Enhanced Data Import**: Improved file format support and validation
- **Advanced Export Options**: More customization for data and graph export

### Future (v12)
- **Equation Solving Module**: Symbolic and numerical equation solver
- **3D Visualization**: Advanced plotting capabilities
- **Plugin System**: Full extensibility framework
- **Advanced Data Analysis**: Statistical tools and enhanced mathematical functions

See [TODO.md](TODO.md) for the complete development roadmap and detailed feature planning.

## Contributing

AnaFis is open for contributions. Please feel free to submit issues, feature requests, or pull requests to improve the application.

## License

This project is available under open source licensing terms. See the license file for details.
