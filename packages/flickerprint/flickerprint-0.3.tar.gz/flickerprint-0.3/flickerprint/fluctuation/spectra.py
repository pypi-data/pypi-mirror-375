#!/usr/bin/env python

""" Theoretical fluctuation spectra for granules.

Spectrum Fitting
================

Given an experimental spectrum find the best fit values of surface tension and bending
rigidity.

"""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import MaxNLocator
from scipy.constants import Boltzmann as kB
from scipy.optimize import basinhopping, minimize, least_squares
from scipy.special import factorial, lpmv

import flickerprint.tools.plot_tools as pt
from flickerprint.common.configuration import config


@lru_cache(maxsize=None)
def numerator(l, q):
    """ Calculate the numerator terms for spectrum, while caching the results. """
    return _norm(l, q) * lpmv(q, l, 0) ** 2


def _norm(l, q):
    """ Squared normalisation used in Häckl """
    if q > l:
        raise ValueError("Invalid order used in _norm()")
    return (2.0 * l + 1) / (4 * np.pi) * factorial(l - q) / factorial(l + q)


@dataclass
class Result:
    """ Storage for the fitting results. """

    sigma_bar: float
    kappa_scale: float

    surface_tension_defined: float


class _Fitting:
    def __init__(self, fourier_terms: pd.DataFrame, frame_info):
        """Base class for spectrum fitting.

        He were use the L-BFGS-B fitting, while this is an accurate method that works
        nicley for simulations, it tends to behave poorly when we consider physical
        granules where the surface tension may be poorly defined.
        """
        self.pass_rate, self.pass_count = self._validate_fourier_terms(fourier_terms)
        granule_id = fourier_terms["granule_id"].iloc[0]

        self.pixel_size = frame_info["pixel_size"]
        self.input_path = Path(frame_info["input_path"])
        # self.mean_radius = fourier_terms["mean_radius"]

        # Add additional terms required for fitting
        fourier_terms["mag_abs"] = np.abs(fourier_terms["magnitude"])
        fourier_terms["mag_squared"] = fourier_terms["mag_abs"] ** 2

        # Create a DF of the time averaged terms
        # This is the experimental spectrum that we compare against
        # We have to do the latter term using λ as otherwise it uses a cython version
        # without complex support.
        self.mag_df = fourier_terms.groupby(by="order").agg(
            mag_squ_mean=("mag_squared", "mean"),
            mag_mean=("magnitude", lambda x: np.mean(x)),
        )
        self.mag_df.reset_index(inplace=True)

        # Supplementary columns used in Pécréaux 2004
        # These terms differ from the definition in the paper as we take
        # |〈mag〉|**2 rather than 〈|mag|〉**2
        self.mag_df["fixed_squ"] = np.abs(self.mag_df["mag_mean"]) ** 2
        self.mag_df["fluct_squ"] = (
            self.mag_df["mag_squ_mean"] - self.mag_df["fixed_squ"]
        )

        # Choose the correct fitting spectrum
        exp_spectrum = config("spectrum_fitting", "experimental_spectrum")
        if exp_spectrum == "corrected":
            self.mag_df["experiment_spectrum"] = self.mag_df["fluct_squ"]
        elif exp_spectrum == "direct":
            self.mag_df["experiment_spectrum"] = self.mag_df["mag_squ_mean"]

        # Name unique to this fitting
        self.save_dir = Path("fitting/spectra")
        self.save_name = (
            Path(frame_info["input_path"]).stem + f"--G{granule_id:02d}.png"
        )
        self.fitting_parameters = ("sigma_bar", "kappa_scale")

        self.best_fit_vals = None
        self.fit_para_err = None
        self.original_fit = None

    def get_best_fit(self, x0=None):
        """Return a results tuple with the best fit parameters.

        In this simple implementation we use a L-BFGS minimiser however, this tends to
        perform badly when there is a neglible surface tension contribution.
        """

        if x0 is None:
            x0 = np.ones(len(self.fitting_parameters), dtype=float)
        minimiser_result = minimize(
            self._get_fitting_error,
            x0,
            method="L-BFGS-B",
            bounds=((1e-6, None), (1e-6, None)),
        )

        self.best_fit_vals = minimiser_result["x"]
        self.mag_df["best_fit"] = self._fit_func(self.best_fit_vals)

        self.fitting_error = minimiser_result["fun"]

        return minimiser_result

    def _get_fitting_error(self, fitting_vals):
        """Return the fitting error between the experimental spectrum and the theoretical
        spectrum for the given parameters.

        A simple RMS error favoured the first order, we therefore use a multiplicative
        error that treats all terms equally.
        """
        spectrum_theory = self._fit_func(fitting_vals)
        spectrum_experiment = self.mag_df["experiment_spectrum"]

        # Return a overly large value if the theory spectrum is negative
        if np.any(np.isnan(spectrum_theory)) or np.any(np.isinf(spectrum_theory)):
            raise ValueError
        #if np.any(spectrum_theory < 0):
        #    return 1e9
        relative_error = np.abs(np.log10(np.abs(spectrum_theory / spectrum_experiment)))
        error = np.sum(relative_error ** 2)

        return error

    def _get_fitting_error_data(self,fitting_vals,data):
        """Return the fitting error between the any spectrum and the theoretical
        spectrum for the given parameters.

        A simple RMS error favoured the first order, we therefore use a multiplicative
        error that treats all terms equally.
        """
        spectrum_theory = self._fit_func(fitting_vals)
        spectrum_experiment = data

        # Return a overly large value if the theory spectrum is negative
        if np.any(np.isnan(spectrum_theory)) or np.any(np.isinf(spectrum_theory)):
            raise ValueError
        #if np.any(spectrum_theory < 0):
        #    return 1e9
        relative_error = np.log10(np.abs(spectrum_theory / spectrum_experiment))
        error = np.sum(relative_error ** 2)

        return error       

    def _get_residual(self, fitting_vals, order, experiment):
        """ get the residual between the experimantal and theoretical spectrum at one point """
        theory = self._spectrum(order, fitting_vals)
        if np.isnan(theory) or np.isinf(theory):
            raise ValueError
        #if theory < 0:
        #    return 1e9
        return np.log10(np.abs(theory / experiment))

    def _get_residuals(self, fitting_vals, orders, experiments):
        return np.array([self._get_residual(fitting_vals, order, experiment) for order,experiment in zip(orders,experiments)])

    @staticmethod
    def _residual_to_displacment(deltas,spectrum):
        return spectrum / ( 10. ** np.array(deltas))

    def _fit_func(self, fitting_vals):
        """ Give the theoretical spectrum for the give parameters. """
        orders = self.mag_df["order"]
        spectrum_theory = np.zeros(len(orders))

        for index_, order in enumerate(orders):
            spectrum_theory[index_] = self._spectrum(order, fitting_vals)

        return spectrum_theory

    @staticmethod
    def _spectrum(q, args, l_max=60):
        """ Return the value of the spectrum at the given order, q. """
        sigma_bar, kappa_scale = args

        val = 0
        for l in range(q, l_max + 1):
            numer = numerator(l, q)
            denom = (l - 1) * (l + 2) * (l * (l + 1) + sigma_bar) * kappa_scale
            val += numer / denom

        return val
    
    def _extreme_func(self,const):
        """ Give the theoretical spectrum for the give parameters in the case kappa and sigma related at hgh sigma. """
        orders = self.mag_df["order"]
        spectrum_theory = np.zeros(len(orders))

        for index_, order in enumerate(orders):
            spectrum_theory[index_] = self._extreme_spectrum(order, const)

        return spectrum_theory 

    @staticmethod
    def _extreme_spectrum(q, const, l_max=60):
        """ Return the value of the spectrum at the given order, q. """

        val = 0
        for l in range(q, l_max + 1):
            numer = numerator(l, q)
            denom = (l - 1) * (l + 2) * const
            val += numer / denom

        return val   

    def _extreme_kappa(self,const):
        """ Give the theoretical spectrum for the give parameters in the case kappa and sigma related at hgh sigma. """
        orders = self.mag_df["order"]
        spectrum_theory = np.zeros(len(orders))

        for index_, order in enumerate(orders):
            spectrum_theory[index_] = self._extreme_kappa_spectrum(order, const)

        return spectrum_theory 

    @staticmethod
    def _extreme_kappa_spectrum(q, const, l_max=60):
        """ Return the value of the spectrum at the given order, q. """

        val = 0
        for l in range(q, l_max + 1):
            numer = numerator(l, q)
            denom = (l - 1) * (l + 2) * l * (l+1) * const
            val += numer / denom

        return val  

    def plot(
        self, ax=None, fixed=True, mean_radius=None, outdir: Path = None, label=False
    ):
        """Create a plot of the spectrum.

        Parameters
        ----------

        ax: matplotlib.Axes
            If no ax is provided then create and save a plot, if it is given then simply
            add to this axis.
        """

        #plt.style.use(["seaborn-paper"])
        plt.rcParams["font.family"] = "serif"
        plt.rcParams["mathtext.fontset"] = "dejavuserif"
        # Record if have created the plot
        create_plot = ax is None
        if create_plot:
            fig, ax = pt.create_axes(1, axes_height=3)

        plot_fmt = dict(data=self.mag_df, mew=0.6, ms=4, lw=0.6)
        ax.plot("order", "fluct_squ", "ob", label="Fluct. only", **plot_fmt)
        if fixed:
            ax.plot("order", "fixed_squ", "+g", label="Fixed", **plot_fmt)
        else:
            ax.plot(
                "order", "mag_squ_mean", "1r", label="Total Perturbation", **plot_fmt
            )
        if self.best_fit_vals is not None:
            ax.plot("order", "best_fit", "-k", label="Best Fit", **plot_fmt)

            sigma_bar, kappa_scale = self.best_fit_vals
            # We can only provide physical values if a radius is provided
            if mean_radius is None or self.fit_para_err == None:
                title_str = (
                    f"sigma_bar = {sigma_bar:0.2f}, kappa_scale = {kappa_scale:0.2f}"
                )
            else:
                # Print the formatted values
                sigma, kappa_scale = self.physical_vals(mean_radius)
                sigma_err, kappa_err = self.physical_errors(mean_radius)
                sigma_si = pt.format_si(sigma)
                sigma_err_si = pt.format_si(sigma_err)
                title_str = f"σ = {sigma_si} ± {sigma_err_si} N/m, κ = {kappa_scale:0.2f} ± {kappa_err:0.2f} kT"# fitting = {self.fitting_error}"

            ax.set_title(title_str, fontsize=8)

        if label:
            annotation = (f"pass rate = {self.pass_rate:2.0%}",)
            pt.annotate_axis(ax, annotation, pos=(0.05, 0.05), fontsize=8)

        ax.legend(title="Spectrum", fancybox=False, fontsize=8)
        ax.set_yscale("log")
        ax.set_ylabel("Mean Perturbation Mag. Squ.")
        ax.set_xlabel("$q$")
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

        if create_plot:
            save_path = Path(self.save_dir) / self.save_name
            print(f"save_path = {save_path}")

            if outdir is not None:
                save_path = outdir / save_path

            pt.save_figure_and_trim(save_path.with_suffix(".png"))

    def plot_heatmap(
        self,
        ax=None,
        save_name: Path = "/tmp/heatmap.png",
        sigma_bars=None,
        kappa_scales=None,
        mean_radius = None
    ):
        """ Plot heatmap for the fitting quality. """

        create_plot = ax is None
        if create_plot:
            fig, axs = pt.create_axes(
                3,
                # axes_height=2.5,
                axes_height=6.5,
                col_wrap=3,
                sharex=False,
                sharey=False,
                aspect=1,
                # aspect=1.13
            )

        temperature = float(config("spectrum_fitting", "temperature")) + 273.15

        if sigma_bars is None:
            n_sigma = 60
            sigma_bars = np.logspace(1, 5, num=n_sigma)
            x_log = True
        else:
            n_sigma = len(sigma_bars)
            x_log = (sigma_bars.max() / sigma_bars.min()) > 25
            #print(f"alt_width = {sigma_bars.max() / sigma_bars.min()}")

        if kappa_scales is None:
            n_kappa = 60
            kappa_scales = np.logspace(-3, 1, num=n_kappa)
            y_log = True
        else:
            n_kappa = len(kappa_scales)
            y_log = (kappa_scales.max() / kappa_scales.min()) > 25

        rms_grid = np.zeros((n_kappa, n_sigma))
        sigma_grid, kappa_grid = np.meshgrid(sigma_bars, kappa_scales)

        for col_num, kappa_scale in enumerate(kappa_scales):
            for row_num, sigma_bar in enumerate(sigma_bars):
                rms_grid[col_num, row_num] = self._get_fitting_error(
                    (sigma_bar, kappa_scale)
                )

        rms_invert = np.log(rms_grid / rms_grid.min()) #so no log(0)
        # rms_invert = rms_grid - rms_grid.min()

        axs[0].pcolormesh(
            sigma_bars, kappa_scales, rms_grid, cmap="inferno_r", shading="nearest",
        )
        axs[1].pcolormesh(
            sigma_bars, kappa_scales, rms_invert, cmap="inferno_r", shading="nearest",
        )
        data = {"sigma_bars": sigma_bars, "kappa_scales": kappa_scales, "rms_grid": rms_grid, "rms_invert": rms_invert}

        min_error = np.min(rms_grid)
        min_args = np.unravel_index(np.argmin(rms_grid, axis=None), rms_grid.shape)
        sigma_bar_min = sigma_bars[min_args[1]]
        kappa_min = kappa_scales[min_args[0]]
        sigma_min = sigma_bar_min / mean_radius ** 2 * kappa_min * kB * temperature
        sigma_min_si = pt.format_si(sigma_min)

        axs[1].set_title(f"σ = {sigma_min_si}N/m, κ = {kappa_min:0.2f} kT fitting = {min_error:0.2f}", fontsize=8)
        axs[1].plot([sigma_bar_min],[kappa_min], "ro")

        plot_fmt = dict(data=self.mag_df, mew=0.6, ms=4, lw=0.6)
        axs[2].plot("order", "fluct_squ", "ob", label="Fluct. only", **plot_fmt)
        axs[2].plot("order", "best_fit", "-k", label="Best Fit", **plot_fmt)
        y = self._fit_func( (sigma_bar_min,kappa_min) )
        axs[2].plot(self.mag_df["order"],y,'r-')

        if self.original_fit != None :
            y = self._fit_func(self.original_fit)
            axs[2].plot(self.mag_df["order"],y,'b-')

        sigma_bar, kappa_scale = self.best_fit_vals
        sigma = sigma_bar / mean_radius ** 2 * kappa_scale * kB * temperature
        sigma_si = pt.format_si(sigma)

        axs[1].plot([sigma_bar],[kappa_scale], "ko")

        if self.fit_para_err != None:
            sigma_err, kappa_err = self.physical_errors(mean_radius)
            sigma_err_si = pt.format_si(sigma_err)
            title_str = f"σ = {sigma_si} +- {sigma_err_si} N/m, κ = {kappa_scale:0.2f} +- {kappa_err:0.2f} kT fitting = {self.fitting_error:0.2f}"
        else:
            title_str = f"σ = {sigma_si} N/m, κ = {kappa_scale:0.2f} kT fitting = {self.fitting_error:0.2f}"

        axs[2].set_title(title_str, fontsize=8)

        #line fit
        x = sigma_bars[int(len(sigma_bars)/2):]
        y = [1.8e2 / (sigma) for sigma in x]
        axs[1].plot(x,y,"b-")

        axs[0].contour(sigma_grid, kappa_grid, rms_grid, cmap="Blues_r")
        # axs[0].contour(sigma_grid, kappa_grid, rms_grid, cmap="Blues")
        labels = [f"({i})" for i in "ab"]
        label_colors = ["black", "white"]
        for label, color, ax in zip(labels, label_colors, axs):
            if x_log:
                ax.set_yscale("log")
            if y_log:
                ax.set_xscale("log")
            pt.annotate_axis(ax, label, color=color, fontsize=8)
        pt.set_labels(
            axs,
            ylabels="Bending Rigidity",
            xlabels="Reduced Surface Tension",
            fontsize=8,
        )

        if create_plot:
            pt.save(save_name)

    @staticmethod
    def _validate_fourier_terms(fourier_terms: pd.DataFrame):
        """Ensure that we have the required data for fitting and return the pass
        percentage for a granule."""
        n_granules = fourier_terms["granule_id"].nunique()
        if n_granules != 1:
            raise ValueError("Multiple granules_id given to _Fitting.")

        # We only need to consider a single order term as the results will be the same
        # for all of them
        try:
            filtered_terms = fourier_terms.query("order == 2")
            counts = filtered_terms["valid"].value_counts()
        except KeyError:
            return 0

        pass_count = counts[True] if True in counts else 0
        fail_count = counts[False] if False in counts else 0
        pass_rate = pass_count / (pass_count + fail_count)
        return pass_rate, pass_count

    def physical_vals(self, mean_radius):
        """ Return the best fit values for the fitting. """
        temperature = float(config("spectrum_fitting", "temperature")) + 273.15
        sigma_bar, kappa_scale = self.best_fit_vals
        sigma = sigma_bar / mean_radius ** 2 * kappa_scale * kB * temperature
        return sigma, kappa_scale

    def physical_errors(self,mean_radius):
        if self.fit_para_err == None:
            return None
        """ return the proper error sigma and kappa_scale. """
        sigma_bar, kappa_scale = self.best_fit_vals
        sigma, kappa_scale = self.physical_vals(mean_radius)
        sigma_bar_err, kappa_err = self.fit_para_err
        sigma_err = sigma * np.sqrt( (sigma_bar_err / sigma_bar) ** 2 + (kappa_err / kappa_scale) ** 2  )
        return sigma_err, kappa_err
    
    def durbin_watson_statistic(self, experimental_spectrum, best_fit_spectrum)->float:
        """Calculates the Durbin-Watson statistic to test correlation between residuals. Details on how it is calculated and uses can be found here: https://en.wikipedia.org/wiki/Durbin–Watson_statistic"""
        # Calculate the residuals (as a fraction of their original values)
        residuals = np.log10(np.array(experimental_spectrum)/np.array(best_fit_spectrum))
        # Calculate the Durbin-Watson statistic
        durbin_watson_stat = np.sum(np.square(residuals[1:]-residuals[:-1]))/np.sum(np.square(residuals))
        return durbin_watson_stat



