"""Data handling module for curve fitting GUI"""

import os
import json
import numpy as np
import pandas as pd
from tkinter import messagebox
from typing import Tuple, cast, Optional
from numpy.typing import NDArray
from app_files.utils.translations.api import get_string


def detect_3column_format(file_name: str, delimiter: Optional[str] = None) -> str:
    """Detect the format of a 3-column data file by checking the header

    Args:
        file_name: Path to the data file
        delimiter: Delimiter character (None for whitespace)

    Returns:
        Either 'x_y_sigmay' or 'x_sigmax_y' based on header detection
    """
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            # Read first non-comment, non-empty line
            for line in f:
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    # Check if this looks like a header (contains letters)
                    if delimiter is None:
                        parts = stripped.split()
                    else:
                        parts = stripped.split(delimiter)

                    if len(parts) == 3:
                        # Check for common patterns in header
                        header_str = " ".join(parts).lower()

                        # Look for sigma_x or uncertainty_x patterns
                        if any(
                            pattern in header_str
                            for pattern in [
                                "sigma_x",
                                "unc_x",
                                "uncx",
                                "sigmax",
                                "inc_x",
                                "incx",
                                "dx",
                                "err_x",
                                "errx",
                            ]
                        ):
                            return "x_sigmax_y"

                        # Look for sigma_y or uncertainty_y patterns (default)
                        if any(
                            pattern in header_str
                            for pattern in [
                                "sigma_y",
                                "unc_y",
                                "uncy",
                                "sigmay",
                                "inc_y",
                                "incy",
                                "dy",
                                "err_y",
                                "erry",
                            ]
                        ):
                            return "x_y_sigmay"

                        # Check if middle column looks like it could be sigma_x based on naming
                        middle_col = parts[1].lower()
                        if any(
                            pattern in middle_col
                            for pattern in ["sigma", "unc", "inc", "err", "delta"]
                        ):
                            if "x" in middle_col:
                                return "x_sigmax_y"

                    # If we get here, assume default: x, y, sigma_y
                    break
    except Exception:
        pass

    # Default to x, y, sigma_y format
    return "x_y_sigmay"


def detect_4column_format(file_name: str, delimiter: Optional[str] = None) -> str:
    """Detect the format of a 4-column data file by checking the header

    Args:
        file_name: Path to the data file
        delimiter: Delimiter character (None for whitespace)

    Returns:
        Either 'x_sigmax_y_sigmay' or 'x_y_sigmax_sigmay' based on header detection
    """
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            # Read first non-comment, non-empty line
            for line in f:
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    # Check if this looks like a header (contains letters)
                    if delimiter is None:
                        parts = stripped.split()
                    else:
                        parts = stripped.split(delimiter)

                    if len(parts) == 4:
                        # Convert to lowercase for comparison
                        parts_lower = [p.lower() for p in parts]

                        # Check for x, sigma_x, y, sigma_y pattern (standard)
                        # Position 1 should have sigma_x pattern, position 3 should have sigma_y pattern
                        has_sigmax_at_pos1 = any(
                            pattern in parts_lower[1]
                            for pattern in [
                                "sigma_x",
                                "unc_x",
                                "uncx",
                                "sigmax",
                                "inc_x",
                                "incx",
                                "dx",
                                "err_x",
                                "errx",
                            ]
                        )
                        has_sigmay_at_pos3 = any(
                            pattern in parts_lower[3]
                            for pattern in [
                                "sigma_y",
                                "unc_y",
                                "uncy",
                                "sigmay",
                                "inc_y",
                                "incy",
                                "dy",
                                "err_y",
                                "erry",
                            ]
                        )

                        if has_sigmax_at_pos1 and has_sigmay_at_pos3:
                            return "x_sigmax_y_sigmay"

                        # Check for x, y, sigma_x, sigma_y pattern (alternative)
                        # Position 2 should have sigma_x pattern, position 3 should have sigma_y pattern
                        has_sigmax_at_pos2 = any(
                            pattern in parts_lower[2]
                            for pattern in [
                                "sigma_x",
                                "unc_x",
                                "uncx",
                                "sigmax",
                                "inc_x",
                                "incx",
                                "dx",
                                "err_x",
                                "errx",
                            ]
                        )
                        has_sigmay_at_pos3_alt = any(
                            pattern in parts_lower[3]
                            for pattern in [
                                "sigma_y",
                                "unc_y",
                                "uncy",
                                "sigmay",
                                "inc_y",
                                "incy",
                                "dy",
                                "err_y",
                                "erry",
                            ]
                        )

                        if has_sigmax_at_pos2 and has_sigmay_at_pos3_alt:
                            return "x_y_sigmax_sigmay"

                    # If we get here, assume default: x, sigma_x, y, sigma_y
                    break
    except Exception:
        pass

    # Default to standard x, sigma_x, y, sigma_y format
    return "x_sigmax_y_sigmay"


