# AnaFis - Análise de Dados Físicos

## Funcionalidades Principais

### Ajuste de Curvas
- Carregar dados experimentais de arquivos CSV ou TXT
- Ajuste de funções arbitrárias definidas pelo usuário
- Visualização em tempo real do ajuste
- Cálculo automático de incertezas dos parâmetros
- Estatísticas do ajuste (Chi², R²)
- Exportação de gráficos em vários formatos
- Suporte a escala linear e logarítmica

### Cálculo de Incertezas
- Cálculo de propagação de incertezas para funções arbitrárias
- Geração automática de fórmulas de incerteza em formato LaTeX
- Suporte a cálculos com múltiplas variáveis
- Visualização de fórmulas renderizadas
- Resultados com número apropriado de algarismos significativos

## Dependências Python

O programa necessita dos seguintes pacotes Python:
- `numpy`
- `sympy`
- `scipy`
- `matplotlib`
- `tk` (Tkinter)

### Dependências Opcionais
- `pandas` (para manipulação avançada de dados)

Instale usando:
```bash
pip install numpy sympy scipy matplotlib
```
Para incluir dependências opcionais:
```bash
pip install ".[data]"
```

> **Observação:**  
> - O `tk`/`tkinter` já vem instalado por padrão em muitas distribuições do Python, mas em alguns sistemas Linux pode ser necessário instalar manualmente (`sudo apt install python3-tk`).
> - No Windows, certifique-se de baixar o instalador oficial do Python em https://www.python.org/downloads/ e marcar a opção para incluir `tkinter`.

## Estrutura Modular
O código foi modularizado para facilitar a manutenção e expansão. Os principais módulos incluem:
- `models.py`: Classes e utilitários principais.
- `regression.py`: Funções para ajuste de curvas.
- `uncertainties.py`: Cálculo de incertezas.
- `gui.py`: Componentes da interface gráfica.
- `main.py`: Ponto de entrada principal do aplicativo.

## Formato do Arquivo de Dados
O arquivo de dados deve ser um arquivo .csv ou .txt, com valores separados por tabulação (\t) no seguinte formato:

x   σx  y   σy

1.0 0.1 2.0 0.2

2.0 0.1 4.1 0.2

... ... ... ...

O que for escrito em x e y serviram de legenda no gráfico

Onde:
- x: Valores da variável independente
- σx: Incertezas dos valores de x
- y: Valores da variável dependente
- σy: Incertezas dos valores de y

## Sintaxe para Funções de Ajuste/Incertezas

### Operadores Básicos
- Adição: `+`
- Subtração: `-`
- Multiplicação: `*`
- Divisão: `/`
- Potenciação: `**` ou `^`

### Variáveis e Parâmetros
- Use `x` como variável independente
- Parâmetros podem ter qualquer nome (a, b, c, etc.)
- Exemplo: `a*x + b` (ajuste linear)

### Funções Matemáticas Disponíveis
- `exp(x)` - Função exponencial
- `log(x)` - Logaritmo natural
- `sin(x)` - Seno
- `cos(x)` - Cosseno
- `tan(x)` - Tangente
- `sqrt(x)` - Raiz quadrada

### Exemplos de Funções

1. Ajuste Linear:

y = a*x + b

2. Ajuste Quadrático:

y = a*x**2 + bx + c

3. Exponencial:

y = a*exp(bx)

4. Senoidal:

y = a*sin(bx + c) + d


5. Gaussiana:

y = a*exp(-(x - b)**2/(2c**2))

6. Lei de Potência:

y = a*x**b

7. Lorentziana:

y = a/((x - b)2 + c2)

### Dicas Importantes

1. Verificação da Função:
   - Certifique-se de que todos os parâmetros estão definidos
   - Evite divisão por zero
   - Use parênteses para garantir a ordem correta das operações

2. Estimativas Iniciais:
   - Forneça valores iniciais razoáveis para os parâmetros
   - Valores muito distantes podem impedir a convergência
   - Use conhecimento físico do problema quando possível

3. Análise dos Resultados:
   - Verifique o Chi² reduzido (deve ser próximo de 1)
   - Analise o R² (quanto mais próximo de 1, melhor)
   - Observe os erros dos parâmetros

4. Limitações:
   - Funções muito complexas podem não convergir
   - Evite funções descontínuas
   - Considere o domínio físico do problema

## Exemplos Práticos

### Decaimento Radioativo

y = exp(-bx)
Code

- a: Atividade inicial
- b: Constante de decaimento

### Oscilador Amortecido

y = exp(-bx)cos(cx + d)
Code

- a: Amplitude inicial
- b: Fator de amortecimento
- c: Frequência angular
- d: Fase inicial

### Crescimento Populacional

y = a/(1 + sp.exp(-b*(x - c)))
Code

- a: População máxima
- b: Taxa de crescimento
- c: Ponto de inflexão

## Resolução de Problemas Comuns

1. Ajuste não converge:
   - Tente diferentes valores iniciais
   - Simplifique a função
   - Verifique a qualidade dos dados

2. Erros muito grandes:
   - Revise as incertezas experimentais
   - Verifique se o modelo é apropriado
   - Considere termos adicionais

3. R² muito baixo:
   - Revise o modelo teórico
   - Verifique outliers nos dados
   - Considere outros modelos de ajuste

## Recursos Adicionais

Para mais informações sobre:
- Funções matemáticas: Documentação do SymPy (https://docs.sympy.org)
- Análise estatística: Documentação do SciPy (https://docs.scipy.org)
- Visualização: Documentação do Matplotlib (https://matplotlib.org)

## Lista Detalhada de Funcionalidades

### Menu Principal
- Interface gráfica intuitiva com navegação por botões
- Acesso rápido às duas principais ferramentas
- Design responsivo e moderno

### Ajuste de Curvas (Detalhado)
1. Entrada de Dados:
   - Importação de arquivos CSV/TXT com 4 colunas (x, σx, y, σy)
   - Suporte para arquivos com delimitadores diferentes (vírgula ou tab)
   - Validação automática do formato dos dados

2. Definição do Modelo:
   - Editor de equações para funções arbitrárias
   - Detecção automática de parâmetros
   - Suporte para funções matemáticas comuns (exp, log, sin, etc.)

3. Processo de Ajuste:
   - Algoritmo ODR (Orthogonal Distance Regression)
   - Barra de progresso em tempo real
   - Cálculo automático de derivadas
   - Estimativas iniciais configuráveis

4. Visualização:
   - Gráfico interativo com barras de erro
   - Atualização em tempo real durante o ajuste
   - Opções de escala (linear/log) para ambos os eixos
   - Personalização de títulos e legendas

5. Resultados:
   - Parâmetros ajustados com incertezas
   - Chi² total e reduzido
   - Coeficiente de determinação (R²)
   - Matriz de correlação
   - Exportação de gráficos em alta resolução

### Cálculo de Incertezas (Detalhado)
1. Entrada de Variáveis:
   - Interface dinâmica para adicionar variáveis
   - Campos para nome, valor e incerteza
   - Suporte para número arbitrário de variáveis

2. Modos de Operação:
   - Cálculo numérico direto
   - Geração de fórmulas simbólicas

3. Fórmulas:
   - Editor de equações flexível
   - Suporte para funções matemáticas complexas
   - Validação automática de sintaxe

4. Resultados:
   - Valor final com incerteza propagada
   - Fórmulas em LaTeX
   - Visualizador de fórmulas renderizadas
   - Opção de copiar fórmulas para uso externo
