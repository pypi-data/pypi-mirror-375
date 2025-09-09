#!/usr/bin/env python
""" A selection of  plotting routines for Granule Explorer output data.

    Outline
    -------
    We provide a number of routines for visualing the data stored in
    "aggregate_hittings.h5". These include various 1 and 2D histograms,
    quartile plots and error estimates.
"""

from typing import Tuple
import matplotlib.pyplot as plt
import matplotlib.colors as c
from matplotlib.cm import ScalarMappable

import numpy as np
import pandas as pd
import seaborn as sns
import pickle as pkl
import seaborn as sns
import re
import datetime
import warnings

from pathlib import Path
from collections import OrderedDict
from scipy.stats import sem, gmean, gstd,norm
from scipy.stats import gmean as _gmean
from matplotlib import rc
from seaborn._stats.density import KDE
from matplotlib.ticker import EngFormatter

import flickerprint.tools.plot_tools as pt

# Regex capturing --N group termiated with '--' or '.'
re_experiment_name = re.compile("--N(?P<exp>[\d\w_-]+?)(?:--|\.)")
re_time_stamp = re.compile("_(.+)--N")

def histogram2D (
    plot_column,
    plot_title,
    plot_row,
    row_title,
    granule_data,
    group_by = "experiment",
    plot_group = "As",
    column_nbins = 20,
    row_nbins = 20,
    legend = True,
    log_scaleX = True,
    log_scaleY = True,
    save_png = True,
    out_dir = "/tmp/", 
    plot_data: bool = False,
)-> Tuple[plt.figure, pd.DataFrame]:
    """
    A 2D histogram plot to visuale correlations between parameters. If it looks too
    sparse, (not enough points per bin) use scatter_plot instead.

    Parameters
    ----------

    plot_column: str
        The name of the column in [granule_data] to be binned along the y-axis

    plot_title: str
        The label for the y-axis 

    plot_row: str
        The name of the column in [granule_data] to be binned along the x-axis

    plot_row: str
        The label for the y-axis

    granule_data: Pandas dataframe
        The granule data for the plot, see the section in the Docs on "aggregate_fitting.h5"
        for the format required of the dataframe

    group_by: str
        The name of the column in [granule_data] which will be used to group the data before
        plotting. Only granules with a value of [plot_group] in this column will be plotted

    plot_group: anything
        The value in [group_by] of granules that should be plotted

    column_nbins: int
        The number of bins along the column axis

    row_nbins: int
        The number of bins along the row axis

    legend: bool
        Add a legend to the plot or not

    x_log_scale: bool
        Set x axis to a log scale if true

    y_log_scale: bool
        Set y axis to a log scale if true

    save_png: bool
        Saves the figure to a png in [out_dir] if true

    out_dir: str
        The path that the output figure should be saved to

    Outputs
    -------
    Figure to [out_dir] if [save_file] is true

    Returns
    -------
    A matplotlib figure
    """

    fig, ax = pt.create_axes(1, fig_width=8.3 / 2.5, aspect=1)
    my_filter = f'{group_by} == "{plot_group}"'
    group = granule_data.query(my_filter).copy()

    if not log_scaleX:
        bin_max = group[plot_row].max()
        bin_min = group[plot_row].min()
        binsX = np.linspace(bin_min,bin_max,row_nbins + 1,endpoint=True)
    else:
        bin_max = group[plot_row].max()
        bin_min = group[plot_row].min()
        binsX = np.geomspace(bin_min, bin_max, row_nbins + 1)

    if not log_scaleY:
        bin_max = group[plot_column].max()
        bin_min = group[plot_column].min()
        binsY = np.linspace(bin_min,bin_max,column_nbins + 1,endpoint=True)
    else:
        bin_max = group[plot_column].max()
        bin_min = group[plot_column].min()
        binsY = np.geomspace(bin_min, bin_max, column_nbins + 1)

    h = ax.hist2d(plot_row,plot_column, bins = [binsX,binsY],
                label=plot_group, data=granule_data,norm=c.LogNorm(clip=True)) 
    fig.colorbar(h[3])

    ax.set_ylabel(plot_title)
    ax.set_xlabel(row_title)
    if legend:
        ax.legend(fontsize=10)
    if log_scaleY:
        ax.set_yscale("log")
    if log_scaleX:
        ax.set_xscale("log")

    if save_png:
        pt.save(
            Path(out_dir) / f"2D-hist-{plot_group}-{plot_row}-{plot_column}.png",
            padding=0.05,
        )
    if plot_data:
        save_data = group[['experiment', plot_row, plot_column]].reset_index() # Grab x and y-axis  
        # Add x-axis bin limits
        bins = pd.DataFrame({
            'binsX': binsX,
            'binsY': binsY,
        })
        save_data = pd.concat([save_data, bins], axis=1) # Add x and y-axis bins
        save_data = save_data.drop(columns=['index'])    # Remove unused index column    
        return fig, save_data
    else:
        return fig


