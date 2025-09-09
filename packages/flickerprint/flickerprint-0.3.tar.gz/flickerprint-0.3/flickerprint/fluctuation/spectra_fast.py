#!/usr/bin/env python

r"""
Faster version of the spectrum fitting code
===========================================

Due to the need to precalculate the constant values before the fitting, this doesn't fit into the old workflow
and so it has been moved into a separate file.

 We want to minimise the function

 F(\sigma_bar, \kappa, q) = sum_{l=q}^{q_max} f_ql kappa_bar

 f_ql(\sigma_bar, kappa, q) = \frac{N_ql}{(l-1)(l+2)[l(l+1) - \sigma_bar]}

We decompose this into fractions

 f_ql = \frac{A(q, l)}{B(l) + C(l) \sigma_bar}, where,

   - A(q, l) = N_ql
   - B(l) = l(l+1)(l-1)(l+2)
   - C(l) = (l-1)(l+2)
"""

from typing import Callable

import numpy as np
from scipy.special import factorial, lpmv


class SpectrumFitterBuilder:
    """
    This class contains the precomputed values used in the theoretical spectrum calculation.
    """

    def __init__(self, q_max: int = 15, l_max: int = 60):
        self.a_ql = self._get_numerator_factor(q_max, l_max)
        self.b_l = self._get_constant_l_terms(l_max)
        self.c_l = self._get_base_l_terms(l_max)

    def get_spectra(self, sigma_bar: float, kappa_bar: float):
        """Calculate the given theoretical spectrum for the given σ and κ."""
        denominator = kappa_bar * (self.b_l + self.c_l * sigma_bar)
        out = self.a_ql / denominator
        return out.sum(axis=1)

    def create_fitting_function(
        self, spectrum_experimental: np.ndarray
    ) -> Callable[[(float, float)], float]:
        """Create a function that returns the error between the experimental and theoretical spectrum."""

        def fitting_error(fitting_params: (float, float)):
            linear_values = 10**fitting_params
            sigma_bar, kappa_bar = linear_values
            spectrum_theory = self.get_spectra(sigma_bar, kappa_bar)

            relative_error = np.log10(np.abs(spectrum_theory / spectrum_experimental))
            return np.sum(relative_error**2)

        return fitting_error

    @classmethod
    def _get_constant_l_terms(cls, l_max: int = 60):
        """The constant terms on the denominator, given by B(l) above."""
        l = np.arange(2, l_max + 1)
        return l * (l + 1) * (l - 1) * (l + 2)

    @classmethod
    def _get_base_l_terms(cls, l_max: int = 60):
        l = np.arange(2, l_max + 1)
        return (l - 1) * (l + 2)

    @classmethod
    def _get_numerator_factor(cls, q_max: int = 15, l_max: int = 60) -> np.ndarray:
        """
        Returns an array of the A_lq terms as above. 

        This doesn't depend on the physical properties and so can be cached.

        Returns an array of shape
            (2 <= l <= L_MAX, l <= Q <= Q_MAX)
        """
        q_vector = np.arange(2, q_max + 1)
        l_vector = np.arange(2, l_max + 1)

        return _numerator_factor(q_vector, l_vector)


def _numerator_factor(q_vec: np.ndarray, l_vec: np.ndarray):
    ll, qq = np.meshgrid(l_vec, q_vec, indexing="ij")
    valid = ll >= qq

    # Only the terms for which l - q are even are non-zero (odd function otherwise)
    even_terms = (ll + qq) % 2 == 0
    valid = np.logical_and(valid, even_terms)

    def numerator(l, q):
        return _norm_vec(l, q) * lpmv(q, l, 0) ** 2

    out = np.zeros_like(valid, dtype=float)
    out[valid] = numerator(ll[valid], qq[valid])

    return out.T


def _norm_vec(l, q):
    """Squared normalisation used in Häckl (doesn't break with numpy)"""
    return (2.0 * l + 1) / (4 * np.pi) * factorial(l - q) / factorial(l + q)


def calculate_durbin_watson(
    experimental_spectrum: np.ndarray, best_fit_spectrum: np.ndarray
):
    residuals = np.log10(experimental_spectrum / best_fit_spectrum)
    durbin_watson_stat = np.sum(np.square(residuals[1:] - residuals[:1])) / np.sum(
        np.square(residuals)
    )
    return durbin_watson_stat
