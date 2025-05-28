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
    extras_require={
        "data": ["pandas>=1.3.0"]
    },
    author="Pedro",
    description="A Python package for physics data analysis, curve fitting, and uncertainty calculations",
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    long_description="""AnaFis is a Python package for physics data analysis. It provides tools for curve fitting, uncertainty calculations, and data visualization.""",
    long_description_content_type="text/markdown",
)