def pair_plot(granule_data: pd.DataFrame, save_png = True, out_dir: Path = "/tmp/")-> Tuple[plt.figure, pd.DataFrame]:

    """
    Uses seaborn's pairplot to draw 1 and 2D histograms of the Surface Tension,
    Bending Rigidity and Mean Radius for granules in [granule_data].

    Parameters
    ----------

    granule_data: Pandas dataframe
        The granule data for the plot, see the section in the Docs on "aggregate_fitting.h5"
        for the format required of the dataframe

    save_png: bool
        Saves the figure to a png in [out_dir] if true

    out_dir: str
        The path that the output figure should be saved to

    Outputs
    -------
    Figure to [out_dir] if [save_file] is true

    Returns
    -------
    A matplotlib figure
   
    Outputs
    -------
    Figure to [out_dir] 
    """

    #make colour dict
    experiments = set(granule_data["experiment"].to_list())
    get_colour = colour_gen()
    colour_dict = {}
    for experiment in experiments:
        colour_dict[experiment] = get_colour(experiment)

    # pair plot does not work well with log axes, so we set these values directly
    granule_data["log_sigma"] = np.log10(granule_data["sigma"])
    granule_data["log_kappa"] = np.log10(granule_data["kappa_scale"])

    # Create the corner plot
    g = sns.pairplot(
        data=granule_data,
        hue="experiment",
        vars=["log_sigma", "log_kappa", "mean_radius"],
        markers="x",
        plot_kws=dict(linewidths=0.8, levels=4, alpha=0.8),
        kind="kde",
        corner=False,
        palette=colour_dict,
        height=4,
    )

    # Make the names more human readable
    rename_dict = {
        "mean_radius": "Mean Radius",
        "log_kappa": "Log(Bending Rigidity)",
        "log_sigma": "Log(Surface Tension)",
    }
    for ax in g.axes.flat:
        if ax is None:
            continue
        y_label = ax.get_ylabel()
        if y_label in rename_dict:
            ax.set_ylabel(rename_dict[y_label])
        x_label = ax.get_xlabel()
        if x_label in rename_dict:
            ax.set_xlabel(rename_dict[x_label])

    if save_png:
        save_path = Path(out_dir) / "pair_plot.png"
        plt.savefig(save_path)
    return plt.gcf()

