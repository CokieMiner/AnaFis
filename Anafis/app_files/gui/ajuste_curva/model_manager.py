"""Mathematical models and fitting functions for curve fitting GUI"""
import numpy as np
import sympy as sp
import re
import logging
from scipy.odr import ODR, Model, RealData, Output  # type: ignore[import-untyped]
from scipy.optimize import curve_fit  # type: ignore[import-untyped]
from typing import List, Tuple, Callable, Dict, Sequence, Any, Optional, cast # Added Optional, Any, cast, removed Union
from numpy.typing import NDArray

# Type alias for the numerical model functions created by lambdify
# It takes a sequence of parameter values (beta) and an array of x values,
# and returns an array of y values.
ModelCallable = Callable[[Sequence[float], NDArray[np.float64]], NDArray[np.float64]]

from app_files.gui.ajuste_curva.models import (
    ODRModelImplementation, 
    perform_least_squares_fit,
    perform_robust_fit,
    perform_weighted_least_squares_fit,
    perform_bootstrap_fit,
    perform_ridge_fit,
    perform_lasso_fit,
    perform_bayesian_fit
)

# Comprehensive function support for models (same as custom functions)
SUPPORTED_SYMPY_OBJECTS: Dict[str, Any] = {
    # Basic trigonometric functions
    'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan, 'cot': sp.cot, 'sec': sp.sec, 'csc': sp.csc,
    # Inverse trigonometric functions
    'asin': sp.asin, 'acos': sp.acos, 'atan': sp.atan, 'acot': sp.acot, 'asec': sp.asec, 'acsc': sp.acsc,
    'arcsin': sp.asin, 'arccos': sp.acos, 'arctan': sp.atan, 'arccot': sp.acot, 'arcsec': sp.asec, 'arccsc': sp.acsc,
    # Hyperbolic functions
    'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh, 'coth': sp.coth, 'sech': sp.sech, 'csch': sp.csch,
    # Inverse hyperbolic functions
    'asinh': sp.asinh, 'acosh': sp.acosh, 'atanh': sp.atanh, 'acoth': sp.acoth,
    'arcsinh': sp.asinh, 'arccosh': sp.acosh, 'arctanh': sp.atanh, 'arccoth': sp.acoth,    # Exponential and logarithmic functions
    'exp': sp.exp, 'log': sp.log, 'log10': lambda x: sp.log(x, 10), 'log2': lambda x: sp.log(x, 2), 'ln': sp.log, # type: ignore[reportUnknownLambdaType]
    'logb': lambda x, b: sp.log(x, b),  # logarithm with any base: logb(x, base)  # type: ignore[reportUnknownLambdaType]
    # Power and root functions
    'sqrt': sp.sqrt, 'cbrt': sp.cbrt, 'pow': sp.Pow, 'square': lambda x: x**2, # type: ignore[reportUnknownLambdaType]
    # Rounding and integer functions
    'abs': sp.Abs, 'sign': sp.sign, 'floor': sp.floor, 'ceil': sp.ceiling,
    # Special mathematical functions
    'gamma': sp.gamma, 'factorial': sp.factorial, 'erf': sp.erf, 'erfc': sp.erfc,
    # Step and discontinuous functions
    'heaviside': sp.Heaviside,
    # Piecewise functions
    'piecewise': sp.Piecewise,
    # Constants
    'pi': sp.pi, 'e': sp.E, 'inf': sp.oo, 'infinity': sp.oo
}