class FittingLBFGS(_Fitting):
    """ Fitting for the granules using an additional step to calculate the error bars. """


class _FittingPlanar(_Fitting):
    """Fit the planar fluctuation spectrum.

    This is a much simpler spectrum to fit compared to the spherical case.
    Allowing us to compare the approximation and the separation of fixed and
    fluctuating terms.
    """

    @staticmethod
    def _spectrum(q, args):
        """ Return the value of the spectrum at the given order, q. """
        sigma_bar, kappa_scale = args

        denom = (q - 1) * (q + 2) * (q * (q + 1) + sigma_bar)
        val = 1.0 / denom / kappa_scale

        return val

 
class FittingLeastSquares(_Fitting):
    """ use lease square method, with scan initial guess, to fit spectra and get errors """

    def get_best_fit(self, x0=None):
        # generate initial guess
        n_kappa, n_sigma = 100, 100
        sigma_mid, kappa_mid  = 10e1,10e-1
        width = 1000000.0
        line_func = np.linspace if width <= 5 else np.geomspace
        sigma_bars = line_func(sigma_mid / width, sigma_mid * width, num=n_sigma)
        kappa_scales = line_func(kappa_mid / width, kappa_mid * width, num=n_kappa)                   
        rms_grid = np.zeros((n_kappa, n_sigma))
        sigma_grid, kappa_grid = np.meshgrid(sigma_bars, kappa_scales)

        for col_num, kappa_scale in enumerate(kappa_scales):
            for row_num, sigma_bar in enumerate(sigma_bars):
                rms_grid[col_num, row_num] = self._get_fitting_error(
                    (sigma_bar, kappa_scale)
                )
        min_args = np.unravel_index(np.argmin(rms_grid, axis=None), rms_grid.shape)
        initial_guess = np.array([sigma_bars[min_args[1]], kappa_scales[min_args[0]]])

        # least squares
        dataX = self.mag_df["order"]
        dataY = self.mag_df["experiment_spectrum"]

        res_lsq = least_squares(self._get_residuals,initial_guess,
            args = (dataX,dataY),
            diff_step = 0.01,
            bounds=([0.0, 0.0],[np.inf,np.inf])
            )   

        pfit = res_lsq["x"]
        #print(pfit)
        J = res_lsq["jac"]
        try:
            pcov = np.linalg.inv(J.T.dot(J))
        except:
            pcov = None

        if (len(dataY) > len(initial_guess)) and pcov is not None:
            s_sq = (self._get_residuals(pfit, dataX, dataY)**2).sum()/(len(dataY)-len(initial_guess))
            pcov = pcov * s_sq
            self.fit_para_err = [np.abs(pcov[0][0]) ** 0.5, \
                                np.abs(pcov[1][1]) ** 0.5]
        else:
            raise ValueError("basin numerically flat")
            
        #outputs
        self.best_fit_vals = pfit
        self.mag_df["best_fit"] = self._fit_func(self.best_fit_vals)
        self.fitting_error = self._get_fitting_error_data(self.best_fit_vals,dataY)
        self.durbin_watson = self.durbin_watson_statistic(experimental_spectrum = self.mag_df["experiment_spectrum"], 
                                                            best_fit_spectrum=self.mag_df["best_fit"])

    @staticmethod
    def _get_mid_point(param):
        print(param)
        if param == "sigma_bar":
            return 10e1
        elif param == "kappa_scale":
            return 10e-1
        else:
            raise ValueError("fitting parameter not recognised")


