def update_adjustment_points(self, selected_indices):
    """Update the adjustment points used for curve fitting
    
    Args:
        selected_indices: List of indices of points to use
    """
    # Store the selected indices
    self.selected_indices = selected_indices
    
    # Update the plot to highlight selected points
    if hasattr(self, 'plot_manager'):
        self.plot_manager.highlight_selected_points(selected_indices)

def update_selection_mode(self, mode):
    """Update the selection mode
    
    Args:
        mode: Selection mode ("Todos", "Selecionados", "Faixa")
    """
    # Store the mode
    self.selection_mode = mode

def update_fit_with_current_points(self):
    """Update the fit using the current selected points"""
    # Perform the fit if we have data and a model
    if hasattr(self, 'x') and hasattr(self, 'y') and hasattr(self, 'model_function'):
        # Use only selected points for fitting
        x_fit = [self.x[i] for i in self.selected_indices]
        y_fit = [self.y[i] for i in self.selected_indices]
        
        # Update the plot with selected points highlighted
        if hasattr(self, 'plot_manager'):
            self.plot_manager.update_data(self.x, self.y, self.selected_indices)
        
        # Perform fit with selected points
        if hasattr(self, 'fit_manager'):
            self.fit_manager.perform_fit(x_fit, y_fit)