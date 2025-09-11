import sympy as sp
import re

class Eq4:
    equation_str = None
    x = sp.Symbol('x')

    @classmethod
    def setEquation(cls, equation: str):
        cls.equation_str = equation.replace("^", "**")
        cls.equation_str = cls._insert_multiplication(cls.equation_str)
        left, right = cls.equation_str.split("=")
        expr = sp.sympify(left) - sp.sympify(right)
        cls.expr = sp.expand(expr)

    @staticmethod
    def _insert_multiplication(eq: str):
        # добавя * между число и x
        eq = re.sub(r'(\d)(x)', r'\1*\2', eq)
        return eq

    @classmethod
    def simpleEq(cls):
        if cls.equation_str is None:
            raise ValueError("Set the equation first with Eq4.setEquation('...')")
        simplified = sp.simplify(cls.expr)
        return cls.expr_to_str(simplified)

    @classmethod
    def findRoots(cls):
        if cls.equation_str is None:
            raise ValueError("Set the equation first with Eq4.setEquation('...')")
        roots = sp.solve(cls.expr, cls.x)
        output = ""
        for i, r in enumerate(roots, 1):
            if i < 4:
                output += f"x{i} = {cls.format_root(r)}; "
            else:
                output += f"x{i} = {cls.format_root(r)}"
        return output.strip()

    @classmethod
    def shEq(cls):
        if cls.equation_str is None:
            raise ValueError("Set the equation first with Eq4.setEquation('...')")
        roots = sp.solve(cls.expr, cls.x)
        factors = []
        for r in roots:
            factors.append(f"(x {cls.format_factor(r)})")
        return "".join(factors) + " = 0"

    @staticmethod
    def format_root(r):
        r = sp.simplify(r)
        # Ако е корен (sqrt)
        if isinstance(r, sp.Pow) and r.exp == sp.Rational(1,2):
            return f"√{r.base}"
        # Ако е отрицателен корен
        if isinstance(r, sp.Mul):
            coeff, term = r.as_coeff_Mul()
            if coeff == -1 and isinstance(term, sp.Pow) and term.exp == sp.Rational(1,2):
                return f"-√{term.base}"
        # Ако е отрицателно число
        if r.is_number and r.is_negative:
            return f"-{abs(r)}"
        return str(r)

    @staticmethod
    def format_factor(r):
        r = sp.simplify(r)
        # Ако е положителен корен
        if isinstance(r, sp.Pow) and r.exp == sp.Rational(1,2):
            return f"- √{r.base}"
        # Ако е отрицателен корен
        if isinstance(r, sp.Mul):
            coeff, term = r.as_coeff_Mul()
            if coeff == -1 and isinstance(term, sp.Pow) and term.exp == sp.Rational(1,2):
                return f"+ √{term.base}"
        # Число
        if r.is_negative:
            return f"+ {abs(r)}"
        return f"- {r}"


    @staticmethod
    def expr_to_str(expr):
        # Преобразува ** в ^ и маха *
        s = str(expr)
        s = s.replace("**", "^")
        s = s.replace("*", "")
        return s
