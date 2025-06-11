# -*- coding: utf-8 -*-
"""
PyInstaller hook for NumPy optimization.
Reduces the size and improves loading of NumPy components.
"""

from PyInstaller.utils.hooks import collect_all

# Only include essential NumPy modules
hiddenimports = [
    'numpy.core._methods',
    'numpy.core._dtype_ctypes',
    'numpy.core._internal',
    'numpy.lib.recfunctions',
    'numpy.random._pickle',
    'numpy.random._bounded_integers',
]

# Exclude unnecessary NumPy components
excludedimports = [
    'numpy.distutils',
    'numpy.f2py',
    'numpy.testing',
    'numpy.tests'
]

# Only collect essential data files
datas, binaries, hiddenimports = collect_all('numpy')
