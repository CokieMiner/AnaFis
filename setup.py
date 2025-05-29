"""Setup script for AnaFis package"""
from setuptools import setup, find_packages

setup(
    name="AnaFis",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "sympy",
        "matplotlib",
        "pandas"
    ],
    author="Pedro",
    description="A Python app for physics data analysis, curve fitting, and uncertainty calculations",
    python_requires=">=3.8",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    long_description="""AnaFis is a Python app for physics data analysis. It provides tools for curve fitting, uncertainty calculations, and data visualization.""",
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "anafis=app_files.main:main"
        ]
    }
)