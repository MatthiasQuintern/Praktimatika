"""
Matthias Quintern
2021

TODO: Gamma-Func, sinh, cosh, arcsinh, arccosh, simplify a*(x*b) to (a*b * x), same with fraction, test complex numbers, evtl add complex exp/ln function

"""


import numpy as np


# UNUSED
def sgn(value):
    """returns '+' or '-' depending on the sign of the value"""
    if value < 0:
        return "-"
    else:
        return "+"


# UNUSED
def is_number(num):
    """Check if 'num' has all needed methods for mathematical operations"""
    attrs = ['__add__', '__sub__', '__mul__', '__truediv__', '__pow__']
    return all(hasattr(num, attr) for attr in attrs)


def factorial(value: int):
    """returns the factiorial (n!) of an interger n"""
    if value <= 0:
        return 1
    else:
        return value * factorial(value - 1)


class MathFunction:
    """USAGE:
    define Variables:
        x = V("x")
        y = V("name") the "name" is only used for printing the function, not for calculations
    define Functions with previously defined var:
        f = Sum(x,y)
    combine Functions:
        h = Quot(f, x)
        k = Exp(Power(h, 2))
    calculate explicit values:
        for a function f only dependet on one variable x you can use
        solution = f.calc(8.3)
        for a function g dependet on multiple var x, y, z use
        solution = g.calc({x: 4, y: 3, z: 7})
    derivate a function f in respect to a certain variable x:
        df = f.d(x)
        this derivates and simplifies the function. f.derivate(x) does only derivate, not simplify.
    Parameters:
        a = Param("a", 5)
        you can change the value of the paramter a with
        a.set(-4)
    """
    def __init__(self):
        pass

    # '__add__', '__sub__', '__mul__', '__truediv__', '__pow__'

    def __add__(self, other):
        return Sum(self, other)

    def __sub__(self, other):
        return Sub(self, other)

    def __mul__(self, other):
        return Prod(self, other)

    def __truediv__(self, other):
        return Frac(self, other)

    def __pow__(self, power, modulo=None):
        return Pow(self, power)

    def calc(self, x):
        """returns the value of the function for x"""
        return MathFunction()

    def derivate(self, var):
        """returns the derivative of the cuntion in respect to var"""
        return MathFunction()
    
    def simplify(self):
        return MathFunction()

    def d(self, var):
        """Derivates and then simplifies"""
        return self.derivate(var).simplify()

    def latex(self):
        return ""


class Variable(MathFunction):
    """variable"""
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def calc(self, x):
        if type(x) == dict:
            return x[self]
        elif is_number(x):
            return x

    def derivate(self, var):
        if self == var:
            return Constant(1)
        else:
            return Constant(0)

    def simplify(self):
        return self

    def __repr__(self):
        return self.name

    def latex(self):
        return self.name


class V(Variable):
    """Shorter name for the Variable Class"""
    def __init__(self, name: str):
        super().__init__(name)


class Constant(MathFunction):
    """A constant value."""
    def __init__(self, value):
        super().__init__()
        self.value = value

    def calc(self, x):
        return self.value

    def derivate(self, var):
        return Constant(0)

    def simplify(self):
        if self.value == 0:
            return Constant(0)
        else:
            return self

    def __repr__(self):
        return str(self.value)

    def latex(self):
        return str(self.value)


class C(Constant):
    """A short name for the Constant class. Has to be used with the "+-*/**" operators"""
    def __init__(self, value):
        super().__init__(value)


class Param(Variable):
    """A Parameter. You can change the value, but it behaves like a constant, so you can not derivate in respect to it.
    TODO: Could be useful for Curve-Fitting"""
    def __init__(self, name: str, value):
        super().__init__(name)
        self.value = value

    def calc(self, x):
        return self.value

    def derivate(self, var):
        return Constant(0)

    def simplify(self):
        return self

    def set(self, value):
        self.value=value

    def __repr__(self):
        return self.name

    def latex(self):
        return self.name


