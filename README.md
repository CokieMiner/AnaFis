# Instruções para Escrita de Funções de Ajuste

## Formato do Arquivo de Dados
O arquivo de dados deve ser um arquivo de texto (.txt) com valores separados por tabulação (\t) no seguinte formato:

x   σx  y   σy\n
1.0 0.1 2.0 0.2\n
2.0 0.1 4.1 0.2\n
... ... ... ...\n

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