"""Setup script for AnaFis package"""
import os
from setuptools import setup, find_packages

# Read the README file for long description
def read_readme() -> str:
    """Read README.md file content for package long description.
    
    Returns:
        str: Content of README.md file or default description if file not found.
    """
    try:
        with open(os.path.join(os.path.dirname(__file__), "README.md"), "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ("AnaFis is a Python app for physics data analysis. "
                "It provides tools for curve fitting, uncertainty calculations, "
                "and data visualization.")

setup(
    name="AnaFis",
    version="9",
    description="AnaFis - Physics Data Analysis Application",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="CokieMiner",
    author_email="pedromamartins@live.com",
    url="",
    packages=find_packages(),
    zip_safe=False,
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "scipy>=1.7.0", 
        "sympy>=1.8.0",
        "matplotlib>=3.3.0",
        "pandas>=1.3.0"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],    keywords="physics data-analysis curve-fitting uncertainty-propagation",
    entry_points={
        "console_scripts": [
            "anafis=run:main"
        ]
    },
    include_package_data=True,
    package_data={
        "app_files": ["*.json"],
    }
)
