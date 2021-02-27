import sympy as sy
from sympy.abc import *
f = sy.sympify("x + cos(rho) ** 2")
print(f)
print(f.subs({x: 5, rho: 3}).evalf())

