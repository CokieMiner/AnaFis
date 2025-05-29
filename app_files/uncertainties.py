import math
import sympy as sp
from typing import Dict, List, Tuple

class UncertaintyCalculator:
    """Handles uncertainty calculations and propagation"""
    @staticmethod
    def calcular_incerteza(formula: str, variaveis: Dict[str, Tuple[float, float]], language: str = 'pt') -> Tuple[float, float]:
        error_messages = {
            'invalid_formula': {
                'pt': "Erro ao processar a fórmula: {error}",
                'en': "Error processing the formula: {error}"
            }
        }

        translations = {
            'pt': {
                'sin': 'sen'
            },
            'en': {
                'sin': 'sin'
            }
        }
        formula = formula.replace(translations['pt']['sin'], translations[language]['sin'])

        try:
            # Calculate value
            valor_final = eval(
                formula,
                {
                    "sin": math.sin, "cos": math.cos, "tan": math.tan,
                    "exp": math.exp, "log": math.log, "sqrt": math.sqrt,
                    "pi": math.pi
                },
                {k: valor for k, (valor, _) in variaveis.items()}
            )

            # Calculate uncertainty
            expr = sp.sympify(formula)
            incerteza_total = 0
            for var, (val, sigma) in variaveis.items():
                derivada = sp.diff(expr, sp.Symbol(var))
                derivada_num = derivada.subs(
                    {sp.Symbol(k): valor for k, (valor, _) in variaveis.items()}
                )
                derivada_num = float(sp.N(derivada_num))
                incerteza_total += (derivada_num * sigma) ** 2
                
            incerteza_total = math.sqrt(incerteza_total)
            
            return valor_final, incerteza_total
        except Exception as e:
            raise ValueError(error_messages['invalid_formula'][language].format(error=str(e)))

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