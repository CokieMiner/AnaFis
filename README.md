# AnaFis - Physics Data Analysis

## Overview

AnaFis is a comprehensive physics data analysis application with a modern graphical interface designed for researchers, students, and professionals working with experimental data. The application provides powerful tools for curve fitting and uncertainty propagation with real-time visualization capabilities.

**Recent Updates (v10):**
- 🎨 **Plastik theme as default** - Modern, consistent UI across all components
- 🛠️ **Enhanced stability** - Fixed threading issues and memory leaks
- ⚡ **Performance optimizations** - Background loading and lazy module initialization
- 🧹 **Code quality improvements** - Comprehensive cleanup, removed unused code, type ignore comments
- 🔧 **Development tools** - Added Black, Vulture, and MyPy for code quality
- 🐍 **Python 3.13 support** - Updated to support latest Python versions

## Installation

**🐍 Python 3.8+ Required (Python 3.13 Recommended)**

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
- **Advanced Curve Fitting**: Multiple algorithms including Least Squares, Robust, Bootstrap, Bayesian, and ODR (Orthogonal Distance Regression)
- **Uncertainty Propagation**: Symbolic mathematics with automatic derivative calculation and LaTeX rendering
- **Multi-language Support**: Portuguese and English with runtime switching and complete localization
- **Real-time Visualization**: Interactive plots with residuals analysis and custom function overlay

### Enhanced Interface (v10)
- **Modern Theme System**: 29+ themes including Vista, Plastik, and ttkthemes package themes
- **Tabbed Interface**: Work with multiple analyses simultaneously with intelligent session management
- **Comprehensive Settings**: Advanced configuration dialog with theme selection, export preferences, and user customization
- **Robust Error Handling**: Comprehensive error recovery with user-friendly messages and logging

### Advanced Curve Fitting Tools
- **Multiple Fitting Algorithms**: 5 different methods for various data types and analysis needs
- **Preset Models**: Linear, exponential, power law, logarithmic, polynomial, and custom functions
- **Custom Function Builder**: Define mathematical models with symbolic parameter estimation
- **Parameter Management**: Automatic initial estimates with manual override capability
- **History System**: Track and restore previous analyses with full state preservation
- **Advanced Configuration**: Fine-tune fitting parameters, convergence criteria, and numerical methods

### Uncertainty Analysis Module
- **Symbolic Mathematics**: Full SymPy integration for complex uncertainty propagation
- **LaTeX Rendering**: Beautiful mathematical formula display with uncertainty expressions
- **Multi-variable Support**: Handle complex formulas with multiple interdependent variables
- **Automatic Derivatives**: Symbolic differentiation for precise uncertainty calculation
- **Formula Validation**: Real-time syntax checking and error highlighting

### Data Management & Export
- **Flexible Data Import**: CSV, TXT, Excel (.xlsx/.xls) with automatic format detection
- **Column Assignment**: Custom mapping of data columns with format override options
- **Multiple Export Formats**: PNG, JPG, SVG, PDF with configurable quality and resolution
- **Graph Customization**: Adjustable plot appearance, legends, and annotations
- **Data Preview**: Real-time data visualization before fitting

### Performance & Architecture
- **Lazy Loading System**: On-demand module loading for optimal startup performance
- **Background Processing**: Non-blocking operations with progress indicators
- **Memory Optimization**: Automatic cleanup and resource management
- **Threading Safety**: Proper GUI thread management with matplotlib integration
- **Session Management**: Intelligent tab limiting to prevent system overload

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
1. **Load Data**: Import CSV, TXT, or Excel files with automatic column detection
2. **Data Preview**: Review data in the integrated preview pane with formatting options
3. **Select Fitting Algorithm**: Choose from 5 different fitting methods:
   - **Least Squares**: Standard minimization for well-behaved data
   - **Robust**: Resistant to outliers and anomalous points
   - **Bootstrap**: Statistical confidence analysis with resampling
   - **Bayesian**: Probabilistic parameter estimation with priors
   - **ODR**: Orthogonal Distance Regression for errors in both variables
4. **Choose Model**: Select from preset models or define custom mathematical functions
5. **Parameter Estimation**: Automatic initial parameter calculation with manual refinement
6. **Advanced Configuration**: Fine-tune convergence criteria, iteration limits, and numerical precision
7. **Execute Fit**: Run the selected algorithm with real-time progress feedback
8. **Analyze Results**: View parameter values, uncertainties, goodness-of-fit metrics (χ², R²)
9. **Visualization**: Interactive plots with residuals, confidence bands, and custom overlays
10. **Export**: Save publication-quality graphs in PNG, JPG, SVG, or PDF formats

