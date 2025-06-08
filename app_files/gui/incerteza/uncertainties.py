"""
Module for uncertainty calculations and propagation.

This module provides the UncertaintyCalculator class which handles
mathematical uncertainty calculations and generates LaTeX formulas
for uncertainty propagation.
"""

import math
from typing import Dict, List, Tuple

import sympy as sp


class UncertaintyCalculator:
    """Handles uncertainty calculations and propagation"""

    @staticmethod
    def _get_error_messages():
        """Get error messages for different languages."""
        return {
            'invalid_formula': {
                'pt': "Erro ao processar a fórmula: {error}",
                'en': "Error processing the formula: {error}"
            }
        }

    @staticmethod
    def _get_translations():
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
    def _get_math_functions():
        """Get mathematical functions mapping for sympy."""
        return {
            'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan,
            'exp': sp.exp, 'log': sp.log, 'sqrt': sp.sqrt,
            'pi': sp.pi
        }

    @staticmethod
    def _calculate_formula_value(expr, variables_values, math_functions):
        """Calculate the final value of the formula."""
        expr_substituted = expr.subs(variables_values)
        return float(sp.N(expr_substituted.subs(math_functions)))

    @staticmethod
    def _calculate_uncertainty(expr, variaveis, variables_values):
        """Calculate the total uncertainty using error propagation."""
        incerteza_total = 0
        for var, (_, sigma) in variaveis.items():
            derivada = sp.diff(expr, sp.Symbol(var))
            derivada_num = derivada.subs(variables_values)
            derivada_num = float(sp.N(derivada_num))
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

        formula = formula.replace(translations['pt']['sin'], translations[language]['sin'])

        try:
            # Calculate value using sympy for safer evaluation
            expr = sp.sympify(formula)
            variables_values = {k: valor for k, (valor, _) in variaveis.items()}
            math_functions = UncertaintyCalculator._get_math_functions()

            # Calculate final value and uncertainty using helper methods
            valor_final = UncertaintyCalculator._calculate_formula_value(
                expr, variables_values, math_functions
            )
            incerteza_total = UncertaintyCalculator._calculate_uncertainty(
                expr, variaveis, variables_values
            )

            return valor_final, incerteza_total
        except Exception as e:
            raise ValueError(
                error_messages['invalid_formula'][language].format(error=str(e))
            ) from e

    @staticmethod
    def gerar_formula_incerteza(formula: str, variaveis: List[str]) -> str:
        """Generate LaTeX formula for uncertainty"""
        formula = formula.replace("sen", "sin")
        simbolos = {var.strip(): sp.Symbol(var.strip()) for var in variaveis}
        expr = sp.sympify(formula, locals=simbolos)

        termos = []
        for var in variaveis:
            var = var.strip()
            derivada = sp.diff(expr, simbolos[var])
            termos.append(f"(\\sigma_{{{var}}} \\cdot {sp.latex(derivada)})^2")

        return "\\sigma_{\\text{total}} = \\sqrt{" + " + ".join(termos) + "}"