def overlap_hist(
    plot_column,
    plot_label,
    granule_data: pd.DataFrame,
    plot_errors=None,
    group_by = "experiment",
    n_bins=20,
    agg = gmean,
    density=False,
    legend=False,
    log_scale = True,
    quiet: bool = True,
    save_png = True,
    out_dir = "/tmp/", 
    plot_data: bool = False,
)-> Tuple[plt.figure, pd.DataFrame]:
    """
    Draw overlapping histograms of [plot_column], split by [group_by].
    
    Plots a histogram of a variable with the 67% of points cloest to the medium shown in a darker colour,
    and the average (as determined by agg) shown with a verticle line.
    Also prints a summary of the mean and error. 

    Parameters
    ----------

    plot_column: str
        The name of the column in [granule_data] to be plotted as a histogram

    plot_label: str
        The label for the x-axis

    granule_data: Pandas dataframe
        The granule data for the plot, see the section in the Docs on "aggregate_fitting.h5"
        for the format required of the dataframe

    plot_errors: str or None
        If None, errorbars are not plotted
        The column in [granule_data] containing the error estimates for the values in [plot_column],
        used to estimate the error bars on the histogram bars.

    group_by: str
        The name of the column in [granule_data] which will be used to group the data before
        plotting. The graphs for each group will be plotted one on top of the other.

    n_bins: int or array
        If int, then the number of bins.
        If array, then the bin edges.

    agg: function Pandas dataseries -> float
        The function used to calculate the colour values. Usually some type of mean.

    out_dir: str
        The path that the output figure should be saved to

    density: bool
        If true, plot a probability density so the area under the graph is 1.

    legend: bool
        Add a legend to the plot or not

    log_scale: bool
        Set x axis to a log scale if true

    benchling_format: bool
        If true, print summary to the screen, optimized for cutting and pasting into tables.

    save_png: bool
        Saves the figure to a png in [out_dir] if true

    out_dir: str
        The path that the output figure should be saved to

    Outputs
    -------
    Figure to [out_dir] if [save_file] is true

    Returns
    -------
    A matplotlib figure

    """
    if plot_errors == 'None':
        plot_errors = None

    fig, ax = pt.create_axes(1, axes_height= 8.3 / 2.5,aspect = 1)

    chunks = granule_data.groupby(group_by)
    get_colour = colour_gen()
    #fix n_bins
    if type(n_bins) == int and log_scale == True:
        bin_max = granule_data[plot_column].max()
        bin_min = granule_data[plot_column].min()
        n_bins = np.geomspace(bin_min, bin_max, n_bins + 1)    
    if type(n_bins) == np.ndarray:
        bins_size = n_bins.size
    elif type(n_bins) == int:
        bins_size = n_bins
    else:
        raise ValueError("n_bins must be an array or an integer")
    plot_data = dict({
        'experiment':[],#['Null' for i in range(len(chunks)*int((bins_size-1)))],
        'hist_values': [],#np.zeros(len(chunks)*(bins_size-1)),
        'bin_edges':[],#np.zeros(len(chunks)*(bins_size-1)),
        'hist_values_normalized': [],#np.zeros(len(chunks)*(bins_size-1)),
        'hist_errorbar': [],#np.zeros(len(chunks)*(bins_size-1)),
    })  

    for num, (label, chunk) in enumerate(chunks):
        colour = get_colour(label)
        hist_vals, bin_edges = np.histogram(
            chunk[plot_column], bins=n_bins, density=density
        )

        plot_data['experiment'][num*(bins_size):(num+1)*(bins_size-1)] = [label for _ in range(len(hist_vals))]
        plot_data['hist_values'] += hist_vals.tolist()
        plot_data['bin_edges'] += bin_edges[:-1].tolist() # Exclude last value, defaults to 1 (last bin edge)

        widths = bin_edges[1:] - bin_edges[:-1]
        if plot_errors is None:
            plot_data["hist_errorbar"] += [0.0 for _ in range(len(hist_vals))]
            hist_err = None
        else:
            # plot_data['hist_errorbar'] = []
            hist_err = _get_hist_err(chunk[plot_column], chunk[plot_errors], bin_edges)
            plot_data['hist_errorbar'] += hist_err.tolist()

        hist_vals, hist_err = _get_normalised(hist_vals, hist_err)
        plot_data['hist_values_normalized'] += hist_vals.tolist()

        # bin_data.append(hist_vals)
        low_index, low_limit, high_index, high_limit = _calculate_limits(hist_vals,chunk,plot_column)

        ax.bar(
            bin_edges[:low_index],
            hist_vals[:low_index],
            label="_",
            alpha=0.410,
            color=colour,
            width=widths[:low_index],
            align="edge",
        )

        ax.bar(
            bin_edges[low_index:high_index],
            hist_vals[low_index:high_index],
            label=label,
            alpha=0.8,
            color=colour,
            width=widths[low_index:high_index],
            align="edge",
        )

        ax.bar(
            bin_edges[high_index:-1],
            hist_vals[high_index:],
            label="_",
            alpha=0.410,
            color=colour,
            width=widths[high_index:],
            align="edge",
        )

        if log_scale:
            bar_centers = np.exp(0.5 * (np.log(bin_edges[1:]) + np.log(bin_edges[:-1])))
        else:
            bar_centers = 0.5*(bin_edges[1:] + bin_edges[:-1])
        ax.errorbar(
            bar_centers,
            hist_vals,
            yerr=hist_err,
            lw=0.0,
            elinewidth=0.5,
            ecolor=colour,
            capsize=2.0,
            capthick=0.5,
            zorder=10,
        )

        n_granules = len(chunk)
        # if plot_column == "sigma":
        #     gmean = agg(chunk[plot_column]*chunk["mean_radius"]**2/(4.11)*4*np.pi)
        # else:
        gmean = agg(np.abs(chunk[plot_column]))
        plt.axvline(gmean, 0, 1, color=colour, ls="--", lw=0.8, alpha=1.0, zorder = 11,)

        if not quiet:
            print(
                f"For {n_granules} granules is {pt.format_si(gmean)}"
                f" for {label} - {plot_label}",
            )

            print(
                f"Lower bound {pt.format_si(low_limit)}. Upper bound {pt.format_si(high_limit)}"
            )


    ax.set_xlabel(plot_label)
    ax.set_ylabel("Count")
    ax.set_ylim(bottom=0.0)
    if legend:
        ax.legend(fontsize=10)

    if log_scale:
        ax.set_xscale("log")

    if save_png:
        out_dir = Path(out_dir)
        save_path = out_dir / f"overlap-{plot_column}-{group_by}.png"
        sns.despine()
        plt.tight_layout()
        plt.savefig(save_path, dpi=330)
    if plot_data:
        return fig, pd.DataFrame(plot_data)
    else:
        return fig


