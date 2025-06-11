# -*- coding: utf-8 -*-
"""
PyInstaller hook for SciPy optimization.
Reduces the size and improves loading of SciPy components.
"""
# Only include essential SciPy modules
hiddenimports = [
    'scipy.special._ufuncs_cxx',
    'scipy.linalg.cython_blas',
    'scipy.linalg.cython_lapack',
    'scipy.integrate._ode',
    'scipy.integrate._odepack',
    'scipy.integrate._quadpack',
    'scipy.optimize._minpack',
    'scipy.sparse.linalg._dsolve',
    'scipy.sparse.linalg._eigen',
]

# Exclude unnecessary SciPy components
excludedimports = [
    'scipy.weave',
    'scipy.sandbox',
    'scipy.testing',
    'scipy.tests'
]
