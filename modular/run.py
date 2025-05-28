"""Launcher script for AnaFis modular version"""
import sys
import os

# Add the modular folder to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath('AnaFis/modular')))

from modular.main import AplicativoUnificado

def main():
    """Main entry point for the application"""
    app = AplicativoUnificado()
    app.run()

if __name__ == "__main__":
    main()