import pytest
from app_files.uncertainties import UncertaintyCalculator

def test_calcular_incerteza():
    calculator = UncertaintyCalculator()
    # Add test cases for uncertainty calculation
    assert True

def test_calcular_incerteza_basic():
    calculator = UncertaintyCalculator()
    formula = 'x + y'
    variaveis = {'x': (2.0, 0.1), 'y': (3.0, 0.2)}
    result = calculator.calcular_incerteza(formula, variaveis, language='en')
    assert isinstance(result, tuple)