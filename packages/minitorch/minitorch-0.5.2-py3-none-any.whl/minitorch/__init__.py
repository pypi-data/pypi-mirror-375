"""
MiniTorch - A miniature deep learning framework built from scratch with NumPy
"""

from .minitorch import (
    Tensor,
    Linear,
    LeakyReLU,
    ReLU,
    Sigmoid,
    Tanh,
    Softmax,
    Dropout,
    BatchNorm1D,
    Sequential,
    mse,
    bce,
    cross_entropy,
    Adam,
    Pipeline,
    generate_mixed_data,
    generate_classification_data,
    generate_quadratic_data,
    generate_nonlinear_data
)

__version__ = "0.5.2"
__author__ = "Your Name"
__license__ = "MIT"

__all__ = [
    "Tensor",
    "Linear",
    "LeakyReLU",
    "ReLU",
    "Sigmoid",
    "Tanh",
    "Softmax",
    "Dropout",
    "BatchNorm1D",
    "Sequential",
    "mse",
    "bce",
    "cross_entropy",
    "Adam",
    "Pipeline",
    "generate_mixed_data",
    "generate_classification_data",
    "generate_quadratic_data",
    "generate_nonlinear_data"
]

# Package description
__doc__ = """
MiniTorch - A lightweight deep learning framework

Features:
- Automatic differentiation with Tensor class
- Neural network layers (Linear, activations, normalization, dropout)
- Loss functions (MSE, BCE, CrossEntropy)
- Optimizers (Adam with learning rate scheduling)
- Training pipeline with evaluation metrics
- Synthetic data generation utilities

Example usage:
    >>> from minitorch import Tensor, Linear, ReLU, mse, Adam
    >>> import numpy as np
    >>> 
    >>> # Create a simple model
    >>> model = Sequential(
    ...     Linear(1, 10),
    ...     ReLU(),
    ...     Linear(10, 1)
    ... )
    >>> 
    >>> # Create optimizer
    >>> optimizer = Adam(model.parameters(), lr=0.01)
    >>> 
    >>> # Generate some data
    >>> X = Tensor(np.random.randn(100, 1))
    >>> y = Tensor(2 * X.data + 1 + np.random.randn(100, 1) * 0.1)
    >>> 
    >>> # Training loop
    >>> for epoch in range(100):
    ...     optimizer.zero_grad()
    ...     pred = model(X)
    ...     loss = mse(pred, y)
    ...     loss.backward()
    ...     optimizer.step()
    ...     if epoch % 10 == 0:
    ...         print(f"Epoch {epoch}, Loss: {loss.data:.4f}")
"""