def preprocess_implicit_multiplication(expression: str) -> str:
    """
    Preprocess mathematical expressions to handle implicit multiplication.
    
    Converts patterns like:
    - 3x -> 3*x
    - 2sin(x) -> 2*sin(x)
    - (x+1)(x-1) -> (x+1)*(x-1)
    - x(x+1) -> x*(x+1)
    - 2(x+1) -> 2*(x+1)    
    Args:
        expression: The mathematical expression string
        
    Returns:
        The expression with explicit multiplication operators and SymPy function references
    """
    if not expression:
        return expression
    
    # Remove spaces for easier processing
    expr = expression.replace(' ', '')
    
    # Step 1: Replace ^ with ** for power operations
    expr = expr.replace('^', '**')
    
    # Step 2: Handle implicit multiplication before function substitution
    # This avoids conflicts with the sp. prefixes
    math_functions = list(SUPPORTED_SYMPY_OBJECTS.keys())
    
    # Pattern 1: Number followed by function name (e.g., 2sin, 3cos)
    # Sort functions by length (longest first) to handle overlapping names correctly
    sorted_functions = sorted(math_functions, key=len, reverse=True)
    for func in sorted_functions:
        expr = re.sub(rf'(\d)({func})\b', r'\1*\2', expr)
      
    # Pattern 2: Number followed by variable (e.g., 3x, 2y)
    # Look for digit followed by single letter that's not a function name
    function_pattern = r'\b(?:' + '|'.join(sorted_functions) + r')\b'
    expr = re.sub(rf'(\d)([a-zA-Z])(?!' + function_pattern + r')', r'\1*\2', expr)
    
    # Pattern 3: Single variable followed by opening parenthesis (e.g., x(, y()
    # But not function names - be very specific: single letter variables only
    expr = re.sub(r'(\b[a-zA-Z]\b)(?!' + function_pattern + r')\(', r'\1*(', expr)
    
    # Pattern 4: Closing parenthesis followed by opening parenthesis (e.g., )(
    expr = re.sub(r'\)\(', r')*(', expr)
    
    # Pattern 5: Closing parenthesis followed by letter or number (e.g., )x, )2
    expr = re.sub(r'\)([a-zA-Z0-9])', r')*\1', expr)
      
    # Pattern 6: Number followed by opening parenthesis (e.g., 2(, 3()
    expr = re.sub(r'(\d)\(', r'\1*(', expr)
    
    # Pattern 7: Function followed by function (e.g., sin(x)cos(x))
    # This handles cases like sin(x)cos(x) -> sin(x)*cos(x)
    expr = re.sub(rf'(\))((?:' + '|'.join(sorted_functions) + r')\b)', r'\1*\2', expr)
    
    return expr

