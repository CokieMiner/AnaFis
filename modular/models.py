"""Models and utility classes for AnaFis"""
from __future__ import annotations
import numpy as np
import numpy.typing as npt
from typing import Protocol, List, Callable

FloatArray = npt.NDArray[np.float64]

class ODRModel(Protocol):
    """Protocol for ODR model interface"""
    def __call__(self, beta: FloatArray, x: FloatArray) -> FloatArray: ...
    def fjb(self, beta: FloatArray, x: FloatArray) -> List[FloatArray]: ...
    def fdb(self, beta: FloatArray, x: FloatArray) -> FloatArray: ...

class ODRModelImplementation:
    """ODR model implementation"""
    def __init__(self, function: Callable[[FloatArray, FloatArray], FloatArray],
                derivatives: List[Callable[[FloatArray, FloatArray], FloatArray]]) -> None:
        self.function = function
        self.derivatives = derivatives
        
    def __call__(self, parameters: FloatArray, x: FloatArray) -> FloatArray:
        return self.function(parameters, x)

    def fjb(self, parameters: FloatArray, x: FloatArray) -> List[FloatArray]:
        """Returns derivatives with respect to parameters"""
        return [d(parameters, x) for d in self.derivatives]

    def fdb(self, parameters: FloatArray, x: FloatArray) -> FloatArray:
        """Returns derivative with respect to independent variable"""
        return np.zeros_like(x)

class ProgressTracker:
    """Track ODR fitting progress"""
    def __init__(self, progress_var, status_label, odr_object) -> None:
        self.progress_var = progress_var
        self.status_label = status_label
        self.odr = odr_object
        self.last_iter = 0
        
    def update(self) -> None:
        if self.odr.iwork is not None:
            current_iter = int(self.odr.iwork[0])
            if current_iter != self.last_iter:
                self.last_iter = current_iter
                self.status_label.configure(text=f"Iteration: {current_iter}")
                self.progress_var.set(min(100, current_iter * 10))