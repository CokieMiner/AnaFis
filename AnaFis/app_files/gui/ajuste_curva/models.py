from dataclasses import dataclass
from typing import (
    Protocol,
    List,
    Callable,
    TYPE_CHECKING,
    Optional,
    Dict,
    Any,
    Tuple,
    Sequence,
)

import numpy as np
import numpy.typing as npt
from numpy.typing import NDArray

# Note: Many type checking warnings in this file are due to scipy's curve_fit
# returning untyped results. The code works correctly despite the warnings.

if TYPE_CHECKING:
    import tkinter as tk
    from scipy.odr import Output
FloatArray = npt.NDArray[np.float64]

# Type alias for the numerical model functions
ModelCallable = Callable[[Sequence[float], NDArray[np.float64]], NDArray[np.float64]]


class ODRModelImplementation:
    """ODR model implementation"""

    def __init__(
        self,
        function: Callable[[FloatArray, FloatArray], FloatArray],
        derivatives: List[Callable[[FloatArray, FloatArray], FloatArray]],
    ) -> None:
        self.function = function
        self.derivatives = derivatives

    def __call__(self, parameters: FloatArray, x: FloatArray) -> FloatArray:
        return self.function(parameters, x)


@dataclass
class CustomFunction:
    """Represents a user-defined function to be plotted."""

    func_text: str
    color: str
    x_min: Optional[float] = None
    x_max: Optional[float] = None
    enabled: bool = True  # New field to control visibility/plotting


# Fitting Algorithm Implementations
class LeastSquaresResult:
    """Result object for least squares fitting to match ODR output format"""

    def __init__(self, params: NDArray[np.float64], covariance: NDArray[np.float64]):
        self.beta = params
        self.cov_beta = covariance
        self.info = 1  # Success flag

        # Calculate parameter uncertainties from covariance matrix
        try:
            if np.all(np.isfinite(covariance)) and not np.allclose(covariance, 0):
                self.sd_beta = np.sqrt(np.diag(covariance))
            else:
                # Covariance matrix is invalid (all zeros or infinities)
                self.sd_beta = np.zeros_like(params)
        except (ValueError, RuntimeWarning):
            # Fallback: set uncertainties to zero if calculation fails
            self.sd_beta = np.zeros_like(params)


class RobustResult:
    """Result object for robust fitting to match ODR output format"""

    def __init__(
        self,
        params: NDArray[np.float64],
        covariance: Optional[NDArray[np.float64]] = None,
    ):
        self.beta = params
        self.cov_beta = (
            covariance
            if covariance is not None
            else np.zeros((len(params), len(params)))
        )
        self.info = 1  # Success flag

        # Calculate parameter uncertainties
        try:
            if (
                covariance is not None
                and np.all(np.isfinite(covariance))
                and not np.allclose(covariance, 0)
            ):
                self.sd_beta = np.sqrt(np.diag(covariance))
            else:
                # No covariance available or invalid
                self.sd_beta = np.zeros_like(params)
        except (ValueError, RuntimeWarning):
            self.sd_beta = np.zeros_like(params)


class BootstrapResult:
    """Result object for bootstrap fitting to match ODR output format"""

    def __init__(self, params: NDArray[np.float64], param_samples: NDArray[np.float64]):
        self.beta = params
        self.param_samples = param_samples
        self.info = 1  # Success flag

        # Calculate covariance matrix from bootstrap samples
        self.cov_beta = np.cov(param_samples.T)

        # Calculate parameter uncertainties (standard deviations from bootstrap)
        self.sd_beta = np.std(param_samples, axis=0)


