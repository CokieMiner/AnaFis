import pytest
from app_files.regression import RegressionAnalyzer

def test_read_file():
    analyzer = RegressionAnalyzer()
    # Add test cases for reading files
    assert True

def test_create_model():
    analyzer = RegressionAnalyzer()
    equation = 'a*x + b'
    import sympy as sp
    a, b = sp.symbols('a b')
    model, derivs = analyzer.create_model(equation, [a, b])
    assert callable(model)
    assert isinstance(derivs, list)

def test_perform_fit(monkeypatch):
    analyzer = RegressionAnalyzer()
    # Provide dummy data
    import numpy as np
    analyzer.x = np.array([1, 2, 3])
    analyzer.y = np.array([2, 4, 6])
    analyzer.sigma_x = np.array([0.1, 0.1, 0.1])
    analyzer.sigma_y = np.array([0.2, 0.2, 0.2])
    equation = 'a*x'
    import sympy as sp
    a = sp.symbols('a')
    analyzer.create_model(equation, [a])
    result = analyzer.perform_fit([1.0])
    assert hasattr(result, 'beta')