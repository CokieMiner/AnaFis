# AnaFis - TODO List - Doing this as summer project if I don't put much expectations - base programing language probably will change.

## ✅ Completed Features

### Core Functionality
- [x] **Curve Fitting Module**: Advanced curve fitting with ODR (Orthogonal Distance Regression)
  - [x] User-defined functions and built-in mathematical models
  - [x] Parameter estimation with uncertainty calculation
  - [x] Real-time visualization with residuals plotting
  - [x] Custom function manager for adding mathematical expressions
  - [x] History management for fit results
  - [x] Advanced configuration dialog for fitting parameters

- [x] **Uncertainty Propagation Module**: Symbolic uncertainty calculations
  - [x] Error propagation using partial derivatives  
  - [x] LaTeX formula rendering for uncertainty expressions
  - [x] Support for mathematical functions (sin, cos, exp, log, etc.)
  - [x] Real-time calculation updates

- [x] **Data Management**:
  - [x] CSV and tab-separated text file import
  - [x] Support for x, σx, y, σy data format
  - [x] Data export functionality
  - [x] Graph export in multiple formats (PNG, PDF, SVG)

### User Interface
- [x] **Modern GUI**: Clean tkinter-based interface
- [x] **Tabbed Interface**: Multiple analyses simultaneously
- [x] **Multi-language Support**: Portuguese and English
  - [x] Dynamic language switching without restart
  - [x] Complete interface translation
- [x] **Splash Screen**: Loading progress indicator
- [x] **Application Icon**: Custom icon support
- [x] **Context Menus**: Right-click tab management

### Settings System (Partial)
- [x] **User Preferences Manager**: Complete backend system
  - [x] JSON-based configuration storage
  - [x] Validation system for preference values
  - [x] Default preferences management
  - [x] Import/export configuration functionality
- [x] **Settings Dialog**: Comprehensive settings interface
  - [x] General settings tab (language, auto-save, backup)
  - [x] Interface settings tab (theme selection, font size, tooltips)
  - [x] Data/Export settings tab (decimal places, DPI, export format)
  - [x] Advanced settings tab (advanced mode)

### Code Quality
- [x] **Comment System Review**: 
  - [x] Removed unnecessary inline comments
  - [x] Added useful algorithmic explanations
  - [x] Proper comment formatting (no same-line comments)
- [x] **Type Annotations**: Complete typing throughout codebase
- [x] **Error Handling**: Comprehensive exception management
- [x] **Logging System**: Proper logging implementation

---

## 🚧 TODO - High Priority

### 1. Complete Settings Integration
- [ ] **Theme Support Implementation**
  - [ ] Create theme manager class
  - [ ] Implement light/dark/auto theme switching
  - [ ] Apply themes to all UI components (matplotlib plots, tkinter widgets)
  - [ ] Auto theme detection based on system preferences
  - [ ] Theme persistence and restoration
  
- [ ] **Settings Application**
  - [ ] Connect settings dialog changes to actual UI updates
  - [ ] Implement font size changes across all components
  - [ ] Apply window size remembering functionality
  - [ ] Implement auto-save and backup features
  - [ ] Add tooltips system throughout the interface

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

### 3. Equation Solving Module
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

### 4. Enhanced Data Visualization
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

### 5. File Management Improvements
- [ ] **Recent Files System**
  - [ ] Recent files menu implementation
  - [ ] Project file format (.anafis files)
  - [ ] Session saving and restoration
  - [ ] Auto-save functionality
  
- [ ] **Backup System**
  - [ ] Automatic backup creation
  - [ ] Backup restoration interface
  - [ ] Configurable backup intervals

### 6. Advanced Mathematical Features
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

### 7. User Experience Enhancements
- [ ] **Help System**
  - [ ] Built-in help documentation
  - [ ] Tutorial system for new users
  - [ ] Keyboard shortcuts
  - [ ] Context-sensitive help
  
- [ ] **Accessibility**
  - [ ] High contrast themes
  - [ ] Font size scaling
  - [ ] Keyboard navigation
  - [ ] Screen reader compatibility

### 8. Performance Optimizations
- [ ] **Large Dataset Handling**
  - [ ] Lazy loading for large files
  - [ ] Data sampling for visualization
  - [ ] Memory usage optimization
  - [ ] Background processing for long calculations

### 9. Plugin System
- [ ] **Extensibility Framework**
  - [ ] Plugin architecture design
  - [ ] Custom model plugins
  - [ ] Third-party integration support
  - [ ] Plugin manager interface

---

## 🐛 Known Issues to Fix

### Bug Fixes
- [ ] **Settings Persistence**: Some settings not properly saved between sessions
- [ ] **Memory Management**: Potential memory leaks in plot management
- [ ] **Unicode Handling**: Issues with special characters in file paths
- [ ] **Error Recovery**: Better error handling for malformed data files

### Improvements
- [ ] **Code Optimization**: Refactor some complex functions for better maintainability  
- [ ] **Test Coverage**: Add comprehensive unit tests
- [ ] **Documentation**: Expand inline documentation and user guides
- [ ] **Build System**: Improve packaging and distribution

---

## 📦 Release Planning

### Next Release
- Complete settings integration
- Theme support
- Excel-like tables
- Equation solving module

### Future
- Advanced plotting features
- Enhanced file management
- Extended mathematical functions

### Long-term
- Plugin system
- Advanced data analysis tools
- Performance optimizations
- Mobile/web interface consideration

---

## 💡 Feature Requests & Ideas

### Community Suggestions
- [ ] **Collaboration**: Share projects and analyses
- [ ] **Database Integration**: Connect to external databases
- [ ] **Report Generation**: Automated report creation in PDF/Word
- [ ] **Version Control**: Track changes in analyses
- [ ] **Batch Processing**: Process multiple files automatically

### Research Features
- [ ] **Monte Carlo Analysis**: Statistical simulation capabilities
- [ ] **Bayesian Analysis**: Bayesian inference tools
- [ ] **Machine Learning**: Basic ML integration for pattern recognition
- [ ] **Signal Processing**: Time series analysis and signal processing

---

*Last updated: 2025-06-11*  
*This TODO list is a living document and will be updated as features are implemented and new requirements emerge.*
