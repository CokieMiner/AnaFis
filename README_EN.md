# AnaFis - Physics Data Analysis

## Installation

AnaFis requires Python 3.8 or newer. It is recommended to use a virtual environment.

To install all required dependencies, run:
```bash
pip install numpy sympy scipy matplotlib pandas
```

## Main Features
- Curve fitting with user-defined functions
- Uncertainty propagation for arbitrary formulas
- Real-time fit visualization
- Export graphs in various formats

## Data File Format
Tab-separated .csv or .txt file with columns:

x   σx  y   σy

Example:
1.0 0.1 2.0 0.2
2.0 0.1 4.1 0.2

Where:
- x: Independent variable
- σx: Uncertainty in x
- y: Dependent variable
- σy: Uncertainty in y

## Troubleshooting
- If fit does not converge: try different initial values or check data quality.
- For large errors: review uncertainties and model choice.
- For missing tkinter: install it via your OS package manager or ensure it is included in your Python installation.