"""
Translation constants for the AnaFis application.
Organized by module/component for easier maintenance.
"""

from typing import Dict, Any

TRANSLATIONS: Dict[str, Dict[str, Any]] = {
    'pt': {
        # ===============================
        # MAIN APPLICATION (main.py)
        # ===============================
        'app_title': 'AnaFis - Análise de Dados Físicos',
        'language_label': 'Idioma:',
        'curve_fitting': 'Ajuste de Curvas',
        'uncertainty_calc': 'Cálculo de Incertezas',
        'home': 'Início',
        'settings': 'Configurações',

        # ===============================
        # SPLASH SCREEN (run.py)
        # ===============================
        'loading_title': 'Carregando AnaFis',
        'loading_message': 'Iniciando AnaFis...',

        # ===============================
        # SHARED/GENERAL UI ELEMENTS
        # ===============================
        'error': 'Erro',
        'info': 'Informação',
        'warning': 'Aviso',
        'close': 'Fechar',
        'add': 'Adicionar',
        'remove': 'Remover',
        'browse': 'Procurar',
        'open': 'Abrir',
        'save': 'Salvar',
        'exit': 'Sair',
        'help': 'Ajuda',
        'about': 'Sobre',
        'preview': 'Visualizar',
        'color': 'Cor:',
        'progress': 'Progresso',
        'results': 'Resultados',
        'equation': 'Equação:',
        'title': 'Título:',
        'parameters': 'Parâmetros',
        'variables': 'Variáveis',
        'value': 'Valor',
        'uncertainty': 'Incerteza',
        'formula': 'Fórmula:',
        'calculate': 'Calcular',
        'variable': 'Variável',

        # File operations
        'data_file': 'Arquivo de Dados:',
        'open_file': 'Abrir Arquivo',
        'save_file': 'Salvar Arquivo',
        'supported_files': 'Arquivos Suportados',
        'all_files': 'Todos os Arquivos',
        'select_data_file': 'Selecionar arquivo de dados',
        'no_data_loaded': 'Nenhum dado carregado',

        # ===============================
        # CURVE FITTING MODULE (gui/ajuste_curva/)
        # ===============================

        # Main GUI (main_gui.py)
        'data_input': 'Entrada de Dados',
        'load_data': 'Carregar Dados',
        'fit_model': 'Ajustar Modelo',
        'plot_data': 'Plotar Dados',
        'perform_fit': 'Realizar Ajuste',
        'fitting_parameters': 'Parâmetros do Ajuste',
        'fitting_actions': 'Ajuste e Progresso',

        # UI Builder (ui_builder.py)
        'graph_settings': 'Configurações do Gráfico',
        'graph_title': 'Título:',
        'x_scale': 'Escala X:',
        'y_scale': 'Escala Y:',
        'axis_labels': 'Rótulos dos Eixos',
        'x_label': 'Rótulo X',
        'y_label': 'Rótulo Y',
        'x_axis': 'Eixo X',
        'y_axis': 'Eixo Y',
        'linear': 'Linear',
        'log': 'Log',
        'max_iterations': 'Máx. iterações:',
        'num_points': 'Pontos do ajuste:',
        'more_configs': 'Mais configurações...',

        # Plot Manager (plot_manager.py)
        'data_label': 'Dados',
        'fit_label': 'Ajuste',
        'fit_title_prefix': 'Ajuste:',
        'residuals': 'Resíduos',
        'data_points': 'Pontos',
        'fit_curve': 'Ajuste',

        # Parameter Estimates Manager (parameter_estimates_manager.py)
        'initial_values': 'Valores iniciais:',
        'initial_estimates': 'Estimativas Iniciais',

        # Adjustment Points Manager (adjustment_points_manager.py)
        'fit_points': 'Pontos do ajuste:',
        'adjustment_points': 'Pontos de ajuste',
        'min_x': 'X Mínimo',
        'max_x': 'X Máximo',
        'points_type': 'Tipo de pontos:',

        # Advanced Config Dialog (advanced_config_dialog.py)
        'advanced_config': 'Configurações avançadas',

        # Custom Function Manager (custom_function_manager.py)
        'custom_functions': 'Funções personalizadas',
        'custom_funcs_desc': 'Adicione funções para mostrar no gráfico:',

        # History Manager (history_manager.py)
        'fit_history': 'Histórico de Ajustes',
        'preset_models': 'Modelos Pré-definidos',

        # Export Managers (graph_export_manager.py, data_export_manager.py)
        'save_graph': 'Salvar Gráfico',
        'export_graph': 'Exportar Gráfico',
        'export_data': 'Exportar Dados',
        'export_results': 'Exportar Resultados',
        'data_preview': 'Pré-visualização dos Dados',
        'fit_and_data': 'Ajuste + dados',
        'only_data': 'Apenas dados',
        'only_fit': 'Apenas ajuste',
        'only_residuals': 'Apenas resíduos',
        'full_graph': 'Gráfico completo',
        'main_graph': 'Gráfico principal',

        # Fitting process status
        'fit_in_progress': 'Ajuste em andamento...',
        'fit_complete': 'Ajuste concluído!',
        'fit_error': 'Erro durante o ajuste',
        'starting_fit': 'Iniciando ajuste...',
        'chi_squared': 'Chi Quadrado',
        'r_squared': 'R Quadrado',
        'reduced_chi_squared': 'Chi² reduzido',
        'iteration': 'Iteração: {iter}',

        # ===============================
        # UNCERTAINTY CALCULATOR MODULE (gui/incerteza/)
        # ===============================

        # Main uncertainty GUI (calculo_incertezas_gui.py)
        'operation_mode': 'Modo de operação',
        'calc_value_uncertainty': 'Calcular valor e incerteza',
        'generate_uncertainty_formula': 'Gerar fórmula de incerteza',
        'number_of_variables': 'Número de variáveis:',
        'create_fields': 'Criar campos',
        'variables_list': 'Separadas por vírgula:',
        'generate_formula': 'Gerar fórmula',
        'copy_formula': 'Copiar fórmula',
        'show_latex': 'Exibir em LaTeX',

        # Results display
        'result_header': '=== Resultado ===',
        'calculated_value': 'Valor calculado:',
        'total_uncertainty': 'Incerteza total:',
        'final_result': 'Resultado final:',
        'uncertainty_formula_header': '=== Fórmula de Incerteza (LaTeX) ===',
        'copy_latex_code': 'Copie o código abaixo para LaTeX:',

        # ===============================
        # ERROR MESSAGES
        # ===============================
        'file_not_found': "O arquivo '{file}' não foi encontrado.",
        'invalid_number': "Por favor, insira um número válido.",
        'invalid_file': 'Arquivo inválido',
        'invalid_data': 'Dados inválidos',
        'plot_error': 'Erro ao plotar',
        'invalid_formula': 'Erro ao processar a fórmula: {error}',
        'invalid_vars': 'Por favor, insira nomes e valores válidos para as variáveis.',
        'positive_points': 'O número de pontos deve ser positivo',
        'invalid_points': 'Por favor, insira um número válido de pontos para o ajuste.',
        'verify_and_retry': 'Ocorreu um erro. Verifique os dados e tente novamente.',

        # ===============================
        # SETTINGS DIALOG (gui/settings/settings_dialog.py)
        # ===============================

        'general': 'Geral',
        'interface': 'Interface',
        'data': 'Dados',
        'export': 'Exportação',
        'general_settings': 'Configurações Gerais',
        'cancel': 'Cancelar',
        'reset': 'Restaurar Padrões',
        'auto_save': 'Salvar automaticamente',
        'auto_backup': 'Fazer backup automaticamente',
        'backup_interval': 'Intervalo de backup (minutos):',
        'check_updates': 'Verificar atualizações ao iniciar',
        'interface_settings': 'Configurações de Interface',
        'theme': 'Tema:',
        'font_size': 'Tamanho da fonte:',
        'show_tooltips': 'Mostrar dicas de ferramentas',
        'remember_window_size': 'Lembrar tamanho da janela',
        'show_welcome_screen': 'Mostrar tela de boas-vindas',
        'data_settings': 'Configurações de Dados',
        'decimal_places': 'Casas decimais:',
        'advanced_mode': 'Modo avançado',
        'export_settings': 'Configurações de Exportação',
        'graph_dpi': 'DPI do gráfico:',
        'export_format': 'Formato de exportação:',
        'last_export_directory': 'Último diretório de exportação:',
        'select_directory': 'Selecionar Diretório',
        'confirm': 'Confirmar',
        'reset_confirm': ('Restaurar todas as configurações para os '
                          'valores padrão?'),
        'save_error': 'Erro ao salvar configurações',
    },
    'en': {
        # ===============================
        # MAIN APPLICATION (main.py)
        # ===============================
        'app_title': 'AnaFis - Physics Data Analysis',
        'language_label': 'Language:',
        'curve_fitting': 'Curve Fitting',
        'uncertainty_calc': 'Uncertainty Calculator',
        'home': 'Home',
        'settings': 'Settings',

        # ===============================
        # SPLASH SCREEN (run.py)
        # ===============================
        'loading_title': 'Loading AnaFis',
        'loading_message': 'Starting AnaFis...',

        # ===============================
        # SHARED/GENERAL UI ELEMENTS
        # ===============================
        'error': 'Error',
        'info': 'Information',
        'warning': 'Warning',
        'close': 'Close',
        'add': 'Add',
        'remove': 'Remove',
        'browse': 'Browse',
        'open': 'Open',
        'save': 'Save',
        'exit': 'Exit',
        'help': 'Help',
        'about': 'About',
        'preview': 'Preview',
        'color': 'Color:',
        'progress': 'Progress',
        'results': 'Results',
        'equation': 'Equation:',
        'title': 'Title:',
        'parameters': 'Parameters',
        'variables': 'Variables',
        'value': 'Value',
        'uncertainty': 'Uncertainty',
        'formula': 'Formula:',
        'calculate': 'Calculate',
        'variable': 'Variable',

        # File operations
        'data_file': 'Data File:',
        'open_file': 'Open File',
        'save_file': 'Save File',
        'supported_files': 'Supported Files',
        'all_files': 'All Files',
        'select_data_file': 'Select data file',
        'no_data_loaded': 'No data loaded',

        # ===============================
        # CURVE FITTING MODULE (gui/ajuste_curva/)
        # ===============================

        # Main GUI (main_gui.py)
        'data_input': 'Data Input',
        'load_data': 'Load Data',
        'fit_model': 'Fit Model',
        'plot_data': 'Plot Data',
        'perform_fit': 'Perform Fit',
        'fitting_parameters': 'Fitting Parameters',
        'fitting_actions': 'Fitting & Progress',

        # UI Builder (ui_builder.py)
        'graph_settings': 'Graph Settings',
        'graph_title': 'Title:',
        'x_scale': 'X Scale:',
        'y_scale': 'Y Scale:',
        'axis_labels': 'Axis Labels',
        'x_label': 'X Label',
        'y_label': 'Y Label',
        'x_axis': 'X Axis',
        'y_axis': 'Y Axis',
        'linear': 'Linear',
        'log': 'Log',
        'max_iterations': 'Max iterations:',
        'num_points': 'Fit points:',
        'more_configs': 'More settings...',

        # Plot Manager (plot_manager.py)
        'data_label': 'Data',
        'fit_label': 'Fit',
        'fit_title_prefix': 'Fit:',
        'residuals': 'Residuals',
        'data_points': 'Data Points',
        'fit_curve': 'Fit',

        # Parameter Estimates Manager (parameter_estimates_manager.py)
        'initial_values': 'Initial Values:',
        'initial_estimates': 'Initial Estimates',

        # Adjustment Points Manager (adjustment_points_manager.py)
        'fit_points': 'Fit points:',
        'adjustment_points': 'Adjustment Points',
        'min_x': 'Minimum X',
        'max_x': 'Maximum X',
        'points_type': 'Points type:',

        # Advanced Config Dialog (advanced_config_dialog.py)
        'advanced_config': 'Advanced configuration',

        # Custom Function Manager (custom_function_manager.py)
        'custom_functions': 'Custom functions',
        'custom_funcs_desc': 'Add functions to show on graph:',

        # History Manager (history_manager.py)
        'fit_history': 'Fit History',
        'preset_models': 'Preset Models',

        # Export Managers (graph_export_manager.py, data_export_manager.py)
        'save_graph': 'Save Graph',
        'export_graph': 'Export Graph',
        'export_data': 'Export Data',
        'export_results': 'Export Results',
        'data_preview': 'Data Preview',
        'fit_and_data': 'Fit + data',
        'only_data': 'Data only',
        'only_fit': 'Fit only',
        'only_residuals': 'Residuals only',
        'full_graph': 'Full graph',
        'main_graph': 'Main graph',

        # Fitting process status
        'fit_in_progress': 'Fit in progress...',
        'fit_complete': 'Fit complete!',
        'fit_error': 'Error during fit',
        'starting_fit': 'Starting fit...',
        'chi_squared': 'Chi Squared',
        'r_squared': 'R Squared',
        'reduced_chi_squared': 'Reduced Chi²',
        'iteration': 'Iteration: {iter}',

        # ===============================
        # UNCERTAINTY CALCULATOR MODULE (gui/incerteza/)
        # ===============================

        # Main uncertainty GUI (calculo_incertezas_gui.py)
        'operation_mode': 'Operation mode',
        'calc_value_uncertainty': 'Calculate value and uncertainty',
        'generate_uncertainty_formula': 'Generate uncertainty formula',
        'number_of_variables': 'Number of variables:',
        'create_fields': 'Create fields',
        'variables_list': 'Comma separated:',
        'generate_formula': 'Generate formula',
        'copy_formula': 'Copy formula',
        'show_latex': 'Show LaTeX',

        # Results display
        'result_header': '=== Result ===',
        'calculated_value': 'Calculated value:',
        'total_uncertainty': 'Total uncertainty:',
        'final_result': 'Final result:',
        'uncertainty_formula_header': '=== Uncertainty Formula (LaTeX) ===',
        'copy_latex_code': 'Copy the code below for LaTeX:',

        # ===============================
        # ERROR MESSAGES
        # ===============================
        'file_not_found': "The file '{file}' was not found.",
        'invalid_number': "Please enter a valid number.",
        'invalid_file': 'Invalid file',
        'invalid_data': 'Invalid data',
        'plot_error': 'Plot error',
        'invalid_formula': 'Error processing formula: {error}',
        'invalid_vars': 'Please enter valid names and values for the variables.',
        'positive_points': 'Number of points must be positive',
        'invalid_points': 'Please enter a valid number of points for the fit.',
        'verify_and_retry': 'An error occurred. Please verify the data and try again.',

        # ===============================
        # SETTINGS DIALOG (gui/settings/settings_dialog.py)
        # ===============================

        'general': 'General',
        'interface': 'Interface',
        'data': 'Data',
        'export': 'Export',
        'general_settings': 'General Settings',
        'cancel': 'Cancel',
        'reset': 'Restore Defaults',
        'auto_save': 'Auto save',
        'auto_backup': 'Auto backup',
        'backup_interval': 'Backup interval (minutes):',
        'check_updates': 'Check for updates on startup',
        'interface_settings': 'Interface Settings',
        'theme': 'Theme:',
        'font_size': 'Font size:',
        'show_tooltips': 'Show tooltips',
        'remember_window_size': 'Remember window size',
        'show_welcome_screen': 'Show welcome screen',
        'data_settings': 'Data Settings',
        'decimal_places': 'Decimal places:',
        'advanced_mode': 'Advanced mode',
        'export_settings': 'Export Settings',
        'graph_dpi': 'Graph DPI:',
        'export_format': 'Export format:',        
        'last_export_directory': 'Last export directory:',        
        'select_directory': 'Select Directory',
        'confirm': 'Confirm',
        'reset_confirm': 'Reset all settings to default values?',
        'save_error': 'Error saving settings',
    }
}
