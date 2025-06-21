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
        'curve_fitting_title': 'Ajuste de Curvas - AnaFis',
        'language_label': 'Idioma:',
        'curve_fitting': 'Ajuste de Curvas',
        'uncertainty_calc': 'Cálculo de Incertezas',
        'home': 'Início',
        'settings': 'Configurações',
        'about_version': 'Versão 1.0',
        'about_description': 'Uma aplicação de análise de dados físicos',
        'about_copyright': '© 2023 Seu Nome',
        'ok': 'OK',

        # ===============================
        # SPLASH SCREEN (run.py)
        # ===============================
        'loading_title': 'Carregando AnaFis',
        'loading_message': 'Iniciando AnaFis...',
        'initializing': 'Inicializando...',
        'initialization_complete': 'Inicialização concluída',
        'loading_preferences': 'Carregando preferências...',
        'loading_features': 'Inicializando recursos...',
        'loading_modules': 'Carregando módulos...',
        'loading_plugins': 'Carregando plugins...',
        'loading_interface': 'Carregando interface...',
        'loading_curve_fitting': 'Carregando módulo de ajuste de curvas',
        'loading_uncertainty_calc': 'Carregando calculadora de incertezas',
        'curve_fitting_load_error': 'Falha ao carregar módulo de ajuste de curvas',
        'uncertainty_calc_load_error': 'Falha ao carregar calculadora de incertezas',
        'initialization_error_title': 'Erro de Inicialização',
        'anafis_initialization_error': 'Erro de Inicialização do AnaFis',
        'initialization_failed_message': 'A aplicação falhou ao inicializar corretamente:',
        'exit_application': 'Sair da Aplicação',

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
        'actions': 'Ações',

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
        'help_models': 'Ajuda',
        'help': 'Ajuda',
        'help_models_title': 'Ajuda - Funções em Modelos',
        'help_custom_functions_title': 'Ajuda - Funções Personalizadas',
        'close': 'Fechar',
        
        # Help content for models
        'help_models_content': """=== FUNÇÕES MATEMÁTICAS SUPORTADAS EM MODELOS ===

FUNÇÕES TRIGONOMÉTRICAS:
• sin(x), cos(x), tan(x), cot(x), sec(x), csc(x)
• asin(x), acos(x), atan(x), acot(x), asec(x), acsc(x)
• arcsin(x), arccos(x), arctan(x), arccot(x), arcsec(x), arccsc(x)

FUNÇÕES HIPERBÓLICAS:
• sinh(x), cosh(x), tanh(x), coth(x), sech(x), csch(x)
• asinh(x), acosh(x), atanh(x), acoth(x)
• arcsinh(x), arccosh(x), arctanh(x), arccoth(x)

FUNÇÕES EXPONENCIAIS E LOGARÍTMICAS:
• exp(x) - exponencial natural (e^x)
• log(x) - logaritmo natural (ln)
• ln(x) - logaritmo natural
• log10(x) - logaritmo base 10
• log2(x) - logaritmo base 2
• logb(x, base) - logaritmo com base específica

FUNÇÕES DE POTÊNCIA E RAIZ:
• sqrt(x) - raiz quadrada
• cbrt(x) - raiz cúbica
• square(x) - quadrado (x²)
• pow(x,y) - x elevado a y
• x**y - notação de potência

FUNÇÕES DE ARREDONDAMENTO:
• abs(x) - valor absoluto
• sign(x) - sinal (-1, 0, 1)
• floor(x) - maior inteiro ≤ x
• ceil(x) - menor inteiro ≥ x

FUNÇÕES ESPECIAIS:
• gamma(x) - função gamma
• factorial(x) - fatorial
• erf(x) - função erro
• erfc(x) - função erro complementar
• heaviside(x) - função degrau

CONSTANTES:
• pi - π (3.14159...)
• e - número de Euler (2.71828...)
• inf, infinity - infinito

SINTAXE PARA MODELOS:
• Use parâmetros como: a, b, c, d, e, ...
• Variável independente: x
• Multiplicação implícita: 2x = 2*x, 3sin(x) = 3*sin(x)
• Potências: x^2 = x**2, x² = x**2
• Parênteses: 2(x+1) = 2*(x+1)

EXEMPLOS DE MODELOS:
• Linear: a*x + b
• Exponencial: a*exp(b*x) + c
• Senoidal: a*sin(b*x + c) + d
• Gaussiana: a*exp(-((x-b)/c)^2)
• Potência: a*x^b
• Racional: (a*x + b)/(c*x + d)
""",
        
        # Help content for custom functions
        'help_custom_functions_content': """=== FUNÇÕES MATEMÁTICAS SUPORTADAS EM FUNÇÕES PERSONALIZADAS ===

FUNÇÕES TRIGONOMÉTRICAS:
• sin(x), cos(x), tan(x), cot(x), sec(x), csc(x)
• asin(x), acos(x), atan(x), acot(x), asec(x), acsc(x)
• arcsin(x), arccos(x), arctan(x), arccot(x), arcsec(x), arccsc(x)

FUNÇÕES HIPERBÓLICAS:
• sinh(x), cosh(x), tanh(x), coth(x), sech(x), csch(x)
• asinh(x), acosh(x), atanh(x), acoth(x)
• arcsinh(x), arccosh(x), arctanh(x), arccoth(x)

FUNÇÕES EXPONENCIAIS E LOGARÍTMICAS:
• exp(x) - exponencial natural (e^x)
• log(x) - logaritmo natural (ln)
• ln(x) - logaritmo natural
• log10(x) - logaritmo base 10
• log2(x) - logaritmo base 2
• logb(x, base) - logaritmo com base específica

FUNÇÕES DE POTÊNCIA E RAIZ:
• sqrt(x) - raiz quadrada
• cbrt(x) - raiz cúbica
• square(x) - quadrado (x²)
• pow(x,y) - x elevado a y
• x**y - notação de potência

FUNÇÕES DE ARREDONDAMENTO:
• abs(x) - valor absoluto
• sign(x) - sinal (-1, 0, 1)
• floor(x) - maior inteiro ≤ x
• ceil(x) - menor inteiro ≥ x

FUNÇÕES ESPECIAIS:
• gamma(x) - função gamma
• factorial(x) - fatorial
• erf(x) - função erro
• erfc(x) - função erro complementar
• heaviside(x) - função degrau
• piecewise(cond1, val1, cond2, val2, ...) - função por partes

CONSTANTES:
• pi - π (3.14159...)
• e - número de Euler (2.71828...)
• inf, infinity - infinito

SINTAXE PARA FUNÇÕES PERSONALIZADAS:
• Variável independente: x
• Multiplicação implícita: 2x = 2*x, 3sin(x) = 3*sin(x)
• Potências: x^2 = x**2, x² = x**2
• Parênteses: 2(x+1) = 2*(x+1)
• Combinação de funções: sin(x)*cos(x) = sin(x)*cos(x)

EXEMPLOS DE FUNÇÕES PERSONALIZADAS:
• Trigonométrica: sin(2*pi*x)
• Exponencial: exp(-x^2)
• Composta: sin(x)*exp(-x)
• Logarítmica: ln(x+1)
• Hiperbólica: tanh(x)
• Potência: x^3 - 2*x^2 + x
• Gaussiana: exp(-(x-2)^2/2)
• Combinada: sin(x) + cos(2*x) + 0.5*sin(4*x)

DICAS:
• Use parênteses para clareza: sin(2*x) em vez de sin 2x
• Multiplicação implícita é suportada: 2x, 3sin(x), x(x+1)
• Teste suas funções com diferentes intervalos de x
• Funções podem ser plotadas em qualquer intervalo especificado
""",

        # ===============================
        # PRESET MODELS DICTIONARY
        # ===============================
        'models_presets': {
            # Basic polynomial models
            "Linear: a*x + b": "a*x + b",
            "Quadrático: a*x² + b*x + c": "a*x**2 + b*x + c", 
            "Cúbico: a*x³ + b*x² + c*x + d": "a*x**3 + b*x**2 + c*x + d",
            "Polinômio 4º grau": "a*x**4 + b*x**3 + c*x**2 + d*x + e",
            
            # Exponential and decay models  
            "Exponencial: a*exp(b*x)": "a*exp(b*x)",
            "Exponencial com offset: a*exp(b*x) + c": "a*exp(b*x) + c",
            "Decaimento exponencial: a*exp(-b*x)": "a*exp(-b*x)",
            "Crescimento limitado: a*(1 - exp(-b*x))": "a*(1 - exp(-b*x))",
            "Duplo exponencial: a*exp(b*x) + c*exp(d*x)": "a*exp(b*x) + c*exp(d*x)",
            
            # Logarithmic models
            "Logarítmico: a*log(x) + b": "a*log(x) + b",
            "Log natural: a*ln(x) + b": "a*ln(x) + b", 
            "Log base 10: a*log10(x) + b": "a*log10(x) + b",
            "Log com offset: a*log(b*x + c)": "a*log(b*x + c)",
            
            # Power and root models
            "Potência: a*x^b": "a*x**b",
            "Potência com offset: a*x^b + c": "a*x**b + c",
            "Raiz quadrada: a*sqrt(x) + b": "a*sqrt(x) + b",
            "Raiz cúbica: a*cbrt(x) + b": "a*cbrt(x) + b",
            "Lei de potência: a*x^b*exp(c*x)": "a*x**b*exp(c*x)",
            
            # Trigonometric models
            "Senoidal: a*sin(b*x + c) + d": "a*sin(b*x + c) + d",
            "Cossenoidal: a*cos(b*x + c) + d": "a*cos(b*x + c) + d",
            "Tangente: a*tan(b*x + c) + d": "a*tan(b*x + c) + d",
            "Senoidal amortecida: a*exp(-b*x)*sin(c*x + d)": "a*exp(-b*x)*sin(c*x + d)",
            "Dupla senoidal: a*sin(b*x) + c*sin(d*x)": "a*sin(b*x) + c*sin(d*x)",
            
            # Hyperbolic models
            "Senh: a*sinh(b*x) + c": "a*sinh(b*x) + c",
            "Cosh: a*cosh(b*x) + c": "a*cosh(b*x) + c",
            "Tanh: a*tanh(b*x) + c": "a*tanh(b*x) + c",
            "Hipérbole: a/(b*x + c) + d": "a/(b*x + c) + d",
            
            # Rational functions
            "Racional linear: (a*x + b)/(c*x + d)": "(a*x + b)/(c*x + d)",
            "Racional quadrática: (a*x**2 + b*x + c)/(d*x + e)": "(a*x**2 + b*x + c)/(d*x + e)",
            "Michaelis-Menten: a*x/(b + x)": "a*x/(b + x)",
            
            # Gaussian and bell curves
            "Gaussiana: a*exp(-((x-b)/c)**2)": "a*exp(-((x-b)/c)**2)",
            "Gaussiana normalizada: a*exp(-(x-b)**2/(2*c**2))": "a*exp(-(x-b)**2/(2*c**2))",
            "Dupla gaussiana: a*exp(-((x-b)/c)**2) + d*exp(-((x-e)/f)**2)": "a*exp(-((x-b)/c)**2) + d*exp(-((x-e)/f)**2)",
            "Lorentziana: a/((x-b)**2 + c**2)": "a/((x-b)**2 + c**2)",
            
            # Sigmoidal and logistic functions
            "Sigmoidal: a/(1 + exp(-b*(x-c)))": "a/(1 + exp(-b*(x-c)))",
            "Logística: a/(1 + b*exp(-c*x))": "a/(1 + b*exp(-c*x))",
            "Gompertz: a*exp(-b*exp(-c*x))": "a*exp(-b*exp(-c*x))",
            "Weibull: a*(1 - exp(-(x/b)**c))": "a*(1 - exp(-(x/b)**c))",
            
            # Oscillatory and wave models
            "Onda amortecida: a*exp(-b*x)*cos(c*x + d)": "a*exp(-b*x)*cos(c*x + d)",
            "Batimento: a*sin(b*x)*sin(c*x)": "a*sin(b*x)*sin(c*x)",
            "Chirp linear: a*sin(b*x**2)": "a*sin(b*x**2)",
            
            # Special and physics models
            "Planck: a*x**3/(exp(b*x) - 1)": "a*x**3/(exp(b*x) - 1)",
            "Boltzmann: a*exp(-b*x)": "a*exp(-b*x)",
            "Arrhenius: a*exp(-b/x)": "a*exp(-b/x)",            
            "Saturação: a*x/(b + x)": "a*x/(b + x)"
        },

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
        'all_points': 'Todos',
        'selected_points': 'Selecionados',
        'range_points': 'Faixa',
        'all_points_value': 'Todos',
        'selected_points_value': 'Selecionados',
        'range_points_value': 'Faixa',
        
        # File dialog translations
        'all_compatible': 'Todos os compatíveis',
        'excel_files': 'Arquivos Excel',
        'text_csv_files': 'Arquivos Texto ou CSV',
        'json_files': 'Arquivos JSON',
        'all_files': 'Todos os arquivos',
        
        # UI labels
        'loaded_data': 'Dados Carregados',
        
        # Error messages
        'results_error': 'Erro ao mostrar resultados',
        'file_read_error': 'Erro ao ler arquivo',
        'file_empty_error': 'O arquivo está vazio ou só contém o cabeçalho.',
        'file_columns_error': 'O arquivo precisa ter 4 colunas separadas por \'{delimiter}\' (linha {line}).',
        'file_columns_error_2_3_4': 'O arquivo deve ter 2 colunas (x, y), 3 colunas (x, y, σy) ou 4 colunas (x, σx, y, σy) separadas por \'{delimiter}\' (linha {line}). Encontrado: {cols} colunas.',
        'file_single_column_error': 'O arquivo possui apenas 1 coluna. Para análise de curvas, são necessárias pelo menos 2 colunas (x, y).',
        'file_too_many_columns_error': 'O arquivo possui {cols} colunas, mas apenas 2-4 colunas são suportadas.',
        'file_format_guidance': 'Formatos suportados:\n• 2 colunas: x, y (sem incertezas)\n• 3 colunas: x, y, σy (incerteza apenas em y)\n• 4 colunas: x, σx, y, σy (incertezas em ambos)',
        'file_columns_inconsistent': 'Número inconsistente de colunas na linha {line}. Esperado: {expected}, Encontrado: {found} (separador: \'{delimiter}\').',
        'file_processing_error': 'Erro ao processar o arquivo: {error}',
        'verify_and_retry': 'Ocorreu um erro. Por favor, verifique os dados e tente novamente.',
        'select_file_first': 'Por favor, selecione um arquivo primeiro.',

        # Advanced Config Dialog (advanced_config_dialog.py)
        'advanced_config': 'Configurações avançadas',
        'config_error_adjust_manager': 'Erro de configuração: gerenciador de pontos de ajuste não inicializado',
        'config_error_param_manager': 'Erro de configuração: gerenciador de estimativas de parâmetros não inicializado', 
        'config_error_custom_func': 'Erro de configuração: gerenciador de funções personalizadas não inicializado',

        # Custom Function Manager (custom_function_manager.py)
        'custom_functions': 'Funções personalizadas',
        'custom_funcs_desc': 'Adicione funções para mostrar no gráfico:',
        'function_list': 'Lista de Funções',
        'add_function': 'Adicionar Função',
        'function_example': 'Exemplo: x**2 + 2*x + 1',
        'function_column': 'Função',
        'range_column': 'Intervalo',
        'color_column': 'Cor',
        'enabled_column': '✓',
        'y_equals': 'y =',
        'auto_range': 'Auto',

        # History Manager (history_manager.py)
        'fit_history': 'Histórico de Ajustes',
        'preset_models': 'Modelos Pré-definidos',

        # Graph export options (graph_export_manager.py)
        'save_graph': 'Salvar Gráfico',
        'export_graph': 'Exportar Gráfico',


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

        # Quick actions and UI elements
        'controls': 'Controles',
        'plot': 'Gráfico',
        'quick_actions': 'Ações Rápidas',
        'fit_now': 'Ajustar Agora',
        'clear_all': 'Limpar Tudo',
        'status': 'Status',
        'data': 'Dados',
        'model': 'Modelo',
        'fitting_method': 'Método de ajuste:',
        'odr_method': 'ODR (Regressão Ortogonal)',
        'least_squares_method': 'Mínimos Quadrados',
        'robust_method': 'Robusto (RANSAC/Huber)',
        'weighted_method': 'Mínimos Quadrados Ponderados',
        'bootstrap_method': 'Bootstrap',
        'ridge_method': 'Ridge (Regularização L2)',
        'lasso_method': 'Lasso (Regularização L1)',
        'bayesian_method': 'Bayesiano',
        'fitting_method_used': 'Método utilizado:',
        'fit_results_header': 'Resultados do Ajuste',
        'equation_label': 'Equação:',
        'parameters_header': 'Parâmetros:',
        'statistics_header': 'Estatísticas:',
        'display_error': 'Erro ao exibir resultados',
        'data_no_uncertainties_warning': 'Dados sem incertezas não são adequados para ODR. Usando Mínimos Quadrados.',
        'least_squares_ignores_inc_x': 'Mínimos Quadrados irá ignorar incertezas em X.',
        'odr_requires_y_uncertainties': 'ODR requer incertezas em Y. Use Mínimos Quadrados ou forneça incertezas.',
        'last_fit': 'Último Ajuste',
        'fit': 'Ajuste',

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
        
        # Formula help window
        'formula_help_title': 'Ajuda de Fórmulas',
        'formula_help_basic': 'Operações Básicas:',
        'formula_help_implicit': 'Multiplicação Implícita:',
        'formula_help_functions': 'Funções Disponíveis:',
        'formula_help_trig': 'Trigonométricas:',
        'formula_help_hyp': 'Hiperbólicas:',
        'formula_help_log': 'Logarítmicas e Exponenciais:',
        'formula_help_powers': 'Potências e Raízes:',
        'formula_help_special': 'Funções Especiais:',
        'formula_help_constants': 'Constantes:',
        'formula_help_examples': 'Exemplos:',
        'formula_help_close': 'Fechar',
        
        # Formula help content
        'formula_addition': 'Adição',
        'formula_subtraction': 'Subtração',
        'formula_multiplication': 'Multiplicação',
        'formula_division': 'Divisão',
        'formula_power': 'Potência',
        'formula_for': 'para',
        'formula_parentheses': 'Parênteses para agrupamento',
        'formula_implicit_desc': 'Você pode escrever expressões como 2x ou 3(x+y), que serão interpretadas como 2*x ou 3*(x+y).',
        
        # Function descriptions
        'formula_sine': 'Seno',
        'formula_cosine': 'Cosseno',
        'formula_tangent': 'Tangente',
        'formula_cotangent': 'Cotangente',
        'formula_secant': 'Secante',
        'formula_cosecant': 'Cossecante',
        'formula_arcsine': 'Arco seno',
        'formula_arccosine': 'Arco cosseno',
        'formula_arctangent': 'Arco tangente',
        'formula_arccotangent': 'Arco cotangente',
        'formula_arcsecant': 'Arco secante',
        'formula_arccosecant': 'Arco cossecante',
        'formula_arctangent2': 'Arco tangente de 2 argumentos',
        
        # Hyperbolic functions
        'formula_sinh': 'Seno hiperbólico',
        'formula_cosh': 'Cosseno hiperbólico',
        'formula_tanh': 'Tangente hiperbólica',
        'formula_coth': 'Cotangente hiperbólica',
        'formula_sech': 'Secante hiperbólica',
        'formula_csch': 'Cossecante hiperbólica',
        'formula_asinh': 'Seno hiperbólico inverso',
        'formula_acosh': 'Cosseno hiperbólico inverso',
        'formula_atanh': 'Tangente hiperbólica inversa',
        'formula_acoth': 'Cotangente hiperbólica inversa',
        'formula_asech': 'Secante hiperbólica inversa',
        'formula_acsch': 'Cossecante hiperbólica inversa',
        
        # Logarithmic functions
        'formula_exp': 'Função exponencial',
        'formula_log': 'Logaritmo natural (base e)',
        'formula_ln': 'Logaritmo natural (alias)',
        'formula_logbase': 'Logaritmo com base específica',
        
        # Powers and roots
        'formula_sqrt': 'Raiz quadrada',
        'formula_cbrt': 'Raiz cúbica',
        'formula_root': 'Raiz n-ésima de x',
        'formula_pow': 'Potência',
        'formula_equivalent': 'equivalente a',
        
        # Special functions
        'formula_abs': 'Valor absoluto',
        'formula_sign': 'Função sinal (+1, 0, ou -1)',
        'formula_floor': 'Maior inteiro menor ou igual a x',
        'formula_ceil': 'Menor inteiro maior ou igual a x',
        'formula_frac': 'Parte fracionária de x',
        'formula_gamma': 'Função gama',
        'formula_erf': 'Função erro',
        'formula_erfc': 'Função erro complementar',
        'formula_beta': 'Função beta',
        'formula_min': 'Valor mínimo',
        'formula_max': 'Valor máximo',
        
        # Constants
        'formula_infinity': 'Infinito',
        'formula_golden_ratio': 'Razão áurea',
        'formula_euler_gamma': 'Constante de Euler-Mascheroni',
        'formula_catalan': 'Constante de Catalan',
        'formula_imaginary_unit': 'Unidade imaginária',
        'formula_not_a_number': 'Não é um número',
        'formula_tribonacci': 'Constante de Tribonacci',
        'formula_khinchin': 'Constante de Khinchin',
        'formula_mertens': 'Constante de Mertens',
        'formula_stieltjes': 'Constante de Stieltjes',
        
        # Constants formatting
        'pi_value': '(3,14159...)',
        'e_value': '(2,71828...)',
        'gr_value': '(1,618...)',
        'eg_value': '(0,5772...)',
        'cat_value': '(0,9159...)',

        # Examples
        'formula_circle_area': 'Área de um círculo',
        'formula_quadratic': 'Fórmula quadrática',
        'formula_projectile': 'Movimento de projétil',
        'formula_ohm': 'Lei de Ohm',
        'formula_kinetic': 'Energia cinética',
        'formula_snell': 'Lei de Snell',
        'formula_coulomb': 'Lei de Coulomb',
        'formula_einstein': 'Equivalência massa-energia',
        
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
        'unexpected_error': 'Erro inesperado',
        'error_title': 'Erro',
        'input_error_title': 'Erro de Entrada',
        'formula_error_title': 'Erro na Fórmula',
        'value_error_title': 'Erro de Valor',
        'notice_title': 'Aviso',
        'help_button_text': '?',
        'rendered_formula_title': 'Fórmula Renderizada (LaTeX)',

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
        'check_updates': 'Verificar atualizações ao iniciar',
        'current_theme': 'Tema atual:',
        'available_themes': 'Temas disponíveis:',
        'interface_settings': 'Configurações de Interface',
        'theme': 'Tema:',
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
        'save_error_specific': 'Erro ao salvar configurações específicas',

        # ===============================
        # NEW SETTINGS AND THEMES
        # ===============================
        'updates': 'Atualizações',
        'update_settings': 'Configurações de Atualizações',
        'current_version': 'Versão Atual:',
        'check_for_updates': 'Verificar Atualizações',
        'checking_for_updates': 'Verificando atualizações...',
        'last_checked': 'Última verificação',
        'never_checked': 'Nunca verificado',
        'check_failed': 'Falha na verificação',
        'update_available': 'Atualização disponível',
        'up_to_date': 'Você está usando a versão mais recente',
        'not_checked': 'Clique em "Verificar Atualizações" para verificar',
        'download_update': 'Baixar Atualização',
        'auto_check_updates': 'Verificar atualizações automaticamente',
        
        'light_theme': 'Claro',
        'dark_theme': 'Escuro',
        'system_theme': 'Sistema',

        # ===============================
        # LANGUAGE NAMES
        # ===============================
        'language_pt': 'Portuguese',
        'language_en': 'English',
        
        # ===============================
        # THEME NAMES
        # ===============================
        'theme_light': 'Light',
        'theme_dark': 'Dark',
        'theme_auto': 'Automatic',
        
        # ===============================
        # FILE FORMATS
        # ===============================
        'format_png': 'PNG (Image)',
        'format_jpg': 'JPG (Image)',
        'format_svg': 'SVG (Vector)',
        'format_pdf': 'PDF (Document)',
        
        # ===============================
        # TOOLTIPS
        # ===============================
        'tooltip_theme_dropdown': 'Selecionar o tema da aplicação',
        'tooltip_reload_themes': 'Recarregar todos os temas (integrados e TCL personalizados)',
        'tooltip_open_themes_dir': 'Abrir diretório de temas personalizados',

        # ===============================
        # MAIN APPLICATION ERROR MESSAGES
        # ===============================
        'tab_creation_error': 'Falha ao criar aba',
        'tab_creation_error_detailed': 'Falha ao criar aba: {error}',

        # ===============================
        # UPDATE CHECKER
        # ===============================
        'update_available': 'Atualização Disponível',
        'new_version_available': 'Nova versão disponível',
        'release_notes': 'Notas da Versão',
        'visit_download_page': 'Gostaria de visitar a página de download?',
        'check_for_updates': 'Verificar Atualizações',
        'checking_updates': 'Verificando atualizações...',
        'checking_for_updates': 'Verificando atualizações...',
        'no_updates_available': 'Nenhuma atualização disponível',
        'update_check_failed': 'Falha na verificação de atualizações',
        'current_version': 'Versão atual',
        'latest_version': 'Última versão',
        'auto_check_updates': 'Verificar atualizações automaticamente',
        'last_checked': 'Última verificação',
        'never_checked': 'Nunca verificou atualizações',
        'check_failed': 'Verificação falhou',
        'up_to_date': 'Você está usando a versão mais recente',
        'not_checked': 'Clique "Verificar Atualizações" para verificar atualizações',
        'download': 'Baixar',
        'download_update': 'Baixar Atualização',
        'update_settings': 'Atualizações',

        # ===============================
    },
    'en': {
        # ===============================
        # MAIN APPLICATION (main.py)
        # ===============================
        'app_title': 'AnaFis - Physics Data Analysis',
        'curve_fitting_title': 'Curve Fitting - AnaFis',
        'language_label': 'Language:',
        'curve_fitting': 'Curve Fitting',
        'uncertainty_calc': 'Uncertainty Calculator',
        'home': 'Home',
        'settings': 'Settings',
        'about_version': 'Version 1.0',
        'about_description': 'A physics data analysis application',
        'about_copyright': '© 2023 Your Name',
        'ok': 'OK',

        # ===============================
        # SPLASH SCREEN (run.py)
        # ===============================
        'loading_title': 'Loading AnaFis',
        'loading_message': 'Starting AnaFis...',
        'initializing': 'Initializing...',
        'initialization_complete': 'Initialization complete',
        'loading_preferences': 'Loading preferences...',
        'loading_features': 'Initializing features...',
        'loading_modules': 'Loading modules...',
        'loading_plugins': 'Loading plugins...',
        'loading_interface': 'Loading interface...',
        'loading_curve_fitting': 'Loading curve fitting module',
        'loading_uncertainty_calc': 'Loading uncertainty calculator',
        'curve_fitting_load_error': 'Failed to load curve fitting module',
        'uncertainty_calc_load_error': 'Failed to load uncertainty calculator',
        'initialization_error_title': 'Initialization Error',
        'anafis_initialization_error': 'AnaFis Initialization Error',
        'initialization_failed_message': 'The application failed to initialize properly:',
        'exit_application': 'Exit Application',

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
        'actions': 'Actions',

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
        'help_models': 'Help',
        'help': 'Help',
        'help_models_title': 'Help - Model Functions',
        'help_custom_functions_title': 'Help - Custom Functions',
        'close': 'Close',
        
        # Help content for models
        'help_models_content': """=== SUPPORTED MATHEMATICAL FUNCTIONS IN MODELS ===

TRIGONOMETRIC FUNCTIONS:
• sin(x), cos(x), tan(x), cot(x), sec(x), csc(x)
• asin(x), acos(x), atan(x), acot(x), asec(x), acsc(x)
• arcsin(x), arccos(x), arctan(x), arccot(x), arcsec(x), arccsc(x)

HYPERBOLIC FUNCTIONS:
• sinh(x), cosh(x), tanh(x), coth(x), sech(x), csch(x)
• asinh(x), acosh(x), atanh(x), acoth(x)
• arcsinh(x), arccosh(x), arctanh(x), arccoth(x)

EXPONENTIAL AND LOGARITHMIC FUNCTIONS:
• exp(x) - natural exponential (e^x)
• log(x) - natural logarithm (ln)
• ln(x) - natural logarithm
• log10(x) - base 10 logarithm
• log2(x) - base 2 logarithm
• logb(x, base) - logarithm with specific base

POWER AND ROOT FUNCTIONS:
• sqrt(x) - square root
• cbrt(x) - cube root
• square(x) - square (x²)
• pow(x,y) - x to the power y
• x**y - power notation

ROUNDING FUNCTIONS:
• abs(x) - absolute value
• sign(x) - sign (-1, 0, 1)
• floor(x) - largest integer ≤ x
• ceil(x) - smallest integer ≥ x

SPECIAL FUNCTIONS:
• gamma(x) - gamma function
• factorial(x) - factorial
• erf(x) - error function
• erfc(x) - complementary error function
• heaviside(x) - step function

CONSTANTS:
• pi - π (3.14159...)
• e - Euler's number (2.71828...)
• inf, infinity - infinity

MODEL SYNTAX:
• Use parameters as: a, b, c, d, e, ...
• Independent variable: x
• Implicit multiplication: 2x = 2*x, 3sin(x) = 3*sin(x)
• Powers: x^2 = x**2, x² = x**2
• Parentheses: 2(x+1) = 2*(x+1)

MODEL EXAMPLES:
• Linear: a*x + b
• Exponential: a*exp(b*x) + c
• Sinusoidal: a*sin(b*x + c) + d
• Gaussian: a*exp(-((x-b)/c)^2)
• Power: a*x^b
• Rational: (a*x + b)/(c*x + d)
""",
        
        # Help content for custom functions
        'help_custom_functions_content': """=== SUPPORTED MATHEMATICAL FUNCTIONS IN CUSTOM FUNCTIONS ===

TRIGONOMETRIC FUNCTIONS:
• sin(x), cos(x), tan(x), cot(x), sec(x), csc(x)
• asin(x), acos(x), atan(x), acot(x), asec(x), acsc(x)
• arcsin(x), arccos(x), arctan(x), arccot(x), arcsec(x), arccsc(x)

HYPERBOLIC FUNCTIONS:
• sinh(x), cosh(x), tanh(x), coth(x), sech(x), csch(x)
• asinh(x), acosh(x), atanh(x), acoth(x)
• arcsinh(x), arccosh(x), arctanh(x), arccoth(x)

EXPONENTIAL AND LOGARITHMIC FUNCTIONS:
• exp(x) - natural exponential (e^x)
• log(x) - natural logarithm (ln)
• ln(x) - natural logarithm
• log10(x) - base 10 logarithm
• log2(x) - base 2 logarithm
• logb(x, base) - logarithm with specific base

POWER AND ROOT FUNCTIONS:
• sqrt(x) - square root
• cbrt(x) - cube root
• square(x) - square (x²)
• pow(x,y) - x to the power y
• x**y - power notation

ROUNDING FUNCTIONS:
• abs(x) - absolute value
• sign(x) - sign (-1, 0, 1)
• floor(x) - largest integer ≤ x
• ceil(x) - smallest integer ≥ x

SPECIAL FUNCTIONS:
• gamma(x) - gamma function
• factorial(x) - factorial
• erf(x) - error function
• erfc(x) - complementary error function
• heaviside(x) - step function
• piecewise(cond1, val1, cond2, val2, ...) - piecewise function

CONSTANTS:
• pi - π (3.14159...)
• e - Euler's number (2.71828...)
• inf, infinity - infinity

CUSTOM FUNCTION SYNTAX:
• Independent variable: x
• Implicit multiplication: 2x = 2*x, 3sin(x) = 3*sin(x)
• Powers: x^2 = x**2, x² = x**2
• Parentheses: 2(x+1) = 2*(x+1)
• Function combination: sin(x)*cos(x) = sin(x)*cos(x)

CUSTOM FUNCTION EXAMPLES:
• Trigonometric: sin(2*pi*x)
• Exponential: exp(-x^2)
• Composite: sin(x)*exp(-x)
• Logarithmic: ln(x+1)
• Hyperbolic: tanh(x)
• Power: x^3 - 2*x^2 + x
• Gaussian: exp(-(x-2)^2/2)
• Combined: sin(x) + cos(2*x) + 0.5*sin(4*x)

TIPS:
• Use parentheses for clarity: sin(2*x) instead of sin 2x
• Implicit multiplication is supported: 2x, 3sin(x), x(x+1)
• Test your functions with different x intervals
• Functions can be plotted over any specified interval
""",

        # ===============================
        # PRESET MODELS DICTIONARY
        # ===============================
        'models_presets': {
            # Basic polynomial models
            "Linear: a*x + b": "a*x + b",
            "Quadrático: a*x² + b*x + c": "a*x**2 + b*x + c", 
            "Cúbico: a*x³ + b*x² + c*x + d": "a*x**3 + b*x**2 + c*x + d",
            "Polinômio 4º grau": "a*x**4 + b*x**3 + c*x**2 + d*x + e",
            
            # Exponential and decay models  
            "Exponencial: a*exp(b*x)": "a*exp(b*x)",
            "Exponencial com offset: a*exp(b*x) + c": "a*exp(b*x) + c",
            "Decaimento exponencial: a*exp(-b*x)": "a*exp(-b*x)",
            "Crescimento limitado: a*(1 - exp(-b*x))": "a*(1 - exp(-b*x))",
            "Duplo exponencial: a*exp(b*x) + c*exp(d*x)": "a*exp(b*x) + c*exp(d*x)",
            
            # Logarithmic models
            "Logarítmico: a*log(x) + b": "a*log(x) + b",
            "Log natural: a*ln(x) + b": "a*ln(x) + b", 
            "Log base 10: a*log10(x) + b": "a*log10(x) + b",
            "Log com offset: a*log(b*x + c)": "a*log(b*x + c)",
            
            # Power and root models
            "Potência: a*x^b": "a*x**b",
            "Potência com offset: a*x^b + c": "a*x**b + c",
            "Raiz quadrada: a*sqrt(x) + b": "a*sqrt(x) + b",
            "Raiz cúbica: a*cbrt(x) + b": "a*cbrt(x) + b",
            "Lei de potência: a*x^b*exp(c*x)": "a*x**b*exp(c*x)",
            
            # Trigonometric models
            "Senoidal: a*sin(b*x + c) + d": "a*sin(b*x + c) + d",
            "Cossenoidal: a*cos(b*x + c) + d": "a*cos(b*x + c) + d",
            "Tangente: a*tan(b*x + c) + d": "a*tan(b*x + c) + d",
            "Senoidal amortecida: a*exp(-b*x)*sin(c*x + d)": "a*exp(-b*x)*sin(c*x + d)",
            "Dupla senoidal: a*sin(b*x) + c*sin(d*x)": "a*sin(b*x) + c*sin(d*x)",
            
            # Hyperbolic models
            "Senh: a*sinh(b*x) + c": "a*sinh(b*x) + c",
            "Cosh: a*cosh(b*x) + c": "a*cosh(b*x) + c",
            "Tanh: a*tanh(b*x) + c": "a*tanh(b*x) + c",
            "Hipérbole: a/(b*x + c) + d": "a/(b*x + c) + d",
            
            # Rational functions
            "Racional linear: (a*x + b)/(c*x + d)": "(a*x + b)/(c*x + d)",
            "Racional quadrática: (a*x**2 + b*x + c)/(d*x + e)": "(a*x**2 + b*x + c)/(d*x + e)",
            "Michaelis-Menten: a*x/(b + x)": "a*x/(b + x)",
            
            # Gaussian and bell curves
            "Gaussiana: a*exp(-((x-b)/c)**2)": "a*exp(-((x-b)/c)**2)",
            "Gaussiana normalizada: a*exp(-(x-b)**2/(2*c**2))": "a*exp(-(x-b)**2/(2*c**2))",
            "Dupla gaussiana: a*exp(-((x-b)/c)**2) + d*exp(-((x-e)/f)**2)": "a*exp(-((x-b)/c)**2) + d*exp(-((x-e)/f)**2)",
            "Lorentziana: a/((x-b)**2 + c**2)": "a/((x-b)**2 + c**2)",
            
            # Sigmoidal and logistic functions
            "Sigmoidal: a/(1 + exp(-b*(x-c)))": "a/(1 + exp(-b*(x-c)))",
            "Logística: a/(1 + b*exp(-c*x))": "a/(1 + b*exp(-c*x))",
            "Gompertz: a*exp(-b*exp(-c*x))": "a*exp(-b*exp(-c*x))",
            "Weibull: a*(1 - exp(-(x/b)**c))": "a*(1 - exp(-(x/b)**c))",
            
            # Oscillatory and wave models
            "Onda amortecida: a*exp(-b*x)*cos(c*x + d)": "a*exp(-b*x)*cos(c*x + d)",
            "Batimento: a*sin(b*x)*sin(c*x)": "a*sin(b*x)*sin(c*x)",
            "Chirp linear: a*sin(b*x**2)": "a*sin(b*x**2)",
            
            # Special and physics models
            "Planck: a*x**3/(exp(b*x) - 1)": "a*x**3/(exp(b*x) - 1)",
            "Boltzmann: a*exp(-b*x)": "a*exp(-b*x)",
            "Arrhenius: a*exp(-b/x)": "a*exp(-b/x)",            
            "Saturação: a*x/(b + x)": "a*x/(b + x)"
        },

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
        'all_points': 'All',
        'selected_points': 'Selected',
        'range_points': 'Range',
        'all_points_value': 'All',
        'selected_points_value': 'Selected',
        'range_points_value': 'Range',

        # File dialog translations
        'all_compatible': 'All compatible',
        'excel_files': 'Excel files',
        'text_csv_files': 'Text or CSV files',
        'json_files': 'JSON files',
        'all_files': 'All files',
        
        # UI labels
        'loaded_data': 'Loaded Data',
        
        # Error messages
        'results_error': 'Error showing results',
        'file_read_error': 'Error reading file',
        'file_empty_error': 'The file is empty or only contains the header.',
        'file_columns_error': 'The file must have 4 columns separated by \'{delimiter}\' (line {line}).',
        'file_columns_error_2_3_4': 'The file must have 2 columns (x, y), 3 columns (x, y, σy) or 4 columns (x, σx, y, σy) separated by \'{delimiter}\' (line {line}). Found: {cols} columns.',
        'file_single_column_error': 'The file has only 1 column. For curve analysis, at least 2 columns (x, y) are required.',
        'file_too_many_columns_error': 'The file has {cols} columns, but only 2-4 columns are supported.',
        'file_format_guidance': 'Supported formats:\n• 2 columns: x, y (no uncertainties)\n• 3 columns: x, y, σy (uncertainty in y only)\n• 4 columns: x, σx, y, σy (uncertainties in both)',
        'file_columns_inconsistent': 'Inconsistent number of columns at line {line}. Expected: {expected}, Found: {found} (delimiter: \'{delimiter}\').',
        'file_processing_error': 'Error processing the file: {error}',

        # Advanced Config Dialog (advanced_config_dialog.py)
        'advanced_config': 'Advanced configuration',
        'config_error_adjust_manager': 'Configuration error: adjustment points manager not initialized',
        'config_error_param_manager': 'Configuration error: parameter estimates manager not initialized',
        'config_error_custom_func': 'Configuration error: custom function manager not initialized',

        # Custom Function Manager (custom_function_manager.py)
        'custom_functions': 'Custom functions',
        'custom_funcs_desc': 'Add functions to show on graph:',
        'function_list': 'Function List',
        'add_function': 'Add Function',
        'function_example': 'Example: x**2 + 2*x + 1',
        'function_column': 'Function',
        'range_column': 'Range',
        'color_column': 'Color',
        'enabled_column': '✓',
        'y_equals': 'y =',
        'auto_range': 'Auto',

        # History Manager (history_manager.py)
        'fit_history': 'Fit History',
        'preset_models': 'Preset Models',

        # Graph export options
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

        # Quick actions and UI elements
        'controls': 'Controls',
        'plot': 'Plot',
        'quick_actions': 'Quick Actions',
        'fit_now': 'Fit Now',
        'clear_all': 'Clear All',
        'status': 'Status',
        'data': 'Data',
        'model': 'Model',
        'fitting_method': 'Fitting method:',
        'odr_method': 'ODR (Orthogonal Distance Regression)',
        'least_squares_method': 'Least Squares',
        'robust_method': 'Robust (RANSAC/Huber)',
        'weighted_method': 'Weighted Least Squares',
        'bootstrap_method': 'Bootstrap',
        'ridge_method': 'Ridge (L2 Regularization)',
        'lasso_method': 'Lasso (L1 Regularization)',
        'bayesian_method': 'Bayesian',
        'fitting_method_used': 'Fitting method used:',
        'fit_results_header': 'Fitting Results',
        'equation_label': 'Equation:',
        'parameters_header': 'Parameters:',
        'statistics_header': 'Statistics:',
        'display_error': 'Error displaying results',
        'data_no_uncertainties_warning': 'Data without uncertainties is not suitable for ODR. Using Least Squares.',
        'least_squares_ignores_inc_x': 'Least Squares fitting will ignore uncertainty in X values.',
        'odr_requires_y_uncertainties': 'ODR requires Y uncertainties. Use Least Squares or provide uncertainties.',
        'last_fit': 'Last Fit',
        'fit': 'Fit',

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
        
        # Formula help window
        'formula_help_title': 'Formula Help',
        'formula_help_basic': 'Basic Operations:',
        'formula_help_implicit': 'Implicit Multiplication:',
        'formula_help_functions': 'Available Functions:',
        'formula_help_trig': 'Trigonometric:',
        'formula_help_hyp': 'Hyperbolic:',
        'formula_help_log': 'Logarithmic and Exponential:',
        'formula_help_powers': 'Powers and Roots:',
        'formula_help_special': 'Special Functions:',
        'formula_help_constants': 'Constants:',
        'formula_help_examples': 'Examples:',
        'formula_help_close': 'Close',
        
        # Formula help content
        'formula_addition': 'Addition',
        'formula_subtraction': 'Subtraction',
        'formula_multiplication': 'Multiplication',
        'formula_division': 'Division',
        'formula_power': 'Power',
        'formula_for': 'for',
        'formula_parentheses': 'Parentheses for grouping',
        'formula_implicit_desc': 'You can write expressions like 2x or 3(x+y), which will be interpreted as 2*x or 3*(x+y).',
        
        # Function descriptions
        'formula_sine': 'Sine',
        'formula_cosine': 'Cosine',
        'formula_tangent': 'Tangent',
        'formula_cotangent': 'Cotangent',
        'formula_secant': 'Secant',
        'formula_cosecant': 'Cosecant',
        'formula_arcsine': 'Arcsine',
        'formula_arccosine': 'Arccosine',
        'formula_arctangent': 'Arctangent',
        'formula_arccotangent': 'Arccotangent',
        'formula_arcsecant': 'Arcsecant',
        'formula_arccosecant': 'Arccosecant',
        'formula_arctangent2': '2-argument arctangent',
        
        # Hyperbolic functions
        'formula_sinh': 'Hyperbolic sine',
        'formula_cosh': 'Hyperbolic cosine',
        'formula_tanh': 'Hyperbolic tangent',
        'formula_coth': 'Hyperbolic cotangent',
        'formula_sech': 'Hyperbolic secant',
        'formula_csch': 'Hyperbolic cosecant',
        'formula_asinh': 'Inverse hyperbolic sine',
        'formula_acosh': 'Inverse hyperbolic cosine',
        'formula_atanh': 'Inverse hyperbolic tangent',
        'formula_acoth': 'Inverse hyperbolic cotangent',
        'formula_asech': 'Inverse hyperbolic secant',
        'formula_acsch': 'Inverse hyperbolic cosecant',
        
        # Logarithmic functions
        'formula_exp': 'Exponential function',
        'formula_log': 'Natural logarithm (base e)',
        'formula_ln': 'Natural logarithm (alias)',
        'formula_logbase': 'Logarithm with specified base',
        
        # Powers and roots
        'formula_sqrt': 'Square root',
        'formula_cbrt': 'Cube root',
        'formula_root': 'nth root of x',
        'formula_pow': 'Power',
        'formula_equivalent': 'equivalent to',
        
        # Special functions
        'formula_abs': 'Absolute value',
        'formula_sign': 'Sign function (+1, 0, or -1)',
        'formula_floor': 'Greatest integer less than or equal to x',
        'formula_ceil': 'Least integer greater than or equal to x',
        'formula_frac': 'Fractional part of x',
        'formula_gamma': 'Gamma function',
        'formula_erf': 'Error function',
        'formula_erfc': 'Complementary error function',
        'formula_beta': 'Beta function',
        'formula_min': 'Minimum value',
        'formula_max': 'Maximum value',
        
        # Constants
        'formula_infinity': 'Infinity',
        'formula_golden_ratio': 'Golden ratio',
        'formula_euler_gamma': 'Euler-Mascheroni constant',
        'formula_catalan': 'Catalan constant',
        'formula_imaginary_unit': 'Imaginary unit',
        'formula_not_a_number': 'Not a number',
        'formula_tribonacci': 'Tribonacci constant',
        'formula_khinchin': 'Khinchin constant',
        'formula_mertens': 'Mertens constant',
        'formula_stieltjes': 'Stieltjes constant',
        
        # Constants formatting
        'pi_value': '(3.14159...)',
        'e_value': '(2.71828...)',
        'gr_value': '(1.618...)',
        'eg_value': '(0.5772...)',
        'cat_value': '(0.9159...)',

        # Examples
        'formula_circle_area': 'Area of a circle',
        'formula_quadratic': 'Quadratic formula',
        'formula_projectile': 'Projectile motion',
        'formula_ohm': 'Ohm\'s law',
        'formula_kinetic': 'Kinetic energy',
        'formula_snell': 'Snell\'s law',
        'formula_coulomb': 'Coulomb\'s law',
        'formula_einstein': 'Mass-energy equivalence',
        
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
        'unexpected_error': 'Unexpected error',
        'error_title': 'Error',
        'input_error_title': 'Input Error',
        'formula_error_title': 'Formula Error',
        'value_error_title': 'Value Error',
        'notice_title': 'Notice',
        'help_button_text': '?',
        'rendered_formula_title': 'Rendered Formula (LaTeX)',
        'empty_variable_name': 'Please enter variable names.',
        'empty_formula': 'Please enter a formula.',
        'generate_formula': 'Generate Formula',
        'invalid_vars': 'Please enter a valid number of variables',
        'invalid_vars': 'Please enter valid names and values for the variables.',
        'positive_points': 'Number of points must be positive',
        'invalid_points': 'Please enter a valid number of points for the fit.',
        'verify_and_retry': 'An error occurred. Please verify the data and try again.',
        'select_file_first': 'Please select a file first.',
        'empty_variable_name': 'Please enter non-empty variable names.',
        'empty_formula': 'Please enter a formula.',
        'unexpected_error': 'Unexpected error',
        'error_title': 'Error',
        'input_error_title': 'Input Error',
        'formula_error_title': 'Formula Error',
        'value_error_title': 'Value Error',
        'notice_title': 'Notice',
        'help_button_text': '?',
        'rendered_formula_title': 'Rendered Formula (LaTeX)',

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
        'check_updates': 'Check for updates on startup',
        'current_theme': 'Current theme:',
        'available_themes': 'Available themes:',
        'interface_settings': 'Interface Settings',
        'theme': 'Theme:',
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
        'save_error_specific': 'Error saving specific settings',

        # ===============================
        # NEW SETTINGS AND THEMES
        # ===============================
        'updates': 'Updates',
        'update_settings': 'Update Settings',
        'current_version': 'Current Version:',
        'check_for_updates': 'Check for Updates',
        'checking_for_updates': 'Checking for updates...',
        'last_checked': 'Last checked',
        'never_checked': 'Never checked',
        'check_failed': 'Check failed',
        'update_available': 'Update available',
        'up_to_date': 'You are using the latest version',
        'not_checked': 'Click "Check for Updates" to check',
        'download_update': 'Download Update',
        'auto_check_updates': 'Check for updates automatically',
        
        'light_theme': 'Light',
        'dark_theme': 'Dark',
        'system_theme': 'System',

        # ===============================
        # LANGUAGE NAMES
        # ===============================
        'language_pt': 'Portuguese',
        'language_en': 'English',
        
        # ===============================
        # THEME NAMES
        # ===============================
        'theme_light': 'Light',
        'theme_dark': 'Dark',
        'theme_auto': 'Automatic',
        
        # ===============================
        # FILE FORMATS
        # ===============================
        'format_png': 'PNG (Image)',
        'format_jpg': 'JPG (Image)',
        'format_svg': 'SVG (Vector)',
        'format_pdf': 'PDF (Document)',
        
        # ===============================
        # TOOLTIPS
        # ===============================
        'tooltip_theme_dropdown': 'Select the application theme',
        'tooltip_reload_themes': 'Reload all themes (built-in and custom TCL themes)',
        'tooltip_open_themes_dir': 'Open custom themes directory',

        # ===============================
        # MAIN APPLICATION ERROR MESSAGES
        # ===============================
        'tab_creation_error': 'Failed to create tab',
        'tab_creation_error_detailed': 'Failed to create tab: {error}',

        # ===============================
        # UPDATE CHECKER
        # ===============================
        'update_available': 'Update Available',
        'new_version_available': 'A new version is available',
        'release_notes': 'Release Notes',
        'visit_download_page': 'Would you like to visit the download page?',
        'check_for_updates': 'Check for Updates',
        'checking_updates': 'Checking for updates...',
        'checking_for_updates': 'Checking for updates...',
        'no_updates_available': 'No updates available',
        'update_check_failed': 'Update check failed',
        'current_version': 'Current version',
        'latest_version': 'Latest version',
        'auto_check_updates': 'Check for updates automatically',
        'last_checked': 'Last checked',
        'never_checked': 'Never checked for updates',
        'check_failed': 'Check failed',
        'up_to_date': 'You are using the latest version',
        'not_checked': 'Click "Check for Updates" to check for updates',
        'download': 'Download',
        'download_update': 'Download Update',
        'update_settings': 'Updates',

        # ===============================
    }
}
