"""Setup script for AnaFis package"""
from setuptools import setup, find_packages

setup(
    name="anafis",
    version="7.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "sympy>=1.9",
        "matplotlib>=3.4.0"
    ],
    author="Pedro",
    description="A Python package for physics data analysis",
    python_requires=">=3.8",
)