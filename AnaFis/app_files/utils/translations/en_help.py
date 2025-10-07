"""
English help dialog translations for AnaFis.
Each key is a component or help topic, value is a dict of string keys (alphabetical order).
"""

from typing import Dict

TRANSLATIONS_HELP: Dict[str, Dict[str, str]] = {
    "curve_fitting_help": {},
    "uncertainty_help": {},
    "custom_functions_help": {},
    "uncertainty_calc": {
        "formula_help_title": "Formula Help - Available Functions",
        "formula_help_full": """UNCERTAINTY CALCULATOR - FORMULA GUIDE

This tool calculates uncertainties using error propagation formulas.
You can use mathematical expressions with the following functions:

═══════════════════════════════════════════════════════════════════

BASIC ARITHMETIC OPERATORS:
  +       Addition                  a + b
  -       Subtraction               a - b
  *       Multiplication            a * b
  /       Division                  a / b
  **      Power/Exponentiation      a**2, x**0.5
  ^       Alternative power         a^2 (same as **)

═══════════════════════════════════════════════════════════════════

TRIGONOMETRIC FUNCTIONS:

Basic Trigonometric:
  sin(x)      Sine
  cos(x)      Cosine
  tan(x)      Tangent
  cot(x)      Cotangent
  sec(x)      Secant
  csc(x)      Cosecant

Inverse Trigonometric:
  asin(x)     Arc sine (inverse sine)
  acos(x)     Arc cosine
  atan(x)     Arc tangent
  acot(x)     Arc cotangent
  asec(x)     Arc secant
  acsc(x)     Arc cosecant
  
  atan2(y,x)  Two-argument arc tangent

Hyperbolic:
  sinh(x)     Hyperbolic sine
  cosh(x)     Hyperbolic cosine
  tanh(x)     Hyperbolic tangent
  coth(x)     Hyperbolic cotangent
  sech(x)     Hyperbolic secant
  csch(x)     Hyperbolic cosecant

Inverse Hyperbolic:
  asinh(x)    Inverse hyperbolic sine
  acosh(x)    Inverse hyperbolic cosine
  atanh(x)    Inverse hyperbolic tangent
  acoth(x)    Inverse hyperbolic cotangent
  asech(x)    Inverse hyperbolic secant
  acsch(x)    Inverse hyperbolic cosecant

═══════════════════════════════════════════════════════════════════

EXPONENTIAL AND LOGARITHMIC FUNCTIONS:

  exp(x)      Exponential e^x
  log(x)      Natural logarithm (ln x)
  ln(x)       Natural logarithm (same as log)
  log10(x)    Base-10 logarithm
  log2(x)     Base-2 logarithm
  sqrt(x)     Square root (same as x**0.5)

═══════════════════════════════════════════════════════════════════

SPECIAL FUNCTIONS:

  abs(x)      Absolute value |x|
  sign(x)     Sign function (-1, 0, or 1)
  
  factorial(n)    Factorial n!
  gamma(x)        Gamma function Γ(x)
  
  erf(x)      Error function
  erfc(x)     Complementary error function

═══════════════════════════════════════════════════════════════════

ROUNDING FUNCTIONS:

  floor(x)    Largest integer ≤ x
  ceiling(x)  Smallest integer ≥ x
  round(x)    Round to nearest integer

═══════════════════════════════════════════════════════════════════

CONSTANTS:

  pi          π ≈ 3.14159...
  e           Euler's number ≈ 2.71828...
  E           Same as e
  
  Example: 2*pi*r  or  exp(1)  or  e**x

═══════════════════════════════════════════════════════════════════

FORMULA EXAMPLES:

Simple operations:
  a + b
  a * b / c
  (a + b) / (c - d)

Powers and roots:
  a**2                  Square
  sqrt(a)               Square root
  a**(1/3)              Cube root
  a**b                  General power

Mixed operations:
  a*b**2 + c
  (a + b)**2
  sqrt(a**2 + b**2)     Pythagorean theorem

With functions:
  sin(a) + cos(b)
  log(a/b)
  exp(-x**2/2)          Gaussian
  a * exp(-b*t)         Exponential decay

Complex formulas:
  (g * h**2) / (8 * l)                    Pendulum period
  sqrt((v*sin(theta))**2 + 2*g*h)         Projectile velocity
  R*T/P                                    Ideal gas
  4*pi*r**2                                Sphere surface area

═══════════════════════════════════════════════════════════════════

IMPORTANT NOTES:

⚠️  Use parentheses to control order of operations!
    a + b / c       means  a + (b/c)
    (a + b) / c     means  (a+b)/c

⚠️  Variable names are case-sensitive!
    'A' and 'a' are different variables

⚠️  Avoid naming variables the same as functions!
    DON'T use: sin, cos, log, exp, pi, e, etc.
    OK to use: angle, length, mass, time, x1, y2, etc.

⚠️  Use * for multiplication explicitly!
    2a         ❌ Wrong
    2*a        ✅ Correct

⚠️  Trigonometric functions expect radians!
    For degrees, convert: sin(angle*pi/180)

═══════════════════════════════════════════════════════════════════

UNCERTAINTY PROPAGATION:

The calculator automatically computes:

  δf = √[ Σ(∂f/∂xᵢ)² · δxᵢ² ]

Where:
  f        = your formula
  xᵢ       = each variable
  δxᵢ      = uncertainty in xᵢ
  ∂f/∂xᵢ   = partial derivative (computed automatically)

This assumes uncorrelated variables. For correlated variables,
covariance terms would need to be added.

═══════════════════════════════════════════════════════════════════

TIPS:

• Test your formula first with "Calculate Value and Uncertainty"
• Check that the result makes physical sense
• Use "Generate Uncertainty Formula" to see the full expression
• Simplify complex formulas when possible
• Document your formula for future reference

═══════════════════════════════════════════════════════════════════

Need more help? Check the SymPy documentation for advanced
mathematical functions and symbolic computation capabilities.
""",
    },
    "ajuste_curva": {
        "help_models_title": "Fitting Methods Guide",
        "help_models_content": """FITTING METHODS GUIDE

AnaFis offers 6 different fitting methods, each with specific use cases and limitations.

═══════════════════════════════════════════════════════════════════

1. ODR (Orthogonal Distance Regression) [DEFAULT]
   
   ✓ Best for: Data with uncertainties in BOTH X and Y
   ✓ Uses: Analytical derivatives for fast, accurate fitting
   ✓ Handles: Non-linear models perfectly
   ✗ Requires: Uncertainties in data
   
   When to use: This is the most accurate method when you have
   measurement uncertainties in both variables. It minimizes the
   orthogonal distance to the curve, accounting for both X and Y errors.

═══════════════════════════════════════════════════════════════════

2. LEAST SQUARES
   
   ✓ Best for: Data with Y uncertainties only (or no uncertainties)
   ✓ Uses: scipy.optimize.curve_fit (very reliable)
   ✓ Handles: Non-linear models, weighted/unweighted
   ✗ Ignores: X uncertainties completely
   
   When to use: When only Y has measurement errors, or for quick fits.
   Fastest method for most cases. Automatically handles zero uncertainties.

═══════════════════════════════════════════════════════════════════

3. ROBUST (RANSAC)
   
   ✓ Best for: Data with outliers or bad points
   ✓ Uses: Random sample consensus algorithm
   ✓ Handles: Automatically identifies and ignores outliers
   ✗ Slower: Requires multiple random trials
   ✗ No uncertainties: Doesn't use measurement errors
   
   When to use: When you suspect some data points are wrong or
   contaminated. RANSAC will find the best fit ignoring outliers.

═══════════════════════════════════════════════════════════════════

4. WEIGHTED LEAST SQUARES
   
   ✓ Best for: Custom weighting schemes
   ✓ Uses: User-defined weights (not just 1/σ²)
   ✓ Handles: Non-uniform importance of data points
   ✗ Requires: Manual weight specification
   
   When to use: When some points should have more influence than
   others, beyond simple uncertainty weighting.

═══════════════════════════════════════════════════════════════════

5. BOOTSTRAP
   
   ✓ Best for: Non-parametric uncertainty estimation
   ✓ Uses: Resampling with replacement (1000 iterations)
   ✓ Provides: Confidence intervals without assumptions
   ✗ Very slow: 1000 fits required
   
   When to use: When you want robust uncertainty estimates without
   assuming Gaussian errors. Provides distribution of parameters.

═══════════════════════════════════════════════════════════════════

6. BAYESIAN REGRESSION
   
   ⚠️ LIMITATION: Uses polynomial approximation for complex models
   
   ✓ Best for: Full probabilistic uncertainty quantification
   ✓ Uses: Bayesian Ridge with automatic regularization
   ✓ Provides: Credible intervals (Bayesian confidence)
   ✗ Approximation: Uses polynomial basis for non-polynomial models
   
   When to use: When you want Bayesian posterior distributions
   and automatic regularization learning. For true Bayesian inference
   on complex models, external tools like PyMC3 are needed.

═══════════════════════════════════════════════════════════════════

CHOOSING THE RIGHT METHOD:

┌─────────────────────────────────────────────────────────────────┐
│ Your Situation               │ Recommended Method              │
├─────────────────────────────────────────────────────────────────┤
│ X and Y uncertainties        │ ODR (default)                   │
│ Only Y uncertainties         │ Least Squares                   │
│ Data has outliers            │ Robust (RANSAC)                 │
│ Need uncertainty intervals   │ Bootstrap or Bayesian           │
│ Quick exploratory fit        │ Least Squares                   │
└─────────────────────────────────────────────────────────────────┘

STATISTICS EXPLANATION:

• χ² (Chi-squared): Measures goodness of fit. Lower is better.
  For weighted fits: Σ((y - ŷ)/σ)²
  Ideally close to (number of points - number of parameters)

• χ²/dof (Reduced chi-squared): χ² divided by degrees of freedom
  Should be close to 1.0 for good fits with correct uncertainties
  >> 1: Poor fit or underestimated uncertainties
  << 1: Overestimated uncertainties

• R² (R-squared): Fraction of variance explained (0 to 1)
  1.0 = Perfect fit
  0.0 = Fit no better than mean
  Use with caution for non-linear models!

COVARIANCE MATRIX: Shows correlations between fitted parameters.
Diagonal elements are parameter variances (σ²).

═══════════════════════════════════════════════════════════════════

For more details, consult the documentation or scientific literature
on each method.
""",
    },
}
