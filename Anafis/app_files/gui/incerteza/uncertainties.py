"""
Module for uncertainty calculations and propagation.

This module provides the UncertaintyCalculator class which handles
mathematical uncertainty calculations and generates LaTeX formulas
for uncertainty propagation.
"""

import math
import re
from typing import Dict, List, Tuple, Any

import sympy as sp

from app_files.utils.constants import TRANSLATIONS


class UncertaintyCalculator:
    """
    Handles uncertainty calculations and propagation.
      This class provides static methods for calculating uncertainty propagation
    in mathematical formulas and generating LaTeX representations of uncertainty
    formulas.
    """

    @staticmethod
    def _get_error_messages() -> Dict[str, Dict[str, str]]:
        """Get error messages for different languages."""
        return {
            'invalid_formula': {
                'pt': TRANSLATIONS['pt']['invalid_formula'],
                'en': TRANSLATIONS['en']['invalid_formula']
            }
        }

    @staticmethod
    def _get_translations() -> Dict[str, Dict[str, str]]:
        """Get translation mappings for mathematical functions."""
        # For now, this only handles the sine function which has different naming in Portuguese
        return {
            'pt': {
                'sin': TRANSLATIONS['pt'].get('sin', 'sen')
            },
            'en': {
                'sin': TRANSLATIONS['en'].get('sin', 'sin')
            }
        }

    @staticmethod
    def _get_math_functions() -> Dict[str, Any]:
        """Get dictionary of all available mathematical functions and constants."""
        return {
            # Trigonometric functions
            'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
            'cot': sp.cot, 'sec': sp.sec, 'csc': sp.csc,
            'asin': sp.asin, 'arcsin': sp.asin,
            'acos': sp.acos, 'arccos': sp.acos,
            'atan': sp.atan, 'arctan': sp.atan,
            'acot': sp.acot, 'arccot': sp.acot,
            'asec': sp.asec, 'arcsec': sp.asec,
            'acsc': sp.acsc, 'arccsc': sp.acsc,
            'atan2': sp.atan2,
            
            # Hyperbolic functions
            'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh,
            'coth': sp.coth, 'sech': sp.sech, 'csch': sp.csch,
            'asinh': sp.asinh, 'arcsinh': sp.asinh,
            'acosh': sp.acosh, 'arccosh': sp.acosh,
            'atanh': sp.atanh, 'arctanh': sp.atanh,
            'acoth': sp.acoth, 'arccoth': sp.acoth,
            'asech': sp.asech, 'arcsech': sp.asech,
            'acsch': sp.acsch, 'arccsch': sp.acsch,
            
            # Exponential and logarithmic functions
            'exp': sp.exp,
            'log': sp.log, 'ln': sp.ln,
            
            # Powers and roots
            'sqrt': sp.sqrt, 'cbrt': lambda x: x**(sp.Rational(1, 3)),  # type: ignore
            'root': lambda x, n: x**(sp.Rational(1, n)),  # type: ignore
            
            # Special functions
            'abs': sp.Abs, 'Abs': sp.Abs,
            'sign': sp.sign, 'sgn': sp.sign,
            'floor': sp.floor, 'ceiling': sp.ceiling, 'ceil': sp.ceiling,
            'frac': lambda x: x - sp.floor(x), # type: ignore
            'Min': sp.Min, 'min': sp.Min,
            'Max': sp.Max, 'max': sp.Max,
            
            # Continuous combinatorial functions
            'binomial': sp.binomial,
            
            # Constants
            # Mathematical constants
            'pi': sp.pi, 'e': sp.E, 'E': sp.E,
            'inf': sp.oo, 'infinity': sp.oo, 'oo': sp.oo,
            'nan': sp.nan,
            'GR': sp.GoldenRatio,  # Golden Ratio (simplified from GoldenRatio)
            'EG': sp.EulerGamma,   # Euler-Mascheroni constant (simplified from EulerGamma)
            'Cat': sp.Catalan,     # Catalan constant (simplified from Catalan)
            
            # Additional mathematical constants
            'I': sp.I, 'j': sp.I,  # Imaginary unit
            'zoo': sp.zoo,  # Complex infinity
            
            # Additional constants
            'TC': sp.S.TribonacciConstant,  # Tribonacci constant (simplified from TribonacciConstant)
            'Pi': sp.pi,  # Alternative name for pi
        }
        

    @staticmethod
    def _calculate_formula_value(
        expr: Any, # Reverted from sp.Expr due to stub issues
        variables_values: Dict[str, float],
        math_functions: Dict[str, Any]
    ) -> float:
        """Calculate the final value of the formula."""
        expr_substituted = expr.subs(variables_values) # type: ignore
        evaluated_expr = expr_substituted.subs(math_functions) # type: ignore
        return float(sp.N(evaluated_expr)) # type: ignore

    @staticmethod
    def _calculate_uncertainty(
        expr: Any, # Reverted from sp.Expr
        variaveis: Dict[str, Tuple[float, float]],
        variables_values: Dict[str, float]
    ) -> float:
        """Calculate the total uncertainty using error propagation.
        
        Uses the standard uncertainty propagation formula:
        ∂_f² = ∂ (∂f/∂x_i)² * ∂_x_i²
        where f is the function, x_i are the variables, and ∂_x_i are their uncertainties.
        """
        incerteza_total = 0.0
        for var, (_, sigma) in variaveis.items():
            symbol_var = sp.Symbol(var)
            derivada = sp.diff(expr, symbol_var) # type: ignore
            derivada_substituted = derivada.subs(variables_values) # type: ignore
            derivada_num: float = float(sp.N(derivada_substituted)) # type: ignore
            incerteza_total += (derivada_num * sigma) ** 2
        return math.sqrt(incerteza_total)

    @staticmethod
    def calcular_incerteza(
        formula: str,
        variaveis: Dict[str, Tuple[float, float]],
        language: str = 'pt'
    ) -> Tuple[float, float]:
        """
        Calculate uncertainty propagation for a given formula.

        Args:
            formula: Mathematical formula as string
            variaveis: Dictionary mapping variable names to (value, uncertainty) tuples
            language: Language for error messages ('pt' or 'en')

        Returns:
            Tuple containing (final_value, total_uncertainty)

        Raises:
            ValueError: If formula processing fails
        """
        error_messages = UncertaintyCalculator._get_error_messages()
        translations = UncertaintyCalculator._get_translations()

        formula = formula.replace(translations['pt'].get('sin', 'sin'), translations[language].get('sin', 'sin'))
        
        # Preprocess formula to handle implicit multiplication
        formula = UncertaintyCalculator.preprocess_formula(formula)

        try:
            # Calculate value using sympy for safer evaluation
            expr = sp.sympify(formula) # type: ignore
            variables_values = {k: valor for k, (valor, _) in variaveis.items()}
            math_functions = UncertaintyCalculator._get_math_functions()

            # Calculate final value and uncertainty using helper methods
            valor_final = UncertaintyCalculator._calculate_formula_value(
                expr, variables_values, math_functions # No ignore needed here if expr is Any
            )
            incerteza_total = UncertaintyCalculator._calculate_uncertainty(
                expr, variaveis, variables_values # No ignore needed here if expr is Any
            )
            return valor_final, incerteza_total
        except sp.SympifyError as e: # type: ignore
            raise ValueError(
                error_messages['invalid_formula'][language].format(error=f"SympyError: {str(e)}")
            ) from e
        except (TypeError, AttributeError) as e: # Errors during sympy evaluation
            raise ValueError(
                error_messages['invalid_formula'][language].format(error=f"EvaluationError: {str(e)}")
            ) from e
        except Exception as e: # Catch any other unexpected errors
            # It's good practice to log unexpected errors if a logging system is in place
            # logging.error(f"Unexpected error in calcular_incerteza: {e}", exc_info=True)
            raise ValueError(
                error_messages['invalid_formula'][language].format(error=f"Unexpected: {str(e)}")
            ) from e

    @staticmethod
    def gerar_formula_incerteza(formula: str, variaveis: List[str], language: str = 'pt') -> str:
        """Generate LaTeX formula for uncertainty"""
        error_messages = UncertaintyCalculator._get_error_messages()
        translations = UncertaintyCalculator._get_translations()
        
        # Normalize formula for the target language
        formula = formula.replace(translations['pt'].get('sin', 'sin'), translations[language].get('sin', 'sin'))
        
        # Preprocess formula to handle implicit multiplication
        formula = UncertaintyCalculator.preprocess_formula(formula)

        try:
            simbolos = {var.strip(): sp.Symbol(var.strip()) for var in variaveis}
            if not all(simbolos.keys()): # Check for empty variable names after stripping
                raise ValueError("Variable names cannot be empty.")

            expr = sp.sympify(formula, locals=simbolos) # type: ignore

            termos: List[str] = []
            for var_name_orig in variaveis:
                var_name_stripped = var_name_orig.strip()
                if not var_name_stripped: # Should be caught by the check above, but good for safety
                    continue 
                
                # Ensure the symbol used for differentiation matches the one in 'simbolos'
                symbol_to_diff = simbolos.get(var_name_stripped)
                if symbol_to_diff is None:
                    # This case should ideally not happen if variaveis list is consistent with formula
                    # Or if variables in formula are a subset of 'variaveis' list
                    raise ValueError(f"Variable '{var_name_stripped}' not found in symbol list for differentiation.")

                derivada = sp.diff(expr, symbol_to_diff) # type: ignore
                latex_derivada: str = sp.latex(derivada) # type: ignore
                # Use original var_name_orig for display if needed, or stripped for consistency
                termos.append(f"(\\\\\\\\sigma_{{{var_name_stripped}}} \\\\\\\\cdot {latex_derivada})^2")

            return "\\\\\\\\sigma_{\\\\\\\\text{total}} = \\\\\\\\sqrt{" + " + ".join(termos) + "}"
        except sp.SympifyError as e: # type: ignore
            raise ValueError(
                error_messages['invalid_formula'][language].format(error=f"SympyError: {str(e)}")
            ) from e
        except (TypeError, AttributeError) as e: # Errors during sympy processing
            raise ValueError(
                error_messages['invalid_formula'][language].format(error=f"ProcessingError: {str(e)}")
            ) from e
        except ValueError as e: # Catch our own raised ValueError (e.g. empty variable name)
             raise ValueError(
                error_messages['invalid_formula'][language].format(error=str(e))
            ) from e
        except Exception as e: # Catch any other unexpected errors
            # logging.error(f"Unexpected error in gerar_formula_incerteza: {e}", exc_info=True)
            raise ValueError(
                error_messages['invalid_formula'][language].format(error=f"Unexpected: {str(e)}")
            ) from e

    @staticmethod
    def preprocess_formula(formula: str) -> str:
        """Preprocess the formula to handle implicit multiplication and other adjustments."""
        # Handle different forms of implicit multiplication
        # Replace number followed by variable: 3x -> 3*x
        formula = re.sub(r'(\d+)([a-zA-Z_])', r'\1*\2', formula)
        
        # Replace number followed by parenthesis: 3(x+y) -> 3*(x+y)
        formula = re.sub(r'(\d+)\s*\(', r'\1*(', formula)
        
        # Replace variable followed by parenthesis: x(y+z) -> x*(y+z)
        formula = re.sub(r'([a-zA-Z_])\(', r'\1*(', formula)

        # Replace Portuguese function names with their English counterparts
        translations = UncertaintyCalculator._get_translations()['pt']
        for pt_func, en_func in translations.items():
            formula = formula.replace(pt_func, en_func)

        return formula