import sympy as sp
# Import the C++ compiled module. The name of the module will be 'iLaplace_core'.
try:
    import iLaplace_core as core
except ImportError:
    raise ImportError("The C++ core library 'iLaplace_core' is not found. "
                      "Please ensure you have built the C++ module correctly by running 'pip install .' "
                      "in the project's root directory.")

def i_laplace(laplace_expression, t_value):
    """
    Computes the numerical inverse Laplace transform of a SymPy expression using C++ core.

    Args:
        laplace_expression (sympy.Expr): The Laplace domain expression (must be convertible to string
                                         format parsable by SymEngine).
        t_value (float): The time at which to evaluate the inverse transform.

    Returns:
        float: The numerical result of the inverse Laplace transform.
    """
    if not isinstance(t_value, (int, float)):
        raise TypeError("t_value must be a number.")

    # Convert the SymPy expression to a string representation that SymEngine can parse.
    # This requires careful handling of SymPy syntax to be compatible with SymEngine.
    # For example, sympy.log is symengine.log, sympy.exp is symengine.exp, etc.
    # The default string representation usually works well for common functions.
    expr_str = str(laplace_expression)
    
    # Call the C++ function
    result = core.compute_inverse_laplace_numerical(expr_str, float(t_value))
    
    return result