class ModelManager:
    """Manages mathematical models for curve fitting"""
    model_cache: Dict[str, Tuple[ModelCallable, List[ModelCallable]]]
    preset_models: Dict[str, str]

    def __init__(self, language: str = 'pt') -> None:
        """Initialize model manager
        
        Args:
            language: Interface language (default: 'pt')
        """
        self.language = language
        self.model_cache = {}
          # Initialize preset models from translations
        from app_files.utils.constants import TRANSLATIONS
        try:
            preset_models_data = TRANSLATIONS[language]['models_presets']
            if isinstance(preset_models_data, dict):
                self.preset_models = preset_models_data
            else:                # Fallback to default if there's an issue
                logging.warning(f"Warning: preset_models is not a dict, got {type(preset_models_data)}: {preset_models_data}")
                self.preset_models = {"Linear: a*x + b": "a*x + b"}  # Simple fallback
        except (KeyError, TypeError) as e:
            logging.error(f"Error loading preset models: {e}")
            self.preset_models = {"Linear: a*x + b": "a*x + b"}  # Simple fallback
    
    def create_model(self, equation: str, parameters: List[sp.Symbol]) -> Tuple[ModelCallable, List[ModelCallable]]:
        """Create numerical model with caching
        
        Args:
            equation (str): The equation to model
            parameters (List[sp.Symbol]): List of parameters
            
        Returns:
            Tuple containing the model function and its derivatives
        """
        # Check cache first  
        cache_key: str = f"{equation}-{'-'.join(str(p) for p in parameters)}"
        if cache_key in self.model_cache:
            return self.model_cache[cache_key]
            
        x_sym: sp.Symbol = sp.Symbol('x')
        
        # Preprocess the equation to handle implicit multiplication
        preprocessed_equation = preprocess_implicit_multiplication(equation)
          # Use comprehensive function dictionary for parsing
        expr: sp.Expr = cast(sp.Expr, sp.sympify(preprocessed_equation, locals=SUPPORTED_SYMPY_OBJECTS))  # type: ignore[reportUnknownMemberType]
        
        derivadas_expr: List[sp.Expr] = [cast(sp.Expr, sp.diff(expr, p)) for p in parameters]  # type: ignore[reportUnknownMemberType]
        
        # Lambdify expects parameters as the first argument (a sequence), and x as the second.
        # The 'numpy' module ensures numpy functions are used for operations.
        modelo_numerico: ModelCallable = sp.lambdify((parameters, x_sym), expr, 'numpy') # type: ignore[assignment]
        derivadas_numericas: List[ModelCallable] = [sp.lambdify((parameters, x_sym), d, 'numpy') for d in derivadas_expr] # type: ignore[assignment]
        
        # Cache the result
        self.model_cache[cache_key] = (modelo_numerico, derivadas_numericas)
        return modelo_numerico, derivadas_numericas
    
    def extract_parameters(self, equation: str) -> List[sp.Symbol]:
        """Extract parameters from equation
        
        Args:
            equation (str): The equation to analyze
            
        Returns:
            List of parameters (symbols)        
        """
        # Preprocess equation to handle implicit multiplication
        preprocessed_equation = preprocess_implicit_multiplication(equation)
        
        if '=' in preprocessed_equation:
            # Assuming equation is in the form 'y = f(x, params)'
            # We are interested in the right-hand side for parameter extraction
            equation_rhs = preprocessed_equation.split('=', 1)[1].strip()
        else:
            equation_rhs = preprocessed_equation

        x_sym: sp.Symbol = sp.Symbol('x')
          # Use comprehensive function dictionary for parsing
        expr: sp.Expr = cast(sp.Expr, sp.sympify(equation_rhs, locals=SUPPORTED_SYMPY_OBJECTS))  # type: ignore[reportUnknownMemberType]
        
        # Identify free symbols in the expression
        # Sympy's free_symbols returns a Set of Basic objects, which can include Symbols.
        # We cast to Set[sp.Symbol] assuming only symbols are relevant as parameters here.
        free_symbols: set[sp.Symbol] = cast(set[sp.Symbol], expr.free_symbols)
        
        # Parameters are free symbols excluding 'x'
        # Sort parameters by name for consistent order
        parameter_symbols: List[sp.Symbol] = sorted(
            list(free_symbols - {x_sym}), 
            key=lambda s: s.name
        )
        return parameter_symbols
    def perform_odr_fit(self, 
                       x: NDArray[np.float64], 
                       y: NDArray[np.float64], 
                       sigma_x: Optional[NDArray[np.float64]], 
                       sigma_y: Optional[NDArray[np.float64]],
                       model_func: ModelCallable,
                       derivs: List[ModelCallable],
                       initial_params: List[float],
                       max_iter: int) -> Tuple[Output, float, float]:
        """Perform ODR fitting
        
        Args:
            x, y: Data arrays (numpy.ndarray)
            sigma_x, sigma_y: Standard deviations for x and y (numpy.ndarray or None)
            model_func: Model function (callable)
            derivs: List of derivative functions (list of callables)
            initial_params: Initial parameter estimates (list of floats)
            max_iter: Maximum number of iterations (int)
            
        Returns:
            Tuple containing (ODR result object, chi-squared, R-squared)
        """
        
        # Create ODR model using the custom implementation
        # The type ignore is kept because ODRModelImplementation might have a more generic internal signature
        # that Pylance tries to match strictly, while ModelCallable is specific to lambdify's output.
        modelo_odr = Model(ODRModelImplementation(model_func, derivs)) # type: ignore[arg-type]
        
        # Prepare uncertainties for ODR
        # Handle cases where only Y uncertainties are provided (sigma_x is None or zeros)
        # ODR works fine with only Y uncertainties, but we need to handle sigma_x properly
        odr_sigma_x = None
        odr_sigma_y = None
        
        # Handle X uncertainties
        if sigma_x is not None and len(sigma_x) > 0 and not np.allclose(sigma_x, 0):
            odr_sigma_x = sigma_x
        
        # Handle Y uncertainties 
        if sigma_y is not None and len(sigma_y) > 0 and not np.allclose(sigma_y, 0):
            odr_sigma_y = sigma_y
        
        # Prepare data for ODR
        # RealData handles None for sx or sy by treating them as unweighted
        dados = RealData(x, y, sx=odr_sigma_x, sy=odr_sigma_y)
          # Initialize and run ODR
        odr = ODR(dados, modelo_odr, beta0=initial_params, maxit=max_iter)
        
        # Set fitting type to handle the case appropriately
        # For ODR, we don't need to change job parameters as it handles missing uncertainties automatically
        # The RealData object with None values handles this correctly
        
        resultado: Output = odr.run()
        
        # Calculate statistics
        # Ignore type checking for the beta attribute since Pylance can't infer its type
        # pragma: Pylance gets confused about the beta attribute type, but we know it's a sequence of floats
        y_pred: NDArray[np.float64] = model_func(  # type: ignore[arg-type]
            resultado.beta,  # type: ignore[attr-defined]
            x
        )
        
        # Chi-squared calculation - use the actual uncertainties that were used in fitting
        chi2_total: float = np.nan # Default to NaN if no uncertainties available
        if odr_sigma_y is not None and np.all(odr_sigma_y > 0):
            chi2_total = float(np.sum(((y - y_pred) / odr_sigma_y) ** 2)) # Cast to float
        elif odr_sigma_y is None:
            # No Y uncertainties - use unweighted chi-squared (essentially sum of squared residuals)
            chi2_total = float(np.sum((y - y_pred) ** 2)) # Cast to float
        
        # R-squared calculation
        # Avoid division by zero if all y values are the same
        ss_tot: float = float(np.sum((y - np.mean(y)) ** 2)) # Cast to float
        ss_res: float = float(np.sum((y - y_pred) ** 2)) # Cast to float
        
        r2: float = np.nan # Default to NaN
        if ss_tot > 0:
            r2 = 1 - (ss_res / ss_tot)
        else:
            if ss_res == 0: # Perfect fit to a constant
                r2 = 1.0
            # else, ss_tot is 0 and ss_res is > 0, which shouldn't happen if y_pred is based on y.
            # If y is constant and model predicts it perfectly, r2 is 1.
            # If y is constant and model does not predict it perfectly, ss_tot is 0, r2 is undefined or -inf.
            # np.nan is a safe bet here.

        return resultado, chi2_total, r2  # type: ignore[reportPossiblyUnboundVariable]    
    def perform_least_squares_fit(self, 
                                 x: NDArray[np.float64], 
                                 y: NDArray[np.float64], 
                                 sigma_y: Optional[NDArray[np.float64]],
                                 model_func: ModelCallable,
                                 initial_params: List[float],
                                 max_iter: int) -> Tuple[Any, float, float]:
        """Perform Least Squares fitting using the models module implementation"""
        return perform_least_squares_fit(x, y, sigma_y, model_func, initial_params, max_iter)
    
    def perform_robust_fit(self,
                          x: NDArray[np.float64], 
                          y: NDArray[np.float64], 
                          model_func: ModelCallable,
                          initial_params: List[float],
                          method: str = 'huber',
                          max_iter: int = 1000) -> Tuple[Any, float, float]:
        """Perform robust fitting using RANSAC or Huber regression"""
        return perform_robust_fit(x, y, model_func, initial_params, method, max_iter)
    
    def perform_weighted_least_squares_fit(self,
                                          x: NDArray[np.float64], 
                                          y: NDArray[np.float64], 
                                          weights: NDArray[np.float64],
                                          model_func: ModelCallable,
                                          initial_params: List[float],
                                          max_iter: int) -> Tuple[Any, float, float]:
        """Perform Weighted Least Squares fitting with custom weights"""
        return perform_weighted_least_squares_fit(x, y, weights, model_func, initial_params, max_iter)
    
    def perform_bootstrap_fit(self,
                             x: NDArray[np.float64], 
                             y: NDArray[np.float64], 
                             sigma_y: Optional[NDArray[np.float64]],
                             model_func: ModelCallable,
                             initial_params: List[float],
                             max_iter: int,
                             n_bootstrap: int = 1000) -> Tuple[Any, float, float]:
        """Perform Bootstrap fitting for uncertainty estimation"""
        return perform_bootstrap_fit(x, y, sigma_y, model_func, initial_params, max_iter, n_bootstrap)
    
    def perform_ridge_fit(self,
                         x: NDArray[np.float64], 
                         y: NDArray[np.float64], 
                         model_func: ModelCallable,
                         initial_params: List[float],
                         alpha: float = 1.0,
                         max_iter: int = 1000) -> Tuple[Any, float, float]:
        """Perform Ridge regression (L2 regularization)"""
        return perform_ridge_fit(x, y, model_func, initial_params, alpha, max_iter)
    
    def perform_lasso_fit(self,
                         x: NDArray[np.float64], 
                         y: NDArray[np.float64], 
                         model_func: ModelCallable,
                         initial_params: List[float],
                         alpha: float = 1.0,
                         max_iter: int = 1000) -> Tuple[Any, float, float]:
        """Perform Lasso regression (L1 regularization)"""
        return perform_lasso_fit(x, y, model_func, initial_params, alpha, max_iter)
    
    def perform_bayesian_fit(self,
                            x: NDArray[np.float64], 
                            y: NDArray[np.float64], 
                            sigma_y: Optional[NDArray[np.float64]],
                            model_func: ModelCallable,
                            initial_params: List[float],
                            max_iter: int = 1000,
                            n_samples: int = 1000) -> Tuple[Any, float, float]:
        """Perform Bayesian regression with uncertainty quantification"""
        return perform_bayesian_fit(x, y, sigma_y, model_func, initial_params, max_iter, n_samples)
    
    def get_supported_functions_help(self) -> str:
        """Get help text for supported mathematical functions in models
        
        Returns:
            Formatted help text describing all supported functions
        """
        from app_files.utils.constants import TRANSLATIONS
        # Try to get current language from parent, fallback to 'pt'
        try:
            language = getattr(self, 'language', 'pt')
        except:
            language = 'pt'
        
        return TRANSLATIONS[language]['help_models_content']
    
    def show_model_help(self, parent_window) -> None:  # type: ignore[reportMissingParameterType]
        """Show help dialog for model functions
        
        Args:
            parent_window: Parent window for the dialog
        """
        import tkinter as tk
        from tkinter import ttk
        from app_files.utils.constants import TRANSLATIONS
        
        # Try to get current language from parent, fallback to 'pt'
        try:            language = getattr(self, 'language', 'pt')
        except:
            language = 'pt'
        
        help_window = tk.Toplevel(parent_window)  # type: ignore[reportUnknownArgumentType]
        help_window.title(TRANSLATIONS[language]['help_models_title'])
        help_window.geometry("700x600")
        help_window.resizable(True, True)
        
        # Apply theme-adaptive background
        from app_files.utils.theme_manager import theme_manager
        help_window.configure(bg=theme_manager.get_adaptive_color('background'))
        
        # Make window modal
        help_window.transient(parent_window)  # type: ignore[reportUnknownArgumentType]
        help_window.grab_set()
        
        # Create scrollable text widget
        frame = ttk.Frame(help_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(
            frame, 
            wrap=tk.WORD, 
            font=('Consolas', 10),
            bg=theme_manager.get_adaptive_color('background'),
            fg=theme_manager.get_adaptive_color('foreground')
        )
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)  # type: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Insert help text
        help_text = self.get_supported_functions_help()
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)  # Make read-only
        
        # Add close button
        button_frame = ttk.Frame(help_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        close_button = ttk.Button(button_frame, text=TRANSLATIONS[language]['close'], command=help_window.destroy)
        close_button.pack(side=tk.RIGHT)
        
        # Center the window
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (help_window.winfo_width() // 2)
        y = (help_window.winfo_screenheight() // 2) - (help_window.winfo_height() // 2)
        help_window.geometry(f"+{x}+{y}")
          # Focus on the help window
        help_window.focus_set()

    def set_language(self, language: str) -> None:
        """Update language and reload preset models
        
        Args:
            language: New language code ('pt' or 'en')
        """
        self.language = language
        from app_files.utils.constants import TRANSLATIONS
        try:
            preset_models_data = TRANSLATIONS[language]['models_presets']
            if isinstance(preset_models_data, dict):                self.preset_models = preset_models_data
            else:
                logging.warning(f"Warning: models_presets is not a dict, got {type(preset_models_data)}: {preset_models_data}")
                self.preset_models = {"Linear: a*x + b": "a*x + b"}  # Simple fallback
        except (KeyError, TypeError) as e:
            logging.error(f"Error loading preset models: {e}")
            self.preset_models = {"Linear: a*x + b": "a*x + b"}  # Simple fallback
