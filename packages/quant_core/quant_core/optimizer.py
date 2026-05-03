from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .oracle import MVSKOracle
from .simplex import alpha_max_for_simplex, project_simplex, projected_kkt_residual, tangent_basis


@dataclass(frozen=True)
class YANDConfig:
    max_iter: int = 120
    tolerance: float = 1e-6
    tau: float = 1e-8
    regularization: float = 1e-4
    projected_trial_step: float = 0.05
    use_pcg_threshold: int = 120
    pcg_max_iter: int = 25
    pcg_tol: float = 1e-3


@dataclass
class YANDResult:
    weights: np.ndarray
    objective: float
    kkt_residual: float
    iterations: int
    converged: bool
    method: str
    history: list[dict[str, float]] = field(default_factory=list)


class YANDMVSKOptimizer:
    """Simplex-aware YAND-MVSK solver prototype.

    This first implementation keeps the paper's exact sample oracle and quartic line search. The
    affine-normal block is represented by a reduced, regularized tangent solve. For small universes
    the reduced Hessian is assembled exactly through Hessian-vector products; for larger universes a
    matrix-free PCG solve is used.
    """

    def __init__(self, oracle: MVSKOracle, config: YANDConfig | None = None):
        self.oracle = oracle
        self.config = config or YANDConfig()
        self.u = tangent_basis(oracle.n)
        self.xref = np.ones(oracle.n, dtype=float) / oracle.n

    def solve(self, x0: np.ndarray | None = None) -> YANDResult:
        n = self.oracle.n
        x = project_simplex(self.xref if x0 is None else x0, floor=self.config.tau)
        method = "pcg" if n >= self.config.use_pcg_threshold else "direct"
        history: list[dict[str, float]] = []

        for iteration in range(1, self.config.max_iter + 1):
            value, grad = self.oracle.value_grad(x)
            kkt = projected_kkt_residual(x, grad, tol=self.config.tau * 10.0)
            history.append({"objective": value, "kkt_residual": kkt})
            if kkt <= self.config.tolerance:
                return YANDResult(x, value, kkt, iteration - 1, True, method, history)

            direction = (
                self._pcg_direction(x, grad)
                if method == "pcg"
                else self._direct_direction(x, grad)
            )
            direction = direction - np.mean(direction)
            if not np.all(np.isfinite(direction)) or np.linalg.norm(direction) <= 1e-14:
                direction = -self._projected_gradient(grad)

            if float(grad @ direction) >= 0:
                direction = -self._projected_gradient(grad)

            alpha_max = alpha_max_for_simplex(x, direction, tau=self.config.tau)
            if alpha_max <= 0:
                trial = project_simplex(x - self.config.projected_trial_step * grad, floor=self.config.tau)
                direction = trial - x
                alpha_max = 1.0

            alpha = self.oracle.exact_quartic_step(x, direction, alpha_max)
            if alpha <= 0:
                alpha = min(alpha_max, self.config.projected_trial_step)

            x_next = x + alpha * direction
            if np.min(x_next) < self.config.tau or abs(np.sum(x_next) - 1.0) > 1e-8:
                x_next = project_simplex(x_next, floor=self.config.tau)

            next_value = self.oracle.value(x_next)
            if next_value > value and alpha > 0:
                repaired = project_simplex(x - self.config.projected_trial_step * grad, floor=self.config.tau)
                if self.oracle.value(repaired) < value:
                    x_next = repaired

            if np.linalg.norm(x_next - x, ord=1) <= 1e-12:
                break
            x = x_next

        value, grad = self.oracle.value_grad(x)
        kkt = projected_kkt_residual(x, grad, tol=self.config.tau * 10.0)
        return YANDResult(
            weights=x,
            objective=value,
            kkt_residual=kkt,
            iterations=len(history),
            converged=kkt <= self.config.tolerance,
            method=method,
            history=history,
        )

    def _projected_gradient(self, grad: np.ndarray) -> np.ndarray:
        return grad - np.mean(grad)

    def _direct_direction(self, x: np.ndarray, grad: np.ndarray) -> np.ndarray:
        reduced_grad = self.u.T @ grad
        dim = reduced_grad.size
        hessian = np.empty((dim, dim), dtype=float)
        for j in range(dim):
            hessian[:, j] = self.u.T @ self.oracle.hvp(x, self.u[:, j])
        hessian = 0.5 * (hessian + hessian.T)
        hessian += self.config.regularization * np.eye(dim)
        try:
            reduced_step = -np.linalg.solve(hessian, reduced_grad)
        except np.linalg.LinAlgError:
            reduced_step = -np.linalg.pinv(hessian) @ reduced_grad
        return self.u @ reduced_step

    def _pcg_direction(self, x: np.ndarray, grad: np.ndarray) -> np.ndarray:
        reduced_grad = self.u.T @ grad
        b = -reduced_grad

        def matvec(y: np.ndarray) -> np.ndarray:
            return self.u.T @ self.oracle.hvp(x, self.u @ y) + self.config.regularization * y

        y = np.zeros_like(b)
        r = b - matvec(y)
        p = r.copy()
        rs_old = float(r @ r)
        if rs_old <= 1e-24:
            return -self._projected_gradient(grad)
        for _ in range(self.config.pcg_max_iter):
            ap = matvec(p)
            denom = float(p @ ap)
            if abs(denom) <= 1e-18:
                break
            alpha = rs_old / denom
            y = y + alpha * p
            r = r - alpha * ap
            rs_new = float(r @ r)
            if np.sqrt(rs_new) <= self.config.pcg_tol * max(1.0, np.linalg.norm(b)):
                break
            p = r + (rs_new / rs_old) * p
            rs_old = rs_new
        return self.u @ y
