"""Launcher script for AnaFis modular version"""
import sys
import os

# Add the modular folder to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app_files'))

from app_files.main import AplicativoUnificado

def main():
    """Main entry point for the application"""
    app = AplicativoUnificado()
    app.run()

if __name__ == "__main__":
    main()