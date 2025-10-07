"""Custom function management for curve fitting"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from typing import List, Optional, Tuple, TYPE_CHECKING, Any
from app_files.utils.lazy_loader import lazy_import
from app_files.utils import error_handler
from app_files.utils.translations.api import get_string
from .models import CustomFunction

theme_manager = lazy_import("app_files.utils.theme_manager", "theme_manager")

if TYPE_CHECKING:
    from app_files.gui.ajuste_curva.main_gui import AjusteCurvaFrame
    from app_files.gui.ajuste_curva.plot_manager import PlotManager
    from app_files.utils.user_preferences import UserPreferencesManager


class CustomFunctionManager:
    """Manages custom functions added to the plot"""

    def __init__(
        self,
        parent: "AjusteCurvaFrame",
        plot_manager: "PlotManager",
        user_preferences: "UserPreferencesManager",
    ):
        """
        Initialize the function manager

        Args:
            parent: The main AjusteCurvaFrame instance that owns this manager
            plot_manager: The plot manager instance
            user_preferences: The user preferences instance
        """
        self.parent = parent
        self.plot_manager = plot_manager
        self.user_preferences = user_preferences
        self.language = self.user_preferences.get_language()

        self.function_entry: Optional[ttk.Entry] = None
        self.color_button: Optional[ttk.Button] = None
        self.color_entry: Optional[ttk.Entry] = None
        self.add_button: Optional[ttk.Button] = None
        self.functions_listbox: Optional[tk.Listbox] = (
            None  # Keep for backward compatibility
        )
        self.functions_tree: Optional[ttk.Treeview] = (
            None  # New tree view with checkboxes
        )
        self.remove_button: Optional[ttk.Button] = None
        self.clear_button: Optional[ttk.Button] = None
        self.plot_button: Optional[ttk.Button] = None
        self.x_min_entry: Optional[ttk.Entry] = None
        self.x_max_entry: Optional[ttk.Entry] = None

        self.instruction_label: Optional[ttk.Label] = None
        self.y_equals_label: Optional[ttk.Label] = None
        self.from_label: Optional[ttk.Label] = None
        self.to_label: Optional[ttk.Label] = None

        self.functions: List[CustomFunction] = []
        self.selected_color: str = "#000000"
        self.color_preview: Optional[tk.Label] = None

    def setup_ui(self, parent: ttk.Frame, maximize_scrollbox: bool = False) -> None:
        """Configura a interface gráfica para o gerenciador de funções personalizadas.

        Args:
            parent: The parent frame where UI elements will be placed
            maximize_scrollbox: Whether to maximize the scrollbox height for better visibility
        """
        # Configure parent to allow expansion
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)  # Make the functions list expandable

        # Header section with instruction
        header_frame = ttk.LabelFrame(
            parent,
            text=get_string("custom_function", "custom_functions", self.language),
            padding=10,
        )
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        header_frame.columnconfigure(0, weight=1)

        self.instruction_label = ttk.Label(
            header_frame,
            text=get_string("custom_function", "custom_funcs_desc", self.language),
            font=("TkDefaultFont", 9),
        )
        self.instruction_label.grid(row=0, column=0, sticky="w")

        # Main content area with two columns
        main_frame = ttk.Frame(parent)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        main_frame.columnconfigure(0, weight=2)  # Functions list gets more space
        main_frame.columnconfigure(1, weight=1)  # Input panel gets less space
        main_frame.rowconfigure(0, weight=1)
        # Left panel - Functions list
        list_frame = ttk.LabelFrame(
            main_frame,
            text=get_string("custom_function", "function_list", self.language),
            padding=5,
        )
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Functions list with checkboxes using Treeview
        list_container = ttk.Frame(list_frame)
        list_container.grid(row=0, column=0, sticky="nsew")
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)
        # Create Treeview for functions with checkboxes
        columns = ("enabled", "function", "range", "color")
        self.functions_tree = ttk.Treeview(
            list_container,
            columns=columns,
            show="tree headings",
            height=18 if maximize_scrollbox else 12,
            selectmode=tk.BROWSE,
        )
        # Configure columns
        self.functions_tree.heading("#0", text="", anchor=tk.W)
        self.functions_tree.heading(
            "enabled",
            text=get_string("custom_function", "enabled_column", self.language),
            anchor=tk.CENTER,
        )
        self.functions_tree.heading(
            "function",
            text=get_string("custom_function", "function_column", self.language),
            anchor=tk.W,
        )
        self.functions_tree.heading(
            "range",
            text=get_string("custom_function", "range_column", self.language),
            anchor=tk.CENTER,
        )
        self.functions_tree.heading(
            "color",
            text=get_string("custom_function", "color_column", self.language),
            anchor=tk.CENTER,
        )
        # Set column widths
        self.functions_tree.column("#0", width=0, stretch=False)  # Hide tree column
        self.functions_tree.column("enabled", width=30, stretch=False)
        self.functions_tree.column("function", width=120, stretch=False)
        self.functions_tree.column("range", width=70, stretch=False)
        self.functions_tree.column("color", width=60, stretch=True)

        self.functions_tree.grid(row=0, column=0, sticky="nsew")
        # Add scrollbar
        tree_scrollbar = ttk.Scrollbar(
            list_container, orient="vertical", command=self.functions_tree.yview
        )
        tree_scrollbar.grid(row=0, column=1, sticky="ns")
        self.functions_tree.config(yscrollcommand=tree_scrollbar.set)
        # Bind events for checkbox handling
        self.functions_tree.bind("<Button-1>", self._on_tree_click)
        # List management buttons
        list_buttons_frame = ttk.Frame(list_frame)
        list_buttons_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        list_buttons_frame.columnconfigure(0, weight=1)
        list_buttons_frame.columnconfigure(1, weight=1)
        list_buttons_frame.columnconfigure(2, weight=1)

        self.remove_button = ttk.Button(
            list_buttons_frame,
            text=get_string("custom_function", "remove_selected", self.language),
            command=self.remove_selected_function,
            width=12,
        )
        self.remove_button.grid(row=0, column=0, padx=(0, 2), sticky="ew")

        self.clear_button = ttk.Button(
            list_buttons_frame,
            text=get_string("custom_function", "clear_all", self.language),
            command=self.clear_all_functions,
            width=12,
        )
        self.clear_button.grid(row=0, column=1, padx=2, sticky="ew")

        self.plot_button = ttk.Button(
            list_buttons_frame,
            text=get_string("custom_function", "plot_all", self.language),
            command=self.update_plot,
            width=12,
        )
        self.plot_button.grid(row=0, column=2, padx=(2, 0), sticky="ew")

        # Right panel - Function input
        input_frame = ttk.LabelFrame(
            main_frame,
            text=get_string("custom_function", "add_function", self.language),
            padding=10,
        )
        input_frame.grid(row=0, column=1, sticky="nsew")
        input_frame.columnconfigure(1, weight=1)

        # Function expression input
        expr_frame = ttk.Frame(input_frame)
        expr_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        expr_frame.columnconfigure(1, weight=1)

        self.y_equals_label = ttk.Label(
            expr_frame,
            text=get_string("custom_function", "y_equals", self.language),
            font=("TkDefaultFont", 10, "bold"),
        )
        self.y_equals_label.grid(row=0, column=0, padx=(0, 5), sticky="w")

        self.function_entry = ttk.Entry(expr_frame, font=("Consolas", 10))
        self.function_entry.grid(row=0, column=1, sticky="ew")
        self.function_entry.bind("<Return>", lambda e: self.add_function())
        example_label = ttk.Label(
            input_frame,
            text=get_string("custom_function", "function_example", self.language),
            font=("TkDefaultFont", 8),
            foreground=theme_manager.get_adaptive_color("text_info"),
        )
        example_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # Color selection section
        color_frame = ttk.LabelFrame(
            input_frame,
            text=get_string("custom_function", "color", self.language),
            padding=5,
        )
        color_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        color_frame.columnconfigure(1, weight=1)

        self.color_button = ttk.Button(
            color_frame,
            text=get_string("custom_function", "choose_color", self.language),
            command=self._choose_color,
            width=10,
        )
        self.color_button.grid(row=0, column=0, padx=(0, 5))

        self.color_entry = ttk.Entry(color_frame, width=15, font=("Consolas", 9))
        self.color_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        self.color_entry.insert(0, self.selected_color)

        # Color preview - made slightly larger
        self.color_preview = tk.Label(
            color_frame,
            width=4,
            height=1,
            bg=self.selected_color,
            relief="solid",
            borderwidth=1,
        )
        self.color_preview.grid(row=0, column=2, padx=(5, 0))

        # Bind color entry changes to update preview
        self.color_entry.bind("<KeyRelease>", self._update_color_preview)

        # Interval section
        interval_frame = ttk.LabelFrame(
            input_frame,
            text=get_string("custom_function", "interval", self.language),
            padding=5,
        )
        interval_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # From input
        from_frame = ttk.Frame(interval_frame)
        from_frame.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.from_label = ttk.Label(
            from_frame, text=get_string("custom_function", "from", self.language)
        )
        self.from_label.grid(row=0, column=0, sticky="w")
        self.x_min_entry = ttk.Entry(from_frame, width=12)
        self.x_min_entry.grid(row=1, column=0, sticky="ew")

        # To input
        to_frame = ttk.Frame(interval_frame)
        to_frame.grid(row=0, column=1, sticky="ew")

        self.to_label = ttk.Label(
            to_frame, text=get_string("custom_function", "to", self.language)
        )
        self.to_label.grid(row=0, column=0, sticky="w")
        self.x_max_entry = ttk.Entry(to_frame, width=12)
        self.x_max_entry.grid(row=1, column=0, sticky="ew")
        # Buttons frame for Add and Help
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=0)

        # Add button (prominent)
        self.add_button = ttk.Button(
            buttons_frame,
            text=get_string("custom_function", "add_function", self.language),
            command=self.add_function,
            style="Accent.TButton",
        )
        self.add_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # Help button for custom functions
        help_button = ttk.Button(
            buttons_frame,
            text=get_string("custom_function", "help", self.language),
            command=lambda: self.show_custom_function_help(
                input_frame.winfo_toplevel()
            ),
            width=8,
        )
        help_button.grid(row=0, column=1, sticky="e")
        # Load existing functions
        self.load_functions()

        # Configure tree view styles for enabled/disabled items
        self.functions_tree.tag_configure(
            "enabled", foreground=theme_manager.get_adaptive_color("foreground")
        )
        self.functions_tree.tag_configure(
            "disabled", foreground=theme_manager.get_adaptive_color("text_muted")
        )

    def _update_color_preview(self, _event: Any = None) -> None:
        """Update the color preview based on the color entry value."""
        try:
            if self.color_entry:
                color = self.color_entry.get().strip()
                if color and hasattr(self, "color_preview") and self.color_preview:
                    # Validate color format (basic validation)
                    if color.startswith("#") and len(color) == 7:
                        self.color_preview.config(bg=color)
                        self.selected_color = color
        except (tk.TclError, AttributeError):
            # Invalid color, keep the current color
            pass

    def _choose_color(self) -> None:
        """Abre o seletor de cores e atualiza a cor selecionada."""
        title = get_string(
            "custom_function", "choose_color", self.language, fallback="Choose Color"
        )
        color = colorchooser.askcolor(initialcolor=self.selected_color, title=title)
        if color and color[1]:
            self.selected_color = color[1]
            if self.color_entry:
                self.color_entry.delete(0, tk.END)
                self.color_entry.insert(0, self.selected_color)
            if hasattr(self, "color_preview") and self.color_preview:
                self.color_preview.config(bg=self.selected_color)

    def add_function(self) -> None:
        """Adds a custom function to the list of functions to be plotted"""
        if (
            not self.function_entry
            or not self.color_entry
            or not self.x_min_entry
            or not self.x_max_entry
        ):
            return

        func_text = self.function_entry.get().strip()
        color = self.color_entry.get().strip()
        x_min_str = self.x_min_entry.get().strip()
        x_max_str = self.x_max_entry.get().strip()
        if not func_text:
            error_handler.handle_error(
                get_string("custom_function", "error", self.language, fallback="Error"),
                get_string(
                    "custom_function",
                    "function_cannot_be_empty",
                    self.language,
                    fallback="Function cannot be empty",
                ),
            )
            return
        try:
            x_min = float(x_min_str) if x_min_str else None
            x_max = float(x_max_str) if x_max_str else None
        except ValueError:
            error_handler.handle_error(
                get_string("custom_function", "error", self.language, fallback="Error"),
                get_string(
                    "custom_function",
                    "invalid_interval",
                    self.language,
                    fallback="Invalid interval",
                ),
            )
            return
        new_function = CustomFunction(
            func_text=func_text, color=color, x_min=x_min, x_max=x_max, enabled=True
        )
        self.functions.append(new_function)
        if self.functions_listbox:
            self.functions_listbox.insert(tk.END, f"{func_text} (Color: {color})")
        if self.functions_tree:
            item_id = str(len(self.functions) - 1)
            checkbox = "☑"
            range_text = self._format_function_range(self.functions[-1])
            self.functions_tree.insert(
                "", "end", iid=item_id, values=(checkbox, func_text, range_text, color)
            )
            self.functions_tree.item(item_id, tags=("enabled",))
        self._save_functions()
        self.update_plot()

    def remove_selected_function(self) -> None:
        """Remove the selected function from the list."""
        selected_index = -1
        if self.functions_tree:
            selection = self.functions_tree.selection()
            if selection:
                try:
                    selected_index = int(selection[0])
                except ValueError:
                    pass
        if selected_index == -1 and self.functions_listbox:
            selected_indices: Tuple[int, ...] = self.functions_listbox.curselection()
            if selected_indices:
                selected_index = int(selected_indices[0])
        if selected_index == -1:
            error_handler.handle_error(
                get_string(
                    "custom_function", "warning", self.language, fallback="Warning"
                ),
                get_string(
                    "custom_function",
                    "no_function_selected",
                    self.language,
                    fallback="No function selected",
                ),
            )
            return
        try:
            del self.functions[selected_index]
            if self.functions_listbox:
                self.functions_listbox.delete(selected_index)
            if self.functions_tree:
                self._rebuild_tree_view()
            self._save_functions()
            self.update_plot()
        except (ValueError, IndexError):
            return

    def clear_all_functions(self) -> None:
        """Clear all custom functions."""
        if not self.functions_listbox and not self.functions_tree:
            return
        if not self.functions:
            return

        confirm = messagebox.askyesno(    # Pylance: tkinter dynamic type
            get_string("custom_function", "confirm", self.language, fallback="Confirm"),
            get_string(
                "custom_function",
                "clear_all_confirm",
                self.language,
                fallback="Clear all functions?",
            ),
        )
        if confirm:
            if self.functions_listbox:
                self.functions_listbox.delete(0, tk.END)
            if self.functions_tree:
                for item in self.functions_tree.get_children():
                    self.functions_tree.delete(item)
            self.functions.clear()
            self._save_functions()
            self.update_plot()

    def update_plot(self) -> None:
        """Update the plot with custom functions."""
        # Only plot enabled functions
        enabled_functions = [func for func in self.functions if func.enabled]
        self.plot_manager.plot_custom_functions(enabled_functions)

    def _save_functions(self) -> None:
        """Save functions to session."""
        # Session saving has been disabled
        # pass  # Removed unnecessary pass

    def load_functions(self) -> None:
        """Load functions from session."""
        # Session loading has been disabled
        # pass  # Removed unnecessary pass

    def save_functions(self) -> None:
        """Save the current functions to session state.
        This is a public method that can be called from outside.
        """
        self._save_functions()

    def get_supported_functions_help(self) -> str:
        """Get help text for supported mathematical functions in custom functions
        Returns:
            Formatted help text describing all supported functions
        """
        return get_string(
            "custom_function_help",
            "help_custom_functions_content",
            self.language,
            fallback="Help content not available",
        )

    def show_custom_function_help(self, parent_window: "tk.Tk | tk.Toplevel") -> None:
        """Show help dialog for custom functions

        Args:
            parent_window: Parent window for the dialog
        """
        help_window = tk.Toplevel(parent_window)
        help_window.title(
            get_string(
                "custom_function",
                "help_custom_functions_title",
                self.language,
                fallback="Custom Functions Help",
            )
        )
        help_window.geometry("700x600")
        help_window.resizable(True, True)
        help_window.configure(bg=theme_manager.get_adaptive_color("background"))
        help_window.transient(parent_window)
        help_window.grab_set()
        frame = ttk.Frame(help_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget = tk.Text(
            frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=theme_manager.get_adaptive_color("background"),
            fg=theme_manager.get_adaptive_color("foreground"),
        )
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        help_text = self.get_supported_functions_help()
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
        button_frame = ttk.Frame(help_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        close_button = ttk.Button(
            button_frame,
            text=get_string(
                "custom_function", "close", self.language, fallback="Close"
            ),
            command=help_window.destroy,
        )
        close_button.pack(side=tk.RIGHT)
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (help_window.winfo_width() // 2)
        y = (help_window.winfo_screenheight() // 2) - (help_window.winfo_height() // 2)
        help_window.geometry(f"+{x}+{y}")
        help_window.focus_set()

    def _on_tree_click(self, event: tk.Event) -> None:
        """Handle click events on the tree view to toggle checkboxes"""
        if not self.functions_tree:
            return

        # Get the clicked region
        region = self.functions_tree.identify_region(event.x, event.y)

        if region == "cell":
            column = self.functions_tree.identify_column(event.x)
            item = self.functions_tree.identify_row(event.y)
            # If clicked on the enabled column (checkbox)
            if column == "#1" and item:  # #1 is the "enabled" column
                self._toggle_function_enabled(item)

    def _toggle_function_enabled(self, item: str) -> None:
        """Toggle the enabled state of a function"""
        try:
            item_index = int(item)  # Tree items use 0-indexed IDs
            if 0 <= item_index < len(self.functions):
                # Toggle the enabled state
                self.functions[item_index].enabled = not self.functions[
                    item_index
                ].enabled

                # Update the tree view display
                self._update_tree_item(item, item_index)

                # Save and update plot
                self._save_functions()
                self.update_plot()
        except ValueError:
            pass

    def _update_tree_item(self, item: str, index: int) -> None:
        """Update a single tree view item"""
        if not self.functions_tree or index >= len(self.functions):
            return

        func = self.functions[index]
        checkbox = "☑" if func.enabled else "☐"
        range_text = self._format_function_range(func)

        # Update the tree item
        self.functions_tree.item(
            item, values=(checkbox, func.func_text, range_text, func.color)
        )
        # Apply style based on enabled state
        if func.enabled:
            self.functions_tree.item(item, tags=("enabled",))
        else:
            self.functions_tree.item(item, tags=("disabled",))

    def _rebuild_tree_view(self) -> None:
        """Rebuild the tree view to maintain proper indexing after changes"""
        if not self.functions_tree:
            return
            # Clear existing items
        for item in self.functions_tree.get_children():
            self.functions_tree.delete(item)
            # Add all functions back
        for i, func in enumerate(self.functions):
            item_id = str(i)  # Use 0-indexed function index
            checkbox = "☑" if func.enabled else "☐"
            range_text = self._format_function_range(func)

            self.functions_tree.insert(
                "",
                "end",
                iid=item_id,
                values=(checkbox, func.func_text, range_text, func.color),
            )

            # Apply appropriate style
            if func.enabled:
                self.functions_tree.item(item_id, tags=("enabled",))
            else:
                self.functions_tree.item(item_id, tags=("disabled",))
        # Configure tag styles if not already done
        try:
            self.functions_tree.tag_configure("enabled", foreground="black")
            self.functions_tree.tag_configure("disabled", foreground="gray")
        except tk.TclError:
            pass  # Tags might already be configured

    def _format_function_range(self, func: "CustomFunction") -> str:
        """Format the range of a function for display in the tree"""
        if func.x_min is not None and func.x_max is not None:
            return f"[{func.x_min:.1f}, {func.x_max:.1f}]"
        if func.x_min is not None:
            return f"[{func.x_min:.1f}, ∞)"
        if func.x_max is not None:
            return f"(-∞, {func.x_max:.1f}]"
        return get_string(
            "custom_function", "auto_range", self.language, fallback="Auto"
        )  # Default range determined by plot
