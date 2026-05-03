from __future__ import annotations

import numpy as np

from .simplex import project_simplex


def solve_mean_variance(
    returns: np.ndarray,
    risk_aversion: float = 8.0,
    ridge: float = 1e-5,
    max_iter: int = 800,
) -> np.ndarray:
    """Solve a long-only mean-variance allocation with projected gradient."""

    returns = np.asarray(returns, dtype=float)
    mu = returns.mean(axis=0)
    cov = np.cov(returns, rowvar=False)
    if cov.ndim == 0:
        cov = np.array([[float(cov)]])
    cov = cov + ridge * np.eye(cov.shape[0])
    n = returns.shape[1]
    x = np.ones(n) / n
    lipschitz = float(risk_aversion * np.linalg.norm(cov, ord=2) + 1e-12)
    step = 1.0 / lipschitz
    for _ in range(max_iter):
        grad = risk_aversion * (cov @ x) - mu
        x_next = project_simplex(x - step * grad)
        if np.linalg.norm(x_next - x, ord=1) < 1e-10:
            return x_next
        x = x_next
    return x
