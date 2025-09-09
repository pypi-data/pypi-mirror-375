import pandas as pd
import pickle as pkl
import h5py
from pathlib import Path

from shiny import App, Inputs, Outputs, Session, render, ui, module, reactive
from shiny.types import FileInfo
# from ..plotting_tools.split_histogram import read_data

"""
    Module for handling file uploads, returning the .h5 file to the global context so it may be used by the graphing modules to create plots. 
"""
@module.ui
def file_upload_module_ui():
    return (
        ui.tooltip(
            ui.input_file("graunle_aggregate_data", "Open Aggregate Data", accept=[".h5,.pkl"], multiple=True),
            "Open aggregate_data.h5 files to begin! You can select multiple files at once.",
            id="graunle_aggregate_data_upload_tool_tip",
            options={
                "show":True
            },
            show=True
        ),
        # ui.input_file("graunle_image_data", "Upload image data", accept=[".ims"], multiple=False)
    )

        
@module.server
def file_upload_module_server(input: Inputs, output: Outputs, session: render) -> reactive.Value[pd.DataFrame]:
    uploaded_file = reactive.Value()

    @reactive.Effect
    @reactive.event(input.graunle_aggregate_data)
    def set_uploaded_file():
        """
            Reads and formats the uploaded .h5 files. 
            Sets the results to the reactive value container.
        """
        f: list[FileInfo] = input.graunle_aggregate_data()
        # Get path to each uploaded file
        file_paths: list[Path] = [Path(f[i]["datapath"]) for i in range(len(f))]
        df = read_data(file_paths)
        uploaded_file.set(df)

    
    return uploaded_file


#TODO: Import this from plot_tools?

import re
# Regex capturing --N group termiated with '--' or '.'
re_experiment_name = re.compile("--N(?P<exp>[\d\w_-]+?)(?:--|\.)")
re_time_stamp = re.compile("_(.+)--N")


def read_data(input_file: list[Path], data_file_name="aggregate_fittings.h5"):
    """
    Read and format the data in the given paths. If multiple files are uploaded it will concatenate them.
    Args:
        input_file (list[Path]): _description_
        data_file_name (str, optional): _description_. Defaults to "aggregate_fittings.h5".

    Returns:
        _type_: _description_
    """

    if len(input_file) > 1:       
        granule_data = pd.concat(map(_load_terms, input_file), ignore_index=True)
    else:
        granule_data = _load_terms(input_file[0])

    granule_data["sigma_diff"] = 10000000.0
    granule_data["fitting_diff"] = 10000000.0

    return granule_data

##########################################################################################
def read_data(input_file_list: list[Path], comp_file = None, data_file_name="aggregate_fittings.h5"):

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

    if len(input_file_list) > 1: # If multiple files, concatenate
        granule_data = pd.concat(map(_load_terms, input_file_list), ignore_index=True)
    else:
        granule_data = _load_terms(input_file_list[0])

    if "fitting_diff" in granule_data.columns:
        #new style output, no additional processing needed
        return granule_data

    elif comp_file != None:
        raise Exception("Comp file is not supprted in this version of Granule Explorer Viz Tool")

    else:
        #fallback, set nonsense values in missing columns
        granule_data["sigma_diff"] = 10000000.0
        granule_data["fitting_diff"] = 10000000.0
        return granule_data

def _load_terms(aggregate_fittings_path: Path) -> pd.DataFrame:
    """Load the spectrum fitting terms and physical values from disk."""
    # Container for the physical properties of the granules
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

    try: #TODO fix times frame_gen so this is handled more elegently
        times = [_convert_to_sec(path) for path in aggregate_fittings["figure_path"]]
        start = min(times)
        times = [time - start for time in times]
    except:
        times = 1.0

    aggregate_fittings["times"] = times

    if aggregate_fittings.empty:
        raise ValueError(
            f"The file {aggregate_fittings_path} is empty. Please check the input file."
        )

    return aggregate_fittings


def _get_treament_type(im_path):
    """Get the experiment name from the image path."""
    path_name = Path(im_path).name
    experiment_group = re_experiment_name.search(path_name)

    if experiment_group is None:
        return "unknown"

    experiment_name = experiment_group.groupdict()["exp"]
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


def _convert_to_sec(path):
    time = re_time_stamp.findall(path)
    t = time[0].split(".")
    return int(t[0]) * 3600 + int(t[1]) * 60 + int(t[2])

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