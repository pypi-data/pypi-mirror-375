#include <iostream>
#include <string>
#include <vector>
#include <cmath>
#include <complex>
#include <iomanip>
#include <limits>
#include <stdexcept>
#include <map>

// SymEngine includes
#include <symengine/parser.h>
#include <symengine/eval.h>
#include <symengine/expression.h>
#include <symengine/real_double.h>
#include <symengine/complex_double.h> // For complex number evaluation
#include <symengine/symbol.h>
#include <symengine/subs.h> // For substitution

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;
using namespace SymEngine;

// Helper function to evaluate a SymEngine expression with complex number substitution
// This is a crucial part for Talbot's method.
std::complex<long double> evaluate_complex(const RCP<const Basic>& expr, const Symbol* s_sym, const std::complex<long double>& s_val) {
    std::map<RCP<const Basic>, RCP<const Basic>> substitutions;
    // SymEngine's eval_complex_double expects a complex_double object.
    // We need to create one from our long double complex number.
    substitutions[s_sym] = SymEngine::complex_double(s_val.real(), s_val.imag());
    
    // Evaluate the expression with the substituted complex value.
    // Note: This might require a more advanced evaluation strategy for complex functions
    // if SymEngine's default complex evaluation is limited.
    RCP<const Basic> substituted_expr = expr->subs(substitutions);
    
    // Attempt to evaluate the substituted expression as a complex double.
    // This can throw exceptions if evaluation is not possible or if the expression
    // contains functions not supported by eval_complex_double.
    return SymEngine::eval_complex_double(substituted_expr);
}

// A robust numerical inverse Laplace transform function using Talbot's method.
long double compute_talbot(const std::string& laplace_expr_str, long double t, int N = 32) {
    if (t <= 0) {
        return 0.0L;
    }

    // Parse the expression using SymEngine
    RCP<const Basic> laplace_expr;
    try {
        laplace_expr = SymEngine::parse_expression(laplace_expr_str);
    } catch (const std::exception& e) {
        throw std::runtime_error("Error parsing expression: " + std::string(e.what()));
    }

    // Create a symbol 's' for substitution
    auto s_symbol = SymEngine::symbol("s");

    long double result = 0.0L;

    for (int k = 1; k < N; ++k) {
        long double theta = M_PI * (long double)k / N;
        // Calculate the complex value s_k for Talbot's method
        std::complex<long double> s_k = -theta / t * std::complex<long double>(std::sin(theta), std::cos(theta));

        std::complex<long double> F_s_k_complex;
        try {
            F_s_k_complex = evaluate_complex(laplace_expr, s_symbol.get(), s_k);
        } catch (const std::exception& e) {
            std::cerr << "Error evaluating expression at s=" << s_k << ": " << e.what() << std::endl;
            // If evaluation fails for a point, we might skip it or throw an error.
            // For robustness, let's try to continue with other points.
            continue; 
        }

        // The formula for Talbot's method involves integrating exp(s*t)*F(s) along a contour.
        // For this discrete approximation, we sum: 2 * Re(exp(s_k * t) * F(s_k))
        result += 2.0L * (long double)std::real(std::exp(std::complex<long double>(0.0L, theta)) * F_s_k_complex);
    }
    
    // The final result is obtained by scaling the sum.
    result = result * M_PI / (N * t);
    
    // If the expression is purely real and t is small, sometimes a direct term evaluation is needed.
    // For example, a simple function like 1/s at t=0 is 1.
    // This needs careful handling. For now, we rely on the summation.
    
    return result;
}

// Main function called from Python
long double compute_inverse_laplace_numerical(const std::string& laplace_expr_str, long double t_val) {
    // Use the Talbot method for numerical computation
    return compute_talbot(laplace_expr_str, t_val);
}

// Pybind11 binding module
PYBIND11_MODULE(iLaplace_core, m) {
    m.doc() = "A C++ core for numerical inverse Laplace transform calculations using SymEngine and Talbot's method.";
    m.def("compute_inverse_laplace_numerical", &compute_inverse_laplace_numerical, "Computes the numerical inverse Laplace transform.");
}