class Sum(MathFunction):
    def __init__(self, a, b):
        """Sum of two functions/var/constants"""
        super().__init__()

        if isinstance(a, MathFunction):
            self.a = a
        else:
            self.a = Constant(a)
        if isinstance(b, MathFunction):
            self.b = b
        else:
            self.b = Constant(b)

    def calc(self, x):
        """if type(x) == dict:
            return self.a.calc(x[self.ax]) + self.b.calc(x[self.bx])
        elif is_number(x):
            return self.a.calc(x) + self.b.calc(x)"""
        return self.a.calc(x) + self.b.calc(x)

    def derivate(self, var: V):
        return Sum(self.a.derivate(var), self.b.derivate(var))

    def simplify(self):
        self.a = self.a.simplify()
        self.b = self.b.simplify()
        # if one summand is 0, return just the other
        if isinstance(self.a, Constant) and self.a.value == 0:
            return self.b
        elif isinstance(self.b, Constant) and self.b.value == 0:
            return self.a
        elif isinstance(self.a, Constant) and isinstance(self.b, Constant):
            return Constant(self.calc(1))
        else:
            return self

    def __repr__(self):
        return f"({self.a} + {self.b})"

    def latex(self):
        return f"({self.a.latex()}+{self.b.latex()})"


class Sub(MathFunction):
    def __init__(self, a, b):
        """Subtraction of two functions/var/constants"""
        super().__init__()

        if isinstance(a, MathFunction):
            self.a = a
        else:
            self.a = Constant(a)
        if isinstance(b, MathFunction):
            self.b = b
        else:
            self.b = Constant(b)

    def calc(self, x):
        """if type(x) == dict:
            return self.a.calc(x[self.ax]) + self.b.calc(x[self.bx])
        elif is_number(x):
            return self.a.calc(x) + self.b.calc(x)"""
        return self.a.calc(x) - self.b.calc(x)

    def derivate(self, var: V):
        return Sub(self.a.derivate(var), self.b.derivate(var))

    def simplify(self):
        self.a = self.a.simplify()
        self.b = self.b.simplify()
        # if one summand is 0, return just the other
        if isinstance(self.a, Constant) and self.a.value == 0:
            return Prod(-1, self.b)
        elif isinstance(self.b, Constant) and self.b.value == 0:
            return self.a
        else:
            return self

    def __repr__(self):
        return f"({self.a} - {self.b})"

    def latex(self):
        return f"({self.a.latex()}-{self.b.latex()})"


class Prod(MathFunction):
    def __init__(self, a, b):
        super().__init__()
        if isinstance(a, MathFunction):
            self.a = a
        else:
            self.a = Constant(a)
        if isinstance(b, MathFunction):
            self.b = b
        else:
            self.b = Constant(b)

    def calc(self, x):
        """if type(x) == dict:
            return self.a.calc(x[self.ax]) * self.b.calc(x[self.bx])
        elif is_number(x):
            return self.a.calc(x) * self.b.calc(x)"""
        return self.a.calc(x) * self.b.calc(x)

    def derivate(self, var: V):
        """Prod rule: d/dx(f(x)*g(x)) = f'(x)g(x) + f(x)g'(x)"""
        return Sum(Prod(self.a.derivate(var), self.b), Prod(self.a, self.b.derivate(var)))

    def simplify(self):
        self.a = self.a.simplify()
        self.b = self.b.simplify()
        # if one part is 0, the product is 0. if one part is 1, the prodcut is the other
        ret = self
        if isinstance(self.a, Constant):
            if self.a.value == 0:
                ret = Constant(0)
            elif self.a.value == 1:
                ret = self.b
        if isinstance(self.b, Constant):
            if self.b.value == 0:
                ret = Constant(0)
            elif self.b.value == 1:
                ret = self.a
        if isinstance(self.a, Constant) and isinstance(self.b, Constant):
            ret = Constant(self.calc(1))

        return ret

    def __repr__(self):
        return f"({self.a} * {self.b})"

    def latex(self):
        return f"{self.a.latex()}\\cdot{self.b.latex()}"


