"""UI Builder component for curve fitting"""

from tkinter import ttk
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from typing import TYPE_CHECKING, Optional  # Ensure Optional is imported
from idlelib.tooltip import Hovertip

from app_files.utils.translations.api import get_string

if TYPE_CHECKING:  # Added TYPE_CHECKING block
    from .main_gui import AjusteCurvaFrame


class UIBuilder:
    """Handles building the UI components for curve fitting"""

    def __init__(
        self, parent: "AjusteCurvaFrame", language: str = "pt"
    ) -> None:  # Added type hints
        """Initialize the UI builder

        Args:
            parent: Parent AjusteCurvaFrame instance
            language: Interface language
        """
        self.parent = parent
        self.language = language

        # Initialize UI element attributes with defaults
        self.data_text = None
        self.results_text = None
        self.title_entry = None
        self.x_label_var = None  # Will be created lazily
        self.y_label_var = None  # Will be created lazily
        self.x_scale = None
        self.y_scale = None
        self.file_entry = None
        self.equation_entry = None
        self.model_selector = None
        self.num_points_entry = None
        self.max_iter_entry = None
        self.progress_var = None  # Will be created lazily
        self.status_label = None
        self.save_graph_option = None  # Will be created lazily
        self.plot_area_frame: Optional[ttk.LabelFrame] = (
            None  # Ensure this line is present and correct
        )

        # Fitting method selection
        self.fitting_method_var = None  # Will be created lazily
        self.fitting_method_selector = None

    def _ensure_string_vars(self) -> None:
        """Ensure all StringVar instances are created"""
        if self.x_label_var is None:
            self.x_label_var = tk.StringVar(self.parent, value="X")
        if self.y_label_var is None:
            self.y_label_var = tk.StringVar(self.parent, value="Y")
        if self.progress_var is None:
            self.progress_var = tk.IntVar(self.parent)
        if self.save_graph_option is None:
            self.save_graph_option = tk.StringVar(self.parent, value="full")
        if self.fitting_method_var is None:
            self.fitting_method_var = tk.StringVar(self.parent, value="odr")

    def setup_ui(self):
        """Set up the complete user interface"""
        # Ensure StringVar instances are created
        self._ensure_string_vars()

        # Create main frame
        self.main_frame = ttk.Frame(self.parent)  # Changed parent
        self.main_frame.grid(row=0, column=0, sticky="nsew")  # Changed pack to grid
        # Configure main frame with 2 columns instead of 3
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)  # Control panel
        self.main_frame.columnconfigure(
            1, weight=4
        )  # Plot panel (much larger)# Left panel for controls - using grid
        self.control_frame = ttk.LabelFrame(
            self.main_frame,
            text=get_string(
                "curve_fitting", "controls", self.language, fallback="Controles"
            ),
            padding="5",
            width=150,
        )
        self.control_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.control_frame.grid_propagate(False)  # Prevent shrinking
        # Configure control_frame for its child (control_paned)
        self.control_frame.rowconfigure(0, weight=1)
        self.control_frame.columnconfigure(
            0, weight=1
        )  # Center panel for plots (this is where AjusteCurvaFrame will place its canvas)
        # We create it here so AjusteCurvaFrame can use it as a master for the canvas.
        # UIBuilder itself no longer tries to manage/recreate the canvas.
        self.plot_area_frame = ttk.LabelFrame(
            self.main_frame,
            text=get_string("curve_fitting", "plot", self.language, fallback="Gráfico"),
            padding="5",
        )  # This frame will be the master for the canvas
        self.plot_area_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.plot_area_frame.grid_propagate(False)  # Prevent shrinking
        self.plot_area_frame.rowconfigure(
            0, weight=1
        )  # Allow canvas to expand within plot_area_frame
        self.plot_area_frame.columnconfigure(
            0, weight=1
        )  # Allow canvas to expand within plot_area_frame

        # Create vertical paned window for control sections
        control_paned = ttk.PanedWindow(self.control_frame, orient=tk.VERTICAL)
        control_paned.grid(
            row=0, column=0, sticky="nsew"
        )  # Changed pack to grid        # Setup individual sections
        self._setup_data_input_frame(control_paned)
        self._setup_parameters_frame(control_paned)
        self._setup_graph_settings_frame(control_paned)
        self._setup_action_buttons_frame(control_paned)
        self._setup_progress_frame(control_paned)
        self._setup_results_frame(control_paned)

    def _setup_data_input_frame(self, control_paned: ttk.PanedWindow) -> None:
        """Set up the data input frame"""
        self.data_frame = ttk.LabelFrame(
            control_paned,
            text=get_string(
                "curve_fitting",
                "data_input",
                self.language,
                fallback="Entrada de dados",
            ),
        )
        # Add data input frame to control_paned
        control_paned.add(self.data_frame, weight=1)

        # Configure data frame to expand properly - give more weight to the preview row
        self.data_frame.columnconfigure(1, weight=1)
        self.data_frame.rowconfigure(
            2, weight=1
        )  # Row 2 is the preview frame, give it all the vertical space

        # File selection with more compact layout
        file_input_frame = ttk.Frame(self.data_frame)
        file_input_frame.grid(
            row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=2
        )
        file_input_frame.columnconfigure(1, weight=1)

        ttk.Label(
            file_input_frame,
            text=get_string(
                "curve_fitting", "data_file", self.language, fallback="Arquivo de dados"
            ),
        ).grid(row=0, column=0, sticky="w")
        self.file_entry = ttk.Entry(file_input_frame, width=30)
        self.file_entry.grid(row=0, column=1, padx=5, sticky="ew")
        ttk.Button(
            file_input_frame,
            text=get_string(
                "curve_fitting", "browse", self.language, fallback="Procurar"
            ),
            command=self.parent.browse_file,
            width=10,
        ).grid(row=0, column=2)

        # Format display and override controls - compact layout
        format_frame = ttk.Frame(self.data_frame)
        format_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=1)
        format_frame.columnconfigure(0, weight=1)

        self.format_label = ttk.Label(
            format_frame,
            text=get_string("curve_fitting", "no_file_loaded", self.language),
            foreground="gray",
            font=("", 9),
        )
        self.format_label.grid(row=0, column=0, sticky="w")

        self.reinterpret_btn = ttk.Button(
            format_frame,
            text="⚙",  # Gear icon
            command=self.parent.show_format_override_dialog,
            state="disabled",
            width=3,
        )
        self.reinterpret_btn.grid(row=0, column=1, sticky="e", padx=2)

        # Add tooltip for the button (using hint if available, otherwise basic)
        self.reinterpret_tooltip = None
        try:
            self.reinterpret_tooltip = Hovertip(
                self.reinterpret_btn,
                get_string("curve_fitting", "swap_columns_tooltip", self.language),
            )
        except (ImportError, AttributeError):
            self.reinterpret_tooltip = None  # Tooltip not available
        # Data preview frame that expands with parent - takes all available vertical space
        self.preview_frame = ttk.LabelFrame(
            self.data_frame,
            text=get_string(
                "curve_fitting",
                "loaded_data",
                self.language,
                fallback="Dados carregados",
            ),
        )
        self.preview_frame.grid(
            row=2, column=0, columnspan=3, sticky="nsew", padx=5, pady=5
        )
        self.preview_frame.rowconfigure(0, weight=1)
        self.preview_frame.columnconfigure(0, weight=1)

        # Import theme manager for adaptive colors
        from app_files.utils.theme_manager import theme_manager

        self.data_text = ScrolledText(
            self.preview_frame,
            height=15,  # Increased from 8 to 15 for larger display
            width=50,
            bg=theme_manager.get_adaptive_color("background"),
            fg=theme_manager.get_adaptive_color("foreground"),
        )
        self.data_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    def _setup_parameters_frame(self, control_paned: ttk.PanedWindow) -> None:
        """Set up the parameters frame"""
        self.params_frame = ttk.LabelFrame(
            control_paned,
            text=get_string(
                "curve_fitting",
                "fitting_parameters",
                self.language,
                fallback="Parâmetros de ajuste",
            ),
        )
        # Add parameters frame to control_paned
        control_paned.add(self.params_frame, weight=1)

        # Model presets - More compact layout
        self.params_frame.columnconfigure(1, weight=1)

        # Split the parameters frame into left and right sections
        left_params_frame = ttk.Frame(self.params_frame)
        left_params_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)
        left_params_frame.columnconfigure(1, weight=1)

        right_params_frame = ttk.Frame(self.params_frame)
        right_params_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=2)
        right_params_frame.columnconfigure(1, weight=1)
        # Left side - Model selection and equation
        ttk.Label(
            left_params_frame,
            text=get_string("curve_fitting", "model", self.language, fallback="Modelo"),
        ).grid(row=0, column=0, sticky="w")
        self.model_selector = ttk.Combobox(
            left_params_frame,
            values=list(self.parent.model_manager.preset_models.keys()),
            state="readonly",
            width=30,
        )  # Increased width from 20 to 30
        self.model_selector.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        def _on_combobox_selected_callback(event: tk.Event) -> None:
            self.parent.apply_preset_model(event)

        self.model_selector.bind("<<ComboboxSelected>>", _on_combobox_selected_callback)

        ttk.Label(
            left_params_frame,
            text=get_string(
                "curve_fitting", "equation", self.language, fallback="Equação"
            ),
        ).grid(row=1, column=0, sticky="w")
        self.equation_entry = ttk.Entry(
            left_params_frame, width=30
        )  # Increased width from 20 to 30
        self.equation_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.equation_entry.bind("<KeyRelease>", self.parent.validate_equation)
        self.equation_entry.bind(
            "<FocusOut>", lambda e: self.parent.update_estimates_frame()
        )

        # Fitting method selection
        ttk.Label(
            left_params_frame,
            text=get_string(
                "curve_fitting",
                "fitting_method",
                self.language,
                fallback="Método de ajuste",
            ),
        ).grid(row=2, column=0, sticky="w")
        self.fitting_method_var = tk.StringVar(self.parent, value="odr")
        self.fitting_method_selector = ttk.Combobox(
            left_params_frame,
            textvariable=self.fitting_method_var,
            values=[
                get_string(
                    "curve_fitting", "odr_method", self.language, fallback="ODR"
                ),
                get_string(
                    "curve_fitting",
                    "least_squares_method",
                    self.language,
                    fallback="Mínimos Quadrados",
                ),
                get_string(
                    "curve_fitting", "robust_method", self.language, fallback="Robusto"
                ),
                get_string(
                    "curve_fitting",
                    "bootstrap_method",
                    self.language,
                    fallback="Bootstrap",
                ),
                get_string(
                    "curve_fitting",
                    "bayesian_method",
                    self.language,
                    fallback="Bayesiano",
                ),
            ],
            state="readonly",
            width=30,
        )
        self.fitting_method_selector.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.fitting_method_selector.current(0)  # Default to ODR
        # Bind method selection change - will be connected after main GUI setup
        self.fitting_method_selector.bind(
            "<<ComboboxSelected>>", lambda e: self.parent.on_fitting_method_changed(e)
        )
        # Add "More Configs" and "Help" buttons
        buttons_frame = ttk.Frame(self.params_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=0)

        more_configs_button = ttk.Button(
            buttons_frame,
            text=get_string("curve_fitting", "more_configs", self.language),
            command=self.parent.show_advanced_config,
            width=20,  # Set smaller fixed width
        )
        more_configs_button.grid(row=0, column=0, sticky="w")
        # Always add help button for models; disable if show_model_help does not exist
        help_text = get_string(
            "curve_fitting", "help_models", self.language
        )
        model_help_button = ttk.Button(
            buttons_frame, text=f"💡 {help_text}", width=16  # Add bulb icon
        )
        if hasattr(self.parent.model_manager, "show_model_help"):
            model_help_button.config(
                command=lambda: self.parent.model_manager.show_model_help(self.parent)
            )
        else:
            model_help_button.config(state="disabled")
        model_help_button.grid(row=0, column=1, sticky="e", padx=(5, 0))
        # TODO: Implement show_model_help in ModelManager if model help is needed

        # Numerical settings frame
        num_settings_frame = ttk.Frame(self.params_frame)
        num_settings_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")

        ttk.Label(
            num_settings_frame,
            text=get_string("curve_fitting", "max_iterations", self.language),
        ).grid(row=0, column=0, padx=5)
        self.max_iter_entry = ttk.Entry(num_settings_frame, width=8)
        self.max_iter_entry.insert(0, "1000")
        self.max_iter_entry.grid(row=0, column=1, padx=5)

        ttk.Label(
            num_settings_frame,
            text=get_string("curve_fitting", "num_points", self.language),
        ).grid(row=0, column=2, padx=5)
        self.num_points_entry = ttk.Entry(num_settings_frame, width=8)
        self.num_points_entry.insert(0, "1000")
        self.num_points_entry.grid(row=0, column=3, padx=5)

        # Create parameter estimates frame (hidden by default)
        self.parent.estimates_frame = (
            self.parent.parameter_estimates_manager.create_estimates_frame(
                self.params_frame
            )
        )

    def _setup_graph_settings_frame(self, control_paned: ttk.PanedWindow) -> None:
        """Set up the graph settings frame with axis controls and labels"""
        self.graph_settings_frame = ttk.LabelFrame(
            control_paned,
            text=get_string(
                "curve_fitting",
                "graph_settings",
                self.language,
                fallback="Configurações do gráfico",
            ),
        )
        # Add graph settings frame to control_paned
        control_paned.add(self.graph_settings_frame, weight=1)

        ttk.Label(
            self.graph_settings_frame,
            text=get_string("curve_fitting", "title", self.language, fallback="Título"),
        ).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.title_var = tk.StringVar(self.parent, value="")
        self.title_entry = ttk.Entry(
            self.graph_settings_frame, textvariable=self.title_var, width=40
        )
        self.title_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        # Bind to auto-update on change
        self.title_var.trace_add(
            "write", lambda *args: self.parent.update_graph_labels()
        )

        ttk.Label(
            self.graph_settings_frame,
            text=get_string(
                "curve_fitting", "x_label", self.language, fallback="Eixo X"
            ),
        ).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.x_label_var = tk.StringVar(self.parent, value="X")
        x_entry = ttk.Entry(
            self.graph_settings_frame, textvariable=self.x_label_var, width=40
        )
        x_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        # Bind to auto-update on change
        self.x_label_var.trace_add(
            "write", lambda *args: self.parent.update_graph_labels()
        )

        ttk.Label(
            self.graph_settings_frame,
            text=get_string(
                "curve_fitting", "y_label", self.language, fallback="Eixo Y"
            ),
        ).grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.y_label_var = tk.StringVar(self.parent, value="Y")
        y_entry = ttk.Entry(
            self.graph_settings_frame, textvariable=self.y_label_var, width=40
        )
        y_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        # Bind to auto-update on change
        self.y_label_var.trace_add(
            "write", lambda *args: self.parent.update_graph_labels()
        )

        scales_frame = ttk.Frame(self.graph_settings_frame)
        scales_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")

        ttk.Label(
            scales_frame,
            text=get_string(
                "curve_fitting", "x_scale", self.language, fallback="Escala X"
            ),
        ).grid(row=0, column=0, padx=5)
        self.x_scale = ttk.Combobox(
            scales_frame,
            values=[
                get_string("curve_fitting", "linear", self.language, fallback="Linear"),
                get_string(
                    "curve_fitting", "log", self.language, fallback="Logarítmica"
                ),
            ],
            state="readonly",
            width=8,
        )
        self.x_scale.set(
            get_string("curve_fitting", "linear", self.language, fallback="Linear")
        )
        self.x_scale.grid(row=0, column=1, padx=5)
        self.x_scale.bind("<<ComboboxSelected>>", lambda e: self.parent.update_scales())

        ttk.Label(
            scales_frame,
            text=get_string(
                "curve_fitting", "y_scale", self.language, fallback="Escala Y"
            ),
        ).grid(row=0, column=2, padx=5)
        self.y_scale = ttk.Combobox(
            scales_frame,
            values=[
                get_string("curve_fitting", "linear", self.language, fallback="Linear"),
                get_string(
                    "curve_fitting", "log", self.language, fallback="Logarítmica"
                ),
            ],
            state="readonly",
            width=8,
        )
        self.y_scale.set(
            get_string("curve_fitting", "linear", self.language, fallback="Linear")
        )
        self.y_scale.grid(row=0, column=3, padx=5)
        self.y_scale.bind("<<ComboboxSelected>>", lambda e: self.parent.update_scales())

    def _setup_action_buttons_frame(self, control_paned: ttk.PanedWindow) -> None:
        """Set up the action buttons frame with fitting and plot controls"""
        self.actions_frame = ttk.LabelFrame(
            control_paned, text=get_string("curve_fitting", "actions", self.language)
        )
        # Add actions frame to control_paned
        control_paned.add(self.actions_frame, weight=0)

        # Configure actions frame
        self.actions_frame.columnconfigure(0, weight=1)
        self.actions_frame.columnconfigure(1, weight=1)
        self.actions_frame.columnconfigure(2, weight=1)

        # Action buttons - arranged horizontally
        fit_button = ttk.Button(
            self.actions_frame,
            text=get_string("curve_fitting", "perform_fit", self.language),
            command=self.parent.perform_fit,
        )
        fit_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        save_button = ttk.Button(
            self.actions_frame,
            text=get_string("curve_fitting", "save_graph", self.language),
            command=self.parent.save_graph,
        )
        save_button.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        clear_button = ttk.Button(
            self.actions_frame,
            text=get_string("curve_fitting", "clear_all", self.language),
            command=self.parent.clear_all_data,
        )
        clear_button.grid(row=0, column=2, sticky="ew", padx=5, pady=5)

    def _setup_progress_frame(self, control_paned: ttk.PanedWindow) -> None:
        """Set up the progress frame for displaying fitting progress"""
        self.fitting_frame = ttk.LabelFrame(
            control_paned,
            text=get_string(
                "curve_fitting", "progress", self.language, fallback="Progresso"
            ),
        )
        # Add progress frame to control_paned
        control_paned.add(self.fitting_frame, weight=0)

        # Configure fitting frame
        self.fitting_frame.columnconfigure(0, weight=1)

        self.progress_var = tk.IntVar(self.parent)
        self.progress_bar = ttk.Progressbar(
            self.fitting_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.status_label = ttk.Label(self.fitting_frame, text="")
        self.status_label.grid(row=1, column=0, sticky="w", padx=5)

    def _setup_results_frame(self, control_paned: ttk.PanedWindow) -> None:
        """Set up the results frame for displaying fitting results"""
        self.results_frame = ttk.LabelFrame(
            control_paned,
            text=get_string(
                "curve_fitting", "results", self.language, fallback="Resultados"
            ),
        )
        # Add results frame to control_paned
        control_paned.add(self.results_frame, weight=1)
        # Configure results_frame for its children
        self.results_frame.rowconfigure(0, weight=1)  # For results_text
        self.results_frame.rowconfigure(1, weight=0)  # For buttons_frame
        self.results_frame.columnconfigure(0, weight=1)

        # Import theme manager for adaptive colors
        from app_files.utils.theme_manager import theme_manager

        self.results_text = ScrolledText(
            self.results_frame,
            height=8,
            width=40,
            bg=theme_manager.get_adaptive_color("background"),
            fg=theme_manager.get_adaptive_color("foreground"),
        )
        self.results_text.grid(
            row=0, column=0, sticky="nsew", padx=5, pady=5
        )  # Changed pack to grid

        # Action buttons frame - Keep only unique functionality (save options and history)
        buttons_frame = ttk.Frame(self.results_frame)
        buttons_frame.grid(
            row=1, column=0, sticky="ew", padx=5, pady=5
        )  # Changed pack to grid

        # Save graph frame with dropdown - this is unique functionality
        save_frame = ttk.Frame(buttons_frame)
        save_frame.grid(row=0, column=0, pady=5, padx=2, sticky="ew")

        # Graph type dropdown - this is unique to the results section
        self.save_graph_option = tk.StringVar(self.parent, value="full")
        save_options = [
            ("full", get_string("curve_fitting", "full_graph", self.language)),
            (
                "fit_and_data",
                get_string("curve_fitting", "fit_and_data", self.language),
            ),
            ("only_data", get_string("curve_fitting", "only_data", self.language)),
            ("only_fit", get_string("curve_fitting", "only_fit", self.language)),
            (
                "only_residuals",
                get_string("curve_fitting", "only_residuals", self.language),
            ),
        ]

        save_dropdown = ttk.Combobox(
            save_frame,
            textvariable=self.save_graph_option,
            state="readonly",
            width=16,  # Increased width to fit "Gráfico completo"
        )
        save_dropdown.grid(row=0, column=0, sticky="ew")
        # Set display text for dropdown
        save_dropdown["values"] = [option[1] for option in save_options]
        save_dropdown.current(0)

        # Add history navigation
        self.parent.history_manager.setup_ui(buttons_frame)
        # Configure column weights
        for i in range(3):
            buttons_frame.columnconfigure(i, weight=1)

    def update_theme(self) -> None:
        """Update theme colors for ScrolledText widgets"""
        from app_files.utils.theme_manager import theme_manager

        bg_color = theme_manager.get_adaptive_color("background")
        fg_color = theme_manager.get_adaptive_color("foreground")

        # Update data text widget
        if self.data_text:
            try:
                self.data_text.configure(bg=bg_color, fg=fg_color)
            except tk.TclError:
                # Widget might be destroyed
                pass

        # Update results text widget
        if self.results_text:
            try:
                self.results_text.configure(bg=bg_color, fg=fg_color)
            except tk.TclError:
                # Widget might be destroyed
                pass
