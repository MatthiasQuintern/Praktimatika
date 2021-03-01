import sympy as sy
from sympy.abc import *
f = sy.sympify("x + cos(rho) ** 2")
print(f)
print(f.subs({x: 5, rho: 3}).evalf())

with open("functions", "r") as file:
    s = file.read()
lines = s.replace(" ", "").replace("\n\n", "\n").strip("\n").split("\n")

print(lines)
