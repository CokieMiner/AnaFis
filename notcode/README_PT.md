# AnaFis - Análise de Dados Físicos

## Instalação

Instale as dependências necessárias:
```bash
pip install numpy sympy scipy matplotlib
```

## Funcionalidades Principais
- Ajuste de curvas com funções definidas pelo usuário
- Propagação de incertezas para fórmulas arbitrárias
- Visualização em tempo real do ajuste
- Exportação de gráficos em vários formatos

## Formato do Arquivo de Dados
Arquivo .csv ou .txt separado por tabulação com as colunas:

x   σx  y   σy

Exemplo:
1.0 0.1 2.0 0.2
2.0 0.1 4.1 0.2

Onde:
- x: Variável independente
- σx: Incerteza em x
- y: Variável dependente
- σy: Incerteza em y

## Solução de Problemas
- Se o ajuste não converge: tente valores iniciais diferentes ou verifique a qualidade dos dados.
- Para erros grandes: revise as incertezas e o modelo.
- Se faltar tkinter: instale pelo gerenciador de pacotes do sistema ou certifique-se de incluí-lo na instalação do Python.
