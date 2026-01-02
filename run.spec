# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['AnaFis\\run.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\pedro\\AppData\\Local\\Programs\\Python\\Python314\\Lib\\site-packages\\matplotlib\\mpl-data', 'mpl-data')],
    hiddenimports=['numpy', 'scipy', 'sympy', 'matplotlib', 'pandas', 'sklearn', 'ttkthemes', 'ttkthemes.themes', 'matplotlib.backends.backend_tkagg', 'scipy.optimize', 'scipy.integrate', 'scipy.stats', 'scipy.special', 'scipy.linalg', 'sympy.core', 'sympy.solvers', 'sympy.utilities', 'pandas.io', 'sklearn.linear_model', 'sklearn.metrics', 'sklearn.preprocessing', 'app_files.utils.translations.pt', 'app_files.utils.translations.en', 'app_files.utils.translations.pt_help', 'app_files.utils.translations.en_help', 'app_files.gui.ajuste_curva.main_gui', 'app_files.gui.ajuste_curva.data_handler', 'app_files.gui.ajuste_curva.model_manager', 'app_files.gui.ajuste_curva.plot_manager', 'app_files.gui.ajuste_curva.adjustment_points_manager', 'app_files.gui.ajuste_curva.custom_function_manager', 'app_files.gui.ajuste_curva.advanced_config_dialog', 'app_files.gui.ajuste_curva.history_manager', 'app_files.gui.ajuste_curva.ui_builder', 'app_files.gui.ajuste_curva.graph_export_manager', 'app_files.gui.ajuste_curva.parameter_estimates_manager', 'app_files.gui.ajuste_curva.models', 'app_files.gui.incerteza.calculo_incertezas_gui', 'app_files.gui.settings.settings_dialog', 'app_files.utils.theme_manager', 'app_files.utils.user_preferences', 'app_files.utils.lazy_loader'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='run',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='AnaFis\\app_files\\utils\\icon.ico',
)
