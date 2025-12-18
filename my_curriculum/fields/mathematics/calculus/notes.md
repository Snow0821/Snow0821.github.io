# Calculus

## Index
1. Functions
2. Limits and Continuity
3. Derivatives
4. Applications of Derivatives
5. Integrals
6. Applications of Definite Integrals
7. Integrals and Transcendal Functions
8. Techniques of Integration
9. First-Order Differential Equations
10. Infinite Sequences and Series
11. Parametric Equations and Polar Coordinates
12. Vectors and the Geometry of Space
13. Vector-Valued Functions and Motion in Space
14. Partial Derivatives
15. Multiple Integrals
16. Integrals and Vector Fields
17. Second-Order Differential Equations (Online)

## 1. Functions
### Index
1. Functions and Their Graphs
2. Combining Functions; Shifting and Scaling Graphs
3. Trigonometric Functions
4. Graphing with Software
5. Exponential Functions
6. Inverse Functions and Logarithms

### 1. Functions and Their Graphs
- Domain and Range
    - $y = f(x)$ "y equals f of x"
        - $x$ : independent variable
        - $y$ : depentant variable
        - domain D : $x \in D$
        - range : unique $f(x)$ of $x \in D$
    - natural domain
        - largest set of real x where f(x) is real
        - default if not explicitly restricted
    - real-valued
        - $range(f(x)) = \R$
- Graphs of functions
    - Graph (set notation) : {$(x, f(x)) | (x \in D)$}
- Representing a Function Numerically
    - scatter plot
- The Vertical Line Test for a Function
    - A function $f$ can have only one value $f(x)$ for each $x \in D$
    - for $a \in D$, $x = a$ will intersect with the graph of $f$ at a single point $(a, f(a))$
    - A circle cannot be a graph of a function
        - however does contain the graph of functions of x
            - $f(x) = \sqrt{1 - x^2}$
            - $g(x) = - \sqrt{1 - x^2}$
- Piecewise-Defined Functions
    - absolute value function
        - $|x| = \begin{cases}
        x, & x \ge 0 \\
        -x, & x < 0
        \end{cases}$
    - greatest integer function (integer floor function)
        - $\lfloor x \rfloor$
    - least integer function (integer ceiling function)
        - $\lceil x \rceil$
- Increasing and Decreasing Functions
    - on an interval $l$ and let $x_1$ and $x_2$ be any two points in $l.
    - whenever $x_1 < x_2$
        - if $f(x_2) > f(x_1)$, $f$ is said to be increasing on $l$
        - if $f(x_2) < f(x_1)$, $f$ is said to be decreasing on $l$
- Even Functions and Odd Functions : Symmetry
    - even function : $f(x) = f(-x)$
        - symmetric about the y-axis
    - odd function : $f(-x) = -f(x)$
        - symmetric about the origin
- Common Functions
    - Linear Functions
        - $f(x) = mx + b$, for constants $m$ and $b$
        - identiry function : $f(x) = x$, where $m = 1$ and $b = 0$
        - proportionality relationship : a linear functions where $m \ge 0$, $b = 0$
        - proportional : x, y if $y = kx$ for some nonzero constant k
            - inversely proportional : x, y if $y = k / x$ or y is proportional to $1/x$
    - Power Functions
        - $f(x) = x^a$
        - even function if $a$ is even
        - odd function if $a$ is odd
        - not defined for $x = 0$ if $a < 0$ 
