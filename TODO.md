# AnaFis - TODO List - Doing this as summer project if I don't put much expectations - base programing language probably will change.

### 2. Excel-like Tables Implementation
- [ ] **Data Table Widget**
  - [ ] Create spreadsheet-style data entry/editing widget
  - [ ] Support for copy/paste operations
  - [ ] Cell editing with validation
  - [ ] Column sorting and filtering
  - [ ] Data type detection and formatting
  
- [ ] **Table Integration**
  - [ ] Replace current data import with table widget
  - [ ] Allow direct data entry in table format
  - [ ] Excel file import/export (.xlsx, .xls)
  - [ ] Table-to-plot data synchronization
  - [ ] Undo/redo functionality for table operations

 
- [ ] **Plugin System Enhancement** 🚧 IN PROGRESS
  - [x] Basic plugin system architecture implemented
  - [ ] Create `/plugins` directory structure
  - [ ] Define plugin interface/API specification
  - [ ] Implement actual plugin loading mechanism
  - [ ] Add plugin management UI in settings
  - [ ] Create example plugins for demonstration
  - [ ] Plugin dependency management
  - [ ] Plugin hot-loading/unloading capability

### 4. Equation Solving Module
- [ ] **Symbolic Equation Solver**
  - [ ] Create new module for equation solving
  - [ ] Support for linear and nonlinear equations
  - [ ] System of equations solver
  - [ ] Numerical and symbolic solutions
  - [ ] Step-by-step solution display
  
- [ ] **Solver Integration**
  - [ ] Add equation solver tab to main interface
  - [ ] LaTeX rendering for equations and solutions
  - [ ] Solution export functionality
  - [ ] Integration with uncertainty propagation

---

## 📋 TODO - Medium Priority

### 5. Enhanced Data Visualization
- [ ] **Advanced Plotting Options**
  - [ ] 3D plotting capabilities
  - [ ] Multiple y-axes support
  - [ ] Log scale options
  - [ ] Error bar customization
  - [ ] Plot annotations and text boxes
  
- [ ] **Interactive Features**
  - [ ] Zoom and pan functionality
  - [ ] Data point selection and highlighting
  - [ ] Crosshair cursor with coordinates
  - [ ] Plot legends customization

### 6. File Management Improvements
- [ ] **Recent Files System**
  - [ ] Recent files menu implementation
  - [ ] Project file format (.anafis files)
  - [ ] Session saving and restoration
  - [ ] Auto-save functionality
  
- [ ] **Backup System**
  - [ ] Automatic backup creation
  - [ ] Backup restoration interface
  - [ ] Configurable backup intervals

### 7. Advanced Mathematical Features
- [ ] **Extended Function Library**
  - [ ] More preset models (Gaussian, Lorentzian, etc.)
  - [ ] Statistical distributions
  - [ ] Fourier analysis tools
  - [ ] Integration and differentiation
  
- [ ] **Data Analysis Tools**
  - [ ] Statistical analysis module
  - [ ] Correlation analysis
  - [ ] Data smoothing and filtering
  - [ ] Outlier detection

---

## 🔧 TODO - Low Priority

### 8. User Experience Enhancements
- [ ] **Help System**
  - [ ] Built-in help documentation
  - [ ] Keyboard shortcuts
  - [ ] Context-sensitive help
  
- [ ] **Accessibility**
  - [ ] High contrast themes
  - [ ] Font size scaling
  - [ ] Keyboard navigation
  - [ ] Screen reader compatibility

### 9. Performance Optimizations
- [ ] **Large Dataset Handling**
  - [ ] Lazy loading for large files
  - [ ] Data sampling for visualization
  - [ ] Memory usage optimization
  - [ ] Background processing for long calculations

### 10. Legacy Plugin System (Superseded by #3)
- [ ] **Extensibility Framework**
  - [ ] Plugin architecture design
  - [ ] Custom model plugins
  - [ ] Third-party integration support
  - [ ] Plugin manager interface

---

## 🐛 ~~Known Issues to Fix~~ ✅ MOSTLY RESOLVED

- [ ] **Test Coverage**: Add comprehensive unit tests (still pending)
- [ ] **Build System**: Improve packaging and distribution (still pending)

---

## 📦 Release Planning


### Next Release (v11)
- [ ] Excel-like tables implementation
- [ ] Enhanced data entry and editing capabilities
- [ ] Improved file import/export functionality

### Future (v12)
- [ ] Equation solving module
- [ ] Advanced plotting features
- [ ] Enhanced file management
- [ ] Extended mathematical functions

### Long-term (v13)
- [ ] Full plugin system
- [ ] Advanced data analysis tools
- [ ] Performance optimizations for large datasets

---


### Research Features
- [ ] **Monte Carlo Analysis**: Statistical simulation capabilities
- [ ] **Bayesian Analysis**: Bayesian inference tools
- [ ] **Machine Learning**: Basic ML integration for pattern recognition
- [ ] **Signal Processing**: Time series analysis and signal processing

---

*Last updated: 2025-10-07*  
*Recent updates: Completed comprehensive code cleanup including vulture unused code removal, type ignore comment removal, and __pycache__ cleanup. Added development tools (Black, Vulture, MyPy) to requirements. Application now supports Python 3.13 and maintains high code quality standards.*