class FittingBendingRigidityOnlyLeastSquares(FittingLeastSquares):

    """ use lease square method, with scan initial guess, to fit spectra and get errors """

    def get_best_fit(self, x0=None):

        # generate initial guess
        n_kappa = 100
        kappa_mid  = 10e-1
        width = 1000000.0
        line_func = np.linspace if width <= 5 else np.geomspace
        kappa_scales = line_func(kappa_mid / width, kappa_mid * width, num=n_kappa)                   
        rms_grid = np.zeros(n_kappa)

        for col_num, kappa_scale in enumerate(kappa_scales):
            rms_grid[col_num] = self._get_fitting_error(
                (0.0, kappa_scale)
            )
        min_arg = np.argmin(rms_grid)
        initial_guess = kappa_scales[min_arg]
       
        print("initial guesses",initial_guess)

        #local fitting function
        def _get_residuals_1D (fitting_vals, orders, experiments):
            kappa = fitting_vals[0]
            pair = np.array([0.0,kappa])
            return self._get_residuals(pair, orders, experiments)

        # least squares
        dataX = self.mag_df["order"]
        dataY = self.mag_df["experiment_spectrum"]
        res_lsq = least_squares(_get_residuals_1D,initial_guess,
            args = (dataX,dataY),
            diff_step = 0.01,
            bounds=([0.0],[np.inf])
            )   

        pfit = res_lsq["x"]
        #print(pfit)
        J = res_lsq["jac"]
        pcov = np.linalg.inv(J.T.dot(J))

        if (len(dataY) > 1) and pcov is not None:
            s_sq = (_get_residuals_1D(pfit, dataX, dataY)**2).sum()/(len(dataY)-1)
            pcov = pcov * s_sq
            self.fit_para_err = [0.0,np.abs(pcov[0][0]) ** 0.5]
        else:
            raise ValueError("basin numerically flat")
               
        #outputs
        self.best_fit_vals = np.array([1.0,pfit[0]])
        self.mag_df["best_fit"] = self._fit_func(self.best_fit_vals)
        self.fitting_error = self._get_fitting_error_data(self.best_fit_vals,dataY)
        self.durbin_watson = self.durbin_watson_statistic(experimental_spectrum = self.mag_df["experiment_spectrum"], 
                                                              best_fit_spectrum=self.mag_df["best_fit"])

    @staticmethod
    def _spectrum(q, args, l_max=60):
        """ Return the value of the spectrum at the given order, q. """
        sigma_bar, kappa_scale = args

        val = 0
        for l in range(q, l_max + 1):
            numer = numerator(l, q)
            denom = (l - 1) * (l + 2) * (l * (l + 1)) * kappa_scale
            val += numer / denom

        return val


