# 2025-12-04

## idea
- residual attention as nested learning
    - q as x
    - k as x @ x2
    - (q@k @ v)
    - x updates twice while x2 updates once
    - nest this structure (or recurse)