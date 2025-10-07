"""
Centralized error handler for AnaFis application.
Provides a single function to log and display errors in a consistent way.
"""

# pylint: disable=broad-exception-caught
import logging

try:
    from tkinter import messagebox
except ImportError:
    messagebox = None


def show_error(title: str, message: str, log: bool = True) -> None:
    """
    Show an error dialog and log the error, matching the old messagebox.showerror usage.
    Args:
        title: The dialog title (usually a translation string)
        message: The error message (usually a translation string)
        log: Whether to log the error (default True)
    """
    if log:
        logging.error("%s: %s", title, message)
    if messagebox is not None:
        try:
            messagebox.showerror(title, message)
        except Exception as dialog_error:
            logging.error("Failed to show error dialog: %s", dialog_error)


# Alias for backward compatibility
handle_error = show_error