def read_data(input_file,comp_file = None,data_file_name="aggregate_fittings.h5"):

    """Reads in one or more aggregate_fitting.h5 files and concatenates each one
    
        Parameters
        ----------
        input_file: str
            The path to either a [data_file_name] file or a folder containing data files.
            If a file, it will open that file as a data frame and return it.
            If a folder, it will recursivly search subfolders for files named
            [data_file_name], open all the files and concatenate the result
            into a single data frame.

        comp_file: str
            This is for backwards compatability only! If you have data from before
            May 2022, it may come with a separate "comparision" file containing additional
            information. This parameter should be a path to that file, otherwise None.

        data_file_name: str
            the name of the .h5 file to open. Default: aggregate_fittings.h5

        Returns
        -------
        a pandas data frame containing all the data from the .h5 files opened
    
    """

    if input_file.is_dir():
        input_file_list = input_file.rglob(data_file_name)
        granule_data = pd.concat(map(_load_terms, input_file_list), ignore_index=True)
    else:
        granule_data = _load_terms(input_file)

    if "fitting_diff" in granule_data.columns:
        #new style output, no additional processing needed
        return granule_data

    elif comp_file != None:
        #resolve comparison
        if comp_file.is_dir():
            comp_file_list = comp_file.rglob(data_file_name)
            comp_data = pd.concat(map(_load_terms, comp_file_list), ignore_index=True)
        else:
            comp_data = _load_terms(comp_file)

        sigma_diffs = []
        for granule, comp in zip(granule_data.itertuples(),comp_data.itertuples()):
            sigma_diffs.append(abs(granule.sigma - 4.0 * comp.sigma))    
        granule_data = granule_data.assign(sigma_diff = sigma_diffs)

        fitting_diffs = []
        for granule, comp in zip(granule_data.itertuples(),comp_data.itertuples()):
            fitting_diffs.append(comp.fitting_error - granule.fitting_error)
    
        granule_data = granule_data.assign(fitting_diff = fitting_diffs)
        return granule_data

    else:
        #fallback, set nonsense values in missing columns
        granule_data["sigma_diff"] = 10000000.0
        granule_data["fitting_diff"] = 10000000.0
        return granule_data

