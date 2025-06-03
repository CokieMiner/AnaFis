"""Mathematical models and fitting functions for curve fitting GUI"""
import numpy as np
import sympy as sp
from scipy.odr import ODR, Model, RealData
from typing import List, Tuple, Callable, Any
from app_files.gui.ajuste_curva.models import ODRModelImplementation

class ModelManager:
    """Manages mathematical models for curve fitting"""
    
    def __init__(self):
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
    
    def create_model(self, equation: str, parameters: List[sp.Symbol]) -> Tuple[Callable, List[Callable]]:
        """Create numerical model with caching
        
        Args:
            equation (str): The equation to model
            parameters (List[sp.Symbol]): List of parameters
            
        Returns:
            Tuple containing the model function and its derivatives
        """
        # Check cache first  
        cache_key = f"{equation}-{'-'.join(str(p) for p in parameters)}"
        if cache_key in self.model_cache:
            return self.model_cache[cache_key]
            
        x = sp.Symbol('x')
        expr = sp.sympify(equation)
        
        derivadas = [sp.diff(expr, p) for p in parameters]
        
        modelo_numerico = sp.lambdify((parameters, x), expr, 'numpy')
        derivadas_numericas = [sp.lambdify((parameters, x), d, 'numpy') for d in derivadas]
        
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
        equation = equation.replace('^', '**')
        if '=' in equation:
            equation = equation.split('=')[1].strip()

        x_sym = sp.Symbol('x')
        expr = sp.sympify(equation)
        return sorted(list(expr.free_symbols - {x_sym}), key=lambda s: s.name)
    
    def perform_odr_fit(self, 
                       x: np.ndarray, 
                       y: np.ndarray, 
                       sigma_x: np.ndarray, 
                       sigma_y: np.ndarray,
                       model_func: Callable,
                       derivs: List[Callable],
                       initial_params: List[float],
                       max_iter: int) -> Tuple[Any, float, float]:
        """Perform ODR fitting
        
        Args:
            x, y, sigma_x, sigma_y: Data arrays
            model_func: Model function
            derivs: List of derivative functions
            initial_params: Initial parameter estimates
            max_iter: Maximum number of iterations
            
        Returns:
            Tuple containing (ODR result, chi-squared, R-squared)
        """
        
        
        # Create ODR model
        modelo_odr = Model(ODRModelImplementation(model_func, derivs))
        
        # Execute ODR
        dados = RealData(x, y, sx=sigma_x, sy=sigma_y)
        odr = ODR(dados, modelo_odr, beta0=initial_params, maxit=max_iter)
        resultado = odr.run()
        
        # Calculate statistics
        y_pred = model_func(resultado.beta, x)
        chi2_total = np.sum(((y - y_pred) / sigma_y) ** 2)
        r2 = 1 - np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)
        
        return resultado, chi2_total, r2
