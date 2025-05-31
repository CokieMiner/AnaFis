"""Setup script for AnaFis package"""
from setuptools import setup, find_packages
from Cython.Build.Dependencies import cythonize
import os

# Get all Python files in app_files directory
def get_py_files(directory):
    py_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                py_files.append(os.path.join(root, file))
    return py_files

# Find all Python files to compile
app_files = get_py_files('app_files') if os.path.exists('app_files') else []
main_files = ['run.py']

all_files = main_files + app_files

setup(
    name="AnaFis",
    version="1.0.0",
    description="AnaFis modular application compiled with Cython",
    packages=find_packages(),
    ext_modules=cythonize(
        all_files,
        compiler_directives={
            'language_level': 3,
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True,
        }
    ),
    zip_safe=False,    install_requires=[
        "numpy",
        "scipy",
        "sympy",
        "matplotlib",
        "pandas"
    ],
    author="Pedro",
    long_description="""AnaFis is a Python app for physics data analysis. It provides tools for curve fitting, uncertainty calculations, and data visualization.""",
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "anafis=run:main"
        ]
    }
)