def _load_terms(aggregate_fittings_path: Path) -> pd.DataFrame:
    """Load the spectrum fitting terms and physical values from disk."""
    # Container for the physical properties of the granules
    print(f"Reading from file: {aggregate_fittings_path}")
    if aggregate_fittings_path.name.endswith(".h5"):
        aggregate_fittings = pd.read_hdf(
            aggregate_fittings_path, key="aggregate_data", mode="r"
        )
    elif aggregate_fittings_path.name.endswith(".pkl"):
        file = open(f'{str(aggregate_fittings_path)}', 'rb')
        f = pkl.load(file=file)
        aggregate_fittings = f["aggregate_data"]
    else:
        raise IOError("We can only load data from HDF5 and pkl files currently.")

    if "experiment" not in aggregate_fittings.columns:
        #old style output files need to have the experiment column infered.
        aggregate_fittings["experiment"] = _get_treament_type(
            aggregate_fittings["figure_path"].iloc[0]
        )

    #convert timesstamps to seconds since first granule

    if "timestamp" in aggregate_fittings.columns:
        times = aggregate_fittings["timestamp"]
        try:
            times = [datetime.datetime.strptime(time,"%Y-%m-%dT%H:%M:%S.%f") for time in times]
            earliest = min(times)
            times = [(time - earliest).total_seconds() for time in times]
        except:
            warnings.warn("Warning: times not formatted correctly, need %Y-%m-%dT%H:%M:%S.%f format. Setting times to 0")
            times = [0.0 for time in times]
        aggregate_fittings["times"] = times
    else:
        warnings.warn("Warning: Timestamps missing from aggregate data. Setting to 0")
        times = [0.0 for time in aggregate_fittings["experiment"]]

    aggregate_fittings["times"] = times

    return aggregate_fittings


def _get_treament_type(im_path):
    """Get the experiment name from the image path."""
    path_name = Path(im_path).name
    experiment_group = re_experiment_name.search(path_name)

    if experiment_group is None:
        return "unknown"

    experiment_name = experiment_group.groupdict()["exp"]
    print(path_name, " ", experiment_name)
    if experiment_name.startswith("Control") or experiment_name.startswith("As"):
        return "As"
    if experiment_name.startswith("Cz"):
        return "Cz"
    if experiment_name.startswith("FXR1"):
        if experiment_name.endswith("mCh"):
            return "FXR1-G3BP1"
        elif experiment_name.endswith("GFP"):
            return "FXR1-FXR1"
        else:
            return "NaAs+FXR1"
    if experiment_name.startswith("Caprin"):
        return "NaAs+Caprin1"
    raise ValueError("Unable to get experiment name.")

def _get_hist_err(vals, errors, bin_edges):

    hist_errors = np.zeros(len(bin_edges) - 1)

    for mean, sd in zip(vals, errors):
        for i in range(len(bin_edges) - 1):
            p = norm.cdf(bin_edges[i + 1], loc=mean, scale=np.abs(sd)) - norm.cdf(
                bin_edges[i], loc=mean, scale=np.abs(sd)
            )
            hist_errors[i] += p * (1 - p)
            # print(mean,sd,p)
    return np.sqrt(hist_errors)



def _get_normalised(hist_vals, hist_errors):

    hist_vals_norm = hist_vals / sum(hist_vals)

    if isinstance(hist_errors, np.ndarray):
        hist_errors_norm = [
            norm * err / val if val > 0.0 else 0.0
            for err, val, norm in zip(hist_errors, hist_vals, hist_vals_norm)
        ]
    else:
        hist_errors_norm = None

    return hist_vals_norm, hist_errors_norm


