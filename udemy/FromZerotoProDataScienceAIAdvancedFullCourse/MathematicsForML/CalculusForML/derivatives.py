import sympy as sp

x = sp.Symbol('x')
f = x**2
derivative = sp.diff(f, x)

print("Derivative: ", derivative)