class Frac(MathFunction):
    def __init__(self, a, b):
        super().__init__()
        if isinstance(a, MathFunction):
            self.a = a
        else:
            self.a = Constant(a)
        if isinstance(b, MathFunction):
            self.b = b
        else:
            self.b = Constant(b)

    def calc(self, x):
        """if type(x) == dict:
            return self.a.calc(x[self.ax]) * self.b.calc(x[self.bx])
        elif is_number(x):
            return self.a.calc(x) * self.b.calc(x)"""
        return self.a.calc(x) / self.b.calc(x)

    def derivate(self, var: V):
        """Prod rule: d/dx(f(x)*g(x)) = f'(x)g(x) + f(x)g'(x)"""
        enumerator = Sub(Prod(self.a.derivate(var), self.b), Prod(self.a, self.b.derivate(var)))
        denominator = Pow(self.b, 2)
        return Frac(enumerator, denominator)

    def simplify(self):
        self.a = self.a.simplify()
        self.b = self.b.simplify()
        # if enumerator is 0, frac is 0, if denumerator is 1, frac is enumerator
        if not self.a:
            return Constant(0)
        elif isinstance(self.b, Constant) and self.b.value == 1:
            return self.a
        elif isinstance(self.b, Constant) and self.b.value == -1:
            return Prod(-1, self.a)
        elif isinstance(self.a, Constant) and isinstance(self.b, Constant):
            return Constant(self.calc(1))
        else:
            return self

    def __repr__(self):
        return f"({self.a} / {self.b})"

    def latex(self):
        return r"\frac{"+str(self.a.latex())+"}{"+str(self.b.latex())+"}"


class Pow(MathFunction):
    def __init__(self, a, b):
        """Power Function a**b"""
        super().__init__()
        if isinstance(a, MathFunction):
            self.a = a
        else:
            self.a = Constant(a)
        if isinstance(b, MathFunction):
            self.b = b
        else:
            self.b = Constant(b)

    def calc(self, x):
        """if type(x) == dict:
            return self.a.calc(x[self.ax]) * self.b.calc(x[self.bx])
        elif is_number(x):
            return self.a.calc(x) * self.b.calc(x)"""
        return self.a.calc(x) ** self.b.calc(x)

    def derivate(self, var: V):
        """Power derivative:
        b = const: d/dx[a(x)**b] = b*(a(x))**(b-1)*a'(x)
        b = b(x):  d/dx[a(x)**b(x)] = d/dx[exp(b(x)*ln(a(x))] = a(x)**b(x) * (b'(x)*ln(a(x)) + b(x)a'(x)/a(x))"""
        if isinstance(self.b, Constant):
            prod1 = Prod(self.b, Pow(self.a, Constant(self.b.value-1)))
            return Prod(prod1, self.a.derivate(var))
        else:
            sum1 = Prod(Ln(self.a), self.b.derivate(var))
            sum2 = Prod(Frac(self.a.derivate(var), self.a), self.b)
            return Prod(Sum(sum1, sum2), self)

    def simplify(self):
        self.a = self.a.simplify()
        self.b = self.b.simplify()
        # a^0=1, a^1=a, 0^b=0(except when b=0), opt: a^-b = 1/a^b
        if not self.a and self.b:
            return Constant(0)
        elif not self.b:
            return Constant(1)
        elif isinstance(self.b, Constant) and self.b.value == 1:
            return self.a
        # optional: turn ^-1 in fraction
        # elif isinstance(self.b, Constant) and self.b.value == -1:
        #     return Frac(1, self.a)
        else:
            return self

    def __repr__(self):
        return f"{self.a}^({self.b})"

    def latex(self):
        return str(self.a.latex())+"^{"+str(self.b.latex())+"}"