def colour_gen():
    treatments = {}
    colours = ["#7fc97f","#beaed4","#4da6ff","#ff0000","#fdc086","#cc7700"]
    num = 0
    def get_colour(treatment):
        nonlocal treatments
        nonlocal colours
        nonlocal num
        if treatment in treatments:
            return treatments[treatment]
        else:
            if colours != []:
                colour = colours[0]
                colours = colours[1:]
            else:
                colour = list(c.CSS4_COLORS.values())[num]
                num +=1

            treatments[treatment] = colour
            return colour
    return get_colour


def _calculate_limits(vals,chunk,plot_column):

    tot = 0
    low_index = 0
    for index, val in enumerate(vals):
        tot += val
        if tot > 0.165:
            low_index = index
            break

    tot = 0
    high_index = len(vals)-1
    for index,val in enumerate(vals):
        tot += val
        if tot > 1.0 - 0.165:
            high_index = index
            break

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

    return low_index, low_limit, high_index, high_limit


def violin(granule_data: pd.DataFrame,
           plot_column, 
           plot_label, 
           quantiles=None, 
           log_scale: bool =True,
           save_png: bool =True,
           out_dir: Path = "/tmp/",
           plot_data: bool = False,
           group_by = 'experiment',
           )-> plt.figure:
    fig, ax = pt.create_axes(1, axes_height= 8.3 / 2.5,aspect = 1)
    get_colour = colour_gen()

    violins = sns.violinplot(data=granule_data, x=group_by,hue=group_by, y=plot_column, ax=ax, log_scale=log_scale, cut=0, common_norm=True, inner=None, palette=[get_colour(expt) for expt in granule_data['experiment'].unique()], alpha=0.6, saturation=1, legend=False)#"#4da6ff", "#FF47FF", "#47D348"],alpha=0.8, saturation=1, legend=False)#
    
    for violin in ax.collections:
        violin.set_edgecolor("none")
    
    all_vals = []
    all_densities = []
    expts = []
    all_log_values = []
    means = []

    # Calculations for adding quantile lines
    for i, expt in enumerate(granule_data[group_by].unique()):
        if group_by == 'experiment':
            values = granule_data.query("experiment == @expt", inplace=False)
        else:
            raise ValueError("Only group_by='experiment' is supported")
        values = values[plot_column]
        if log_scale:
            log_values = np.log10(values)
            means.append(gmean(values))
        else:
            log_values = values
            means.append(np.mean(values))
        all_log_values.append(log_values)
        
        kde = KDE(cut=0)
        vals=kde._transform(pd.DataFrame({"y": np.sort(log_values), "weight": np.ones_like(log_values)}), "y", [])
        if log_scale:
            vals['y'] = np.power(10, vals['y'])
        all_vals.append(vals["y"])
        all_densities.append(vals["density"])
        expts.append(expt)
    all_vals = np.array(all_vals)
    all_densities = np.array(all_densities)

    normalised_density = all_densities / np.max(all_densities)

    # Add the lines for the quantiles

    if quantiles == None:
        quantiles = {"values": [16, 84],
                     "styles": ['dotted', 'dotted'],
                     "colors": ['black', 'black']}
    for i in range(all_vals.shape[0]):   
        for j, quantile in enumerate(quantiles['values']):
            quantile_value = np.percentile(np.sort(all_log_values[i]), quantile)
            if log_scale:
                quantile_value = np.power(10, quantile_value)  # Transform back to original scale

            width_at_quantile = np.interp(quantile_value, all_vals[i], normalised_density[i])

            # Add a horizontal line at the quantile
            ax.plot([-width_at_quantile * 0.4 + i, width_at_quantile * 0.4 + i],
                    [quantile_value, quantile_value],
                    color=quantiles['colors'][j], lw=1, ls=quantiles['styles'][j])

        width_at_mean = np.interp(means[i], all_vals[i], normalised_density[i])
        ax.plot([-width_at_mean * 0.4 + i, width_at_mean * 0.4 + i],
                [means[i], means[i]],
                color='black', lw=1, ls='dashed')

    ax.set_ylabel(plot_label)
    if group_by == 'experiment':
        ax.set_xlabel('Experiment')
    ax.set_xticks(range(0, len(expts)))

    return (fig, 1)