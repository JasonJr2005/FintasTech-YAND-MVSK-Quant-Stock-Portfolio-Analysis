from __future__ import annotations

import numpy as np


def normalize_weights(weights: np.ndarray, floor: float = 0.0) -> np.ndarray:
    weights = np.asarray(weights, dtype=float)
    weights = np.maximum(weights, floor)
    total = float(weights.sum())
    if total <= 0:
        return np.ones_like(weights) / weights.size
    return weights / total


def project_simplex(v: np.ndarray, z: float = 1.0, floor: float = 0.0) -> np.ndarray:
    """Euclidean projection onto {x: x_i >= floor, sum x_i = z}."""

    v = np.asarray(v, dtype=float)
    if floor < 0:
        raise ValueError("floor must be non-negative")
    shifted_budget = z - floor * v.size
    if shifted_budget <= 0:
        raise ValueError("floor is too large for simplex budget")
    shifted = v - floor
    u = np.sort(shifted)[::-1]
    cssv = np.cumsum(u)
    rho_candidates = u * np.arange(1, v.size + 1) > (cssv - shifted_budget)
    if not np.any(rho_candidates):
        return np.full_like(v, z / v.size)
    rho = np.nonzero(rho_candidates)[0][-1]
    theta = (cssv[rho] - shifted_budget) / float(rho + 1)
    return np.maximum(shifted - theta, 0.0) + floor


def tangent_basis(n: int) -> np.ndarray:
    """Build an orthonormal basis for the simplex tangent space 1^T x = 0."""

    if n < 2:
        raise ValueError("n must be at least 2")
    basis = np.zeros((n, n - 1), dtype=float)
    for j in range(n - 1):
        k = j + 1
        basis[:k, j] = 1.0 / np.sqrt(k * (k + 1))
        basis[k, j] = -np.sqrt(k / (k + 1))
    return basis


def alpha_max_for_simplex(x: np.ndarray, d: np.ndarray, tau: float = 1e-8) -> float:
    x = np.asarray(x, dtype=float)
    d = np.asarray(d, dtype=float)
    negative = d < -1e-14
    if not np.any(negative):
        return 0.0
    caps = (x[negative] - tau) / (-d[negative])
    return float(max(0.0, np.min(caps)))


def projected_kkt_residual(x: np.ndarray, grad: np.ndarray, tol: float = 1e-10) -> float:
    """Projected first-order residual for long-only simplex constraints."""

    x = np.asarray(x, dtype=float)
    grad = np.asarray(grad, dtype=float)
    active = x <= tol
    free = ~active
    if np.any(free):
        lagrange = float(np.mean(grad[free]))
    else:
        lagrange = float(np.min(grad))
    residual = np.zeros_like(x)
    residual[free] = grad[free] - lagrange
    residual[active] = np.minimum(grad[active] - lagrange, 0.0)
    return float(np.linalg.norm(residual, ord=np.inf))


def effective_number(weights: np.ndarray) -> float:
    weights = np.asarray(weights, dtype=float)
    return float(1.0 / np.sum(np.square(weights))) if weights.size else 0.0
