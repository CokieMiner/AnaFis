"""
Portuguese help dialog translations for AnaFis.
Each key is a component or help topic, value is a dict of string keys (alphabetical order).
"""

from typing import Dict

TRANSLATIONS_HELP: Dict[str, Dict[str, str]] = {
    "curve_fitting_help": {},
    "uncertainty_help": {},
    "custom_functions_help": {},
    "uncertainty_calc": {
        "formula_help_title": "Ajuda de Fórmulas - Funções Disponíveis",
        "formula_help_full": """CALCULADORA DE INCERTEZAS - GUIA DE FÓRMULAS

Esta ferramenta calcula incertezas usando fórmulas de propagação de erros.
Você pode usar expressões matemáticas com as seguintes funções:

═══════════════════════════════════════════════════════════════════

OPERADORES ARITMÉTICOS BÁSICOS:
  +       Adição                    a + b
  -       Subtração                 a - b
  *       Multiplicação             a * b
  /       Divisão                   a / b
  **      Potência/Exponenciação    a**2, x**0.5
  ^       Potência alternativa      a^2 (mesmo que **)

═══════════════════════════════════════════════════════════════════

FUNÇÕES TRIGONOMÉTRICAS:

Trigonométricas Básicas:
  sin(x)      Seno
  cos(x)      Cosseno
  tan(x)      Tangente
  cot(x)      Cotangente
  sec(x)      Secante
  csc(x)      Cossecante

Trigonométricas Inversas:
  asin(x)     Arco seno (seno inverso)
  acos(x)     Arco cosseno
  atan(x)     Arco tangente
  acot(x)     Arco cotangente
  asec(x)     Arco secante
  acsc(x)     Arco cossecante
  
  atan2(y,x)  Arco tangente de dois argumentos

Hiperbólicas:
  sinh(x)     Seno hiperbólico
  cosh(x)     Cosseno hiperbólico
  tanh(x)     Tangente hiperbólica
  coth(x)     Cotangente hiperbólica
  sech(x)     Secante hiperbólica
  csch(x)     Cossecante hiperbólica

Hiperbólicas Inversas:
  asinh(x)    Seno hiperbólico inverso
  acosh(x)    Cosseno hiperbólico inverso
  atanh(x)    Tangente hiperbólica inversa
  acoth(x)    Cotangente hiperbólica inversa
  asech(x)    Secante hiperbólica inversa
  acsch(x)    Cossecante hiperbólica inversa

═══════════════════════════════════════════════════════════════════

FUNÇÕES EXPONENCIAIS E LOGARÍTMICAS:

  exp(x)      Exponencial e^x
  log(x)      Logaritmo natural (ln x)
  ln(x)       Logaritmo natural (mesmo que log)
  log10(x)    Logaritmo base 10
  log2(x)     Logaritmo base 2
  sqrt(x)     Raiz quadrada (mesmo que x**0.5)

═══════════════════════════════════════════════════════════════════

FUNÇÕES ESPECIAIS:

  abs(x)      Valor absoluto |x|
  sign(x)     Função sinal (-1, 0, ou 1)
  
  factorial(n)    Fatorial n!
  gamma(x)        Função Gama Γ(x)
  
  erf(x)      Função erro
  erfc(x)     Função erro complementar

═══════════════════════════════════════════════════════════════════

FUNÇÕES DE ARREDONDAMENTO:

  floor(x)    Maior inteiro ≤ x
  ceiling(x)  Menor inteiro ≥ x
  round(x)    Arredondar para o inteiro mais próximo

═══════════════════════════════════════════════════════════════════

CONSTANTES:

  pi          π ≈ 3,14159...
  e           Número de Euler ≈ 2,71828...
  E           Mesmo que e
  
  Exemplo: 2*pi*r  ou  exp(1)  ou  e**x

═══════════════════════════════════════════════════════════════════

EXEMPLOS DE FÓRMULAS:

Operações simples:
  a + b
  a * b / c
  (a + b) / (c - d)

Potências e raízes:
  a**2                  Quadrado
  sqrt(a)               Raiz quadrada
  a**(1/3)              Raiz cúbica
  a**b                  Potência geral

Operações mistas:
  a*b**2 + c
  (a + b)**2
  sqrt(a**2 + b**2)     Teorema de Pitágoras

Com funções:
  sin(a) + cos(b)
  log(a/b)
  exp(-x**2/2)          Gaussiana
  a * exp(-b*t)         Decaimento exponencial

Fórmulas complexas:
  (g * h**2) / (8 * l)                    Período do pêndulo
  sqrt((v*sin(theta))**2 + 2*g*h)         Velocidade de projétil
  R*T/P                                    Gás ideal
  4*pi*r**2                                Área de esfera

═══════════════════════════════════════════════════════════════════

NOTAS IMPORTANTES:

⚠️  Use parênteses para controlar a ordem das operações!
    a + b / c       significa  a + (b/c)
    (a + b) / c     significa  (a+b)/c

⚠️  Nomes de variáveis diferenciam maiúsculas/minúsculas!
    'A' e 'a' são variáveis diferentes

⚠️  Evite nomear variáveis com nomes de funções!
    NÃO use: sin, cos, log, exp, pi, e, etc.
    PODE usar: angulo, comprimento, massa, tempo, x1, y2, etc.

⚠️  Use * para multiplicação explicitamente!
    2a         ❌ Errado
    2*a        ✅ Correto

⚠️  Funções trigonométricas esperam radianos!
    Para graus, converta: sin(angulo*pi/180)

═══════════════════════════════════════════════════════════════════

PROPAGAÇÃO DE INCERTEZAS:

A calculadora computa automaticamente:

  δf = √[ Σ(∂f/∂xᵢ)² · δxᵢ² ]

Onde:
  f        = sua fórmula
  xᵢ       = cada variável
  δxᵢ      = incerteza em xᵢ
  ∂f/∂xᵢ   = derivada parcial (computada automaticamente)

Isso assume variáveis não-correlacionadas. Para variáveis correlacionadas,
termos de covariância precisariam ser adicionados.

═══════════════════════════════════════════════════════════════════

DICAS:

• Teste sua fórmula primeiro com "Calcular Valor e Incerteza"
• Verifique se o resultado faz sentido físico
• Use "Gerar Fórmula de Incerteza" para ver a expressão completa
• Simplifique fórmulas complexas quando possível
• Documente sua fórmula para referência futura

═══════════════════════════════════════════════════════════════════

Precisa de mais ajuda? Consulte a documentação do SymPy para funções
matemáticas avançadas e capacidades de computação simbólica.
""",
    },
    "ajuste_curva": {
        "help_models_title": "Guia dos Métodos de Ajuste",
        "help_models_content": """GUIA DOS MÉTODOS DE AJUSTE

O AnaFis oferece 6 métodos diferentes de ajuste, cada um com casos
de uso específicos e limitações.

═══════════════════════════════════════════════════════════════════

1. ODR (Regressão de Distância Ortogonal) [PADRÃO]
   
   ✓ Melhor para: Dados com incertezas em X E Y
   ✓ Usa: Derivadas analíticas para ajuste rápido e preciso
   ✓ Suporta: Modelos não-lineares perfeitamente
   ✗ Requer: Incertezas nos dados
   
   Quando usar: Este é o método mais preciso quando você tem
   incertezas de medição em ambas as variáveis. Minimiza a distância
   ortogonal à curva, considerando erros em X e Y.

═══════════════════════════════════════════════════════════════════

2. MÍNIMOS QUADRADOS
   
   ✓ Melhor para: Dados com incertezas apenas em Y (ou sem incertezas)
   ✓ Usa: scipy.optimize.curve_fit (muito confiável)
   ✓ Suporta: Modelos não-lineares, ponderado/não-ponderado
   ✗ Ignora: Incertezas em X completamente
   
   Quando usar: Quando apenas Y tem erros de medição, ou para ajustes
   rápidos. Método mais rápido na maioria dos casos. Lida automaticamente
   com incertezas zero.

═══════════════════════════════════════════════════════════════════

3. ROBUSTO (RANSAC)
   
   ✓ Melhor para: Dados com outliers ou pontos ruins
   ✓ Usa: Algoritmo de consenso por amostra aleatória
   ✓ Suporta: Identifica e ignora outliers automaticamente
   ✗ Mais lento: Requer múltiplas tentativas aleatórias
   ✗ Sem incertezas: Não usa erros de medição
   
   Quando usar: Quando você suspeita que alguns pontos estão errados
   ou contaminados. RANSAC encontrará o melhor ajuste ignorando outliers.

═══════════════════════════════════════════════════════════════════

4. MÍNIMOS QUADRADOS PONDERADOS
   
   ✓ Melhor para: Esquemas de ponderação personalizados
   ✓ Usa: Pesos definidos pelo usuário (não apenas 1/σ²)
   ✓ Suporta: Importância não-uniforme dos pontos
   ✗ Requer: Especificação manual de pesos
   
   Quando usar: Quando alguns pontos devem ter mais influência que
   outros, além da simples ponderação por incerteza.

═══════════════════════════════════════════════════════════════════

5. BOOTSTRAP
   
   ✓ Melhor para: Estimativa não-paramétrica de incertezas
   ✓ Usa: Reamostragem com reposição (1000 iterações)
   ✓ Fornece: Intervalos de confiança sem suposições
   ✗ Muito lento: 1000 ajustes necessários
   
   Quando usar: Quando você quer estimativas robustas de incerteza
   sem assumir erros gaussianos. Fornece distribuição dos parâmetros.

═══════════════════════════════════════════════════════════════════

6. REGRESSÃO BAYESIANA
   
   ⚠️ LIMITAÇÃO: Usa aproximação polinomial para modelos complexos
   
   ✓ Melhor para: Quantificação probabilística completa de incerteza
   ✓ Usa: Ridge Bayesiano com regularização automática
   ✓ Fornece: Intervalos credíveis (confiança Bayesiana)
   ✗ Aproximação: Usa base polinomial para modelos não-polinomiais
   
   Quando usar: Quando você quer distribuições posteriores Bayesianas
   e aprendizado automático de regularização. Para inferência Bayesiana
   verdadeira em modelos complexos, ferramentas externas como PyMC3
   são necessárias.

═══════════════════════════════════════════════════════════════════

ESCOLHENDO O MÉTODO CERTO:

┌─────────────────────────────────────────────────────────────────┐
│ Sua Situação                 │ Método Recomendado              │
├─────────────────────────────────────────────────────────────────┤
│ Incertezas em X e Y          │ ODR (padrão)                    │
│ Apenas incertezas em Y       │ Mínimos Quadrados               │
│ Dados têm outliers           │ Robusto (RANSAC)                │
│ Precisa intervalos incerteza │ Bootstrap ou Bayesiano          │
│ Ajuste exploratório rápido   │ Mínimos Quadrados               │
└─────────────────────────────────────────────────────────────────┘

EXPLICAÇÃO DAS ESTATÍSTICAS:

• χ² (Qui-quadrado): Mede qualidade do ajuste. Menor é melhor.
  Para ajustes ponderados: Σ((y - ŷ)/σ)²
  Idealmente próximo a (número de pontos - número de parâmetros)

• χ²/gl (Qui-quadrado reduzido): χ² dividido pelos graus de liberdade
  Deve estar próximo de 1,0 para bons ajustes com incertezas corretas
  >> 1: Ajuste ruim ou incertezas subestimadas
  << 1: Incertezas superestimadas

• R² (R-quadrado): Fração da variância explicada (0 a 1)
  1,0 = Ajuste perfeito
  0,0 = Ajuste não melhor que a média
  Use com cautela para modelos não-lineares!

MATRIZ DE COVARIÂNCIA: Mostra correlações entre parâmetros ajustados.
Elementos diagonais são variâncias dos parâmetros (σ²).

═══════════════════════════════════════════════════════════════════

Para mais detalhes, consulte a documentação ou literatura científica
sobre cada método.
""",
    },
}
