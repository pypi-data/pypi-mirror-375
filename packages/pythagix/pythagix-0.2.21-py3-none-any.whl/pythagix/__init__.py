from .numbering import gcd, lcm, compress_0, get_factors, prime_factorization, nCr
from .prime import is_prime, nth_prime, filter_primes
from .figurates import triangle_number
from .ratio import simplify_ratio, is_equivalent
from .stat import mean, median, mode, std_dev, variance, pstd_dev, pvariance, product

__all__ = (
    # Numbers
    "gcd",
    "get_factors",
    "lcm",
    "compress_0",
    "prime_factorization",
    "nCr",
    # Primes
    "is_prime",
    "nth_prime",
    "filter_primes",
    # Figurates
    "triangle_number",
    # Ratios
    "simplify_ratio",
    "is_equivalent",
    # Statistics
    "mean",
    "median",
    "mode",
    "std_dev",
    "variance",
    "pvariance",
    "pstd_dev",
    "product",
)
