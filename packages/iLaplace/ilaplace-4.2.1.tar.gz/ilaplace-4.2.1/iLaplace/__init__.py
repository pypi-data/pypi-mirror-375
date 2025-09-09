import sympy as sp
import mpmath
import math
from functools import lru_cache
from multiprocessing import Pool, cpu_count

t, s = sp.symbols('t s', real=True)

@lru_cache(maxsize=None)
def _get_lambdified_func(F):
    return sp.lambdify(s, F, 'mpmath')

def inverse_laplace(F, t_val):
    if t_val <= 0:
        return 0.0
    F_func = _get_lambdified_func(F)
    return float(mpmath.invertlaplace(F_func, t_val, method='talbot'))

def inverse_laplace_fu(F):
  F_t = sp.inverse_laplace_transform(F,s,t)
  return(F_t)

class iLaplace:
    def __init__(self):
        self.inverse_laplace = inverse_laplace
        self.inverse_laplace_fu = inverse_laplace_fu

Fu = iLaplace()

__all__ = ['inverse_laplace', 'inverse_laplace_fu', 'Fu']