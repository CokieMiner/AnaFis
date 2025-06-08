"""Point selection and adjustment UI for curve fitting"""
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING
import numpy as np

from app_files.utils.constants import TRANSLATIONS

if TYPE_CHECKING:
    from app_files.gui.ajuste_curva.main_gui import AjusteCurvaFrame

class AdjustmentPointsManager:
    """Manages selection of adjustment points for curve fitting"""
    
    def __init__(self, parent_frame: 'AjusteCurvaFrame', language: str = 'pt') -> None:
        """Initialize the adjustment points manager
        
        Args:
            parent_frame: The main AjusteCurvaFrame instance that owns this manager
            language: Interface language
        """
        self.parent = parent_frame
        self.language = language
        
        # Create adjustment point type variable
        self.adjustment_points_type = tk.StringVar(value="Todos")
        self.adjust_options_frame = None
        # Storage for scrollable components when maximized
        self.scrollable_frame = None
        self.canvas = None
        self.select_frame = None
        
        # Store the selected points state (default: all selected)
        self.selected_point_indices = None
        # Initialize attributes that are conditionally created in UI methods
        self.point_selections = []
        self.min_x_entry = None
        self.max_x_entry = None
    
    def setup_ui(self, parent_frame: tk.Widget, maximize_scrollbox: bool = False) -> None:
        """Set up the UI for adjustment points
        
        Args:
            parent_frame: Frame to place the UI elements in
            maximize_scrollbox: Whether to maximize the scrollbox size
        """
        # Configure parent frame to expand properly
        parent_frame.columnconfigure(0, weight=1)
        
        # Title label
        ttk.Label(parent_frame, text=TRANSLATIONS[self.language].get('adjustment_points', 'Pontos de ajuste')).grid(
            row=0, column=0, sticky="w", padx=10, pady=5)
        
        # Create frame for scrollable lists
        lists_frame = ttk.Frame(parent_frame)
        lists_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        if maximize_scrollbox:
            # Configure to maximize selected points list
            parent_frame.rowconfigure(1, weight=1)  # Let the content expand
            lists_frame.columnconfigure(0, weight=1)
            lists_frame.rowconfigure(1, weight=1)   # Let the scrollbox expand vertically
        
        # Points dropdown 
        points_frame = ttk.Frame(lists_frame)
        points_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ttk.Label(points_frame, text=TRANSLATIONS[self.language].get('points_type', 'Tipo de pontos:')).grid(
            row=0, column=0, sticky="w", padx=5, pady=5)
        
        points_dropdown = ttk.Combobox(
            points_frame, 
            textvariable=self.adjustment_points_type,
            values=["Todos", "Selecionados", "Faixa"],
            state="readonly",
            width=15
        )
        points_dropdown.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Container for adjustment options that change based on selection
        self.adjust_options_frame = ttk.Frame(lists_frame)
        self.adjust_options_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Initialize the options based on current selection
        self.update_adjustment_points()
          # Bind the dropdown to update the options
        points_dropdown.bind("<<ComboboxSelected>>", self.update_adjustment_points)
    
    def update_adjustment_points(self, _event=None):
        """Update UI based on selected adjustment points type
        
        Args:
            _event: Event parameter required by tkinter combobox binding but not used
        """
        # Make sure adjust_options_frame exists before clearing it
        if self.adjust_options_frame is None:
            return
        
        # Clear existing widgets in the adjustment options frame
        for widget in self.adjust_options_frame.winfo_children():
            widget.destroy()
        
        selection = self.adjustment_points_type.get()
        
        # Every time selection type changes, save it immediately
        # This ensures the curve fitting always uses the current selection mode
        if hasattr(self.parent, 'update_selection_mode'):
            self.parent.update_selection_mode(selection)
        
        if selection == "Todos":            # No additional controls needed
            # Immediately update the parent to use all points
            self.save_points()
            
        elif selection == "Selecionados":
            # Add a frame for point selection checkboxes
            if hasattr(self.parent, 'x') and len(self.parent.x) > 0:
                # Create a canvas with scrollbar for many points
                self.scrollable_frame = ttk.Frame(self.adjust_options_frame)
                self.scrollable_frame.pack(fill=tk.BOTH, expand=True)

                self.canvas = tk.Canvas(self.scrollable_frame, height=150)
                scrollbar = ttk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.canvas.yview)
                self.select_frame = ttk.Frame(self.canvas)
                
                # Configure scrolling
                self.canvas.configure(yscrollcommand=scrollbar.set)
                self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                # Create a window for the frame
                canvas_window = self.canvas.create_window((0, 0), window=self.select_frame, anchor="nw")
                
                # Initialize the selected_point_indices if it's None (first time)
                if self.selected_point_indices is None:
                    self.selected_point_indices = list(range(len(self.parent.x)))
                
                # Add checkboxes for each point
                self.point_selections = []
                for i in range(len(self.parent.x)):
                    # Use the stored selection state
                    is_selected = i in self.selected_point_indices
                    var = tk.BooleanVar(value=is_selected)
                    self.point_selections.append(var)
                    cb = ttk.Checkbutton(self.select_frame, 
                                text=f"({self.parent.x[i]:.3f}, {self.parent.y[i]:.3f})",
                                variable=var)
                    cb.grid(row=i, column=0, sticky="w", padx=5, pady=2)
                    
                    # Add callback to immediately apply changes when checkbox is toggled
                    var.trace_add("write", lambda *args, idx=i: self.on_checkbox_changed(idx))
                
                # Configure canvas scrolling
                def configure_canvas(event):
                    # Check that canvas still exists
                    if self.canvas is not None:
                        # Safe access to canvas methods with proper checks
                        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
                        # Make sure canvas_window is valid before configuring
                        if canvas_window is not None:
                            self.canvas.itemconfig(canvas_window, width=event.width)
                
                self.select_frame.bind("<Configure>", configure_canvas)
                
                # Initial save to apply current selections
                self.save_points()
            else:
                no_data_label = ttk.Label(self.adjust_options_frame, 
                                    text=TRANSLATIONS[self.language]['no_data_loaded'])
                no_data_label.pack(pady=5)
                
        elif selection == "Faixa":
            # Add range selection controls
            range_frame = ttk.Frame(self.adjust_options_frame)
            range_frame.pack(fill=tk.X)
                
            ttk.Label(range_frame, text=TRANSLATIONS[self.language]['min_x']).grid(row=0, column=0, padx=5, pady=2)
            self.min_x_entry = ttk.Entry(range_frame, width=10)
            self.min_x_entry.grid(row=0, column=1, padx=5, pady=2)
            if hasattr(self.parent, 'x') and len(self.parent.x) > 0:
                self.min_x_entry.insert(0, str(np.min(self.parent.x)))
                    
            ttk.Label(range_frame, text=TRANSLATIONS[self.language]['max_x']).grid(row=1, column=0, padx=5, pady=2)
            self.max_x_entry = ttk.Entry(range_frame, width=10)
            self.max_x_entry.grid(row=1, column=1, padx=5, pady=2)
            if hasattr(self.parent, 'x') and len(self.parent.x) > 0:
                self.max_x_entry.insert(0, str(np.max(self.parent.x)))
              # Add an "Apply" button to apply range changes immediately
            apply_button = ttk.Button(
                range_frame, 
                text=TRANSLATIONS[self.language].get('apply', 'Aplicar'),
                command=self.save_points
            )
            apply_button.grid(row=2, column=0, columnspan=2, pady=10)
            
            # Also bind the Return key to save points
            self.min_x_entry.bind("<Return>", lambda e: self.save_points())
            self.max_x_entry.bind("<Return>", lambda e: self.save_points())

    def on_checkbox_changed(self, _index):
        """Handle checkbox state changes
        
        Args:
            _index: Index of the checkbox that changed (required by trace callback but not used)
        """        # Update the points immediately when a checkbox changes
        self.save_points()

    def get_selected_points(self):
        """Get indices of points to use based on current selection mode"""
        if not hasattr(self.parent, 'x') or len(self.parent.x) == 0:
            return []
            
        selection = self.adjustment_points_type.get()
        indices = []
        
        if selection == "Todos" or selection == "":
            # Use all points
            indices = list(range(len(self.parent.x)))
            
        elif selection == "Selecionados" and hasattr(self, 'point_selections'):
            # Use only checked points
            indices = [i for i, var in enumerate(self.point_selections) if var.get()]
            
        elif selection == "Faixa" and hasattr(self, 'min_x_entry') and hasattr(self, 'max_x_entry') and self.min_x_entry is not None and self.max_x_entry is not None:
            # Use points in the specified range
            try:
                min_x = float(self.min_x_entry.get())
                max_x = float(self.max_x_entry.get())
                indices = [i for i, x in enumerate(self.parent.x) if min_x <= x <= max_x]
            except ValueError:
                # Fall back to all points if conversion fails
                indices = list(range(len(self.parent.x)))
                
        return indices
    
    def save_points(self):
        """Save the current adjustment points"""
        selection = self.adjustment_points_type.get()
        
        # Only need to save if in "Selecionados" mode
        if selection == "Selecionados" and hasattr(self, 'point_selections'):
            # Store the current selection state
            self.selected_point_indices = [i for i, var in enumerate(self.point_selections) if var.get()]
        
        # Get the currently selected points based on current mode
        selected_indices = self.get_selected_points()
        
        # Save to parent if it has the appropriate method
        if hasattr(self.parent, 'update_adjustment_points'):
            self.parent.update_adjustment_points(selected_indices)
            
            # Also trigger a replot/refit if available
            if hasattr(self.parent, 'update_fit_with_current_points'):
                self.parent.update_fit_with_current_points()