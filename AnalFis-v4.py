import numpy as np
import sympy as sp
from scipy.odr import ODR, Model, RealData
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel
from tkinter.scrolledtext import ScrolledText
import math
import os

class AplicativoUnificado:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Análise de Dados Físicos")
        self.root.geometry("400x300")
        self.criar_menu_principal()
        
    def criar_menu_principal(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid to expand and center content
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Título centralizado
        ttk.Label(
            main_frame, 
            text="Análise de Dados Físicos", 
            font=('Helvetica', 16)
        ).grid(row=0, column=0, pady=20, sticky="ew")

        # Botões centralizados
        ttk.Button(
            main_frame, 
            text="Ajuste de Curvas", 
            command=self.abrir_ajuste_curvas
        ).grid(row=1, column=0, pady=10, sticky="ew")

        ttk.Button(
            main_frame, 
            text="Cálculo de Incertezas", 
            command=self.abrir_calculo_incertezas
        ).grid(row=2, column=0, pady=10, sticky="ew")

        # Botão para sair centralizado
        ttk.Button(
            main_frame, 
            text="Sair", 
            command=self.root.quit
        ).grid(row=3, column=0, pady=20, sticky="ew")

    def abrir_ajuste_curvas(self):
        self.root.withdraw()  # Esconde a janela principal
        ajuste_window = tk.Toplevel()
        app_ajuste = AjusteCurvaGUI(ajuste_window)
        
        def on_closing():
            ajuste_window.destroy()
            self.root.deiconify()  # Mostra a janela principal novamente
            
        ajuste_window.protocol("WM_DELETE_WINDOW", on_closing)

    def abrir_calculo_incertezas(self):
        self.root.withdraw()  # Esconde a janela principal
        incertezas_window = tk.Toplevel()
        app_incertezas = CalculoIncertezasGUI(incertezas_window)
        
        def on_closing():
            incertezas_window.destroy()
            self.root.deiconify()  # Mostra a janela principal novamente
            
        incertezas_window.protocol("WM_DELETE_WINDOW", on_closing)

    def run(self):
        self.root.mainloop()

class CalculoIncertezasGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cálculo de Incertezas")
        self.var_entries = []
        self.criar_interface()

    def criar_interface(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Modo de operação
        ttk.Label(main_frame, text="Modo de Operação:").grid(row=0, column=0, pady=5, sticky="w")
        self.modo_var = tk.StringVar(value="calcular")
        ttk.Radiobutton(main_frame, text="Calcular valor e incerteza", variable=self.modo_var, 
                    value="calcular", command=self.atualizar_interface).grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(main_frame, text="Gerar fórmula de incerteza", variable=self.modo_var,
                    value="gerar", command=self.atualizar_interface).grid(row=2, column=0, sticky="w")

        # Frame para entrada de variáveis
        self.var_frame = ttk.LabelFrame(main_frame, text="Variáveis", padding="5")
        self.var_frame.grid(row=3, column=0, pady=10, sticky="ew")

        # Número de variáveis (apenas para modo calcular)
        self.num_var_frame = ttk.Frame(self.var_frame)
        self.num_var_frame.grid(row=0, column=0, sticky="w")
        ttk.Label(self.num_var_frame, text="Número de variáveis:").grid(row=0, column=0, sticky="w")
        self.num_var = ttk.Entry(self.num_var_frame, width=5)
        self.num_var.grid(row=0, column=1, padx=2)
        ttk.Button(self.num_var_frame, text="Criar campos", 
                command=self.criar_campos_variaveis).grid(row=0, column=2, padx=2)

        # Frame para os campos das variáveis
        self.campos_frame = ttk.Frame(self.var_frame)
        self.campos_frame.grid(row=1, column=0, sticky="ew")

        # Fórmula
        ttk.Label(main_frame, text="Fórmula:").grid(row=4, column=0, pady=5, sticky="w")
        self.formula_entry = ttk.Entry(main_frame, width=40)
        self.formula_entry.grid(row=5, column=0, pady=5, sticky="ew")

        # Botão calcular/gerar
        self.botao_calcular = ttk.Button(main_frame, text="Calcular", 
                                    command=self.calcular_ou_gerar)
        self.botao_calcular.grid(row=6, column=0, pady=10)

        # Área de resultados
        ttk.Label(main_frame, text="Resultados:").grid(row=7, column=0, pady=5, sticky="w")
        self.resultados_text = ScrolledText(
            main_frame, 
            height=12, 
            width=50,
            font=('Courier New', 10)
        )
        self.resultados_text.grid(row=8, column=0, pady=5, sticky="ew")

        # Botões de copiar fórmula e exibir LaTeX (inicialmente ocultos)
        self.botao_copiar_formula = ttk.Button(main_frame, text="Copiar Fórmula", 
            command=self.copiar_formula)
        self.botao_exibir_latex = ttk.Button(main_frame, text="Exibir em LaTeX", 
            command=lambda: self.exibir_formula_latex(getattr(self, 'formula_latex', r'')))

        self.atualizar_interface()
        self.resultados_text.delete(1.0, tk.END)

    def copiar_formula(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.resultados_text.get(1.0, tk.END))

    def atualizar_interface(self):
        if self.modo_var.get() == "calcular":
            self.num_var_frame.grid()
            self.botao_calcular.configure(text="Calcular")
            for widget in self.campos_frame.winfo_children():
                widget.destroy()
            # Esconde os botões extras
            self.botao_copiar_formula.grid_remove()
            self.botao_exibir_latex.grid_remove()
        else:
            self.num_var_frame.grid_remove()
            for widget in self.campos_frame.winfo_children():
                widget.destroy()
            self.botao_calcular.configure(text="Gerar Fórmula")
            # Para modo gerar, apenas um campo para lista de variáveis
            ttk.Label(self.campos_frame, text="Variáveis (separadas por vírgula):").grid(row=0, column=0)
            self.vars_entry = ttk.Entry(self.campos_frame, width=30)
            self.vars_entry.grid(row=0, column=1)
            # Mostra os botões extras logo abaixo do resultados_text
            self.botao_copiar_formula.grid(row=9, column=0, pady=5)
            self.botao_exibir_latex.grid(row=10, column=0, pady=5)

    def criar_campos_variaveis(self):
        try:
            num = int(self.num_var.get())
            # Limpar campos existentes
            for widget in self.campos_frame.winfo_children():
                widget.destroy()
            # Criar novos campos
            self.var_entries = []
            for i in range(num):
                frame = ttk.Frame(self.campos_frame)
                frame.grid(row=i, column=0, pady=2)
                ttk.Label(frame, text=f"Variável {i+1}:").grid(row=0, column=0)
                nome = ttk.Entry(frame, width=5)
                nome.grid(row=0, column=1)
                ttk.Label(frame, text="Valor:").grid(row=0, column=2)
                valor = ttk.Entry(frame, width=10)
                valor.grid(row=0, column=3)
                ttk.Label(frame, text="Incerteza:").grid(row=0, column=4)
                incerteza = ttk.Entry(frame, width=10)
                incerteza.grid(row=0, column=5)
                self.var_entries.append((nome, valor, incerteza))
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira um número válido de variáveis.")

    def calcular_ou_gerar(self):
        if self.modo_var.get() == "calcular":
            self.calcular_incerteza()
        else:
            self.gerar_formula_incerteza()

    def calcular_incerteza(self):

        if not hasattr(self, 'var_entries') or not self.var_entries:
            messagebox.showerror("Erro", "Crie os campos para as variáveis primeiro!")
            return

        try:
            # Coletar variáveis
            variaveis = {}
            for nome_entry, valor_entry, incerteza_entry in self.var_entries:
                nome = nome_entry.get()
                valor = float(valor_entry.get())
                incerteza = float(incerteza_entry.get())
                variaveis[nome] = (valor, incerteza)
            formula = self.formula_entry.get()
            # Substitui sen -> sin para usuários que digitam em português
            formula = formula.replace("sen", "sin")
            # Calcular valor
            valor_final = eval(formula, {"sin": math.sin, "cos": math.cos, "tan": math.tan,
                                         "exp": math.exp, "log": math.log, "sqrt": math.sqrt, "pi": math.pi},
                               {k: valor for k, (valor, _) in variaveis.items()})
            # Calcular incerteza
            incerteza_total = 0
            expr = sp.sympify(formula)
            for var, (val, sigma) in variaveis.items():
                derivada = sp.diff(expr, sp.Symbol(var))
                derivada_num = derivada.subs({sp.Symbol(k): valor for k, (valor, _) in variaveis.items()})
                derivada_num = float(derivada_num.evalf())
                incerteza_total += (derivada_num * sigma) ** 2
            incerteza_total = math.sqrt(incerteza_total)
            # Mostrar resultados
            self.resultados_text.delete(1.0, tk.END)
            self.resultados_text.insert(tk.END, "=== Resultado ===\n")
            self.resultados_text.insert(tk.END, f"Valor calculado: {valor_final:.6f}\n")
            self.resultados_text.insert(tk.END, f"Incerteza total: ±{incerteza_total:.6f}\n")
            self.resultados_text.insert(tk.END, f"Resultado final: ({valor_final:.6f} ± {incerteza_total:.6f})")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def gerar_formula_incerteza(self):
        try:
            variaveis = self.vars_entry.get().split(',')
            formula = self.formula_entry.get()
            formula = formula.replace("sen", "sin")   # permite também o uso de sen em português
            simbolos = {var.strip(): sp.Symbol(var.strip()) for var in variaveis}
            expr = sp.sympify(formula, locals=simbolos)
            termos = []
            for var in variaveis:
                var = var.strip()
                derivada = sp.diff(expr, simbolos[var])
                termos.append(f"(\\sigma_{{{var}}} \\cdot {sp.latex(derivada)})^2")
            formula_incerteza = "\\sigma_{\\text{total}} = \\sqrt{" + " + ".join(termos) + "}"
            self.resultados_text.delete(1.0, tk.END)
            self.resultados_text.insert(tk.END, "=== Fórmula de Incerteza (LaTeX) ===\n\n")
            self.resultados_text.insert(tk.END, "Copie o código abaixo para LaTeX:\n\n")
            self.resultados_text.insert(tk.END, f"{formula_incerteza}\n\n")
            self.resultados_text.insert(tk.END, "Clique em 'Exibir em LaTeX' para visualizar a fórmula renderizada.\n")
            self.formula_latex = formula_incerteza  # Guarda para visualização
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def exibir_formula_latex(self, formula_latex):
        if not formula_latex or formula_latex.strip() == "":
            messagebox.showinfo("Atenção", "Gere a fórmula primeiro!")
            return
        janela = Toplevel(self.root)
        janela.title("Fórmula Renderizada (LaTeX)")
        fig, ax = plt.subplots(figsize=(7, 2))
        ax.axis('off')
        ax.text(0.5, 0.5, f"${formula_latex}$", fontsize=18, ha='center', va='center')
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=janela)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill='both')


class AjusteCurvaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Ajuste de Curvas")
        
        # Configurar o layout principal
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Variáveis para armazenar dados
        self.parametros = []
        # Criar a figura antes de criar os painéis
        self.fig = plt.figure(figsize=(6, 4))
        self.ax = self.fig.add_subplot(111)
        
        # Criar painéis
        self.criar_painel_parametros()
        self.criar_painel_grafico()
        
    def criar_painel_parametros(self):
        # Frame esquerdo para parâmetros
        left_frame = ttk.Frame(self.root, padding="10")
        left_frame.grid(row=0, column=0, sticky="nsew")
        
        # Widgets para entrada de dados
        ttk.Label(left_frame, text="Arquivo de Dados:").grid(row=0, column=0, sticky="w", pady=5)
        self.arquivo_entry = ttk.Entry(left_frame, width=40)
        self.arquivo_entry.grid(row=1, column=0, sticky="ew", padx=5)
        ttk.Button(left_frame, text="Procurar", command=self.selecionar_arquivo).grid(row=1, column=1)
        
        ttk.Label(left_frame, text="Equação:").grid(row=2, column=0, sticky="w", pady=5)
        self.equacao_entry = ttk.Entry(left_frame, width=40)
        self.equacao_entry.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)
        
        ttk.Label(left_frame, text="Número máximo de iterações:").grid(row=5, column=0, sticky="w", pady=5)
        self.max_iter_entry = ttk.Entry(left_frame, width=10)
        self.max_iter_entry.insert(0, "1000")
        self.max_iter_entry.grid(row=5, column=1, sticky="w", pady=5)
        
        ttk.Label(left_frame, text="Título do gráfico:").grid(row=6, column=0, sticky="w", pady=5)
        self.titulo_entry = ttk.Entry(left_frame, width=40)
        self.titulo_entry.grid(row=7, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Frame para estimativas iniciais (será preenchido dinamicamente)
        self.estimativas_frame = ttk.LabelFrame(left_frame, text="Estimativas Iniciais", padding="5")
        self.estimativas_frame.grid(row=8, column=0, columnspan=2, sticky="ew", pady=10)
        
        # Botão de ajuste
        ttk.Button(left_frame, text="Realizar Ajuste", command=self.realizar_ajuste).grid(row=9, column=0, columnspan=2, pady=10)
        
        # Área de resultados
        ttk.Label(left_frame, text="Resultados:").grid(row=10, column=0, sticky="w", pady=5)
        self.resultados_text = ScrolledText(left_frame, height=10, width=40)
        self.resultados_text.grid(row=11, column=0, columnspan=2, sticky="ew", pady=5)
    
        # Adicionar botão para salvar gráfico
        ttk.Button(left_frame, text="Salvar Gráfico", command=self.salvar_grafico).grid(row=12, column=0, columnspan=2, pady=10, sticky="ew")
        self.equacao_entry.bind("<FocusOut>", lambda e: self.atualizar_estimativas_frame())


    def salvar_grafico(self):
        try:
            # Abrir diálogo para escolher local e nome do arquivo
            filetypes = [
                ('PNG', '*.png'),
                ('PDF', '*.pdf'),
                ('SVG', '*.svg'),
                ('JPEG', '*.jpg')
            ]
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=filetypes,
                title="Salvar Gráfico Como"
            )
            
            if filename:
                # Ajustar o layout antes de salvar
                self.fig.tight_layout()
                
                # Salvar o gráfico
                self.fig.savefig(
                    filename, 
                    dpi=300, 
                    bbox_inches='tight',
                    facecolor='white',
                    edgecolor='none'
                )
                
                messagebox.showinfo(
                    "Sucesso",
                    f"Gráfico salvo com sucesso em:\n{filename}"
                )
                
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Erro ao salvar o gráfico:\n{str(e)}"
            )

    def criar_painel_grafico(self):
        # Frame direito para o gráfico
        right_frame = ttk.Frame(self.root, padding="10")
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        # Canvas para o gráfico
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def selecionar_arquivo(self):
        filename = filedialog.askopenfilename(
            title="Selecionar arquivo de dados",
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        if filename:
            self.arquivo_entry.delete(0, tk.END)
            self.arquivo_entry.insert(0, filename)
            
    def atualizar_estimativas_frame(self):
        # Limpar frame atual
        for widget in self.estimativas_frame.winfo_children():
            widget.destroy()
            
        # Extrair parâmetros da equação
        try:
            equacao = self.equacao_entry.get().replace('^', '**')
            if '=' in equacao:
                equacao = equacao.split('=')[1].strip()
                
            x_sym = sp.Symbol('x')
            expr = sp.sympify(equacao)
            self.parametros = sorted(list(expr.free_symbols - {x_sym}), key=lambda s: s.name)
            
            # Criar campos de entrada para cada parâmetro
            for i, param in enumerate(self.parametros):
                ttk.Label(self.estimativas_frame, text=f"{param}:").grid(row=i, column=0, padx=5, pady=2)
                entry = ttk.Entry(self.estimativas_frame, width=10)
                entry.insert(0, "1.0")
                entry.grid(row=i, column=1, padx=5, pady=2)
                setattr(self, f"estimate_{param}", entry)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar equação: {str(e)}")
            
    def ler_arquivo(self, nome_arquivo):
    # Verifica se o arquivo existe
        if not os.path.isfile(nome_arquivo):
            messagebox.showerror("Erro ao ler arquivo", f"O arquivo '{nome_arquivo}' não foi encontrado.")
            raise FileNotFoundError(f"O arquivo '{nome_arquivo}' não foi encontrado.")
        try:
            with open(nome_arquivo, 'r') as f:
                header = f.readline()
                lines = f.readlines()
            if len(lines) == 0:
                messagebox.showerror("Erro ao ler arquivo", "O arquivo está vazio ou só contém o cabeçalho.")
                raise ValueError("O arquivo está vazio ou só contém o cabeçalho.")
            # Checar se há pelo menos 4 colunas por linha
            for i, line in enumerate(lines):
                parts = line.strip().split('\t')
                if len(parts) != 4:
                    messagebox.showerror("Erro ao ler arquivo",
                        f"O arquivo precisa ter 4 colunas separadas por tabulação (linha {i+2}).")
                    raise ValueError(f"O arquivo precisa ter 4 colunas separadas por tabulação (linha {i+2}).")
            # Carregar dados usando numpy
            dados = np.genfromtxt(nome_arquivo, delimiter='\t', skip_header=1, dtype=str)
            dados = np.char.replace(dados, ',', '.')
            x = dados[:, 0].astype(float)
            sigma_x = dados[:, 1].astype(float)
            y = dados[:, 2].astype(float)
            sigma_y = dados[:, 3].astype(float)
            return x, sigma_x, y, sigma_y
        except Exception as e:
            messagebox.showerror("Erro ao ler arquivo", f"Erro ao processar o arquivo:\n{str(e)}")
            raise
    
    def criar_modelo(self, equacao, parametros):
        x = sp.Symbol('x')
        expr = sp.sympify(equacao)
        
        derivadas = [sp.diff(expr, p) for p in parametros]
        
        modelo_numerico = sp.lambdify((parametros, x), expr, 'numpy')
        derivadas_numericas = [sp.lambdify((parametros, x), d, 'numpy') for d in derivadas]
        
        return modelo_numerico, derivadas_numericas
    
    def realizar_ajuste(self):
        try:
            self.resultados_text.delete(1.0, tk.END)
            # Atualizar estimativas se necessário
            if not self.parametros:
                self.atualizar_estimativas_frame()
                
            # Obter valores dos campos
            caminho = self.arquivo_entry.get()
            equacao = self.equacao_entry.get().replace('^', '**')
            if '=' in equacao:
                equacao = equacao.split('=')[1].strip()
            max_iter = int(self.max_iter_entry.get())
            
            # Obter estimativas iniciais
            chute = []
            for param in self.parametros:
                entry = getattr(self, f"estimate_{param}")
                chute.append(float(entry.get()))
                
            # Carregar dados
            x, sigma_x, y, sigma_y = self.ler_arquivo(caminho)
            with open(caminho, 'r') as f:
                cabecalho = f.readline().strip().split('\t')
                
            # Criar modelo
            modelo, derivadas = self.criar_modelo(equacao, self.parametros)
            modelo_odr = Model(ModeloODR(modelo, derivadas))
            
            # Executar ODR
            dados = RealData(x, y, sx=sigma_x, sy=sigma_y)
            odr = ODR(dados, modelo_odr, beta0=chute, maxit=max_iter)
            resultado = odr.run()
            
            # Calcular estatísticas
            y_pred = modelo(resultado.beta, x)
            chi2_total = np.sum(((y - y_pred) / sigma_y) ** 2)
            r2 = 1 - np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2)
            
            # Mostrar resultados
            self.resultados_text.delete(1.0, tk.END)
            self.resultados_text.insert(tk.END, "=== Resultados ===\n")
            for p, v, e in zip(self.parametros, resultado.beta, resultado.sd_beta):
                self.resultados_text.insert(tk.END, f"{p} = {v:.6f} ± {e:.6f}\n")
            self.resultados_text.insert(tk.END, f"\nChi² total: {chi2_total:.2f}\n")
            self.resultados_text.insert(tk.END, f"Chi² reduzido: {resultado.res_var:.2f}\n")
            self.resultados_text.insert(tk.END, f"R²: {r2:.4f}\n")
            
            # Atualizar gráfico
            self.ax.clear()
            self.ax.errorbar(x, y, xerr=sigma_x, yerr=sigma_y, fmt='o', label='Dados')
            x_fit = np.linspace(min(x), max(x), 100)
            self.ax.plot(x_fit, modelo(resultado.beta, x_fit), 'r-', label='Ajuste')
            self.ax.set_xlabel(cabecalho[0])
            self.ax.set_ylabel(cabecalho[2])
            self.ax.legend()
            self.ax.grid(True)
            
            # Título do gráfico
            titulo = self.titulo_entry.get()
            if titulo:
                self.ax.set_title(titulo)
                
            # Adicionar caixa de texto com informações
            texto_info = f"Equação: y = {equacao}\n"
            texto_info += '\n'.join([f"{p} = {v:.6f} ± {e:.6f}" for p, v, e in 
                                   zip(self.parametros, resultado.beta, resultado.sd_beta)])
            texto_info += f"\nChi² total: {chi2_total:.2f}\nChi² reduzido: {resultado.res_var:.2f}\nR²: {r2:.4f}"
            
            self.ax.text(
                0.98, 0.02,
                texto_info,
                transform=self.ax.transAxes,
                fontsize=7,
                bbox=dict(facecolor='white', alpha=0.5),
                ha='right',
                va='bottom'
            )
            
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante o ajuste: {str(e)}")
            self.resultados_text.insert(tk.END, "Ocorreu um erro. Verifique os dados e tente novamente.\n")
            
class ModeloODR:
    def __init__(self, funcao, derivadas):
        self.funcao = funcao
        self.derivadas = derivadas
        
    def __call__(self, parametros, x):
        return self.funcao(parametros, x)

    def fjb(self, parametros, x):
        """
        Retorna as derivadas em relação aos parâmetros.
        """
        return [d(parametros, x) for d in self.derivadas]

    def fdb(self, parametros, x):
        """
        Retorna a derivada em relação à variável independente.
        """
        return np.zeros_like(x)

if __name__ == "__main__":
    app = AplicativoUnificado()
    app.run()