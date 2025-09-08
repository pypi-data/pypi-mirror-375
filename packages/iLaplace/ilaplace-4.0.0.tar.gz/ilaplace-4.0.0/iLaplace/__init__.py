from .iLaplace_binding import i_laplace
from . import Fu

__all__ = ['i_laplace', 'Fu']

#ive add a check here to ensure the C++ core if built or not
try:
    import iLaplace_core
except ImportError:
    print("Warning: The C++ core library 'iLaplace_core' could not be imported.")
    print("Please ensure you have built the library by running 'pip install .' in the project root.")