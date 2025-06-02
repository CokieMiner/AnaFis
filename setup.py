"""Setup script for AnaFis package"""
from setuptools import setup, find_packages

setup(
    name="AnaFis",
    version="1.0.0",
    description="AnaFis modular application for physics data analysis",
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
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