### Uncertainty Calculator Module
1. **Define Variables**: Specify variable names, values, and uncertainties
2. **Enter Formula**: Input mathematical expressions using symbolic notation
3. **Formula Validation**: Real-time syntax checking with error highlighting
4. **Automatic Calculation**: Symbolic differentiation and uncertainty propagation
5. **LaTeX Display**: Beautiful mathematical rendering of formulas and results
6. **Result Analysis**: View calculated values with propagated uncertainties
7. **Formula Export**: Copy LaTeX code for documentation and reports

### Settings & Customization
1. **Theme Selection**: Choose from 29+ available themes for personalized appearance
2. **Language Settings**: Switch between Portuguese and English interfaces
3. **Export Preferences**: Configure default formats and quality settings
4. **Performance Tuning**: Adjust session limits and memory management
5. **Advanced Options**: Fine-tune application behavior and preferences
2. **Add Variables**: Specify variables with their values and uncertainties
3. **Calculate**: The application will compute uncertainty propagation using partial derivatives
4. **View Results**: See the final result with calculated uncertainty
5. **Formula Visualization**: View LaTeX-rendered formulas for better understanding

## Supported Mathematical Functions

The application supports comprehensive mathematical functions through SymPy integration:

### Basic Operations
- Arithmetic: `+`, `-`, `*`, `/`, `**` (power), `//` (floor division), `%` (modulo)

### Trigonometric Functions
- `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`
- Hyperbolic: `sinh`, `cosh`, `tanh`, `asinh`, `acosh`, `atanh`

### Exponential & Logarithmic
- `exp`, `log` (natural log), `log10`, `log2`
- `sqrt`, `cbrt` (cube root)

### Special Functions
- `erf`, `erfc` (error functions)
- `gamma`, `factorial`
- `abs`, `sign`

### Constants
- `pi` (π), `e` (Euler's number)
- `oo` (infinity), `nan` (not a number)

### Advanced Features
- **Symbolic Differentiation**: Automatic derivative calculation for uncertainty propagation
- **Complex Expressions**: Nested functions and compound expressions
- **Parameter Estimation**: Symbolic solving for curve fitting parameters
- **LaTeX Rendering**: Beautiful mathematical notation display

### Preset Models (Curve Fitting)
- **Linear**: `a*x + b`
- **Exponential**: `a*exp(b*x)`, `a*exp(b*x) + c`
- **Power Law**: `a*x**b`, `a*x**b + c`
- **Logarithmic**: `a*log(x) + b`
- **Polynomial**: `a*x**2 + b*x + c`, higher orders available
- **Custom Functions**: Any mathematical expression with parameters

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

- **Operating System**: Windows 10+, macOS 10.15+, Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or newer (Python 3.13 recommended for optimal performance)
- **Memory**: Minimum 4GB RAM (8GB recommended for large datasets)
- **Storage**: At least 200MB free space for virtual environment and dependencies
- **Display**: 1024x768 minimum resolution (1920x1080 recommended)
- **Processor**: 64-bit processor with SSE2 support

### Recommended Hardware for Advanced Features
- **Large Datasets**: 16GB+ RAM for datasets >10,000 points
- **Complex Models**: Multi-core processor for bootstrap and Bayesian analysis
- **High-DPI Displays**: 4K monitors supported with proper scaling

## Dependencies

AnaFis requires the following Python packages (automatically installed with `requirements.txt`):

### Core Scientific Computing
```
numpy>=1.20.0          # Numerical computing and array operations
scipy>=1.7.0           # Scientific computing (optimization, statistics)
matplotlib>=3.3.0      # Plotting and visualization
sympy>=1.8.0           # Symbolic mathematics
pandas>=1.3.0          # Data manipulation and analysis
scikit-learn>=1.0.0    # Machine learning algorithms
```

### GUI and Theming
```
ttkthemes>=3.2.0       # Additional Tkinter themes
```

### Development and Quality Assurance
```
black>=22.0.0          # Code formatting
vulture>=2.0.0         # Unused code detection
mypy>=1.0.0            # Type checking
```

**Note:** `tkinter` comes pre-installed with Python and doesn't need to be installed separately.

## Code Quality

AnaFis maintains high code quality standards using automated tools:

- **Black**: Code formatting for consistent style
- **Vulture**: Detection of unused code and variables
- **MyPy**: Static type checking for Python
- **Comprehensive Testing**: Unit tests and integration tests

To run code quality checks:

```bash
# Format code with Black
black . --extend-exclude="venv|__pycache__|test"

# Check for unused code with Vulture
vulture . --exclude venv,__pycache__,test

# Type checking with MyPy
mypy . --ignore-missing-imports
```

### Development Workflow
AnaFis includes development tools in `requirements.txt` for easy setup:

```bash
# Install all dependencies including development tools
pip install -r requirements.txt

# Run quality checks
black . && vulture . && mypy .
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