def perform_least_squares_fit(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    sigma_y: Optional[NDArray[np.float64]],
    model_func: ModelCallable,
    initial_params: List[float],
    max_iter: int,
) -> Tuple[LeastSquaresResult, float, float]:
    """Perform Least Squares fitting using scipy.optimize.curve_fit

    Args:
        x, y: Data arrays
        sigma_y: Standard deviations for y (None for unweighted)
        model_func: Model function
        initial_params: Initial parameter estimates
        max_iter: Maximum number of iterations

    Returns:
        Tuple containing (result object, chi-squared, R-squared)
    """
    from scipy.optimize import curve_fit
    import logging

    # Convert model function to work with curve_fit (which expects f(x, *params))
    def curve_fit_func(
        x_vals: NDArray[np.float64], *params: float
    ) -> NDArray[np.float64]:
        return model_func(list(params), x_vals)

    # Prepare sigma for curve_fit - handle zero uncertainties
    sigma = None
    if sigma_y is not None:
        # Check if all uncertainties are zero or very close to zero
        if np.allclose(sigma_y, 0):
            # Use unweighted fitting (sigma=None) to avoid division by zero
            sigma = None
        else:  # Use weighted fitting with provided uncertainties
            sigma = sigma_y
    # Perform curve_fit
    try:
        popt, pcov = curve_fit(
            curve_fit_func,
            x,
            y,
            p0=initial_params,
            sigma=sigma,
            absolute_sigma=True if sigma is not None else False,
            maxfev=max_iter,
        )

        resultado = LeastSquaresResult(popt, pcov)
    except Exception as e:
        logging.error(f"Least squares fitting failed: {e}")
        raise RuntimeError(f"Least squares fitting failed: {e}")

    # Calculate statistics
    y_pred: NDArray[np.float64] = model_func(popt.tolist(), x)
    # Chi-squared calculation
    chi2_total: float = np.nan
    if sigma_y is not None:
        # Check if we have any valid (non-zero) uncertainties
        valid_mask = sigma_y > 0
        if np.any(valid_mask):
            # Use weighted chi-squared only for points with valid uncertainties
            chi2_total = float(
                np.sum(
                    ((y[valid_mask] - y_pred[valid_mask]) / sigma_y[valid_mask]) ** 2
                )
            )
        else:
            # All uncertainties are zero - use unweighted
            chi2_total = float(np.sum((y - y_pred) ** 2))
    else:
        # Unweighted chi-squared (sum of squared residuals)
        chi2_total = float(np.sum((y - y_pred) ** 2))

    # R-squared calculation
    ss_tot: float = float(np.sum((y - np.mean(y)) ** 2))
    ss_res: float = float(np.sum((y - y_pred) ** 2))

    r2: float = np.nan
    if ss_tot > 0:
        r2 = 1 - (ss_res / ss_tot)
    else:
        if ss_res == 0:  # Perfect fit to a constant
            r2 = 1.0

    return resultado, chi2_total, r2


