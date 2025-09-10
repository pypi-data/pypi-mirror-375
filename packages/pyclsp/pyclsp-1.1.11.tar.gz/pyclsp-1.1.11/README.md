# CLSP — Convex Least Squares Programming

**Linear Programming via Pseudoinverse Estimation (LPPINV)** is a two-stage estimation method that reformulates linear programs as structured least-squares problems. Drawing inspiration from the **Convex Least Squares Programming (CLSP)** framework, LPPINV solves linear inequality, equality, and bound constraints by (1) constructing a canonical constraint system and computing a pseudoinverse projection, followed by (2) a convex-programming correction stage to refine the solution under additional regularization (e.g., Lasso, Ridge, or Elastic Net).

## Installation

```bash
pip install pyclsp
```

## Quick Example

```python
import numpy as np
import matplotlib.pyplot as plt
from clsp import CLSP

# Example allocation problem: row sums (first 5) + col sums (last 5)
b = np.array([22, 23, 26, 27, 21, 28, 24, 22, 24, 21], dtype=float)

# Initialize estimator
model = CLSP()

# Solve the system (allocation problem)
result = model.solve(problem='ap', b=b, m=5, p=5, final=True)
print("Estimated matrix:")
print(result.x)

# Access diagnostics
print("NRMSE:", model.nrmse)

# Correlogram: RMSA sensitivity by constraint
corr = model.corr()
plt.figure(figsize=(8, 4))
plt.grid(True, linestyle="--", alpha=0.6)
plt.bar(range(len(corr["rmsa_i"])), corr["rmsa_i"])
plt.xlabel("Constraint index")
plt.ylabel("RMSA (row deletion effect)")
plt.title("CLSP Correlogram")
plt.tight_layout()
plt.show()

# Hypothesis test
print("t-test on NRMSE:", model.ttest())
```

## User Reference

For comprehensive information on the estimator’s capabilities, advanced configuration options, and implementation details, please refer to the docstrings provided in each of the individual .py source files. These docstrings contain complete descriptions of available methods, their parameters, expected input formats, and output structures.

### The `CLSP` Class

```python
self.__init__()
```

Stores the solution, goodness-of-fit statistics, and ancillary parameters.

The class has three core methods: `solve()`, `corr()`, and `ttest()`.

**Selected attributes:**  
`self.A`             : *np.ndarray*  
design matrix `A` = [`C` | `S`; `M` | `Q`], where `Q` is either a zero matrix or *S_residual*.

`self.b`             : *np.ndarray*  
vector of the right-hand side.

`self.zhat`          : *np.ndarray*  
vector of the first-step estimate.

`self.r`             : *int*  
number of refinement iterations performed in the first step.

`self.z`             : *np.ndarray*  
vector of the final solution. If the second step is disabled, it equals `self.zhat`.

`self.x`             : *np.ndarray*  
`m` x `p` matrix or vector containing the variable component of `z`.

`self.y`             : *np.ndarray*  
vector containing the slack component of `z`.

`self.kappaC`        : *float*  
spectral κ() for *C_canon*.

`self.kappaB`        : *float*  
spectral κ() for *B* = *C_canon^+*`A`.

`self.kappaA`        : *float*  
spectral κ() for `A`.

`self.rmsa`          : *float*  
total root mean square alignment (RMSA).

`self.r2_partial`    : *float*  
R^2 for the `M` block in `A`.

`self.nrmse` : *float*  
mean square error calculated from `A` and normalized by standard deviation (NRMSE).

`self.nrmse_partial` : *float*  
mean square error calculated from the `M` block in `A` and normalized by standard deviation (NRMSE).

`self.z_lower`       : *np.ndarray*  
lower bound of the diagnostic interval (confidence band) based on κ(`A`).

`self.z_upper`       : *np.ndarray*  
upper bound of the diagnostic interval (confidence band) based on κ(`A`).

`self.x_lower`       : *np.ndarray*  
lower bound of the diagnostic interval (confidence band) based on κ(`A`).

`self.x_upper`       : *np.ndarray*  
upper bound of the diagnostic interval (confidence band) based on κ(`A`).

`self.y_lower`       : *np.ndarray*  
lower bound of the diagnostic interval (confidence band) based on κ(`A`).

`self.y_upper`       : *np.ndarray*  
upper bound of the diagnostic interval (confidence band) based on κ(`A`).

### Solver Method: `solve()`

```python
self.solve(problem, C, S, M, b, m, p, i, j, zero_diagonal, r, Z, tolerance, iteration_limit, final, alpha)
```

Solves the Convex Least Squares Programming (CLSP) problem.

This method performs a two-step estimation:
(1) a pseudoinverse-based solution using either the Moore–Penrose or Bott–Duffin inverse, optionally iterated for refinement;
(2) a convex-programming correction using Lasso, Ridge, or Elastic Net regularization (if enabled).

**Parameters:**  
`problem` : *str*, optional  
    Structural template for matrix construction. One of:  
    - *'ap'* or *'tm'* : allocation (transaction) matrix problem (AP).  
    - *'cmls'* or *'rp'* : constrained-model least squares (regression) problem.  
    - anything else: general CLSP problem (user-defined `C` and/or `M`).

`C`, `S`, `M` : *np.ndarray* or *None*  
    Blocks of the design matrix `A` = [`C` | `S`; `M` | `Q`]. If `C` and/or `M` are provided, the matrix `A` is constructed accordingly (please note that for AP, `C` is constructed automatically and known values are specified in `M`).

