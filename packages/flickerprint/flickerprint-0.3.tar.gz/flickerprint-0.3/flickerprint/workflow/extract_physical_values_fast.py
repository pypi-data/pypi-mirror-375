#!/usr/bin/env python


""" Generate and store the best fit values and metadata for an experiment.

Quick Start
-----------

Once the Fourier terms have been calculated by ``process_images.py`` this script fits
the data to the experimental spectrum and creates a ``fitting_vals.csv`` table for the
experiment directory. After this use ``create_plots.py`` to merge the results from
several experiments and create summaries of the data.

Outline
-------

For each Fourier terms file we fit every granule to a given theoretical spectrum. From
this we calculate the best estimates for the physical values, typically the surface
tension and bending rigidity.

This is saved in a summary table, with other metadata about the granules, this
includes properties of the granule such as its size or the time since treatment,
    input_path = Path(frame_info["input_path"])
but also abstract parameters, such as the quality of fitting to the expected
spectrum.

Once the summary table is created, we add a number of secondary columns for
convenience, typically physical values re-scaled by some factor or on a log
scale. We also bin the time values into 5 minute intervals that can be used for
aggregation/averaging.

"""

import logging
from pathlib import Path

import argh
import numpy as np
import pandas as pd
from scipy.constants import Boltzmann as kB
from tqdm import tqdm

import flickerprint.fluctuation.minimiser_fast as mf
import flickerprint.fluctuation.spectra_fast as sf
import flickerprint.workflow.extract_physical_values as epv
from flickerprint.common.configuration import config


def process_fourier_file(fourier_path: Path):
    """
    Perform the spectrum fitting on one .h5 file corresponding to one time series image.
    ====================================================================================

    Returns:
      - ``property_df``: one line per granule including sigma/kappa estimates
      - ``magnitude_df``: one line per order per granule, contains the fluctuation/fixed spectrum
    """
    fourier_terms, frame_info = epv.load_fourier_terms(fourier_path)

    # Take ownership of the filtered array to stop warnings
    max_order = 15
    fourier_terms = fourier_terms.query(f"order <= {max_order}").copy()
    fourier_terms["mag_abs"] = np.abs(fourier_terms["magnitude"])
    fourier_terms["mag_squared"] = fourier_terms["mag_abs"] ** 2

    grouped_by_granule = fourier_terms.groupby("granule_id")

    # TODO: Grab the configuration file values
    spectrum_builder = sf.SpectrumFitterBuilder(q_max=max_order, l_max=60)

    property_df = []
    magnitude_df = []

    for granule_id, granule in tqdm(grouped_by_granule):
        metadata = gather_granule_metadata(granule)

        # Create a DF of the time averaged terms
        # This is the experimental spectrum that we compare against
        # We have to do the latter term using λ as otherwise it uses a cython version
        # without complex support.
        mag_df = granule.groupby(by="order").agg(
            mag_squ_mean=("mag_squared", "mean"),
            mag_mean=("magnitude", lambda x: np.mean(x)),
        )
        mag_df.reset_index(inplace=True)

        # Supplementary columns used in Pécréaux 2004
        # These terms differ from the definition in the paper as we take
        # |〈mag〉|**2 rather than 〈|mag|〉**2
        mag_df["fixed_squ"] = np.abs(mag_df["mag_mean"]) ** 2
        mag_df["fluct_squ"] = mag_df["mag_squ_mean"] - mag_df["fixed_squ"]
        mag_df["experiment_spectrum"] = mag_df["fluct_squ"]
        experimental_spectrum = mag_df["experiment_spectrum"].values

        spectrum_total = (experimental_spectrum**2).sum()
        if spectrum_total < 1e-20:
            logging.debug("Skipping spectrum as all values zero: {spectrum_total}")
            continue

        mag_df["granule_id"] = granule_id
        mag_df["figure_path"] = frame_info["input_path"]
        magnitude_df.append(mag_df)

        minimisation_function = spectrum_builder.create_fitting_function(
            experimental_spectrum
        )
        fitting_result = mf.fit_spectrum(minimisation_function)
        if fitting_result is None:
            continue

        best_fit_spectrum = spectrum_builder.get_spectra(
            10**fitting_result.sigma_log, 10**fitting_result.kappa_log
        )
        durbin_watson = sf.calculate_durbin_watson(
            experimental_spectrum, best_fit_spectrum
        )

        fitting_result = fitting_result._asdict()
        fitting_result["granule_id"] = granule_id
        fitting_result["durbin_watson"] = durbin_watson
        fitting_result["q_2_mag"] = mag_df["fixed_squ"][0]
        fitting_result["experiment"] = config("workflow", "experiment_name")
        fitting_result |= metadata

        property_df.append(fitting_result)

    property_df = pd.DataFrame(property_df)
    sigma_bar = 10 ** property_df["sigma_log"]
    property_df["kappa"] = 10 ** property_df["kappa_log"]

    temperature = float(config("spectrum_fitting", "temperature")) + 273.15
    property_df["sigma"] = (
        sigma_bar
        / property_df["mean_radius"] ** 2
        * property_df["kappa"]
        * kB
        * temperature
    )
    property_df["input_path"] = frame_info["input_path"]

    magnitude_df = pd.concat(magnitude_df, ignore_index=True)
    return property_df, magnitude_df


def gather_granule_metadata(granule_df: pd.DataFrame) -> dict:
    props = {}

    # Properties averaged across all frames
    props["mean_radius"] = granule_df["mean_radius"].mean() * 1e-6
    props["mean_intensity"] = granule_df["mean_intensity"].mean()

    # (Mostly) Unchanging parameters where we only need to consider the first frame
    first_frame = granule_df.iloc[0]
    keyword_list = [
        "x",
        "y",
        "timestamp",
        "bbox_left",
        "bbox_bottom",
        "bbox_right",
        "bbox_top",
    ]
    for keyword_ in keyword_list:
        props[keyword_] = first_frame[keyword_]

    return props


def main(working_dir: Path):
    working_dir = Path(working_dir).expanduser()
    config_path = working_dir / "config.yaml"
    config.refresh(config_path)
    logging.info(f"Loading configuration file from {config_path}")

    fourier_files = list(
        working_dir.glob("fourier/*.h5")
    )

    minimisation_results = (
        process_fourier_file(fourier_file) for fourier_file in fourier_files
    )

    property_df, magnitude_df = zip(*minimisation_results)
    property_df = pd.concat(property_df, ignore_index=True)
    magnitude_df = pd.concat(magnitude_df, ignore_index=True)

    epv._write_hdf(working_dir / "aggregate_fittings.h5", property_df, magnitude_df)

if __name__ == "__main__":
    argh.dispatch_command(main)
