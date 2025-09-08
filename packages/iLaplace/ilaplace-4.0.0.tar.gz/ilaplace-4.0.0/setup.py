from setuptools import setup, find_packages
from pybind11.setup_helpers import Pybind11Extension, build_ext
import os
import platform

def find_symengine_paths():
    """
    Finds the SymEngine include and library directories.
    Searches standard paths and then the SYMENGE_ROOT environment variable.
    """
    symengine_root = os.environ.get('SYMENGE_ROOT')
    
    if platform.system() == "Windows":
        # Add common Windows paths here if you know them, e.g., for conda or vcpkg
        symengine_paths = []
    else:
        symengine_paths = [
            '/usr/local',
            '/usr',
            '/opt/homebrew',
            os.path.expanduser('~/.local'),
        ]

    for p in symengine_paths:
        include_dir = os.path.join(p, 'include')
        lib_dir = os.path.join(p, 'lib')
        if os.path.exists(os.path.join(include_dir, 'symengine')):
            print(f"SymEngine found in standard path: {p}")
            return include_dir, lib_dir

    if symengine_root:
        include_dir = os.path.join(symengine_root, 'include')
        lib_dir = os.path.join(symengine_root, 'lib')
        if os.path.exists(os.path.join(include_dir, 'symengine')):
            print(f"SymEngine found via SYMENGE_ROOT: {symengine_root}")
            return include_dir, lib_dir

    raise RuntimeError("SymEngine not found. Please set the SYMENGE_ROOT environment variable "
                       "to the installation path of SymEngine (e.g., /usr/local).")
try:
    symengine_include_dir, symengine_lib_dir = find_symengine_paths()
except RuntimeError as e:
    print(e)
    symengine_include_dir = None
    symengine_lib_dir = None

ext_modules = [
    Pybind11Extension(
        "iLaplace_core",
        ["src/iLaplace_core.cpp"],
        cxx_std=17,
        include_dirs=[symengine_include_dir],
        library_dirs=[symengine_lib_dir],
        libraries=["symengine"],
    ),
]

setup(
    name="iLaplace",
    version="4.0.0",
    author="Mohammad Hossein Rostami",
    author_email="MHRo.R84@Gmail.com",
    description="A Python library for high-precision numerical inverse Laplace transform using C++ (SymEngine) and Symbolic (SymPy).",
    long_description=open('README.md', encoding='utf-8').read() if os.path.exists('README.md') else "",
    long_description_content_type='text/markdown',
    packages=find_packages(),
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    install_requires=[
        "sympy>=1.0",
        "pybind11>=2.0",
    ],
    zip_safe=False,
    keywords=['laplace', 'inverse laplace', 'numerical', 'symbolic', 'python', 'c++', 'symengine', 'sympy', 'high precision'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
)