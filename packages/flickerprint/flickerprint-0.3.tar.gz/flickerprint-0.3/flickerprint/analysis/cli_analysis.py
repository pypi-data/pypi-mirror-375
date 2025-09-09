#!/usr/bin/env python3
from pathlib import Path

import argh
import numpy as np
import pandas as pd
import subprocess
import warnings
from itertools import combinations
from matplotlib import rc
from os.path import isdir

from flickerprint.common.utilities import strtobool
import flickerprint.analysis.statistics as stats
import flickerprint.analysis.plotting as plot
from flickerprint.common.configuration import config

""" Plot the properties of the granules of various treaments. """

def main(input_file: Path, output_dir: Path = "/tmp/", bins=8, density=False, latex=True, img_path_filter:str = None):
    """Create the plots."""
    print(f"\n===================")
    print(f"Population Analysis")
    print(f"===================\n")

    if isdir(Path(input_file)):
        config_location = Path(input_file) / "config.yaml"
    else:
        config_location = Path(input_file).absolute().parent / "config.yaml"
    print(f"\nConfiguration file location: {config_location}")
    config.refresh(config_location)

    if type(density) != bool:
        density = strtobool(density)

    # Check to ensure LaTeX is installed on the system.
    # If not, then we set the LaTeX flag to False.
    if type(latex) != bool:
        latex = strtobool(latex)
    if latex:
        if strtobool(config("plotting", "latex")) == False:
            warnings.warn("\n\nlatex parameter is set to False in configuration file so LaTeX will not be used.\n", Warning)
            latex = False
    if latex:
        try:
            latex_return = subprocess.run(["latex", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if latex_return.returncode != 0:
                latex = False
        except FileNotFoundError:
            warnings.warn("\n\nLaTeX is not installed so it will not be used in plotting\n", Warning)
            latex = False
    if latex:
        rc("text", usetex=True)
        rc("text.latex", preamble=r"\usepackage{siunitx, physics}")
        rc("font", family=r"serif", size=10)
        rc("mathtext", fontset="cm")

    input_file = Path(input_file)
    output_dir = str(Path(output_dir))
    granule_data = plot.read_data(input_file)
    print(f"\n-------------------\n")

    if granule_data.empty:
        raise ValueError(f"\n\nThe aggregate_fittings file is empty. Please check the input file: {input_file}.\n")

    if img_path_filter is not None:
        for index, row in granule_data.iterrows():
            granule_data['image_path'][index] = str(granule_data['image_path'][index])
        granule_data = granule_data[granule_data['image_path'].str.endswith(img_path_filter)==True]
    # Add progressive filters to work out how many granules passed each filtering step.
    filters = ["sigma > 1e-10 and pass_rate > 0.6 and fitting_error < 0.5 and fitting_diff  > 0.03",
               None,"sigma > 1e-10 and pass_rate > 0.6",
               "sigma > 1e-10 and pass_rate > 0.6 and fitting_error < 0.5"
    ]
    for filter in filters:
        if filter is None:
            granule_filter_query_results = granule_data
        else:
            granule_filter_query_results = granule_data.query(filter, inplace=False)
        for label, chunk in granule_filter_query_results.groupby("experiment"):
            n_granules = chunk.shape[0]
            if label == 'unknown':
                print(f"{n_granules} granules when using filter: '{filter}'")
            else:
                print(f"for {label}, {n_granules} granules when using filter: '{filter}'")
    print("\n-----------------\n")

    # Ensure the granules are fully filtered and plot the 1D and 2D histograms.

    granule_data.query(
        "sigma > 1e-10 and pass_rate > 0.6 and fitting_error < 0.5 and fitting_diff > 0.03",# and mean_radius > 0.4 and mean_radius < 0.6",
        inplace=True,
    )
    if granule_data.empty:
        raise ValueError(f"\n\nThe filtered dataset is empty. Please check the input filters.\n")
    granule_data["sigma_micro"] = granule_data["sigma"] * 1e6

    # # Pair plot does not work well with latex for some reason
    # if not latex:
    #     plot.pair_plot(granule_data, output_dir)

    # Create the statistics CSV file
    stats.create_stats_csv(stats.population_statistics(granule_data), f"{output_dir}/../statistics.csv")

    # Create 1D histograms
    hist_plots(granule_data, output_dir, density=density, latex=latex)

    # Create 2D histograms
    if latex:
        specs = [("times","Times(s)",False),
                ("sigma", "Interfacial Tension (N/m)",True),
                ("kappa_scale", "Bending Rigidity ($k_{\mathrm{B}}T$)",True),
                ("sigma_err", "Surface Tension Error (N/m)",True),
                ("kappa_scale_err", "Bending Rigidity Error($k_{\mathrm{B}}T$)",True),
                ("fitting_error", "Fitting Error",False),
                ("q_2_mag", "$|C_2|^2$",False),
                ("mean_radius","Mean Radius",False),
                ("pass_rate","Pass Rate",False),
                ("mean_intensity","Intensity",False)]
    else:
        specs = [("times","Times(s)",False),
                ("sigma", "Interfacial Tension (N/m)",True),
                ("kappa_scale", "Bending Rigidity (kT)",True),
                ("sigma_err", "Surface Tension Error (N/m)",True),
                ("kappa_scale_err", "Bending Rigidity Error(kT)",True),
                ("fitting_error", "Fitting Error",False),
                ("q_2_mag", "|C_2|^2",False),
                ("mean_radius","Mean Radius",False),
                ("pass_rate","Pass Rate",False),
                ("mean_intensity","Intensity",False)]


    for num, (exp_name, group_) in enumerate(granule_data.groupby("experiment")):
        group = group_.copy()
        for x, y in combinations(specs, 2):
            x_name, x_label, x_log = x
            y_name, y_label, y_log = y
            plot.histogram2D(
                y_name,
                y_label,
                x_name,
                x_label,
                group,
                group_by = "experiment",
                plot_group = exp_name,
                out_dir=output_dir,
                log_scaleX=x_log,
                log_scaleY=y_log,
                legend = False
            )
    
    print("\n-----------------\n")
    print(f"Output directory: {output_dir}")
    print(f"\nPopulation analysis complete.\n\n")

def hist_plots(granule_data: pd.DataFrame, out_dir: Path, density=False, latex: bool = True):

    sigma_bins = np.logspace(-9.5, -4, 60)
    plot.overlap_hist(
        "sigma",
        "Surface Tension (N/m)",
        granule_data=granule_data,
        plot_errors="sigma_err",
        group_by="experiment",
        n_bins=sigma_bins,
        out_dir=out_dir,
        density=density,
        log_scale=True,
    )

    kappa_bins = np.logspace(-3, 2, 60)
    if latex:
        kappa_label = "Bending Rigidity ($k_{\mathrm{B}}T$)"
    else:
        kappa_label = "Bending Ridigity (kT)"
    plot.overlap_hist(
        "kappa_scale",
        kappa_label,
        granule_data=granule_data,
        plot_errors="kappa_scale_err",
        group_by="experiment",
        n_bins=kappa_bins,
        out_dir=out_dir,
        density=density,
        log_scale=True,
    )

    radius_bins = 60
    if latex:
        micro_units = r"\si{\micro m}"
        radius_label = f"Mean Radius ({micro_units})"
    else:
        radius_label = f"Mean Radius (µm)"
    plot.overlap_hist(
        "mean_radius",
        radius_label,
        granule_data=granule_data,
        plot_errors=None,
        group_by="experiment",
        n_bins=radius_bins,
        out_dir=out_dir,
        density=density,
        log_scale=False,
    )

    error_bins = 60
    plot.overlap_hist(
        "fitting_error",
        "Goodness of fit",
        granule_data=granule_data,
        plot_errors=None,
        group_by="experiment",
        n_bins=error_bins,
        out_dir=out_dir,
        density=density,
        log_scale=False,
    )

    error_bins = 60
    plot.overlap_hist(
        "fitting_diff",
        "Goodness of fit difference",
        granule_data=granule_data,
        plot_errors=None,
        group_by="experiment",
        n_bins=error_bins,
        out_dir=out_dir,
        density=density,
        log_scale=False,
    )

    intensity_bins = 60
    plot.overlap_hist(
        "mean_intensity",
        "Intensity",
        granule_data=granule_data,
        plot_errors=None,
        group_by="experiment",
        n_bins=intensity_bins,
        out_dir=out_dir,
        density=density,
        log_scale=False,
    )

    q2_bins = np.logspace(-5, 1, 60)
    plot.overlap_hist(
        "q_2_mag",
        "q2",
        granule_data=granule_data,
        plot_errors=None,
        group_by="experiment",
        n_bins=q2_bins,
        out_dir=out_dir,
        density=density,
        log_scale=True,
    )

if __name__ == "__main__":
    argh.dispatch_command(main)
