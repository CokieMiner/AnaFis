"""
Module for uncertainty calculations and propagation.

This module provides the UncertaintyCalculator class which handles
mathematical uncertainty calculations and generates LaTeX formulas
for uncertainty propagation.
"""

import math
from typing import Dict, List, Tuple, Callable, Any

import sympy as sp


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
                'pt': "Erro ao processar a fórmula: {error}",
                'en': "Error processing the formula: {error}"
            }
        }

    @staticmethod
    def _get_translations() -> Dict[str, Dict[str, str]]:
        """Get translation mappings for mathematical functions."""
        return {
            'pt': {
                'sin': 'sen'
            },
            'en': {
                'sin': 'sin'
            }
        }

    @staticmethod
    def _get_math_functions() -> Dict[str, Callable[..., Any] | sp.Number]:
        """Get mathematical functions mapping for sympy."""
        return {
            'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
            'exp': sp.exp, 'log': sp.log, 'sqrt': sp.sqrt, # type: ignore
            'pi': sp.pi
        }

    @staticmethod
    def _calculate_formula_value(
        expr: Any, # Reverted from sp.Expr due to stub issues
        variables_values: Dict[str, float],
        math_functions: Dict[str, Callable[..., Any] | sp.Number]
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
        σ_f² = Σ (∂f/∂x_i)² * σ_x_i²
        where f is the function, x_i are the variables, and σ_x_i are their uncertainties.
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