def read_file(file_name: str, language: str = "pt") -> Tuple[
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    pd.DataFrame,
]:
    """Read data from file

    Args:
        file_name (str): Path to the data file
        language (str, optional): UI language. Defaults to 'pt'.

    Returns:
        Tuple containing x, sigma_x, y, sigma_y arrays and a DataFrame for preview
    """

    if not os.path.isfile(file_name):
        messagebox.showerror(
            get_string("data_handler", "error", language),
            get_string("data_handler", "file_not_found", language).format(
                file=file_name
            ),
        )
        raise FileNotFoundError(
            get_string("data_handler", "file_not_found", language).format(
                file=file_name
            )
        )

    try:
        # Check file extension and read accordingly
        _, ext = os.path.splitext(file_name)
        ext = ext.lower()

        if ext in [".xlsx", ".xls"]:
            # Excel file support
            df: pd.DataFrame = pd.read_excel(file_name)
            num_cols = len(df.columns)

            if num_cols == 2:
                # 2 columns: x, y (no uncertainties)
                x = cast(NDArray[np.float64], df.iloc[:, 0].to_numpy(dtype=float))
                sigma_x = np.zeros_like(x)
                y = cast(NDArray[np.float64], df.iloc[:, 1].to_numpy(dtype=float))
                sigma_y = np.zeros_like(y)
            elif num_cols == 3:
                # 3 columns: detect format from column names
                col_names = [str(col).lower() for col in df.columns]

                # Check if middle column name suggests it's sigma_x
                if any(
                    pattern in col_names[1]
                    for pattern in [
                        "sigma_x",
                        "unc_x",
                        "uncx",
                        "sigmax",
                        "inc_x",
                        "incx",
                        "dx",
                        "err_x",
                        "errx",
                    ]
                ):
                    # Format: x, sigma_x, y
                    x = cast(NDArray[np.float64], df.iloc[:, 0].to_numpy(dtype=float))
                    sigma_x = cast(NDArray[np.float64], df.iloc[:, 1].to_numpy(dtype=float))
                    y = cast(NDArray[np.float64], df.iloc[:, 2].to_numpy(dtype=float))
                    sigma_y = np.zeros_like(y)
                else:
                    # Format: x, y, sigma_y (default)
                    x = cast(NDArray[np.float64], df.iloc[:, 0].to_numpy(dtype=float))
                    sigma_x = np.zeros_like(x)
                    y = cast(NDArray[np.float64], df.iloc[:, 1].to_numpy(dtype=float))
                    sigma_y = cast(NDArray[np.float64], df.iloc[:, 2].to_numpy(dtype=float))
            elif num_cols >= 4:
                # 4+ columns: detect format from column names
                # Could be: x, sigma_x, y, sigma_y OR x, y, sigma_x, sigma_y
                col_names = [str(col).lower() for col in df.columns]

                # Check column positions for sigma_x and sigma_y patterns
                has_sigmax_at_pos1 = any(
                    pattern in col_names[1]
                    for pattern in [
                        "sigma_x",
                        "unc_x",
                        "uncx",
                        "sigmax",
                        "inc_x",
                        "incx",
                        "dx",
                        "err_x",
                        "errx",
                    ]
                )
                has_sigmay_at_pos3 = any(
                    pattern in col_names[3]
                    for pattern in [
                        "sigma_y",
                        "unc_y",
                        "uncy",
                        "sigmay",
                        "inc_y",
                        "incy",
                        "dy",
                        "err_y",
                        "erry",
                    ]
                )

                has_sigmax_at_pos2 = any(
                    pattern in col_names[2]
                    for pattern in [
                        "sigma_x",
                        "unc_x",
                        "uncx",
                        "sigmax",
                        "inc_x",
                        "incx",
                        "dx",
                        "err_x",
                        "errx",
                    ]
                )

                if has_sigmax_at_pos2 and not has_sigmax_at_pos1:
                    # Format: x, y, sigma_x, sigma_y (alternative ordering)
                    x = cast(NDArray[np.float64], df.iloc[:, 0].to_numpy(dtype=float))
                    y = cast(NDArray[np.float64], df.iloc[:, 1].to_numpy(dtype=float))
                    sigma_x = cast(NDArray[np.float64], df.iloc[:, 2].to_numpy(dtype=float))
                    sigma_y = cast(NDArray[np.float64], df.iloc[:, 3].to_numpy(dtype=float))
                else:
                    # Format: x, sigma_x, y, sigma_y (standard ordering) - DEFAULT
                    x = cast(NDArray[np.float64], df.iloc[:, 0].to_numpy(dtype=float))
                    sigma_x = cast(NDArray[np.float64], df.iloc[:, 1].to_numpy(dtype=float))
                    y = cast(NDArray[np.float64], df.iloc[:, 2].to_numpy(dtype=float))
                    sigma_y = cast(NDArray[np.float64], df.iloc[:, 3].to_numpy(dtype=float))
            else:
                raise ValueError(
                    get_string("data_handler", "file_insufficient_columns", language)
                )

            preview_data = pd.DataFrame(
                {"x": x, "sigma_x": sigma_x, "y": y, "sigma_y": sigma_y}
            )
            return x, sigma_x, y, sigma_y, preview_data

        elif ext == ".json":
            # JSON file support
            with open(file_name, "r", encoding="utf-8") as f:
                data = json.load(f)
            x = np.array(data["x"], dtype=np.float64)
            sigma_x = np.array(data["sigma_x"], dtype=np.float64)
            y = np.array(data["y"], dtype=np.float64)
            sigma_y = np.array(data["sigma_y"], dtype=np.float64)
            preview_data = pd.DataFrame(
                {"x": x, "sigma_x": sigma_x, "y": y, "sigma_y": sigma_y}
            )
            return x, sigma_x, y, sigma_y, preview_data

        else:
            # Text/CSV file processing with auto-delimiter detection
            with open(file_name, "r", encoding="utf-8") as f:
                all_lines = f.readlines()

            # Skip comment lines (lines starting with #) and empty lines
            lines = []
            for line in all_lines:
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    lines.append(line)

            # If first remaining line looks like a header (contains non-numeric text), skip it
            if lines and lines[0].strip():
                first_data_line = lines[0].strip().split()
                try:
                    # Try to convert first element to float - if it fails, it's likely a header
                    float(first_data_line[0].replace(",", "."))
                except (ValueError, IndexError):
                    # First line is a header, skip it
                    lines = lines[1:]

            if len(lines) == 0:
                messagebox.showerror(get_string("data_handler", "file_read_error", language), get_string("data_handler", "file_empty_error", language))
                raise ValueError(
                    get_string("data_handler", "file_empty_error", language)
                )

            # Auto-detect delimiter by checking the first data line
            # Priority: semicolon (;) > comma (,) > tab/space (\s+)
            first_line = lines[0].strip()
            if ";" in first_line and first_line.count(";") >= 1:
                delimiter = ";"
            elif "," in first_line and first_line.count(",") >= 1:
                delimiter = ","
            else:
                # For space/tab delimited, we'll use split() without arguments
                # which handles multiple spaces/tabs
                delimiter = None  # Will use split() for whitespace
                # Check number of columns - support 2, 3, and 4 column formats
            num_columns = None
            for i, line in enumerate(lines):
                if delimiter is None:
                    # Use split() for whitespace (handles multiple spaces/tabs)
                    parts = line.strip().split()
                else:
                    parts = line.strip().split(delimiter)
                if num_columns is None:
                    num_columns = len(parts)
                    if num_columns == 1:
                        # Single column - provide helpful guidance
                        messagebox.showerror(
                            get_string("data_handler", "file_read_error", language),
                            f"{get_string('data_handler', 'file_single_column_error', language)}\n\n"
                            + f"{get_string('data_handler', 'file_format_guidance', language)}",
                        )
                        raise ValueError(
                            get_string(
                                "data_handler", "file_single_column_error", language
                            )
                        )
                    elif num_columns >= 5:
                        # Too many columns - provide fallback suggestion
                        messagebox.showerror(
                            get_string("data_handler", "file_read_error", language),
                            f"{get_string('data_handler', 'file_too_many_columns_error', language).format(cols=num_columns)}\n\n"
                            + f"{get_string('data_handler', 'file_format_guidance', language)}",
                        )
                        raise ValueError(
                            get_string(
                                "data_handler", "file_too_many_columns_error", language
                            ).format(cols=num_columns)
                        )
                    elif num_columns not in [2, 3, 4]:
                        # Unexpected number of columns
                        messagebox.showerror(
                            get_string("data_handler", "file_read_error", language),
                            get_string(
                                "data_handler", "file_columns_error_2_3_4", language
                            ).format(delimiter=delimiter, line=i + 2, cols=num_columns),
                        )
                        raise ValueError(
                            get_string(
                                "data_handler", "file_columns_error_2_3_4", language
                            ).format(delimiter=delimiter, line=i + 2, cols=num_columns)
                        )
                elif len(parts) != num_columns:
                    messagebox.showerror(
                        get_string("data_handler", "file_read_error", language),
                        get_string(
                            "data_handler", "file_columns_inconsistent", language
                        ).format(
                            delimiter=delimiter if delimiter else "whitespace",
                            line=i + 2,
                            expected=num_columns,
                            found=len(parts),
                        ),
                    )
                    raise ValueError(
                        get_string(
                            "data_handler", "file_columns_inconsistent", language
                        ).format(
                            delimiter=delimiter if delimiter else "whitespace",
                            line=i + 2,
                            expected=num_columns,
                            found=len(parts),
                        )
                    )

            # Load data using numpy with proper comment and delimiter handling
            if delimiter is None:
                # For whitespace-delimited files, use None as delimiter (handles any whitespace)
                dados: NDArray[np.str_] = np.genfromtxt(file_name, delimiter=None, comments="#", dtype=str, encoding="utf-8")
            else:
                dados = np.genfromtxt(file_name, delimiter=delimiter, comments="#", dtype=str, encoding="utf-8")
            dados = np.char.replace(dados, ",", ".")

            if num_columns == 2:
                # 2 columns: x, y (no uncertainties)
                x: NDArray[np.float64] = dados[:, 0].astype(np.float64)
                sigma_x: NDArray[np.float64] = np.zeros_like(x)  # No uncertainty in x
                y: NDArray[np.float64] = dados[:, 1].astype(np.float64)
                sigma_y: NDArray[np.float64] = np.zeros_like(y)  # No uncertainty in y
                preview_data = pd.DataFrame(
                    {"x": x, "sigma_x": sigma_x, "y": y, "sigma_y": sigma_y}
                )
            elif num_columns == 3:
                # 3 columns: Auto-detect format based on header
                # Could be: x, y, sigma_y OR x, sigma_x, y
                format_type = detect_3column_format(file_name, delimiter)

                if format_type == "x_sigmax_y":
                    # Format: x, sigma_x, y (uncertainty only in X)
                    x = dados[:, 0].astype(np.float64)
                    sigma_x = dados[:, 1].astype(np.float64)
                    y = dados[:, 2].astype(np.float64)
                    sigma_y = np.zeros_like(y)  # No uncertainty in y
                    preview_data = pd.DataFrame(
                        {"x": x, "sigma_x": sigma_x, "y": y, "sigma_y": sigma_y}
                    )
                else:
                    # Format: x, y, sigma_y (uncertainty only in Y) - DEFAULT
                    x = dados[:, 0].astype(np.float64)
                    sigma_x = np.zeros_like(x)  # No uncertainty in x
                    y = dados[:, 1].astype(np.float64)
                    sigma_y = dados[:, 2].astype(np.float64)
                    preview_data = pd.DataFrame(
                        {"x": x, "sigma_x": sigma_x, "y": y, "sigma_y": sigma_y}
                    )
            else:
                # 4 columns: Auto-detect format based on header
                # Could be: x, sigma_x, y, sigma_y OR x, y, sigma_x, sigma_y
                format_type = detect_4column_format(file_name, delimiter)

                if format_type == "x_y_sigmax_sigmay":
                    # Format: x, y, sigma_x, sigma_y (alternative ordering)
                    x = dados[:, 0].astype(np.float64)
                    y = dados[:, 1].astype(np.float64)
                    sigma_x = dados[:, 2].astype(np.float64)
                    sigma_y = dados[:, 3].astype(np.float64)
                    preview_data = pd.DataFrame(
                        {"x": x, "sigma_x": sigma_x, "y": y, "sigma_y": sigma_y}
                    )
                else:
                    # Format: x, sigma_x, y, sigma_y (standard ordering) - DEFAULT
                    x = dados[:, 0].astype(np.float64)
                    sigma_x = dados[:, 1].astype(np.float64)
                    y = dados[:, 2].astype(np.float64)
                    sigma_y = dados[:, 3].astype(np.float64)
                    preview_data = pd.DataFrame(
                        {"x": x, "sigma_x": sigma_x, "y": y, "sigma_y": sigma_y}
                    )

            return x, sigma_x, y, sigma_y, preview_data

    except Exception as e:
        messagebox.showerror(
            get_string("data_handler", "error", language),
            get_string("data_handler", "file_processing_error", language).format(
                error=str(e)
            ),
        )
        raise
