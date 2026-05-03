# Paper To Code: YAND-MVSK

This project implements the software-facing core of *Yau's Affine-Normal Descent for Large-Scale
Unrestricted Higher-Moment Portfolio Optimization*.

## Key Translation

The paper's main engineering lesson is that unrestricted MVSK should not be implemented through
explicit covariance, coskewness, and cokurtosis tensors. Instead, store:

- `R`: sample return matrix.
- `mu`: sample mean vector.
- `A = R - 1 * mu^T`: centered return matrix.

For weights `x`, define `z = A x`. The objective is:

```text
f(x) = -c1 * mu^T x
     + c2 / T * sum(z_t^2)
     - c3 / T * sum(z_t^3)
     + c4 / T * sum(z_t^4)
```

The implementation in `packages/quant_core/quant_core/oracle.py` exposes:

- `value_grad(x)`: exact objective and gradient.
- `hvp(x, v)`: Hessian-vector product.
- `third(x, u, v)`: third-order directional kernel.
- `exact_quartic_step(x, d, alpha_max)`: exact line search along a feasible direction.

## Solver Shape

`YANDMVSKOptimizer` uses a simplex tangent basis, a regularized reduced solve, and exact quartic
line search. For small universes it assembles the reduced Hessian via oracle HVP calls. For larger
universes it switches to matrix-free PCG.

This is a pragmatic MVP implementation. It preserves the paper's exact oracle and line-search
structure while keeping the full affine-normal/log-determinant correction layer modular for future
extension.

## Research Interpretation

The paper's empirical message is conditional, not magical: higher moments add value when the
return mandate leaves enough allocation freedom for skewness and kurtosis to reshape payoff
distribution. This project therefore always compares MVSK against an MV baseline and reports
diagnostics such as KKT residual, active share, effective number of assets, drawdown, and CVaR.
