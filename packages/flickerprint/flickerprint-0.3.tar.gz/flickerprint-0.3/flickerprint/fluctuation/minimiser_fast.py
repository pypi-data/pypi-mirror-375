#!/usr/bin/env python

"""
New workflow for the faster spectrum fitting code.
==================================================

As the constant values are precalculated, the spectrum fitting needs to work slightly differently.
"""

from collections import namedtuple
from time import time
from typing import Callable, Optional

import numpy as np
from scipy.optimize import minimize

FittingResult = namedtuple(
    "FittingResult", ["sigma_log", "kappa_log", "fitting_error", "time"]
)


def fit_spectrum(
    minimisation_function: Callable, n_starting_points: int = 18, n_best_points: int = 3
) -> Optional[FittingResult]:
    """
    Run the minimisation to find the best fit to the spectrum.

    This performs a grid scan with ``n_best_points`` on each side and then runs an ``L-BFGS`` minimizer on the
    ``n_best_points`` and returns the best result from among these.
    See SpectrumFitterBuilder.create_fitting_function for how to create the minimisation_function.

    Returns ``None`` if all of the minimisers fail. This typically occurs when the minimization function returns
    NaN.
    """
    start = time()
    starting_points = grid_scan_points(
        minimisation_function, n_starting_points, n_best_points
    )

    best_fit_value = np.inf
    parameters = None

    for starting_point in starting_points:
        x0 = starting_point[1:]
        minimiser_result = minimize(
            minimisation_function,
            x0,
            method="L-BFGS-B",
            # options={"ftol": 1e-8, "gtol": 1e-16, "maxiter": 100},
        )

        if minimiser_result["fun"] < best_fit_value:
            best_fit_value = minimiser_result["fun"]
            parameters = minimiser_result["x"]

    end = time()
    time_taken = end - start

    if parameters is None:
        return None

    return FittingResult(parameters[0], parameters[1], best_fit_value, time_taken)


def grid_scan_points(
    minimisation_function: Callable, n_points: int = 18, n_best_points: int = 3
):
    """
    Looks for the best starting point in ``n_points`` × ``n_points`` array and return the ``n_best_points`` options.

    Returns an array of shape (``n_best_points`` × 3) with the (fitting_error, sigma, kappa) values
    """
    # TODO: Tweak the starting values for sigma and kappa?
    log_sigma_values = np.linspace(-8, 2.5, n_points)
    log_kappa_values = np.linspace(-2, 2.5, n_points)

    ss, kk = np.meshgrid(log_sigma_values, log_kappa_values, indexing="ij")
    value_array = np.stack([ss, kk])
    fitting_error_array = np.apply_along_axis(
        minimisation_function, axis=0, arr=value_array
    )

    # Trick to get the index of the ``k`` lowest elements, note they're not guaranteed to be ordered
    # This indexes into the flattened array, so we use this for the best sigma and kappa values
    best_indicies = np.argpartition(fitting_error_array, n_best_points, axis=None)[
        :n_best_points
    ]

    best_sigma = ss.ravel()[best_indicies]
    best_kappa = kk.ravel()[best_indicies]
    best_cost = fitting_error_array.ravel()[best_indicies]

    summary = np.stack([best_cost, best_sigma, best_kappa]).T
    return summary