class Sqrt(Pow):
    def __init__(self, a):
        """Power Function a**b"""
        super().__init__(self.a, 0.5)

    def calc(self, x):
        """if type(x) == dict:
            return self.a.calc(x[self.ax]) * self.b.calc(x[self.bx])
        elif is_number(x):
            return self.a.calc(x) * self.b.calc(x)"""
        return np.sqrt(self.a.calc(x))

    def __repr__(self):
        return f"sqrt({self.a})"

    def latex(self):
        return r"\sqrt{" + str(self.a.latex()) + "}"


class Ln(MathFunction):
    def __init__(self, a):
        """Function of the Form a*exp(bx)"""
        super().__init__()
        if isinstance(a, MathFunction):
            self.a = a
        else:
            self.a = Constant(a)

    def calc(self, x):
        return np.log(self.a.calc(x))

    def derivate(self, var):
        """Derivative of Ln: d/dx[ln(a(x))] = a'(x) * 1/a(x)"""
        return Prod(Frac(Constant(1), self.a), self.a.derivate(var))

    def simplify(self):
        self.a = self.a.simplify()
        # ln(1) = 0
        if isinstance(self.a, Constant) and self.a.value == 1:
            return Constant(0)
        elif isinstance(self.a, Exp):
            return self.a.a
        else:
            return self

    def __repr__(self):
        return f"ln({self.a})"

    def latex(self):
        return r"\ln("+str(self.a.latex())+")"


class Exp(MathFunction):
    def __init__(self, a):
        """Function of the Form a*exp(bx)"""
        super().__init__()
        if isinstance(a, MathFunction):
            self.a = a
        else:
            self.a = Constant(a)

    def calc(self, x):
        return np.exp(self.a.calc(x))

    def derivate(self, var):
        """Derivative of Exp: d/dx[exp(a(x))] = a'(x) * exp(a(x))"""
        return Prod(self.a.derivate(var), self)

    def simplify(self):
        self.a = self.a.simplify()
        # exp(0) = 1, exp(ln(x))=x
        if not self.a:
            return Constant(1)
        elif isinstance(self.a, Ln):
            return self.a.a
        else:
            return self

    def __repr__(self):
        return f"exp({self.a})"

    def latex(self):
        return r"\exp("+str(self.a.latex())+")"


class Sin(MathFunction):
    def __init__(self, a):
        """Function of the Form a*exp(bx)"""
        super().__init__()
        if isinstance(a, MathFunction):
            self.a = a
        else:
            self.a = Constant(a)

    def calc(self, x):
        return np.sin(self.a.calc(x))

    def derivate(self, var):
        """Derivative of cos(x): d/dxsin(a(x)) = cos(a(x))*a'(x)"""
        return Prod(Cos(self.a), self.a.derivate(var))

    def simplify(self):
        self.a = self.a.simplify()
        return self

    def __repr__(self):
        return f"sin({self.a})"

    def latex(self):
        return r"\sin("+str(self.a.latex())+")"


class Cos(MathFunction):
    def __init__(self, a):
        """Function of the Form a*exp(bx)"""
        super().__init__()
        if isinstance(a, MathFunction):
            self.a = a
        else:
            self.a = Constant(a)

    def calc(self, x):
        return np.cos(self.a.calc(x))

    def derivate(self, var):
        """Derivative of cos(x): d/dxcos(a(x)) = -sin(a(x))*a'(x)"""
        return Prod(Prod(-1, Sin(self.a)), self.a.derivate(var))

    def simplify(self):
        self.a = self.a.simplify()
        return self

    def __repr__(self):
        return f"cos({self.a})"

    def latex(self):
        return r"\cos("+str(self.a.latex())+")"


