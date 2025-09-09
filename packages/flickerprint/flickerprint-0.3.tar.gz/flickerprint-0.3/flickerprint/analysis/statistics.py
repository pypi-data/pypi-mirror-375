#!/usr/bin/env python
""" Functions for calculating the population statistics of a dataset output by FlickerPrint.
    
"""

import numpy as np
import pandas as pd
import argh
import re
from scipy.stats import gmean


# Regex capturing --N group termiated with '--' or '.'
re_experiment_name = re.compile("--N(?P<exp>[\d\w_-]+?)(?:--|\.)")
re_time_stamp = re.compile("_(.+)--N")

def population_statistics(
    granule_data: pd.DataFrame,
    _gui: bool = False
    ):
    """Calculates the population statistics for a given dataset.
    
    Parameters
    ----------
    
    granule_data : pd.DataFrame
        The data to calculate the statistics for. This should be a DataFrame containing the aggregate data output by FlickerPrint.
    
    _gui : bool
        If True, the outputs are rounded and converted to strings so that they can be displayed correctly in the GUI.
        
    Returns
    -------
    
    dict[pd.DataFrame]
        A dictionary of DataFrames, each containing the statistics for a given experiment. The keys are the experiment names.
    """

    # First, caluclate the appropriate mean
    # Then calcualte the Standard Deviations
    # Then give the max and min values
    # Then give the number of granules

    output = {}

    rows = ["sigma", 
            "kappa_scale", 
            "fitting_error", 
            # "fitting_diff",
            "mean_radius", 
            "mean_intensity", 
            "pass_rate", 
            "pass_count", 
            "durbin_watson"]
    
    log_scales = {
        "sigma": True,
        "kappa_scale": True,
        "fitting_error": False,
        "fitting_diff": False,
        "mean_radius": False,
        "mean_intensity": False,
        "pass_rate": False,
        "pass_count": False,
        "durbin_watson": False,
    }

    friendly_names = {
            "sigma": "Interfacial Tension (µN/m)", 
            "kappa_scale": "Bending Rigidity (kT)", 
            "fitting_error": "Fitting Error", 
            "fitting_diff": "Fitting Difference",
            "mean_radius":"Mean Radius (µm)",
            "mean_intensity":"Mean Intensity (x1000)", 
            "pass_rate":"Pass Rate", 
            "pass_count":"Pass Count",
            "durbin_watson":"Durbin Watson",
            }
    chunks = granule_data.groupby("experiment")

    for num, (label, chunk) in enumerate(chunks):
        tmp = []
        for row in rows:
            log_scale = log_scales[row]
            if row == 'sigma':
                chunk[row] = chunk[row] * 10**6
            if row =='mean_intensity':
                chunk[row] = chunk[row] * 10**-3
            try:
                if log_scale:
                    mean_fct = gmean
                else:
                    mean_fct = np.mean

                mean = mean_fct(chunk[row])
                std_lower, std_upper = _calc_stds(chunk, row)
                max_val = chunk[row].max()
                min_val = chunk[row].min()
                n_granules = len(chunk)

                if _gui: # If it's in the GUI, then we make them rounded strings so they look nice.
                    tmp.append(pd.DataFrame({
                        "Property": friendly_names[row],
                        "Mean Value": f"{mean:.3g}",
                        "Mean -1 SD": f"{std_lower:.3g}",
                        "Mean +1 SD": f"{std_upper:.3g}",
                        "Maximum Value": f"{max_val:.3g}",
                        "Minimum Value": f"{min_val:.3g}",
                        "Sample Size": n_granules,
                        "Log-Normal Distribution": log_scale
                    }, index=[0]))
                else:
                    tmp.append(pd.DataFrame({
                        "Property": friendly_names[row],
                        "Mean Value": mean,
                        "Lower Confidence Limit": std_lower,
                        "Upper Confidence Limit": std_upper,
                        "Maximum Value": max_val,
                        "Minimum Value": min_val,
                        "Sample Size": n_granules,
                        "Log-Normal Distribution": log_scale
                    }, index=[0]))
            except KeyError:
                continue
            
        output[label] = pd.concat(tmp, ignore_index=True)

    return output

def _calc_stds(chunk, plot_column):
    """Calculates the standard deviation of a given column in a DataFrame.

    Parameters
    ----------

    chunk : pd.DataFrame
        The DataFrame to calculate the standard deviation for.
    plot_column : str
        The column to calculate the standard deviation for.

    Returns
    -------
    tuple
        A tuple containing the lower and upper standard deviation.
    """
    chunk_sorted = chunk.sort_values(by=plot_column)
    tot = 0
    target = 0.165 * len(chunk_sorted)
    for _,entry in chunk_sorted.iterrows():
        tot += 1
        if tot > target:
            low_limit = entry[plot_column]
            break

    tot = 0
    target = (1.0 - 0.165) * len(chunk_sorted)
    for _,entry in chunk_sorted.iterrows():
        tot += 1
        if tot > target:
            high_limit = entry[plot_column]
            break
    
    return low_limit, high_limit

def create_stats_csv(stats: dict[pd.DataFrame], output_dir: str = './statistics.csv') -> None:
    """Creates a CSV file from the statistics dictionary produced by ``population_statistics()``.
    
    Parameters
    ----------
    
    stats : dict[pd.DataFrame]
        A dictionary of statistics dataframes. Typically created by the `population_statistics` function.
    
    output_dir : str
        The output directory for the CSV file. Can also be an ``IOBuffer``, as appropriate.
    """
    for key in stats.keys():
        stats[key].insert(0, "Experiment", key)
    stats_df = pd.concat(stats.values(), keys=stats.keys(), ignore_index=True)
    stats_df.to_csv(output_dir)