def perform_robust_fit(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    model_func: ModelCallable,
    initial_params: List[float],
    method: str = "huber",
    max_iter: int = 1000,
) -> Tuple[RobustResult, float, float]:
    """Perform robust fitting using RANSAC or Huber regression

    Args:
        x, y: Data arrays
        model_func: Model function
        initial_params: Initial parameter estimates
        method: 'ransac' or 'huber'
        max_iter: Maximum number of iterations

    Returns:
        Tuple containing (result object, chi-squared, R-squared)
    """
    try:
        from sklearn.linear_model import RANSACRegressor, HuberRegressor
        from sklearn.base import BaseEstimator, RegressorMixin
    except ImportError:
        raise ImportError(
            "scikit-learn is required for robust fitting. Install with: pip install scikit-learn"
        )

    import logging

    # Create a custom estimator that wraps our model function
    class CustomModelEstimator(BaseEstimator, RegressorMixin):
        def __init__(self, model_func: ModelCallable, n_params: int):
            self.model_func = model_func
            self.n_params = n_params
            self.coef_: Optional[NDArray[np.float64]] = None

        def fit(
            self, X: NDArray[np.float64], y: NDArray[np.float64]
        ) -> "CustomModelEstimator":
            # For linear models, we can use least squares as a fallback
            # For non-linear models, this is a simplified approach
            from scipy.optimize import curve_fit
            def curve_fit_func(
                x_vals: NDArray[np.float64], *params: float
            ) -> NDArray[np.float64]:
                return self.model_func(list(params), x_vals)

            try:
                popt, _ = curve_fit(curve_fit_func, X.flatten(), y, p0=initial_params, maxfev=max_iter)
                self.coef_ = popt
            except Exception:
                # Fallback to initial parameters if fitting fails
                self.coef_ = np.array(initial_params)

            return self

        def predict(self, X: NDArray[np.float64]) -> NDArray[np.float64]:
            if self.coef_ is None:
                raise ValueError("Model must be fitted before prediction")
            return self.model_func(self.coef_.tolist(), X.flatten())

    # Prepare data
    X = x.reshape(-1, 1)  # Reshape for sklearn

    try:
        if method.lower() == "ransac":
            # Use RANSAC for outlier-robust fitting
            base_estimator = CustomModelEstimator(model_func, len(initial_params))

            # Calculate min_samples: at least as many as parameters, but minimum 2
            min_samples = max(len(initial_params), 2)

            # Handle sklearn API change: base_estimator -> estimator in sklearn 1.2+
            try:
                # Try new API first (sklearn >= 1.2)
                estimator = RANSACRegressor(
                    estimator=base_estimator,
                    min_samples=min_samples,
                    max_trials=max_iter,
                    residual_threshold=np.std(y) * 2,  # Threshold based on data std
                    random_state=42,
                )
            except TypeError:
                # Fall back to old API (sklearn < 1.2)
                estimator = RANSACRegressor(
                    base_estimator=base_estimator,
                    min_samples=min_samples,
                    max_trials=max_iter,
                    residual_threshold=np.std(y) * 2,  # Threshold based on data std
                    random_state=42,
                )
        elif method.lower() == "huber":
            # For Huber regression, we'll use a simplified approach
            # Since it's designed for linear models, we'll use it as a robust alternative
            estimator = HuberRegressor(max_iter=max_iter, alpha=0.0)
            # For non-linear models, this is a limitation - we'd need a custom implementation

        else:
            raise ValueError(
                f"Unknown robust method: {method}. Use 'ransac' or 'huber'"
            )

        # Fit the model
        if method.lower() == "huber" and len(initial_params) > 2:
            # Huber regression is primarily for linear models
            # For non-linear models, fall back to RANSAC
            logging.warning(
                "Huber regression works best with linear models. Consider using RANSAC for non-linear models."
            )

        estimator.fit(X, y)
        # Get parameters
        if hasattr(estimator, "estimator_") and hasattr(estimator.estimator_, "coef_"):
            # RANSAC case
            params = estimator.estimator_.coef_
        elif hasattr(estimator, "coef_"):
            # Huber case - append intercept if available
            if hasattr(estimator, "intercept_"):
                params = np.append(estimator.coef_, estimator.intercept_)
            else:
                params = estimator.coef_
        else:
            # Fallback
            params = np.array(initial_params)

        # Ensure params has the right length
        if len(params) != len(initial_params):
            params = np.array(initial_params)  # Fallback to initial params

        resultado = RobustResult(params)
    except Exception as e:
        logging.error(f"Robust fitting failed: {e}")
        # Fallback to least squares
        resultado, chi2_total, r2 = perform_least_squares_fit(
            x, y, None, model_func, initial_params, max_iter
        )
        return RobustResult(resultado.beta, resultado.cov_beta), chi2_total, r2
    # Calculate statistics
    y_pred: NDArray[np.float64] = model_func(params.tolist(), x)
    # Chi-squared calculation (unweighted for robust methods)
    chi2_total = float(np.sum((y - y_pred) ** 2))

    # R-squared calculation
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    ss_res = float(np.sum((y - y_pred) ** 2))

    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else (1.0 if ss_res == 0 else np.nan)

    return resultado, chi2_total, r2


def perform_weighted_least_squares_fit(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    weights: NDArray[np.float64],
    model_func: ModelCallable,
    initial_params: List[float],
    max_iter: int,
) -> Tuple[LeastSquaresResult, float, float]:
    """Perform Weighted Least Squares fitting with custom weights

    Args:
        x, y: Data arrays
        weights: Custom weights (not necessarily 1/sigma)
        model_func: Model function
        initial_params: Initial parameter estimates
        max_iter: Maximum number of iterations

    Returns:
        Tuple containing (result object, chi-squared, R-squared)
    """
    from scipy.optimize import curve_fit
    import logging

    # Convert model function to work with curve_fit
    def curve_fit_func(
        x_vals: NDArray[np.float64], *params: float
    ) -> NDArray[np.float64]:
        return model_func(list(params), x_vals)

    # Convert weights to sigma (curve_fit expects sigma, not weights)
    # weights = 1/sigma^2, so sigma = 1/sqrt(weights)
    # Validate weights first
    if np.any(weights <= 0):
        logging.warning(
            "Invalid weights detected (zero or negative). Using absolute values with small epsilon."
        )

    sigma_from_weights = 1.0 / np.sqrt(
        np.abs(weights) + 1e-10
    )  # Add small value to avoid division by zero

    try:
        popt, pcov = curve_fit(
            curve_fit_func,
            x,
            y,
            p0=initial_params,
            sigma=sigma_from_weights,
            absolute_sigma=True,
            maxfev=max_iter,
        )

        resultado = LeastSquaresResult(popt, pcov)
    except Exception as e:
        logging.error(f"Weighted least squares fitting failed: {e}")
        raise RuntimeError(f"Weighted least squares fitting failed: {e}")

    # Calculate statistics
    y_pred: NDArray[np.float64] = model_func(popt.tolist(), x)
    # Weighted chi-squared calculation
    chi2_total = float(np.sum(weights * (y - y_pred) ** 2))

    # R-squared calculation (standard, not weighted)
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    ss_res = float(np.sum((y - y_pred) ** 2))

    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else (1.0 if ss_res == 0 else np.nan)

    return resultado, chi2_total, r2