class FittingSurfaceTensionOnlyLeastSquares(FittingLeastSquares):

    def get_best_fit(self, x0=None):

        # generate initial guess
        n_sigma = 100
        sigma_mid  = 10e1
        width = 1000000.0
        line_func = np.linspace if width <= 5 else np.geomspace
        sigma_bars = line_func(sigma_mid / width, sigma_mid * width, num=n_sigma)                   
        rms_grid = np.zeros(n_sigma)

        for col_num, sigma_bar in enumerate(sigma_bars):
            rms_grid[col_num] = self._get_fitting_error(
                (sigma_bar, 0.0)
            )
        min_arg = np.argmin(rms_grid)
        initial_guess = sigma_bars[min_arg]
       
        #local fitting function
        def _get_residuals_1D (fitting_vals, orders, experiments):
            sigma = fitting_vals[0]
            pair = np.array([sigma,0.0])
            return self._get_residuals(pair, orders, experiments)

        # least squares
        dataX = self.mag_df["order"]
        dataY = self.mag_df["experiment_spectrum"]
        res_lsq = least_squares(_get_residuals_1D,initial_guess,
            args = (dataX,dataY),
            diff_step = 0.01,
            bounds=([0.0],[np.inf])
            )   

        pfit = res_lsq["x"]
        J = res_lsq["jac"]
        pcov = np.linalg.inv(J.T.dot(J))

        if (len(dataY) > 1) and pcov is not None:
            s_sq = (_get_residuals_1D(pfit, dataX, dataY)**2).sum()/(len(dataY)-1)
            pcov = pcov * s_sq
            self.fit_para_err = [np.abs(pcov[0][0]) ** 0.5, 0.0]
        else:
            raise ValueError("basin numerically flat")
               
        #outputs
        self.best_fit_vals = np.array([pfit[0],1.0])
        self.mag_df["best_fit"] = self._fit_func(self.best_fit_vals)
        self.fitting_error = self._get_fitting_error_data(self.best_fit_vals,dataY)
        self.durbin_watson = self.durbin_watson_statistic(experimental_spectrum = self.mag_df["experiment_spectrum"], 
                                                              best_fit_spectrum=self.mag_df["best_fit"])

    @staticmethod
    def _spectrum(q, args, l_max=60):
        """ Return the value of the spectrum at the given order, q. """
        sigma, kappa_scale = args

        val = 0
        for l in range(q, l_max + 1):
            numer = numerator(l, q)
            denom = (l - 1) * (l + 2) * sigma
            val += numer / denom

        return val