`b` : *np.ndarray* or *None*  
    Right-hand side vector. Must have as many rows as `A` (please note that for AP, it should start with row sums). Required.

`m`, `p` : *int* or *None*  
    Dimensions of X ∈ ℝ^{m×p}, relevant for AP.

`i`, `j` : *int*, default = *1*  
    Grouping sizes for row and column sum constraints in AP.

`zero_diagonal` : *bool*, default = *False*  
    If *True*, enforces structural zero diagonals.

`r` : *int*, default = *1*  
    Number of refinement iterations for the pseudoinverse-based estimator.

`Z` : *np.ndarray* or *None*  
    A symmetric idempotent matrix (projector) defining the subspace for Bott–Duffin pseudoinversion. If *None*, the identity matrix is used, reducing the Bott–Duffin inverse to the Moore–Penrose case.

`tolerance` : *float*, default = *square root of machine epsilon*  
    Convergence tolerance for NRMSE change between refinement iterations.

`iteration_limit` : *int*, default = *50*  
    Maximum number of iterations allowed in the refinement loop.

`final` : *bool*, default = *True*  
    If *True*, a convex programming problem is solved to refine `zhat`. The resulting solution `z` minimizes a weighted L1/L2 norm around `zhat` subject to `Az` = `b`.

`alpha` : *float*, default = *1.0*  
    Regularization parameter (weight) in the final convex program:  
	- `α = 0`: Lasso (L1 norm)  
	- `α = 1`: Tikhonov Regularization/Ridge (L2 norm)  
	- `0 < α < 1`: Elastic Net

`*args`, `**kwargs` : optional  
    CVXPY arguments passed to the CVXPY solver.

**Returns:**  
*self*

### Correlogram Method: `corr()`

```python
self.corr(reset, threshold)
```

Computes the structural correlogram of the CLSP constraint part.

This method performs a row-deletion sensitivity analysis on the canonical constraint matrix `[C` | `S`], denoted as *C_canon*, and evaluates the marginal effect of each constraint row on numerical stability, angular alignment, and estimator sensitivity.

For each row `i` in `C_canon`, it computes:  
	- The Root Mean Square Alignment (`RMSA_i`) with all other rows `j` ≠ `i`.  
	- The change in condition numbers κ(`C`), κ(`B`), and κ(`A`) when row `i` is deleted.  
	- The effect on estimation quality: changes in `nrmse`, `zhat`, `z`, and `x` when row `i` is deleted.

Additionally, it computes the total `rmsa` statistic across all rows, summarizing the overall angular alignment of *C_canon*.

**Parameters:**  
`reset` : *bool*, default = *False*  
    If *True*, forces recomputation of all diagnostic values (the results are preserved for eventual reproduction after the method is called).

`threshold` : *float*, default = *0*  
    If positive, limits the output to constraints with `RMSA_i` ≥ `threshold`.

**Returns:**  
*dict* of *list*  
    A dictionary containing per-row diagnostic values:  
    {  
        `"constraint"`   : `[1, 2, ..., k]`,  # 1-based indices  
        `"rmsa_i"`       : list of `RMSA_i` values,  
        `"rmsa_dkappaC"` : list of Δκ(`C`) after deleting row `i`,  
        `"rmsa_dkappaB"` : list of Δκ(`B`) after deleting row `i`,  
        `"rmsa_dkappaA"` : list of Δκ(`A`) after deleting row `i`,  
        `"rmsa_dnrmse"`  : list of Δ`nrmse` after deleting row `i`,  
        `"rmsa_dzhat"`   : list of Δ`zhat` after deleting row `i`,  
        `"rmsa_dz"`      : list of Δ`z` after deleting row `i`,  
        `"rmsa_dx"`      : list of Δ`x` after deleting row `i`,  
    }

### T-Test Method: `ttest`

```python
self.ttest(reset, sample_size, seed, distribution)
```

Performs a Monte Carlo-based one- or two-sided t-test on the NRMSE statistic.

This function simulates right-hand side vectors `b` using a user-defined or default distribution and recomputes the estimator for every new `b`. It 
tests whether the observed NRMSE significantly deviates from the null distribution (under H₀) of simulated NRMSE values. The quality of the test depends on the size of the simulated sample.

**Parameters:**  
`reset` : *bool*, default = *False*  
    If *True*, forces recomputation of the NRMSE null distribution (under H₀) (the results are preserved for eventual reproduction after the method is called).

`sample_size` : *int*, default = *50*  
    Size of the Monte Carlo simulated sample under H₀.

`seed` : *int* or *None*, optional  
    Optional random seed to override the default.

`distribution` : *str* or *None*, default = *’normal’*  
    Distribution for generating simulated `b` vectors. One of (standard): *'normal'*, *'uniform'*, or *'laplace'*.

**Returns:**  
*dict*  
    Dictionary with test results and null distribution statistics:  
    {  
        `'p_one_left'`  : P(nrmse ≤ null mean),  
        `'p_one_right'` : P(nrmse ≥ null mean),  
        `'p_two_sided'` : 2-sided t-test p-value,  
        `'nrmse'`       : observed value,  
        `'mean_null'`   : mean of the null distribution (under H₀),  
        `'std_null'`    : standard deviation of the null distribution (under H₀)  
    }

## Bibliography
To be added.

## License
MIT License — see the [LICENSE](LICENSE) file.