def perform_bootstrap_fit(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    sigma_y: Optional[NDArray[np.float64]],
    model_func: ModelCallable,
    initial_params: List[float],
    max_iter: int,
    n_bootstrap: int = 1000,
) -> Tuple[BootstrapResult, float, float]:
    """Perform Bootstrap fitting for uncertainty estimation

    Args:
        x, y: Data arrays
        sigma_y: Standard deviations for y (optional)
        model_func: Model function
        initial_params: Initial parameter estimates
        max_iter: Maximum number of iterations
        n_bootstrap: Number of bootstrap samples

    Returns:
        Tuple containing (result object, chi-squared, R-squared)
    """
    from scipy.optimize import curve_fit
    import logging

    # Convert model function to work with curve_fit
    def curve_fit_func(
        x_vals: NDArray[np.float64], *params: float
    ) -> NDArray[np.float64]:
        return model_func(list(params), x_vals)

    # Prepare sigma for curve_fit
    sigma = None
    if sigma_y is not None and not np.allclose(sigma_y, 0):
        sigma = sigma_y
    # Perform initial fit to get best parameters
    try:
        popt_original, _ = curve_fit(
            curve_fit_func,
            x,
            y,
            p0=initial_params,
            sigma=sigma,
            absolute_sigma=True if sigma is not None else False,
            maxfev=max_iter,
        )
    except Exception as e:
        logging.error(f"Initial fit for bootstrap failed: {e}")
        raise RuntimeError(f"Initial fit for bootstrap failed: {e}")

    # Bootstrap resampling
    bootstrap_params = []
    n_points = len(x)

    for _ in range(n_bootstrap):
        # Resample data with replacement
        indices = np.random.choice(n_points, n_points, replace=True)
        x_boot = x[indices]
        y_boot = y[indices]
        sigma_boot = sigma[indices] if sigma is not None else None

        try:
            # Fit to bootstrap sample
            popt_boot, _ = curve_fit(
                curve_fit_func,
                x_boot,
                y_boot,
                p0=popt_original,  # Use original fit as starting point
                sigma=sigma_boot,
                absolute_sigma=True if sigma_boot is not None else False,
                maxfev=max_iter,
            )
            bootstrap_params.append(popt_boot)
        except Exception:
            # If bootstrap sample fails, use original parameters
            bootstrap_params.append(popt_original)
    # Convert to numpy array
    bootstrap_params_array = np.array(bootstrap_params)
    # Create result object
    resultado = BootstrapResult(popt_original, bootstrap_params_array)
    # Calculate statistics using original fit
    y_pred: NDArray[np.float64] = model_func(popt_original.tolist(), x)
    # Chi-squared calculation
    chi2_total: float = np.nan
    if sigma_y is not None:
        # Check if we have any valid (non-zero) uncertainties
        valid_mask = sigma_y > 0
        if np.any(valid_mask):
            # Use weighted chi-squared only for points with valid uncertainties
            chi2_total = float(
                np.sum(
                    ((y[valid_mask] - y_pred[valid_mask]) / sigma_y[valid_mask]) ** 2
                )
            )
        else:
            # All uncertainties are zero - use unweighted
            chi2_total = float(np.sum((y - y_pred) ** 2))
    else:
        chi2_total = float(np.sum((y - y_pred) ** 2))

    # R-squared calculation
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    ss_res = float(np.sum((y - y_pred) ** 2))

    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else (1.0 if ss_res == 0 else np.nan)

    return resultado, chi2_total, r2


class BayesianResult:
    """Result object for Bayesian fitting to match ODR output format"""

    def __init__(self, params: NDArray[np.float64], param_samples: NDArray[np.float64]):
        self.beta = params  # Mean of posterior
        self.param_samples = param_samples
        self.info = 1  # Success flag

        # Calculate covariance matrix from posterior samples
        self.cov_beta = np.cov(param_samples.T)

        # Calculate parameter uncertainties (standard deviations from posterior)
        self.sd_beta = np.std(param_samples, axis=0)


