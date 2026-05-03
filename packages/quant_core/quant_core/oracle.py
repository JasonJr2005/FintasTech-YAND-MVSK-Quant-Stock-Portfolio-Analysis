from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class MVSKCoefficients:
    """Investor preference coefficients for the MVSK objective."""

    mean: float = 1.0
    variance: float = 1.0
    skewness: float = 1.0
    kurtosis: float = 1.0

    @classmethod
    def preset(cls, name: str) -> "MVSKCoefficients":
        presets = {
            "balanced": cls(mean=1.0, variance=1.0, skewness=0.6, kurtosis=0.4),
            "skew-focused": cls(mean=1.0, variance=1.0, skewness=1.2, kurtosis=0.2),
            "kurtosis-focused": cls(mean=1.0, variance=1.0, skewness=0.2, kurtosis=1.2),
            "defensive": cls(mean=0.8, variance=1.3, skewness=0.2, kurtosis=1.4),
        }
        if name not in presets:
            raise ValueError(f"Unknown MVSK preset: {name}")
        return presets[name]

    def as_array(self) -> np.ndarray:
        return np.array([self.mean, self.variance, self.skewness, self.kurtosis], dtype=float)


class MVSKOracle:
    """Exact sample-oracle interface for unrestricted long-only MVSK.

    The implementation follows the paper's matrix interface: store the sample mean `mu` and
    centered return matrix `A`, then evaluate all derivatives through matrix-vector products.
    No coskewness or cokurtosis tensors are formed.
    """

    def __init__(self, returns: np.ndarray, coefficients: MVSKCoefficients):
        returns = np.asarray(returns, dtype=float)
        if returns.ndim != 2:
            raise ValueError("returns must be a 2D matrix with shape (time, assets)")
        if returns.shape[0] < 4 or returns.shape[1] < 2:
            raise ValueError("returns must contain at least 4 samples and 2 assets")

        self.returns = np.nan_to_num(returns, nan=0.0, posinf=0.0, neginf=0.0)
        self.coefficients = coefficients
        self.t, self.n = self.returns.shape
        self.mu = self.returns.mean(axis=0)
        self.a = self.returns - self.mu

    def moments(self, x: np.ndarray) -> dict[str, float]:
        x = np.asarray(x, dtype=float)
        z = self.a @ x
        return {
            "mean": float(self.mu @ x),
            "variance": float(np.mean(z**2)),
            "skewness": float(np.mean(z**3)),
            "kurtosis": float(np.mean(z**4)),
        }

    def value(self, x: np.ndarray) -> float:
        moments = self.moments(x)
        c = self.coefficients
        return float(
            -c.mean * moments["mean"]
            + c.variance * moments["variance"]
            - c.skewness * moments["skewness"]
            + c.kurtosis * moments["kurtosis"]
        )

    def value_grad(self, x: np.ndarray) -> tuple[float, np.ndarray]:
        x = np.asarray(x, dtype=float)
        z = self.a @ x
        c = self.coefficients
        value = (
            -c.mean * (self.mu @ x)
            + c.variance * np.mean(z**2)
            - c.skewness * np.mean(z**3)
            + c.kurtosis * np.mean(z**4)
        )
        grad = (
            -c.mean * self.mu
            + (2.0 * c.variance / self.t) * (self.a.T @ z)
            - (3.0 * c.skewness / self.t) * (self.a.T @ (z**2))
            + (4.0 * c.kurtosis / self.t) * (self.a.T @ (z**3))
        )
        return float(value), np.asarray(grad, dtype=float)

    def hvp(self, x: np.ndarray, v: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        v = np.asarray(v, dtype=float)
        z = self.a @ x
        av = self.a @ v
        c = self.coefficients
        return (
            (2.0 * c.variance / self.t) * (self.a.T @ av)
            - (6.0 * c.skewness / self.t) * (self.a.T @ (z * av))
            + (12.0 * c.kurtosis / self.t) * (self.a.T @ ((z**2) * av))
        )

    def third(self, x: np.ndarray, u: np.ndarray, v: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float)
        u = np.asarray(u, dtype=float)
        v = np.asarray(v, dtype=float)
        z = self.a @ x
        au = self.a @ u
        av = self.a @ v
        c = self.coefficients
        return (
            (-6.0 * c.skewness / self.t) * (self.a.T @ (au * av))
            + (24.0 * c.kurtosis / self.t) * (self.a.T @ (z * au * av))
        )

    def line_coefficients(self, x: np.ndarray, d: np.ndarray) -> np.ndarray:
        """Return coefficients A0..A4 of f(x + alpha d)."""

        x = np.asarray(x, dtype=float)
        d = np.asarray(d, dtype=float)
        z = self.a @ x
        w = self.a @ d
        c = self.coefficients

        def power_sum(r: int, s: int) -> float:
            return float(np.mean((z**r) * (w**s)))

        return np.array(
            [
                self.value(x),
                -c.mean * float(self.mu @ d)
                + 2.0 * c.variance * power_sum(1, 1)
                - 3.0 * c.skewness * power_sum(2, 1)
                + 4.0 * c.kurtosis * power_sum(3, 1),
                c.variance * power_sum(0, 2)
                - 3.0 * c.skewness * power_sum(1, 2)
                + 6.0 * c.kurtosis * power_sum(2, 2),
                -c.skewness * power_sum(0, 3) + 4.0 * c.kurtosis * power_sum(1, 3),
                c.kurtosis * power_sum(0, 4),
            ],
            dtype=float,
        )

    def exact_quartic_step(self, x: np.ndarray, d: np.ndarray, alpha_max: float) -> float:
        """Minimize the quartic line model on [0, alpha_max]."""

        if not np.isfinite(alpha_max) or alpha_max <= 0:
            return 0.0
        coeff = self.line_coefficients(x, d)
        deriv = np.array([4.0 * coeff[4], 3.0 * coeff[3], 2.0 * coeff[2], coeff[1]])
        candidates = [0.0, float(alpha_max)]
        for root in np.roots(deriv):
            if abs(root.imag) <= 1e-9:
                alpha = float(root.real)
                if 0.0 < alpha < alpha_max:
                    candidates.append(alpha)
        values = [float(np.polyval(coeff[::-1], alpha)) for alpha in candidates]
        return float(candidates[int(np.argmin(values))])
