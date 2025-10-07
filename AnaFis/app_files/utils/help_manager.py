"""
Help manager for AnaFis application.



This module provides a comprehensive help system with searchable content,

category navigation, and rich text formatting.

"""

import tkinter as tk

from tkinter import ttk, scrolledtext

import logging

from typing import Any, Dict, List, Optional

from dataclasses import dataclass

from app_files.utils.translations.api import get_string


from app_files.utils.theme_manager import theme_manager


@dataclass
class HelpSection:
    """Represents a help section"""

    title: str

    content: str

    keywords: List[str]

    category: str

    priority: int = 0


class HelpManager:
    """Manages help content and provides search functionality"""

    def __init__(self, language: str = "pt"):
        """Initialize help manager"""

        self.language = language

        self.sections: Dict[str, HelpSection] = {}

        self._initialize_help_content()

    def _initialize_help_content(self) -> None:
        """Initialize default help content"""

        # Curve fitting help

        self.add_section(
            "curve_fitting",
            "Curve Fitting",
            self._get_default_curve_fitting_content(),
            ["curve", "fitting", "regression", "model", "data"],
            "analysis",
            1,
        )

        # Uncertainty calculation help

        self.add_section(
            "uncertainty_calc",
            "Uncertainty Calculation",
            self._get_default_uncertainty_content(),
            ["uncertainty", "error", "propagation", "calculation"],
            "analysis",
            1,
        )

        # Getting started help

        self.add_section(
            "getting_started",
            "Getting Started",
            self._get_default_getting_started_content(),
            ["start", "begin", "tutorial", "guide", "first"],
            "general",
            2,
        )

        # Data format help

        self.add_section(
            "data_format",
            "Data Format",
            self._get_default_data_format_content(),
            ["data", "format", "import", "file", "csv"],
            "general",
            1,
        )

        # Settings help

        self.add_section(
            "settings",
            "Settings",
            self._get_default_settings_content(),
            ["settings", "preferences", "configuration", "options"],
            "general",
            1,
        )

    def add_section(
        self,
        section_id: str,
        title: str,
        content: str,
        keywords: List[str],
        category: str,
        priority: int = 0,
    ) -> None:
        """Add a help section"""

        self.sections[section_id] = HelpSection(
            title=title,
            content=content,
            keywords=keywords,
            category=category,
            priority=priority,
        )

    def search_sections(self, query: str) -> List[HelpSection]:
        """Search sections by query"""

        query = query.lower().strip()

        if not query:

            return []

        results: List[HelpSection] = []

        for section in self.sections.values():

            # Check title

            if query in section.title.lower():

                results.append(section)

                continue

            # Check keywords

            if any(query in keyword.lower() for keyword in section.keywords):

                results.append(section)

                continue

            # Check content (simple text search)

            if query in section.content.lower():

                results.append(section)

                continue

        # Sort by relevance (priority first, then alphabetical)

        results.sort(key=lambda x: (-x.priority, x.title.lower()))

        return results

    def get_sections_by_category(self, category: str) -> List[HelpSection]:
        """Get all sections in a category"""

        return [
            section
            for section in self.sections.values()
            if section.category == category
        ]

    def get_all_categories(self) -> List[str]:
        """Get all available categories"""

        return list(set(section.category for section in self.sections.values()))

    def show_help_window(
        self,
        parent_window: tk.Tk,
        initial_section: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> None:
        """Show the main help window"""

        logging.info("Opening help window")  # Use % formatting instead of f-string

        help_window = HelpWindow(self, parent_window, initial_section, search_query)

        help_window.show()

    def show_section_help(self, parent_window: tk.Tk, section_id: str) -> None:
        """Show help for a specific section"""

        if section_id in self.sections:

            self.show_help_window(parent_window, initial_section=section_id)

        else:

            logging.warning("Section %s not found", section_id)

    def _get_default_curve_fitting_content(self) -> str:
        """Get default curve fitting help content"""

        return """

Curve Fitting Module



This module allows you to fit mathematical models to experimental data.



Features:

• Import data from CSV files or manual entry

• Choose from predefined models (linear, polynomial, exponential, etc.)

• Custom model definition with mathematical expressions

• Parameter estimation with uncertainty analysis

• Interactive plot with fitted curve

• Export results and plots



Data Format:

Your data should be in CSV format with:

- First column: X values

- Second column: Y values

- Optional: Additional columns for error bars



Supported Models:

• Linear: y = ax + b

• Polynomial: y = ax² + bx + c

• Exponential: y = ae^(bx)

• Logarithmic: y = a ln(x) + b

• Power: y = ax^b

• Custom: Define your own expression



Usage:

1. Import or enter your data

2. Select a model type

3. Adjust parameters if needed

4. Click "Fit" to perform the analysis

5. View results and plot

6. Export if desired



Tips:

• Ensure your data is properly formatted

• Try different models to find the best fit

• Check the R² value for goodness of fit

• Use the plot to visually verify the fit

"""

    def _get_default_uncertainty_content(self) -> str:
        """Get default uncertainty calculation help content"""

        return """

Uncertainty Calculation Module



This module calculates uncertainty propagation in mathematical formulas.



Features:

• Symbolic differentiation for error propagation

• Support for complex mathematical expressions

• Multiple variable uncertainty analysis

• LaTeX formula generation

• Step-by-step calculation display



Usage:

1. Enter your mathematical formula

2. Define variables and their uncertainties

3. Click "Calculate" to get results

4. View the uncertainty propagation formula



Supported Functions:

• Basic arithmetic: +, -, *, /, ^

• Trigonometric: sin, cos, tan, asin, acos, atan

• Logarithmic: log, ln

• Exponential: exp

• Constants: pi, e

• And many more...



Formula Examples:

• Simple: z = x + y

• Complex: z = sqrt(x² + y²)

• Trigonometric: z = sin(x) * cos(y)

• Exponential: z = a * exp(-b*x)



Tips:

• Use clear variable names

• Ensure all variables are defined

• Check that your formula is mathematically valid

• Review the uncertainty propagation formula

"""

    def _get_default_getting_started_content(self) -> str:
        """Get default getting started help content"""

        return """

Getting Started with AnaFis



Welcome to AnaFis! This guide will help you get started with the application.



First Steps:

1. Familiarize yourself with the interface

2. Try importing some sample data

3. Experiment with different analysis tools

4. Explore the settings and customization options



Main Features:

• Curve Fitting: Fit mathematical models to experimental data

• Uncertainty Analysis: Calculate error propagation in formulas

• Data Visualization: Create publication-quality plots

• Settings Management: Customize the application to your needs



Data Import:

• Supported formats: CSV, TXT

• Column-based data organization

• Automatic data type detection

• Error handling for malformed files



Plotting:

• Interactive plots with zoom and pan

• Multiple plot types and styles

• Export to various formats (PNG, PDF, SVG)

• Customizable appearance



Settings:

• Language selection (Portuguese/English)

• Theme customization

• Export preferences

• Update settings



Tips for Beginners:

• Start with simple examples

• Use the built-in help system

• Save your work regularly

• Experiment with different options

• Check the documentation for advanced features



Need Help?

• Use the help system (F1 or Help menu)

• Check the documentation

• Look for tooltips on interface elements

• Try the tutorial examples

"""

    def _get_default_data_format_content(self) -> str:
        """Get default data format help content"""

        return """

Data Format Guide



AnaFis supports various data formats for analysis and plotting.



CSV Format (Recommended):

• Comma-separated values

• First row can be headers (optional)

• First column: X values

• Second column: Y values

• Additional columns: Error bars, multiple datasets



Example CSV:

x,y,error

1.0,2.1,0.1

2.0,4.3,0.2

3.0,6.2,0.15



Text Format:

• Space or tab-separated values

• One data point per line

• Same column structure as CSV



Data Requirements:

• Numeric values only

• No missing data (NaN, empty cells)

• Consistent number of columns

• Reasonable data ranges



Import Options:

• File selection dialog

• Drag and drop support

• Copy-paste from spreadsheet

• Manual data entry



Data Validation:

• Automatic format detection

• Error reporting for invalid data

• Data range checking

• Column count verification



Tips:

• Use consistent decimal separators

• Avoid special characters in headers

• Check data quality before analysis

• Save original data files

• Use descriptive file names

"""

    def _get_default_settings_content(self) -> str:
        """Get default settings help content"""

        return """

Settings and Preferences



Customize AnaFis to match your preferences and workflow.



General Settings:

• Language: Choose between Portuguese and English

• Decimal Places: Set precision for numerical output

• Auto-save: Enable automatic saving of work



Interface Settings:

• Theme: Light, dark, or system theme

• Font Size: Adjust text size for better readability

• Window Size: Remember window dimensions

• Toolbar: Show/hide toolbar elements



Export Settings:

• Default Format: PNG, PDF, SVG, or other formats

• DPI: Resolution for exported images

• Directory: Default save location

• File Naming: Automatic file naming conventions



Update Settings:

• Check for Updates: Automatic update checking

• Update Frequency: How often to check

• Download Location: Where to save updates

• Auto-install: Automatic installation of updates



Advanced Settings:

• Memory Usage: Limit memory consumption

• Performance: Optimize for speed or quality

• Logging: Debug and error logging options

• Plugins: Third-party extension management



Tips:

• Back up your settings before major changes

• Test settings with sample data

• Use themes that work well in your environment

• Keep the application updated

• Report issues with specific settings

"""


class HelpWindow:
    """Help window implementation"""

    def __init__(
        self,
        help_mgr: HelpManager,
        parent_window: tk.Tk,
        initial_section: Optional[str] = None,
        search_query: Optional[str] = None,
    ):
        """Initialize help window"""

        self.help_manager = help_mgr

        self.parent_window = parent_window

        self.initial_section = initial_section

        self.search_query = search_query

        self.window: Optional[tk.Toplevel] = None

        self.search_var: Optional[tk.StringVar] = None

        self.category_var: Optional[tk.StringVar] = None

        self.section_listbox: Optional[tk.Listbox] = None

        self.content_text: Optional[scrolledtext.ScrolledText] = None

    def show(self) -> None:
        """Show the help window"""

        self._create_window()

        self._create_widgets()

        self._setup_layout()

        self._load_initial_content()

        self._center_window()

    def _create_window(self) -> None:
        """Create the help window"""

        self.window = tk.Toplevel(self.parent_window)

        self.window.title(get_string("help", "help_title", self.help_manager.language))

        self.window.geometry("900x700")

        self.window.resizable(True, True)

        # Apply theme

        if theme_manager.is_initialized:

            self.window.configure(bg=theme_manager.get_adaptive_color("background"))

        # Make modal

        self.window.transient(self.parent_window)

        self.window.grab_set()

    def _create_widgets(self) -> None:
        """Create help window widgets"""

        if not self.window:

            return

        # Search frame

        search_frame = ttk.Frame(self.window)

        search_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)

        self.search_var = tk.StringVar()

        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)

        search_entry.pack(side=tk.LEFT, padx=(5, 10))

        search_entry.bind("<KeyRelease>", self._on_search)

        # Category frame

        category_frame = ttk.Frame(self.window)

        category_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        ttk.Label(category_frame, text="Category:").pack(side=tk.LEFT)

        self.category_var = tk.StringVar()

        category_combo = ttk.Combobox(
            category_frame, textvariable=self.category_var, state="readonly", width=20
        )

        category_combo.pack(side=tk.LEFT, padx=(5, 10))

        category_combo.bind("<<ComboboxSelected>>", self._on_category_change)

        # Main content frame

        content_frame = ttk.Frame(self.window)

        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Left panel (sections)

        left_panel = ttk.Frame(content_frame)

        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        ttk.Label(left_panel, text="Sections:").pack(anchor=tk.W)

        # Section listbox with scrollbar

        listbox_frame = ttk.Frame(left_panel)

        listbox_frame.pack(fill=tk.BOTH, expand=True)

        self.section_listbox = tk.Listbox(listbox_frame, width=30)

        section_scrollbar = ttk.Scrollbar(
            listbox_frame, orient=tk.VERTICAL, command=self.section_listbox.yview
        )

        self.section_listbox.configure(yscrollcommand=section_scrollbar.set)

        self.section_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        section_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.section_listbox.bind("<<ListboxSelect>>", self._on_section_select)

        # Right panel (content)

        right_panel = ttk.Frame(content_frame)

        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(right_panel, text="Content:").pack(anchor=tk.W)

        # Content text with scrollbar

        self.content_text = scrolledtext.ScrolledText(
            right_panel, wrap=tk.WORD, width=60, height=30, font=("Consolas", 10)
        )

        self.content_text.pack(fill=tk.BOTH, expand=True)

        # Apply theme to text widget

        if theme_manager.is_initialized:

            self.content_text.configure(
                bg=theme_manager.get_adaptive_color("background"),
                fg=theme_manager.get_adaptive_color("foreground"),
            )

        # Close button

        button_frame = ttk.Frame(self.window)

        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        close_button = ttk.Button(
            button_frame, text="Close", command=self.window.destroy
        )

        close_button.pack(side=tk.RIGHT)

    def _setup_layout(self) -> None:
        """Setup the layout and populate initial data"""

        if not self.window or not self.category_var:

            return

        # Populate categories

        categories = self.help_manager.get_all_categories()

        category_combo = self.window.nametowidget(self.category_var.get())

        if category_combo:

            category_combo["values"] = categories

            if categories:

                category_combo.set(categories[0])

        # Populate sections for first category

        if categories:

            self._populate_sections(categories[0])

    def _load_initial_content(self) -> None:
        """Load initial content based on parameters"""

        if self.search_query and self.search_var:

            self.search_var.set(self.search_query)

            self._on_search(None)

        elif self.initial_section:

            self._show_section(self.initial_section)

        else:

            # Show first section

            if self.category_var and self.category_var.get():

                sections = self.help_manager.get_sections_by_category(
                    self.category_var.get()
                )

                if sections:

                    self._show_section_content(sections[0])

    def _populate_sections(self, category: str) -> None:
        """Populate section listbox for a category"""

        if not self.section_listbox:

            return

        self.section_listbox.delete(0, tk.END)

        sections = self.help_manager.get_sections_by_category(category)

        for section in sections:

            self.section_listbox.insert(tk.END, section.title)

    def _on_category_change(self, _event: Optional[Any] = None) -> None:
        """Handle category change"""

        if self.category_var:

            category = self.category_var.get()

            if category:

                self._populate_sections(category)

    def _on_search(self, _event: Optional[Any] = None) -> None:
        """Handle search"""

        if not self.search_var:

            return

        query = self.search_var.get().strip()

        if not query:

            # Reset to category view

            self._on_category_change()

            return

        # Search sections

        results = self.help_manager.search_sections(query)

        # Update listbox

        if self.section_listbox:

            self.section_listbox.delete(0, tk.END)

            for section in results:

                self.section_listbox.insert(tk.END, section.title)

    def _on_section_select(self, _event: Optional[Any] = None) -> None:
        """Handle section selection"""

        if not self.section_listbox:

            return

        selection = self.section_listbox.curselection()

        if not selection:

            return

        # Get selected section title

        title = self.section_listbox.get(selection[0])

        # Find section by title

        for section in self.help_manager.sections.values():

            if section.title == title:

                self._show_section_content(section)

                break

    def _show_section(self, section_id: str) -> None:
        """Show a specific section by ID"""

        if section_id in self.help_manager.sections:

            section = self.help_manager.sections[section_id]

            self._show_section_content(section)

    def _show_section_content(self, section: HelpSection) -> None:
        """Show section content in text widget"""

        if not self.content_text:

            return

        self.content_text.delete(1.0, tk.END)

        self.content_text.insert(1.0, section.content)

        self.content_text.config(state=tk.DISABLED)  # Make read-only

    def _center_window(self) -> None:
        """Center the help window on screen"""

        if not self.window:

            return

        self.window.update_idletasks()

        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)

        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)

        self.window.geometry(f"+{x}+{y}")


# Global help manager instance

help_manager = HelpManager()