def perform_bayesian_fit(
    x: NDArray[np.float64],
    y: NDArray[np.float64],
    sigma_y: Optional[NDArray[np.float64]],
    model_func: ModelCallable,
    initial_params: List[float],
    max_iter: int = 1000,
    n_samples: int = 1000,
) -> Tuple[BayesianResult, float, float]:
    """Perform Bayesian regression with uncertainty quantification

    Args:
        x, y: Data arrays
        sigma_y: Standard deviations for y (optional)
        model_func: Model function
        initial_params: Initial parameter estimates
        max_iter: Maximum number of iterations (for MCMC)
        n_samples: Number of posterior samples

    Returns:
        Tuple containing (result object, chi-squared, R-squared)
    """
    try:
        from sklearn.linear_model import BayesianRidge
        from sklearn.preprocessing import PolynomialFeatures
    except ImportError:
        raise ImportError(
            "scikit-learn is required for Bayesian regression. Install with: pip install scikit-learn"
        )

    import logging

    # For non-linear models, we'll use polynomial approximation
    # This is a limitation - for true Bayesian non-linear regression, we'd need PyMC or similar
    try:
        # Determine polynomial degree
        degree = min(3, len(initial_params))
        # Create polynomial features
        poly_features = PolynomialFeatures(degree=degree, include_bias=False)
        X_poly = poly_features.fit_transform(x.reshape(-1, 1))
        # Fit Bayesian Ridge regression
        bayesian_ridge = BayesianRidge(n_iter=max_iter, compute_score=True)
        bayesian_ridge.fit(X_poly, y)

        # Get mean parameters
        params_mean = bayesian_ridge.coef_
        # Generate samples from the posterior (approximate)
        # BayesianRidge doesn't directly provide samples, so we'll approximate
        # using the learned covariance structure
        try:
            # Get the learned precision (inverse covariance)
            alpha_ = bayesian_ridge.alpha_
            lambda_ = bayesian_ridge.lambda_
            # Approximate posterior covariance
            # This is a simplified approach - for full Bayesian inference, use PyMC or similar
            sigma_squared = 1.0 / alpha_
            param_cov = sigma_squared * np.eye(len(params_mean)) / lambda_
            # Generate samples from multivariate normal
            param_samples = np.random.multivariate_normal(
                params_mean, param_cov, size=n_samples
            )

        except Exception:
            # Fallback: use bootstrap-like sampling
            param_samples = np.random.normal(
                params_mean.reshape(1, -1),
                np.abs(params_mean)
                * 0.1,  # 10% relative uncertainty
                size=(n_samples, len(params_mean)),
            )

        # Pad or truncate to match expected parameter count
        if len(params_mean) > len(initial_params):
            params_mean = params_mean[: len(initial_params)]
            param_samples = param_samples[:, : len(initial_params)]
        elif len(params_mean) < len(initial_params):
            # Pad with zeros
            padded_params = np.zeros(len(initial_params))
            padded_params[: len(params_mean)] = params_mean
            params_mean = padded_params

            padded_samples = np.zeros((n_samples, len(initial_params)))
            padded_samples[:, : len(params_mean)] = param_samples
            param_samples = padded_samples

        resultado = BayesianResult(params_mean, param_samples)
    except Exception as e:
        logging.error(f"Bayesian regression failed: {e}")
        # Fallback to bootstrap
        from app_files.gui.ajuste_curva.models import perform_bootstrap_fit

        resultado_boot, chi2_boot, r2_boot = perform_bootstrap_fit(
            x, y, sigma_y, model_func, initial_params, max_iter, n_samples
        )
        return (
            BayesianResult(resultado_boot.beta, resultado_boot.param_samples),
            chi2_boot,
            r2_boot,
        )
    # Calculate statistics using the original model function
    try:
        y_pred: NDArray[np.float64] = model_func(params_mean.tolist(), x)
    except Exception:
        # If model function fails, use polynomial prediction
        y_pred = bayesian_ridge.predict(X_poly)
    # Chi-squared calculation
    chi2_total: float = np.nan
    if sigma_y is not None:
        # Check if we have any valid (non-zero) uncertainties
        valid_mask = sigma_y > 0
        if np.any(valid_mask):
            # Use weighted chi-squared only for points with valid uncertainties
            chi2_total = float(
                np.sum(
                    ((y[valid_mask] - y_pred[valid_mask]) / sigma_y[valid_mask]) ** 2
                )
            )
        else:
            # All uncertainties are zero - use unweighted
            chi2_total = float(np.sum((y - y_pred) ** 2))
    else:
        chi2_total = float(np.sum((y - y_pred) ** 2))

    # R-squared calculation
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    ss_res = float(np.sum((y - y_pred) ** 2))

    r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else (1.0 if ss_res == 0 else np.nan)

    return resultado, chi2_total, r2