class Tan(MathFunction):
    def __init__(self, a):
        """Function of the Form a*exp(bx)"""
        super().__init__()
        if isinstance(a, MathFunction):
            self.a = a
        else:
            self.a = Constant(a)

    def calc(self, x):
        return np.tan(self.a.calc(x))

    def derivate(self, var):
        """Derivative of tan(x): d/dxtan(a(x)) = cos(a(x))^-2*a'(x)"""
        return Frac(self.a.derivate(var), Pow(Cos(self.a), 2))

    def simplify(self):
        self.a = self.a.simplify()
        return self

    def __repr__(self):
        return f"tan({self.a})"

    def latex(self):
        return r"\tan("+str(self.a.latex())+")"


class Arcsin(MathFunction):
    def __init__(self, a):
        """Function of the Form a*exp(bx)"""
        super().__init__()
        if isinstance(a, MathFunction):
            self.a = a
        else:
            self.a = Constant(a)

    def calc(self, x):
        return np.arcsin(self.a.calc(x))

    def derivate(self, var):
        """Derivative of cos(x): d/dxsin(a(x)) = cos(a(x))*a'(x)"""
        return Frac(self.a.derivate(var), Sqrt(Sub(1, Pow(self.a, 2))))

    def simplify(self):
        self.a = self.a.simplify()
        return self

    def __repr__(self):
        return f"arcsin({self.a})"

    def latex(self):
        return r"\arcsin("+str(self.a.latex())+")"


class Arccos(MathFunction):
    def __init__(self, a):
        """Function of the Form a*exp(bx)"""
        super().__init__()
        if isinstance(a, MathFunction):
            self.a = a
        else:
            self.a = Constant(a)

    def calc(self, x):
        return np.arccos(self.a.calc(x))

    def derivate(self, var):
        """Derivative of cos(x): d/dxsin(a(x)) = cos(a(x))*a'(x)"""
        return Frac(Prod(-1, self.a.derivate(var)), Sqrt(Sub(1, Pow(self.a, 2))))

    def simplify(self):
        self.a = self.a.simplify()
        return self

    def __repr__(self):
        return f"arccos({self.a})"

    def latex(self):
        return r"\arccos("+str(self.a.latex())+")"


class Arctan(MathFunction):
    def __init__(self, a):
        """Function of the Form a*exp(bx)"""
        super().__init__()
        if isinstance(a, MathFunction):
            self.a = a
        else:
            self.a = Constant(a)

    def calc(self, x):
        return np.arctan(self.a.calc(x))

    def derivate(self, var):
        """Derivative of cos(x): d/dxsin(a(x)) = cos(a(x))*a'(x)"""
        return Frac(1, Sum(1, Pow(self.a, 2)))

    def simplify(self):
        self.a = self.a.simplify()
        return self

    def __repr__(self):
        return f"arccos({self.a})"

    def latex(self):
        return r"\arccos("+str(self.a.latex())+")"


def polynom(coeffs, var: Variable):
    """Returns a MathFunction. This method only constructs a polynomial function for you,
    it does NOT return a 'Polynom' instance.
    coeffs: 1-dim iterable:
    pol = sum(coeffs[i] * x**i"""
    pol = Prod(coeffs[0], 1)
    for i in range(1, len(coeffs)):
        pol = Sum(Prod(coeffs[i], Pow(var, i)), pol)
    return pol.simplify()


def taylor(f: MathFunction, var: Variable, var_0, order: int):
    """Returns the Taylor Series of f(x)
    f can not be dependent of multiple var"""
    tay = f.calc(var_0)
    for i in range(1, order):
        # derivate i times:
        df = f
        for j in range(0, i):
            df = df.d(var)
        print(i, df)
        power = Pow(Sub(var, var_0), i)
        tay = Sum(tay, Prod(Frac(df.calc(var_0), factorial(i)), power))
    return tay.simplify()


x = V("x")
y = V("y")
z = V("z")


f = Exp(x) + 1
print(f)
# f = Exp(x) + Arctan(x + Constant(77)) ** (Constant(5)/x)
# print(f.derivate(x))
