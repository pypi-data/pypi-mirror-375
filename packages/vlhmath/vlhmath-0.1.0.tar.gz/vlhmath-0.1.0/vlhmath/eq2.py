import sympy as sp
import re

class Eq2:
    equation_str = None
    x = sp.Symbol('x')

    @classmethod
    def setEquation(cls, equation: str):
        cls.equation_str = equation.replace("^", "**")
        cls.equation_str = cls._insert_multiplication(cls.equation_str)
        left, right = cls.equation_str.split("=")
        expr = sp.sympify(left) - sp.sympify(right)
        cls.expr = sp.expand(expr)
        cls.a, cls.b, cls.c = sp.Poly(cls.expr, cls.x).all_coeffs()

    @staticmethod
    def _insert_multiplication(eq: str):
        eq = re.sub(r'(\d)(x)', r'\1*\2', eq)
        return eq

    @classmethod
    def findDiscr(cls):
        if cls.equation_str is None:
            raise ValueError("Set the equation first with Eq2.setEquation('...')")
        return cls.b**2 - 4*cls.a*cls.c

    @classmethod
    def findRoots(cls):
        if cls.equation_str is None:
            raise ValueError("Set the equation first with Eq2.setEquation('...')")
        roots = sp.solve(cls.expr, cls.x)
        # Форматиране на изхода като x1 = ..., x2 = ...
        output = ""
        for i, r in enumerate(roots, 1):
            if i < 2: #Ако е на X1
                output += f"x{i} = {r}; "
            else: #Ако е на X2
                output += f"x{i} = {r}"

        return output.strip()

    @classmethod
    def shEq(cls):
        if cls.equation_str is None:
            raise ValueError("Set the equation first with Eq2.setEquation('...')")
        roots = sp.solve(cls.expr, cls.x)
        def format_root(r):
            if r < 0:
                return f"+ {abs(r)}"
            else:
                return f"- {r}"
        if len(roots) == 2:
            return f"(x {format_root(roots[0])})(x {format_root(roots[1])}) = 0"
        elif len(roots) == 1:
            return f"(x {format_root(roots[0])})^2 = 0"
        else:
            return cls.expr_to_str(cls.expr) + " = 0"

    @classmethod
    def simpleEq(cls):
        if cls.equation_str is None:
            raise ValueError("Set the equation first with Eq2.setEquation('...')")
        simplified = sp.simplify(cls.expr)
        return cls.expr_to_str(simplified)

    @staticmethod
    def expr_to_str(expr):
        # Преобразува ** в ^ и маха *
        s = str(expr)
        s = s.replace("**", "^")
        s = s.replace("*", "")
        return s
