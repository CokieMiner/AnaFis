"""Mathematical models and fitting functions for curve fitting GUI"""
import numpy as np
import sympy as sp
from scipy.odr import ODR, Model, RealData, Output
from typing import List, Tuple, Callable, Dict, Sequence, Any, Optional, cast # Added Optional, Any, cast, removed Union
from numpy.typing import NDArray

# Type alias for the numerical model functions created by lambdify
# It takes a sequence of parameter values (beta) and an array of x values,
# and returns an array of y values.
ModelCallable = Callable[[Sequence[float], NDArray[np.float64]], NDArray[np.float64]]

from app_files.gui.ajuste_curva.models import ODRModelImplementation

class ModelManager:
    """Manages mathematical models for curve fitting"""
    model_cache: Dict[str, Tuple[ModelCallable, List[ModelCallable]]]
    preset_models: Dict[str, str]

    def __init__(self) -> None:
        """Initialize model manager"""
        self.model_cache = {}
        
        # Define preset models
        self.preset_models = {
            "Linear: a*x + b": "a*x + b",
            "Quadrático: a*x² + b*x + c": "a*x**2 + b*x + c", 
            "Exponencial: a*exp(b*x)": "a*exp(b*x)",
            "Logarítmico: a*log(x) + b": "a*log(x) + b",
            "Potência: a*x^b": "a*x**b",
            "Senoidal: a*sin(b*x + c) + d": "a*sin(b*x + c) + d"
        }
    
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
        # Ensure common functions are recognized by sympy, e.g., exp, log, sin
        local_dict: Dict[str, Any] = { # Changed type hint
            "exp": sp.exp,
            "log": sp.log,
            "sin": sp.sin,
            "cos": sp.cos,
            "tan": sp.tan,
            "pi": sp.pi
        }
        expr: sp.Expr = cast(sp.Expr, sp.sympify(equation, locals=local_dict)) # type: ignore[reportUnknownMemberType]
        
        derivadas_expr: List[sp.Expr] = [cast(sp.Expr, sp.diff(expr, p)) for p in parameters] # type: ignore[reportUnknownMemberType] # Added cast for sp.diff
        
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
            List of parameters (symbols)        """
        # Replace ^ with ** for SymPy compatibility
        equation = equation.replace('^', '**')
        if '=' in equation:
            # Assuming equation is in the form 'y = f(x, params)'
            # We are interested in the right-hand side for parameter extraction
            equation_rhs = equation.split('=', 1)[1].strip()
        else:
            equation_rhs = equation

        x_sym: sp.Symbol = sp.Symbol('x')
        # Provide common mathematical functions to sympify's scope
        local_dict: Dict[str, Any] = { # Changed type hint
            "exp": sp.exp,
            "log": sp.log,
            "sin": sp.sin,
            "cos": sp.cos,
            "tan": sp.tan,
            "pi": sp.pi,
            # Add other functions if they might appear in user equations
        }
        expr: sp.Expr = cast(sp.Expr, sp.sympify(equation_rhs, locals=local_dict)) # type: ignore[reportUnknownMemberType]
        
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
        
        # Prepare data for ODR
        # RealData handles None for sx or sy by treating them as unweighted
        dados = RealData(x, y, sx=sigma_x, sy=sigma_y)
        
        # Initialize and run ODR
        odr = ODR(dados, modelo_odr, beta0=initial_params, maxit=max_iter)
        resultado: Output = odr.run()
        
        # Calculate statistics
        # Cast resultado.beta (NDArray[np.float64]) to Sequence[float] if Pylance complains,
        # though NDArray should be a Sequence.
        y_pred: NDArray[np.float64] = model_func(cast(Sequence[float], resultado.beta), x)
        
        # Chi-squared calculation (ensure sigma_y is not None and has no zeros for division)
        chi2_total: float = np.nan # Default to NaN if sigma_y is problematic
        if sigma_y is not None and np.all(sigma_y > 0):
            chi2_total = float(np.sum(((y - y_pred) / sigma_y) ** 2)) # Cast to float
        
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

        return resultado, chi2_total, r2
