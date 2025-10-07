"""GUI module for uncertainty calculations"""

from __future__ import annotations
from typing import Tuple, Dict, List, Optional, Any, Set
import tkinter as tk
from tkinter import ttk, Toplevel
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import logging
import math
import sympy as sp
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.axes import Axes

from app_files.utils.translations.api import get_string, get_help

# Constants
FONT_FAMILY = "Courier New"
FONT_SIZE = 10
ENTRY_WIDTH = {"small": 5, "medium": 10, "large": 30, "formula": 40}


class CalculoIncertezasFrame:
    """Frame-based GUI class for uncertainty calculations"""

    def __init__(self, parent: tk.Widget, language: str = "pt") -> None:
        """Initialize the frame
        Args:
            parent: Parent widget (typically a tab)
            language: Interface language (default: 'pt')
        """
        self.parent = parent
        self.language = language

        # Create StringVar with explicit parent to avoid "no default root window" error
        self.modo_var = tk.StringVar(parent, value="calcular")
        self.num_variaveis_var = tk.StringVar(parent, value="2")
        self.variaveis_var = tk.StringVar(parent, value="x, y")
        self.formula_var = tk.StringVar(parent, value="")
        self.resultado_var = tk.StringVar(parent, value="")
        self.incerteza_var = tk.StringVar(parent, value="")
        self.formula_incerteza_var = tk.StringVar(parent, value="")

        # Initialize all attributes
        self.vars_entry: Optional[ttk.Entry] = None
        self.var_entries: List[Tuple[ttk.Entry, ttk.Entry, ttk.Entry]] = []
        self.formula_latex: str = ""
        self.num_var: ttk.Entry
        self.formula_entry: ttk.Entry
        self.botao_calcular: ttk.Button
        self.resultados_text: ScrolledText
        self.latex_frame: ttk.Frame

        # Create main frame
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Initialize the UI
        self.setup_ui()

    def on_tab_activated(self) -> None:
        """Called when this tab becomes active"""
        self.update_results()

    def cleanup(self) -> None:
        """Clean up resources when tab is closed or application exits"""
        if hasattr(self, "latex_frame"):
            for widget in self.latex_frame.winfo_children():
                widget.destroy()

    def update_results(self) -> None:
        """Update calculation results"""
        if not self.formula_entry.get():
            return

    def setup_ui(self) -> None:
        """Set up the user interface components"""
        from app_files.utils.theme_manager import theme_manager

        self.main_frame.columnconfigure(0, weight=1)

        # Operation mode
        operation_mode_label = ttk.Label(
            self.main_frame,
            text=get_string("uncertainty_calc", "operation_mode", self.language),
        )
        operation_mode_label.grid(row=0, column=0, pady=5, sticky="w")

        calc_radio = ttk.Radiobutton(
            self.main_frame,
            text=get_string(
                "uncertainty_calc", "calc_value_uncertainty", self.language
            ),
            variable=self.modo_var,
            value="calcular",
            command=self.atualizar_interface,
        )
        calc_radio.grid(row=1, column=0, sticky="w")

        generate_radio = ttk.Radiobutton(
            self.main_frame,
            text=get_string(
                "uncertainty_calc", "generate_uncertainty_formula", self.language
            ),
            variable=self.modo_var,
            value="gerar",
            command=self.atualizar_interface,
        )
        generate_radio.grid(row=2, column=0, sticky="w")

        # Variables frame
        var_frame_text = get_string("uncertainty_calc", "variables", self.language)
        self.var_frame = ttk.LabelFrame(
            self.main_frame, text=var_frame_text, padding="5"
        )
        self.var_frame.grid(row=3, column=0, pady=10, sticky="ew")

        # Number of variables
        self.num_var_frame = ttk.Frame(self.var_frame)
        self.num_var_frame.grid(row=0, column=0, sticky="w")

        num_vars_label = ttk.Label(
            self.num_var_frame,
            text=get_string("uncertainty_calc", "number_of_variables", self.language),
        )
        num_vars_label.grid(row=0, column=0, sticky="w")

        self.num_var = ttk.Entry(self.num_var_frame, width=ENTRY_WIDTH["small"])
        self.num_var.grid(row=0, column=1, padx=2)

        create_fields_btn = ttk.Button(
            self.num_var_frame,
            text=get_string("uncertainty_calc", "create_fields", self.language),
            command=self.criar_campos_variaveis,
        )
        create_fields_btn.grid(row=0, column=2, padx=2)

        # Variable fields frame
        self.campos_frame = ttk.Frame(self.var_frame)
        self.campos_frame.grid(row=1, column=0, sticky="ew")
        self.campos_frame.grid_columnconfigure(0, weight=1)
        # Ensure the column within campos_frame expands

        # Formula
        formula_frame = ttk.Frame(self.main_frame)
        formula_frame.grid(row=4, column=0, pady=5, sticky="w")

        formula_label = ttk.Label(
            formula_frame, text=get_string("uncertainty_calc", "formula", self.language)
        )
        formula_label.grid(row=0, column=0, sticky="w")

        help_button_text = get_string(
            "uncertainty_calc", "help_button_text", self.language
        )
        help_button = ttk.Button(
            formula_frame,
            text=f"💡 {help_button_text}",  # Add bulb icon
            width=16,
            command=self.show_formula_help,
        )
        help_button.grid(row=0, column=1, padx=(5, 0), sticky="w")

        self.formula_entry = ttk.Entry(self.main_frame, width=ENTRY_WIDTH["formula"])
        self.formula_entry.grid(row=5, column=0, pady=5, sticky="ew")

        # Calculate/generate button
        calc_btn_text = get_string("uncertainty_calc", "calculate", self.language)
        self.botao_calcular = ttk.Button(
            self.main_frame, text=calc_btn_text, command=self.calcular_ou_gerar
        )
        self.botao_calcular.grid(row=6, column=0, pady=10)

        # Results area
        results_label = ttk.Label(
            self.main_frame,
            text=get_string("uncertainty_calc", "results", self.language),
        )
        results_label.grid(row=7, column=0, pady=5, sticky="w")

        self.resultados_text = ScrolledText(
            self.main_frame,
            height=12,
            width=50,
            font=(FONT_FAMILY, FONT_SIZE),
            bg=theme_manager.get_adaptive_color("background"),
            fg=theme_manager.get_adaptive_color("foreground"),
        )
        self.resultados_text.grid(row=8, column=0, pady=5, sticky="ew")

        # LaTeX frame
        self.latex_frame = ttk.Frame(self.main_frame)
        self.latex_frame.grid(row=9, column=0, pady=5, sticky="ew")

        self.atualizar_interface()
        self.resultados_text.delete(1.0, tk.END)

    def atualizar_interface(self) -> None:
        """Update interface based on selected operation mode"""
        mode = self.modo_var.get()

        if mode == "calcular":
            self.num_var_frame.grid()
            self.botao_calcular.configure(
                text=get_string("uncertainty_calc", "calculate", self.language)
            )
            for widget in self.campos_frame.winfo_children():
                widget.destroy()
        else:
            self.num_var_frame.grid_remove()
            for widget in self.campos_frame.winfo_children():
                widget.destroy()

            self.botao_calcular.configure(
                text=get_string("uncertainty_calc", "generate_formula", self.language)
            )

            # For generate mode - single variable list field
            vars_list_text = get_string(
                "uncertainty_calc", "variables_list", self.language
            )
            vars_label = ttk.Label(self.campos_frame, text=vars_list_text)
            vars_label.grid(row=0, column=0)

            self.vars_entry = ttk.Entry(self.campos_frame, width=ENTRY_WIDTH["large"])
            self.vars_entry.grid(row=0, column=1)

    def criar_campos_variaveis(self) -> None:
        """Create input fields for variables based on the number specified"""
        try:
            num = int(self.num_var.get())
            # Clear existing fields
            for widget in self.campos_frame.winfo_children():
                widget.destroy()

            self.var_entries = []  # Reset var_entries list

            # Column headers
            header_frame = ttk.Frame(self.campos_frame)
            header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))

            # Configure column weights for header_frame
            header_frame.grid_columnconfigure(0, weight=0)  # Spacer column
            header_frame.grid_columnconfigure(1, weight=1)  # Variable header
            header_frame.grid_columnconfigure(2, weight=1)  # Value header
            header_frame.grid_columnconfigure(3, weight=1)  # Uncertainty header

            ttk.Label(header_frame, text="").grid(row=0, column=0, padx=2)  # Spacer

            header_labels_text = [
                get_string("uncertainty_calc", "variable", self.language),
                get_string("uncertainty_calc", "value", self.language),
                get_string("uncertainty_calc", "uncertainty", self.language),
            ]
            for col, text in enumerate(header_labels_text):
                ttk.Label(header_frame, text=text).grid(
                    row=0, column=col + 1, padx=2, sticky="ew"
                )

            for i in range(num):
                frame = ttk.Frame(self.campos_frame)
                frame.grid(row=i + 1, column=0, pady=2, sticky="ew")

                # Configure column weights for individual variable row frame
                frame.grid_columnconfigure(0, weight=0)  # Row number column
                frame.grid_columnconfigure(1, weight=1)  # Name entry
                frame.grid_columnconfigure(2, weight=1)  # Value entry
                frame.grid_columnconfigure(3, weight=1)  # Uncertainty entry

                ttk.Label(frame, text=f"{i+1}:").grid(
                    row=0, column=0, padx=2, sticky="w"
                )

                nome = ttk.Entry(frame, width=ENTRY_WIDTH["medium"])
                nome.grid(row=0, column=1, padx=2, sticky="ew")

                valor = ttk.Entry(frame, width=ENTRY_WIDTH["medium"])
                valor.grid(row=0, column=2, padx=2, sticky="ew")

                incerteza = ttk.Entry(frame, width=ENTRY_WIDTH["medium"])
                incerteza.grid(row=0, column=3, padx=2, sticky="ew")

                self.var_entries.append((nome, valor, incerteza))

        except ValueError:
            error_msg = get_string("uncertainty_calc", "invalid_vars", self.language)
            messagebox.showerror(
                title=get_string("uncertainty_calc", "error_title", self.language),
                message=error_msg,
            )

    def calcular_ou_gerar(self) -> None:
        """Route to appropriate calculation or generation method based on mode"""
        if self.modo_var.get() == "calcular":
            self.calcular_incerteza()
        else:
            self.gerar_formula_incerteza()

    def _preprocess_formula(self, formula: str) -> str:
        """
        Preprocess formula to handle implicit multiplication and other common patterns
        Convert patterns like '3(a+b)' to '3*(a+b)' and '2x' to '2*x'
        """
        import re

        # Remove spaces for easier processing
        formula = formula.replace(" ", "")

        # Known mathematical functions that should NOT be affected
        math_functions = {
            "sin",
            "cos",
            "tan",
            "sec",
            "csc",
            "cot",
            "asin",
            "acos",
            "atan",
            "atan2",
            "asinh",
            "acosh",
            "atanh",
            "sinh",
            "cosh",
            "tanh",
            "exp",
            "log",
            "log10",
            "ln",
            "sqrt",
            "abs",
            "floor",
            "ceil",
            "round",
            "factorial",
            "gamma",
        }

        # Pattern 1: Number followed by opening parenthesis -> add *
        # Examples: 3(a+b) -> 3*(a+b), 2.5(x+y) -> 2.5*(x+y)
        formula = re.sub(r"(\d+\.?\d*)\(", r"\1*(", formula)

        # Pattern 2: Number followed by variable letter -> add * (but avoid function names)
        # Examples: 2x -> 2*x, 3a -> 3*a, 2.5y -> 2.5*y
        for match in re.finditer(r"(\d+\.?\d*)([a-zA-Z_]\w*)", formula):
            number = match.group(1)
            var_name = match.group(2)
            # Only add * if the variable name is not a mathematical function
            if var_name not in math_functions:
                formula = formula.replace(match.group(0), f"{number}*{var_name}", 1)

        # Pattern 3: Closing parenthesis followed by opening parenthesis -> add *
        # Examples: (a+b)(c+d) -> (a+b)*(c+d)
        formula = re.sub(r"\)\(", ")*(", formula)

        # Pattern 4: Variable followed by opening parenthesis -> add * (but avoid function names)
        # Examples: x(a+b) -> x*(a+b), but keep sin(x) as sin(x)
        for match in re.finditer(r"([a-zA-Z_]\w*)\(", formula):
            var_name = match.group(1)
            # Only add * if it's not a mathematical function
            if var_name not in math_functions:
                formula = formula.replace(match.group(0), f"{var_name}*(", 1)

        # Pattern 5: Closing parenthesis followed by variable -> add *
        # Examples: (a+b)x -> (a+b)*x
        formula = re.sub(r"\)([a-zA-Z_]\w*)", r")*\1", formula)

        return formula

    def calcular_incerteza(self) -> None:
        """Calculate uncertainty for given variables and formula"""
        if not self.var_entries:
            error_msg = get_string("uncertainty_calc", "create_fields", self.language)
            messagebox.showerror(
                title=get_string("uncertainty_calc", "error_title", self.language),
                message=error_msg,
            )
            return

        try:
            # Collect variables and validate names
            variaveis: Dict[str, Tuple[float, float]] = {}
            variable_names: List[str] = []

            for nome_entry, valor_entry, incerteza_entry in self.var_entries:
                nome = nome_entry.get().strip()
                if not nome:
                    messagebox.showerror(
                        title=get_string(
                            "uncertainty_calc", "error_title", self.language
                        ),
                        message="Variable name cannot be empty",
                    )
                    return

                variable_names.append(nome)

                try:
                    valor = float(valor_entry.get())
                    incerteza = float(incerteza_entry.get())
                except ValueError:
                    messagebox.showerror(
                        title=get_string(
                            "uncertainty_calc", "error_title", self.language
                        ),
                        message=f"Invalid number for variable {nome}",
                    )
                    return

                variaveis[nome] = (valor, incerteza)

            # Validate variable names
            if not self._validate_variable_names(variable_names):
                return

            formula = self.formula_entry.get().replace("sen", "sin").strip()
            # Preprocess formula for implicit multiplication
            formula = self._preprocess_formula(formula)

            # Create symbol mapping for sympy with explicit symbols
            # Only include user-defined variables, no function names
            symbols_dict: Dict[str, Any] = {}
            for var_name in variaveis.keys():
                symbols_dict[var_name] = sp.Symbol(var_name)

            # Parse and evaluate formula with safe parsing
            try:
                # Use a clean namespace with only user variables
                safe_locals: Dict[str, Any] = symbols_dict.copy()
                expr = sp.sympify(formula, locals=safe_locals)
            except (sp.SympifyError, TypeError) as e:
                messagebox.showerror(
                    title=get_string("uncertainty_calc", "error_title", self.language),
                    message=f"Error parsing formula: {str(e)}\nMake sure variable names don't conflict with mathematical functions.",
                )
                return
            except Exception as e:
                messagebox.showerror(
                    title=get_string("uncertainty_calc", "error_title", self.language),
                    message=f"Unexpected error parsing formula: {str(e)}",
                )
                return

            # Verify that all symbols in the expression are user-defined variables
            formula_symbols: Set[Any] = expr.free_symbols
            for symbol in formula_symbols:
                if str(symbol) not in variaveis:
                    messagebox.showerror(
                        title=get_string(
                            "uncertainty_calc", "error_title", self.language
                        ),
                        message=f"Unknown variable '{symbol}' in formula. Please define all variables.",
                    )
                    return

            # Create substitution mapping for evaluation
            variables_dict_sympy: Dict[Any, float] = {
                symbols_dict[k]: v[0] for k, v in variaveis.items()
            }

            # Calculate final value using sympy
            try:
                valor_final = float(expr.subs(variables_dict_sympy).evalf())
            except Exception as e:
                messagebox.showerror(
                    title=get_string("uncertainty_calc", "error_title", self.language),
                    message=f"Error evaluating formula: {str(e)}",
                )
                return

            # Calculate uncertainty
            try:
                incerteza_total = self._calcular_incerteza_total(formula, variaveis)
            except Exception as e:
                messagebox.showerror(
                    title=get_string("uncertainty_calc", "error_title", self.language),
                    message=f"Error calculating uncertainty: {str(e)}",
                )
                return

            # Show results
            self._mostrar_resultados(valor_final, incerteza_total)

        except Exception as e:
            messagebox.showerror(
                title=get_string("uncertainty_calc", "error_title", self.language),
                message=f"Unexpected error: {str(e)}",
            )

    def _calcular_incerteza_total(
        self, formula: str, variaveis: Dict[str, Tuple[float, float]]
    ) -> float:
        """Calculate total uncertainty using partial derivatives"""
        try:
            # Preprocess formula for implicit multiplication (safety measure)
            formula = self._preprocess_formula(formula)

            # Create symbol mapping with only user-defined variables
            symbols_dict: Dict[str, Any] = {}
            for var_name in variaveis.keys():
                symbols_dict[var_name] = sp.Symbol(var_name)

            # Parse expression with safe namespace
            safe_locals: Dict[str, Any] = symbols_dict.copy()
            expr = sp.sympify(formula, locals=safe_locals)
            # Create substitution mapping
            symbols_map: Dict[Any, float] = {
                symbols_dict[k]: v[0] for k, v in variaveis.items()
            }

            incerteza_total = 0.0
            for var, (_, sigma) in variaveis.items():
                symbol: Any = symbols_dict[var]

                # Calculate partial derivative
                try:
                    derivada = sp.diff(expr, symbol)
                except Exception as e:
                    raise ValueError(
                        f"Error calculating derivative for variable '{var}': {str(e)}"
                    )

                # Evaluate derivative at the point
                try:
                    derivada_num = derivada.subs(symbols_map)
                    derivada_num_val = float(derivada_num.evalf())
                except Exception as e:
                    raise ValueError(
                        f"Error evaluating derivative for variable '{var}': {str(e)}"
                    )

                # Add contribution to total uncertainty
                incerteza_total += (derivada_num_val * sigma) ** 2

            return math.sqrt(incerteza_total)

        except Exception as e:
            # Re-raise with more context
            raise ValueError(f"Error in uncertainty calculation: {str(e)}")

    def _mostrar_resultados(self, valor: float, incerteza: float) -> None:
        """Display calculation results in the text area"""
        self.resultados_text.delete(1.0, tk.END)
        self.resultados_text.insert(
            tk.END,
            f"{get_string('uncertainty_calc', 'result_header', self.language)}\n",
        )
        self.resultados_text.insert(
            tk.END,
            f"{get_string('uncertainty_calc', 'calculated_value', self.language)} {valor:.6f}\n",
        )
        self.resultados_text.insert(
            tk.END,
            f"{get_string('uncertainty_calc', 'total_uncertainty', self.language)} ±{incerteza:.6f}\n",
        )
        self.resultados_text.insert(
            tk.END,
            f"{get_string('uncertainty_calc', 'final_result', self.language)} ({valor:.6f} ± {incerteza:.6f})",
        )

        # Clear LaTeX display
        self._clear_latex_display()

    def _clear_latex_display(self) -> None:
        """Clear any LaTeX rendering from the interface"""
        for widget in self.latex_frame.winfo_children():
            widget.destroy()

    def gerar_formula_incerteza(self) -> None:
        """Generate uncertainty formula for given variables"""
        if self.vars_entry is None:
            return

        try:
            variaveis_str = [v.strip() for v in self.vars_entry.get().split(",")]
            if not all(variaveis_str):  # Check for empty variable names
                messagebox.showerror(
                    title=get_string(
                        "uncertainty_calc", "input_error_title", self.language
                    ),
                    message=get_string(
                        "uncertainty_calc", "empty_variable_name", self.language
                    ),
                )
                return

            # Validate variable names before proceeding
            if not self._validate_variable_names(variaveis_str):
                return

            formula = self.formula_entry.get().replace("sen", "sin")
            if not formula:
                messagebox.showerror(
                    title=get_string(
                        "uncertainty_calc", "input_error_title", self.language
                    ),
                    message=get_string(
                        "uncertainty_calc", "empty_formula", self.language
                    ),
                )
                return

            # Preprocess formula for implicit multiplication
            formula = self._preprocess_formula(formula)

            # Create symbol mapping with explicit Symbol creation, only for user variables
            simbolos: Dict[str, Any] = {}
            for var in variaveis_str:
                simbolos[var] = sp.Symbol(var)

            # Parse expression with safe symbol mapping
            try:
                safe_locals: Dict[str, Any] = simbolos.copy()
                expr = sp.sympify(formula, locals=safe_locals)
            except (sp.SympifyError, TypeError) as e:
                messagebox.showerror(
                    title=get_string("uncertainty_calc", "error_title", self.language),
                    message=f"Error parsing formula: {str(e)}\nMake sure variable names don't conflict with mathematical functions.",
                )
                return
            except Exception as e:
                messagebox.showerror(
                    title=get_string("uncertainty_calc", "error_title", self.language),
                    message=f"Unexpected error parsing formula: {str(e)}",
                )
                return

            # Verify that all symbols in the expression are user-defined variables
            try:
                formula_symbols: Set[Any] = expr.free_symbols
                for symbol in formula_symbols:
                    if str(symbol) not in simbolos:
                        messagebox.showerror(
                            title=get_string(
                                "uncertainty_calc", "error_title", self.language
                            ),
                            message=f"Unknown variable '{symbol}' in formula. Please include all variables in the variable list.",
                        )
                        return
            except Exception as e:
                messagebox.showerror(
                    title=get_string("uncertainty_calc", "error_title", self.language),
                    message=f"Error analyzing formula variables: {str(e)}",
                )
                return

            # Generate uncertainty terms
            termos: List[str] = []
            for var_str in variaveis_str:
                try:
                    symbol: Any = simbolos[var_str]
                    derivada = sp.diff(expr, symbol)
                    # Get LaTeX representation - keep it simple
                    latex_derivada: str = str(sp.latex(derivada))
                    # Create the term with simpler LaTeX formatting
                    latex_term = f"({latex_derivada} \\cdot \\delta_{{{var_str}}})^2"
                    termos.append(latex_term)
                except Exception as e:
                    messagebox.showerror(
                        title=get_string(
                            "uncertainty_calc", "error_title", self.language
                        ),
                        message=f"Error calculating derivative for {var_str}: {str(e)}",
                    )
                    return

            # Build the complete uncertainty formula with simpler LaTeX syntax
            formula_incerteza = "\\delta_{total} = \\sqrt{" + " + ".join(termos) + "}"

            # Debug: Log the generated formula
            logging.debug(f"Generated LaTeX formula: {formula_incerteza}")

            # Display results
            self.resultados_text.delete(1.0, tk.END)
            self.resultados_text.insert(
                tk.END,
                f"{get_string('uncertainty_calc', 'uncertainty_formula_header', self.language)}\n\n",
            )
            self.resultados_text.insert(
                tk.END,
                f"{get_string('uncertainty_calc', 'copy_latex_code', self.language)}\n\n",
            )
            self.resultados_text.insert(tk.END, f"{formula_incerteza}\n\n")
            self.formula_latex = formula_incerteza

            # Render LaTeX with additional error handling
            try:
                self._renderizar_formula_incerteza_na_interface(formula_incerteza)
                logging.debug("LaTeX rendering completed successfully")
            except Exception as e:
                logging.error(f"LaTeX rendering failed: {str(e)}")
                # Show error to user but don't stop the process
                messagebox.showerror(
                    title=get_string("uncertainty_calc", "error_title", self.language),
                    message=get_string(
                        "uncertainty_calc", "latex_render_error", self.language
                    ),
                )

        except sp.SympifyError as e:
            messagebox.showerror(
                title=get_string(
                    "uncertainty_calc", "formula_error_title", self.language
                ),
                message=f"{get_string('uncertainty_calc', 'invalid_formula', self.language)}: {str(e)}",
            )
        except ValueError as e:  # Catch specific errors for better feedback
            messagebox.showerror(
                title=get_string(
                    "uncertainty_calc", "value_error_title", self.language
                ),
                message=str(e),
            )
        except Exception as e:  # Catch all other potential errors
            messagebox.showerror(
                title=get_string("uncertainty_calc", "error_title", self.language),
                message=f"{get_string('uncertainty_calc', 'unexpected_error', self.language)}: {str(e)}",
            )

    def _renderizar_formula_incerteza_na_interface(self, formula_latex: str) -> None:
        """Render the uncertainty formula using matplotlib"""
        self._clear_latex_display()

        try:
            fig = Figure(figsize=(7, 2))
            ax: Axes = fig.add_subplot(111)
            ax.axis("off")
            # Try to render the LaTeX formula
            ax.text(
                0.5,
                0.5,
                f"${formula_latex}$",
                fontsize=16,
                ha="center",
                va="center",
            )
            fig.tight_layout(pad=0)

            canvas = FigureCanvasTkAgg(fig, master=self.latex_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            # If LaTeX rendering fails, show a simplified version
            logging.warning(f"LaTeX rendering failed: {str(e)}")
            try:
                fig = Figure(figsize=(7, 2))
                ax: Axes = fig.add_subplot(111)
                ax.axis("off")
                # Show a simple text version if LaTeX fails
                simple_text = "Uncertainty formula generated (LaTeX rendering failed)"
                ax.text(
                    0.5,
                    0.5,
                    simple_text,
                    fontsize=12,
                    ha="center",
                    va="center",
                )
                fig.tight_layout(pad=0)

                canvas = FigureCanvasTkAgg(fig, master=self.latex_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            except Exception:
                # If everything fails, just show an error message
                pass

            # Show error to user
            messagebox.showerror(
                title=get_string("uncertainty_calc", "error_title", self.language),
                message=get_string(
                    "uncertainty_calc", "latex_render_error_detailed", self.language
                ),
            )

    def exibir_formula_latex(self, formula_latex: str) -> None:
        """Display LaTeX formula in a separate window"""
        if not formula_latex.strip():
            messagebox.showinfo(
                title=get_string("uncertainty_calc", "notice_title", self.language),
                message=get_string(
                    "uncertainty_calc", "generate_formula", self.language
                ),
            )  # Already covered by line 6 ignore
            return

        janela = Toplevel(self.parent)
        janela.title(
            get_string("uncertainty_calc", "rendered_formula_title", self.language)
        )

        # Apply theme-adaptive background
        from app_files.utils.theme_manager import theme_manager

        janela.configure(bg=theme_manager.get_adaptive_color("background"))

        fig = Figure(figsize=(7, 2))
        ax: Axes = fig.add_subplot(111)
        ax.axis("off")
        ax.text(
            0.5,
            0.5,
            f"${formula_latex}$",
            fontsize=18,
            ha="center",
            va="center",
        )
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=janela)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill="both")

    def switch_language(self, language: str) -> None:
        """Update language for this component using selective updates"""
        self.language = language

        # Update all labels and buttons without destroying the UI
        self._update_operation_mode_labels()
        self._update_variable_frame_labels()
        self._update_formula_labels()
        self._update_button_texts()
        self._update_results_label()

        # Update interface mode-dependent text
        self.atualizar_interface()

    def _update_operation_mode_labels(self) -> None:
        """Update operation mode radio button labels"""
        # Find and update radio buttons in main_frame
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Label):
                current_text = widget.cget("text")
                # Check if it's the operation mode label
                if any(
                    x in current_text for x in ["Modo de operação", "Operation mode"]
                ):
                    widget.config(
                        text=get_string(
                            "uncertainty_calc", "operation_mode", self.language
                        )
                    )
            elif isinstance(widget, ttk.Radiobutton):
                # Update radio button texts based on their values
                value = widget.cget("value")
                if value == "calcular":
                    widget.config(
                        text=get_string(
                            "uncertainty_calc", "calc_value_uncertainty", self.language
                        )
                    )
                elif value == "gerar":
                    widget.config(
                        text=get_string(
                            "uncertainty_calc",
                            "generate_uncertainty_formula",
                            self.language,
                        )
                    )

    def _update_variable_frame_labels(self) -> None:
        """Update variable frame labels"""
        if hasattr(self, "var_frame") and self.var_frame:
            # Update frame title
            self.var_frame.config(
                text=get_string("uncertainty_calc", "variables", self.language)
            )

            # Update number of variables label
            if hasattr(self, "num_var_frame"):
                for widget in self.num_var_frame.winfo_children():
                    if isinstance(widget, ttk.Label):
                        widget.config(
                            text=get_string(
                                "uncertainty_calc", "number_of_variables", self.language
                            )
                        )
                    elif isinstance(widget, ttk.Button):
                        widget.config(
                            text=get_string(
                                "uncertainty_calc", "create_fields", self.language
                            )
                        )

    def _update_formula_labels(self) -> None:
        """Update formula section labels"""
        # Find formula frame and update its labels
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Frame) and widget != self.var_frame:
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label):
                        current_text = child.cget("text")
                        if any(x in current_text for x in ["Fórmula", "Formula"]):
                            child.config(
                                text=get_string(
                                    "uncertainty_calc", "formula", self.language
                                )
                            )
                    elif isinstance(child, ttk.Button):
                        # Help button
                        child.config(
                            text=get_string(
                                "uncertainty_calc", "help_button_text", self.language
                            )
                        )

    def _update_button_texts(self) -> None:
        """Update button texts based on current mode"""
        if hasattr(self, "botao_calcular"):
            mode = self.modo_var.get()
            if mode == "calcular":
                self.botao_calcular.config(
                    text=get_string("uncertainty_calc", "calculate", self.language)
                )
            else:
                self.botao_calcular.config(
                    text=get_string(
                        "uncertainty_calc", "generate_formula", self.language
                    )
                )

    def _update_results_label(self) -> None:
        """Update results section label"""
        # Find the results label
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, ttk.Label):
                current_text = widget.cget("text")
                if any(x in current_text for x in ["Resultados", "Results"]):
                    widget.config(
                        text=get_string("uncertainty_calc", "results", self.language)
                    )
                    break

    def show_formula_help(self) -> None:
        """Display comprehensive help information about formula input and available functions"""
        help_window = Toplevel(self.parent)
        help_window.title(
            get_string("uncertainty_calc", "formula_help_title", self.language)
        )
        help_window.geometry("700x600")

        # Apply theme-adaptive background
        from app_files.utils.theme_manager import theme_manager

        help_window.configure(bg=theme_manager.get_adaptive_color("background"))

        # Make the window modal
        help_window.grab_set()

        # Create a scrolled text widget for the help content
        help_text = ScrolledText(
            help_window,
            wrap=tk.WORD,
            width=80,
            height=30,
            bg=theme_manager.get_adaptive_color("background"),
            fg=theme_manager.get_adaptive_color("foreground"),
        )
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Define help content sections using translations
        content = get_help("uncertainty_calc", "formula_help_full", self.language)
        help_text.insert(tk.END, content)
        help_text.configure(state=tk.DISABLED)  # Make read-only

    def _validate_variable_names(self, variables: list[str]) -> bool:
        """Validate that variable names don't conflict with mathematical functions"""
        # Mathematical function names that could cause conflicts with SymPy
        reserved_names = {
            # Trigonometric functions
            "sin",
            "cos",
            "tan",
            "cot",
            "sec",
            "csc",
            "asin",
            "acos",
            "atan",
            "acot",
            "asec",
            "acsc",
            "arcsin",
            "arccos",
            "arctan",
            "arccot",
            "arcsec",
            "arccsc",
            "atan2",
            # Hyperbolic functions
            "sinh",
            "cosh",
            "tanh",
            "coth",
            "sech",
            "csch",
            "asinh",
            "acosh",
            "atanh",
            "acoth",
            "asech",
            "acsch",
            # Logarithmic and exponential functions
            "exp",
            "log",
            "ln",
            "log10",
            "log2",
            "logb",
            # Power and root functions
            "sqrt",
            "cbrt",
            "root",
            "pow",
            # Special functions
            "abs",
            "sign",
            "floor",
            "ceiling",
            "ceil",
            "frac",
            "gamma",
            "erf",
            "erfc",
            "beta",
            "min",
            "max",
            # Constants that SymPy recognizes
            "pi",
            "e",
            "I",
            "E",
            "S",
            "N",
            "C",
            "O",
            "inf",
            "infinity",
            "oo",
            "nan",
            "GR",
            "EG",
            "Cat",
            "j",
            "TC",
        }
        # Characters that are definitely problematic
        invalid_chars = set("`()[]{};=**/^\\:,@#$%!&|~'\"")
        seen = set()
        for var in variables:
            var_original = var.strip()
            var_lower = var_original.lower()
            # Check if empty
            if not var_original:
                messagebox.showerror(
                    title=get_string(
                        "uncertainty_calc", "input_error_title", self.language
                    ),
                    message=get_string(
                        "uncertainty_calc", "empty_variable_name", self.language
                    ),
                )
                return False
            # Check for invalid characters
            if any(c in invalid_chars for c in var_original):
                messagebox.showerror(
                    title=get_string(
                        "uncertainty_calc", "input_error_title", self.language
                    ),
                    message=get_string(
                        "uncertainty_calc", "invalid_variable_name", self.language
                    )
                    + f": {var_original}",
                )
                return False
            # Check for reserved names
            if var_lower in reserved_names:
                messagebox.showerror(
                    title=get_string(
                        "uncertainty_calc", "input_error_title", self.language
                    ),
                    message=get_string(
                        "uncertainty_calc", "reserved_variable_name", self.language
                    )
                    + f": {var_original}",
                )
                return False
            # Check for duplicates
            if var_lower in seen:
                messagebox.showerror(
                    title=get_string(
                        "uncertainty_calc", "input_error_title", self.language
                    ),
                    message=get_string(
                        "uncertainty_calc", "duplicate_variable_name", self.language
                    )
                    + f": {var_original}",
                )
                return False
            seen.add(var_lower)
        return True
