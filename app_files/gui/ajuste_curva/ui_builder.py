"""UI Builder component for curve fitting"""
from tkinter import ttk
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from typing import TYPE_CHECKING, Optional # Ensure Optional is imported

from app_files.utils.constants import TRANSLATIONS

if TYPE_CHECKING: # Added TYPE_CHECKING block
    from .main_gui import AjusteCurvaFrame

class UIBuilder:
    """Handles building the UI components for curve fitting"""
    
    def __init__(self, parent: 'AjusteCurvaFrame', language: str ='pt') -> None: # Added type hints
        """Initialize the UI builder
        
        Args:
            parent: The parent AjusteCurvaFrame instance
            language: Interface language (default: 'pt')
        """
        self.parent = parent
        self.language = language
        
        # Initialize UI element attributes with defaults
        self.data_text = None
        self.results_text = None
        self.title_entry = None
        self.x_label_var = tk.StringVar(value="X")
        self.y_label_var = tk.StringVar(value="Y")
        self.x_scale = None
        self.y_scale = None
        self.file_entry = None
        self.equation_entry = None
        self.model_selector = None
        self.num_points_entry = None
        self.max_iter_entry = None
        self.progress_var = tk.IntVar()
        self.status_label = None
        self.save_graph_option = tk.StringVar(value="full")
        self.plot_area_frame: Optional[ttk.Frame] = None # Ensure this line is present and correct
        
    def setup_ui(self):
        """Set up the complete user interface"""
        # Create main frame
        self.main_frame = ttk.Frame(self.parent)  # Changed parent
        self.main_frame.grid(row=0, column=0, sticky="nsew") # Changed pack to grid
        
        # Configure main frame with 2 columns for horizontal layout
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)  # Control panel
        self.main_frame.columnconfigure(1, weight=3)  # Plot panel
        
        # Left panel for controls - using grid
        control_frame = ttk.Frame(self.main_frame, padding="5", width=400)
        control_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        control_frame.grid_propagate(False)  # Prevent shrinking
        # Configure control_frame for its child (control_paned)
        control_frame.rowconfigure(0, weight=1)
        control_frame.columnconfigure(0, weight=1)
        
        # Right panel for plots (this is where AjusteCurvaFrame will place its canvas)
        # We create it here so AjusteCurvaFrame can use it as a master for the canvas.
        # UIBuilder itself no longer tries to manage/recreate the canvas.
        self.plot_area_frame = ttk.Frame(self.main_frame, width=800) # This frame will be the master for the canvas
        self.plot_area_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.plot_area_frame.grid_propagate(False)  # Prevent shrinking
        self.plot_area_frame.rowconfigure(0, weight=1) # Allow canvas to expand within plot_area_frame
        self.plot_area_frame.columnconfigure(0, weight=1) # Allow canvas to expand within plot_area_frame
        
        # Create vertical paned window for control sections
        control_paned = ttk.PanedWindow(control_frame, orient=tk.VERTICAL)
        control_paned.grid(row=0, column=0, sticky="nsew") # Changed pack to grid
        
        # Setup individual sections
        self._setup_data_input_frame(control_paned)
        self._setup_parameters_frame(control_paned)
        self._setup_graph_settings_frame(control_paned)
        self._setup_progress_frame(control_paned)
        self._setup_results_frame(control_paned)
    def _setup_data_input_frame(self, control_paned: ttk.PanedWindow) -> None: # Added type hint
        """Set up the data input frame"""
        data_frame = ttk.LabelFrame(control_paned, text=TRANSLATIONS[self.language]['data_input'])
        # Add data input frame to control_paned
        control_paned.add(data_frame, weight=1) # type: ignore[reportUnknownMemberType]
        
        # Configure data frame to expand properly
        data_frame.columnconfigure(1, weight=1)
        data_frame.rowconfigure(1, weight=1)
        
        # File selection with more compact layout
        file_input_frame = ttk.Frame(data_frame)
        file_input_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=2)
        file_input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_input_frame, text=TRANSLATIONS[self.language]['data_file']).grid(row=0, column=0, sticky="w")
        self.file_entry = ttk.Entry(file_input_frame, width=30)
        self.file_entry.grid(row=0, column=1, padx=5, sticky="ew")
        ttk.Button(file_input_frame, text=TRANSLATIONS[self.language]['browse'],
                  command=self.parent.browse_file, width=10).grid(row=0, column=2)
        
        # Data preview frame that expands with parent
        preview_frame = ttk.LabelFrame(data_frame, text="Dados Carregados")
        preview_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        preview_frame.rowconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        
        self.data_text = ScrolledText(preview_frame, height=8, width=50)
        self.data_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    def _setup_parameters_frame(self, control_paned: ttk.PanedWindow) -> None: # Added type hint
        """Set up the parameters frame"""
        params_frame = ttk.LabelFrame(control_paned, text=TRANSLATIONS[self.language]['fitting_parameters'])
        # Add parameters frame to control_paned
        control_paned.add(params_frame, weight=1) # type: ignore[reportUnknownMemberType]
        
        # Model presets - More compact layout
        params_frame.columnconfigure(1, weight=1)
        
        # Split the parameters frame into left and right sections
        left_params_frame = ttk.Frame(params_frame)
        left_params_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)
        left_params_frame.columnconfigure(1, weight=1)
        
        right_params_frame = ttk.Frame(params_frame)
        right_params_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=2)
        right_params_frame.columnconfigure(1, weight=1)
        
        # Left side - Model selection and equation
        ttk.Label(left_params_frame, text="Modelo:").grid(row=0, column=0, sticky="w")
        self.model_selector = ttk.Combobox(left_params_frame, 
                                         values=list(self.parent.model_manager.preset_models.keys()),
                                         state="readonly",
                                         width=20)
        self.model_selector.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        def _on_combobox_selected_callback(event: tk.Event) -> None: # type: ignore[reportGeneralTypeIssues]
            self.parent.apply_preset_model(event) # type: ignore[reportUnknownMemberType]
            
        self.model_selector.bind("<<ComboboxSelected>>", _on_combobox_selected_callback) # type: ignore[reportUnknownArgumentType]
        # self.model_selector.pack(pady=5) # Removed redundant pack call
        
        ttk.Label(left_params_frame, text=TRANSLATIONS[self.language]['equation']).grid(row=1, column=0, sticky="w")
        self.equation_entry = ttk.Entry(left_params_frame, width=20)
        self.equation_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.equation_entry.bind("<KeyRelease>", self.parent.validate_equation)
        self.equation_entry.bind("<FocusOut>", lambda e: self.parent.update_estimates_frame())
        
        # Add "More Configs" button
        more_configs_button = ttk.Button(
            params_frame, 
            text=TRANSLATIONS[self.language].get('more_configs', 'Mais configurações...'),
            command=self.parent.show_advanced_config
        )
        more_configs_button.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=10)
        
        # Numerical settings frame
        num_settings_frame = ttk.Frame(params_frame)
        num_settings_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")
        
        ttk.Label(num_settings_frame, text=TRANSLATIONS[self.language]['max_iterations']).grid(row=0, column=0, padx=5)
        self.max_iter_entry = ttk.Entry(num_settings_frame, width=8)
        self.max_iter_entry.insert(0, "1000")
        self.max_iter_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(num_settings_frame, text=TRANSLATIONS[self.language]['num_points']).grid(row=0, column=2, padx=5)
        self.num_points_entry = ttk.Entry(num_settings_frame, width=8)
        self.num_points_entry.insert(0, "1000")
        self.num_points_entry.grid(row=0, column=3, padx=5)
        
        # Create parameter estimates frame (hidden by default)
        # self.parent.estimates_frame = self.parent.parameter_estimates_manager.create_estimates_frame(params_frame) # type: ignore[reportUnknownMemberType]
    def _setup_graph_settings_frame(self, control_paned: ttk.PanedWindow) -> None: # Added type hint
        """Set up the graph settings frame"""
        graph_settings_frame = ttk.LabelFrame(control_paned, text=TRANSLATIONS[self.language]['graph_settings'])
        # Add graph settings frame to control_paned
        control_paned.add(graph_settings_frame, weight=1) # type: ignore[reportUnknownMemberType]
        
        ttk.Label(graph_settings_frame, text=TRANSLATIONS[self.language]['title']).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.title_entry = ttk.Entry(graph_settings_frame, width=40)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(graph_settings_frame, text=TRANSLATIONS[self.language]['x_label']).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.x_label_var = tk.StringVar(value="X")
        x_entry = ttk.Entry(graph_settings_frame, textvariable=self.x_label_var, width=40)
        x_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        
        ttk.Label(graph_settings_frame, text=TRANSLATIONS[self.language]['y_label']).grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.y_label_var = tk.StringVar(value="Y")
        y_entry = ttk.Entry(graph_settings_frame, textvariable=self.y_label_var, width=40)
        y_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")      
        
        scales_frame = ttk.Frame(graph_settings_frame)
        scales_frame.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")
        
        ttk.Label(scales_frame, text=TRANSLATIONS[self.language]['x_scale']).grid(row=0, column=0, padx=5)
        self.x_scale = ttk.Combobox(scales_frame, 
                                  values=[TRANSLATIONS[self.language]['linear'], TRANSLATIONS[self.language]['log']], 
                                  state="readonly", width=8)
        self.x_scale.set(TRANSLATIONS[self.language]['linear'])
        self.x_scale.grid(row=0, column=1, padx=5)
        self.x_scale.bind('<<ComboboxSelected>>', lambda e: self.parent.update_scales())
        
        ttk.Label(scales_frame, text=TRANSLATIONS[self.language]['y_scale']).grid(row=0, column=2, padx=5)
        self.y_scale = ttk.Combobox(scales_frame, 
                                  values=[TRANSLATIONS[self.language]['linear'], TRANSLATIONS[self.language]['log']], 
                                  state="readonly", width=8)
        self.y_scale.set(TRANSLATIONS[self.language]['linear'])
        self.y_scale.grid(row=0, column=3, padx=5)
        self.y_scale.bind('<<ComboboxSelected>>', lambda e: self.parent.update_scales())
    def _setup_progress_frame(self, control_paned: ttk.PanedWindow) -> None: # Added type hint
        """Set up the fitting actions frame"""
        fitting_frame = ttk.LabelFrame(control_paned, text=TRANSLATIONS[self.language].get('fitting_actions', 'Ajuste e Progresso'))
        # Add progress frame to control_paned
        control_paned.add(fitting_frame, weight=0) # type: ignore[reportUnknownMemberType]
        
        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(
            fitting_frame, 
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        self.status_label = ttk.Label(fitting_frame, text="")
        self.status_label.grid(row=1, column=0, sticky="w", padx=5)

        # Add the 'do fit' button here
        ttk.Button(
            fitting_frame,
            text=TRANSLATIONS[self.language]['perform_fit'],
            command=self.parent.perform_fit
        ).grid(row=2, column=0, pady=8, padx=5, sticky="ew")

    def _setup_results_frame(self, control_paned: ttk.PanedWindow) -> None: # Added type hint
        """Set up the results frame"""
        results_frame = ttk.LabelFrame(control_paned, text=TRANSLATIONS[self.language]['results'])
        # Add results frame to control_paned
        control_paned.add(results_frame, weight=1) # type: ignore[reportUnknownMemberType]
        
        # Configure results_frame for its children
        results_frame.rowconfigure(0, weight=1)  # For results_text
        results_frame.rowconfigure(1, weight=0)  # For buttons_frame
        results_frame.columnconfigure(0, weight=1)

        self.results_text = ScrolledText(results_frame, height=8, width=40)
        self.results_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5) # Changed pack to grid
        
        # Action buttons frame
        buttons_frame = ttk.Frame(results_frame)
        buttons_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5) # Changed pack to grid
        
        # Save graph frame with dropdown
        save_frame = ttk.Frame(buttons_frame)
        save_frame.grid(row=0, column=1, pady=5, padx=2, sticky="ew")
        
        # Graph type dropdown
        self.save_graph_option = tk.StringVar(value="full")        
        save_options = [
            ("full", TRANSLATIONS[self.language].get('full_graph', "Gráfico completo")),
            ("fit_and_data", TRANSLATIONS[self.language].get('fit_and_data', "Ajuste + dados")),
            ("only_data", TRANSLATIONS[self.language].get('only_data', "Apenas dados")),
            ("only_fit", TRANSLATIONS[self.language].get('only_fit', "Apenas ajuste")),
            ("only_residuals", TRANSLATIONS[self.language].get('only_residuals', "Apenas resíduos"))
        ]
        
        save_dropdown = ttk.Combobox(
            save_frame, 
            textvariable=self.save_graph_option,
            state="readonly",
            width=16  # Increased width to fit "Gráfico completo"
        )
        save_dropdown.grid(row=0, column=0, sticky="ew")
        # Set display text for dropdown
        save_dropdown['values'] = [option[1] for option in save_options]
        save_dropdown.current(0)
        
        ttk.Button(
            save_frame,
            text=TRANSLATIONS[self.language]['save_graph'],
            command=self.parent.save_graph
        ).grid(row=0, column=1, sticky="ew")
        ttk.Button(
            buttons_frame,
            text=TRANSLATIONS[self.language].get('export_data', "Exportar Dados"),
            command=self.parent.export_results
        ).grid(row=0, column=2, pady=5, padx=2, sticky="ew")
        
        # Add history navigation
        self.parent.history_manager.setup_ui(buttons_frame) # type: ignore[reportArgumentType]
        
        # Configure column weights
        for i in range(3):
            buttons_frame.columnconfigure(i, weight=1)