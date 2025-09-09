from shiny import App, Inputs, Outputs, Session, module, render, ui, reactive
from shiny.types import ImgData, FileInfo
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as co
import io
import numpy as np
from typing import Callable

from plotting_tools.create_plot import create_download_figure, create_fig

@module.ui
def graph_module_ui(label: str, plot_input_options: dict[dict[dict]]):
    # Create text_input elements
    plot_input_text_ui_elements = []
    for k,v in plot_input_options['text_input'].items(): # TODO: Handle KeyError for dictionaries. Prevents UI config from having to include all possible options.
        plot_input_text_ui_elements.append(ui.input_text(id=k, **v))

    # Create select elements that will be updated by the update_axies_select(). Adding dataset column names to the 'choices' parameter.
    plot_input_select_axis_ui_elements = []
    for k, v in plot_input_options['select_input_dataset_columns'].items():
        plot_input_select_axis_ui_elements.append(ui.input_select(id=k, **v))

    # Create normal select elements without any serverside update function 
    plot_input_select_ui_elements = []
    for k, v in plot_input_options['select_input'].items():
        plot_input_select_ui_elements.append(ui.input_select(id=k, **v))

    # Create switch elements
    plot_input_switch_ui_elements = []
    for k, v in plot_input_options['bool_input'].items():
        plot_input_switch_ui_elements.append(ui.input_switch(id=k, **v))

    # Create switch elements
    plot_input_numeric_ui_elements = []
    for k, v in plot_input_options['numeric_input'].items():
        plot_input_numeric_ui_elements.append(ui.input_numeric(id=k, **v))

    if plot_input_options['allow_multiple_experiments']:
        # TODO: Add config option for restricting amount of experiments (treatments) that are allowed to be selected at ones
        #     -> multiple=True, just turn this to False?
        allow_multiple_experiments = True
    else:
        allow_multiple_experiments = False

    labels = {"sigma": "Interfacial Tension (N/m)", 
              "kappa_scale": "Bending Rigidity (kT)", 
              "fitting_error": "Fitting Error", 
              "fitting_diff": "Fitting Difference",
              "mean_radius":"Mean Radius (µm)",
              "mean_intensity":"Mean Intensity", 
              "pass_rate":"Pass Rate", 
              "pass_count":"Pass Count",
              "durbin_watson":"Durbin Watson",
              }
    
    default_max_values = {"sigma": None,
                            "kappa_scale": None,
                            "fitting_error": 0.5,
                            "fitting_diff": None,
                            "mean_radius": None,
                            "mean_intensity": None,
                            "pass_rate": None,
                            "pass_count": None,
                            "durbin_watson": None,
                            }
    
    default_min_values = {"sigma": 1e-10,
                            "kappa_scale": None,
                            "fitting_error": None,
                            "fitting_diff": 0.03,
                            "mean_radius": None,
                            "mean_intensity": None,
                            "pass_rate": 0.6,
                            "pass_count": None,
                            "durbin_watson": None,
                            }
    
    params = ["sigma", 
              "kappa_scale", 
              "fitting_error", 
              "fitting_diff", 
              "mean_radius", 
              "mean_intensity", 
              "pass_rate", 
              "pass_count", 
              "durbin_watson"
              ]
    
    rows = []
    for param in params:
        row_tmp1 = ui.row(
            f"{labels[param]}",
            )
        row_tmp2 = ui.row(
            ui.input_numeric(id=f"{param}_filter_input_lower", label=f"min:", value=default_min_values[param], step=1e-10, width="200px"),
            ui.input_numeric(id=f"{param}_filter_input_upper", label=f"max:", value=default_max_values[param], step=1e-10, width="200px")
        )
        rows.append(row_tmp1)
        rows.append(row_tmp2)


        
    return ui.row(
        ui.row(
            ui.column(4,
                ui.row(),
                
                ui.page_bootstrap(ui.input_action_button("update_plot", "Update Plot", style="background-color: #b6e0b1"),
                                    # ui.download_button("download_plot_png", "Download Plot"),
                                    ui.input_action_button("modal_download", "Save Plot")),
                ui.hr(),

                # Unpack ui elemets from list
                ui.input_selectize(id="experiment_selectize_input", label="Select experiments", choices=[""], multiple=allow_multiple_experiments, width="100%"),
                *plot_input_select_axis_ui_elements,
                *plot_input_switch_ui_elements,
                
            ),
            ui.column(8,
                ui.card(
                    ui.card_header(label),
                    ui.output_plot("plot", click=True)
                ),
                # {"style": "background-color: #eee;"}
            )
    ),
        ui.row(
            ui.row(
                # Filter
                ui.layout_column_wrap(#"450px",
                    ui.card(
                        ui.card_header("Dataset filters"),
                        *rows,
                        max_height="600px",
                        fill=False
                    ),

                    ui.card(
                        ui.card_header("Plot parameters"),
                        ui.page_bootstrap(
                            *plot_input_text_ui_elements, # Unpack plot input ui elements
                            *plot_input_select_ui_elements,
                            *plot_input_numeric_ui_elements,
                            max_height="600px",
                        ),
                    )
                )
             
            
            )
        )
    )



@module.server
def graph_module_server(input: Inputs,
                        output: Outputs,
                        session: Session,  
                        granule_data_reactive_value: reactive.Value[pd.DataFrame], 
                        plot_function: Callable, 
                        plot_parameters: dict[dict[dict]]):
    """Module class for server side handling of plot generation 

    Args:
        input (Inputs): Shiny class containing all ui inputs
        output (Outputs): Shiny class, see Shiny documentation, not in direct use by this code
        session (Session): Shiny class, see Shiny documentation, not in direct use by this code
        granule_data_reactive_value (reactive.Value[pd.DataFrame]): The uploaded pandas dataframe with experiment data
        plot_function (Callable): Function returning matplotlib.figure object and a an optional dataframe with the underlying plot data.  
        plot_parameters (dict[dict[dict]]): Config containing ui and server elements. 
    """
    def determine_bin_edges(parameters_from_user_input):
        """
            Takes in the plot parameters, calculate the number of bins based on n_bins, bin_start and bin_end, then puts the bin edges back into the plot parameters, ready for plotting.
        """
        
        bin_start = input['bin_start']()
        bin_end = input['bin_end']()
        n_bins = input['n_bins']()
        log_scale = input['bin_type']()

        if log_scale == 'log':
            bin_edges = np.geomspace(bin_start, bin_end, n_bins + 1)
            log_scale = True
        elif log_scale == 'linear':
            bin_edges = np.linspace(bin_start, bin_end, n_bins + 1)
            log_scale = False
        else:
            raise ValueError("bin_type must be either 'log' or 'linear'")

        parameters_from_user_input['n_bins'] = bin_edges
        parameters_from_user_input['log_scale'] = log_scale

        return parameters_from_user_input
    
    def determine_log_scale(parameters_from_user_input: dict):
        """
            Determines if the plot should be on a log scale or not.
        """
        log_scale = input['bin_type']()
        if log_scale == 'log':
            log_scale =  True
        elif log_scale == 'linear':
            log_scale =  False
        else:
            raise ValueError("bin_type must be either 'log' or 'linear'")
        
        parameters_from_user_input['log_scale'] = log_scale

        return parameters_from_user_input

    def parse_plot_parameters() -> dict:
        """Parses and returns a 1d dictonary with the plot parameters required for the plot function.
                -> Any non-static elements value is retrieved from the ui. 

        Returns:
            dict: Dictionary with key value pairs for the plotting function
        """
        plot_parameters_from_user_input = dict()
        if plot_function.__name__ == "overlap_hist":
            plot_parameters_from_user_input = determine_bin_edges(plot_parameters_from_user_input) # Update bin edges based on user input
        elif plot_function.__name__ == "violin":
            plot_parameters_from_user_input = determine_log_scale(plot_parameters_from_user_input)
        # Update user input values from corresponding ui input elements. k_2 is the id for each input in ui.
        for k, _ in plot_parameters.items():
            if k in ['allow_multiple_experiments', "plot_type", "allow_internal_plot_data_download"]: # Logic not needed in plot function.
                continue
            for k_2, v_2 in plot_parameters[k].items():
                if k_2 in ['bin_type', 'bin_start', 'bin_end', 'n_bins', "above_res_threshold"]:
                    continue
                if k == "static_input": # If static value, no need to get it from ui
                    plot_parameters_from_user_input[k_2] = v_2['value']
                elif k == 'select_input_dataset_columns':
                    plot_parameters_from_user_input[k_2] = alias_to_column(input[k_2]()) # Get user input from select elements and transform them back into dataframe column name
                else:
                    plot_parameters_from_user_input[k_2] = input[k_2]() # Get user input from ui
        return plot_parameters_from_user_input
    
    @output
    @render.plot(alt="Plot")
    @reactive.event(input.update_plot, input.experiment_selectize_input) 
    def plot():
        """
            Renders a new plot based on the given plot function and its plot-parameters.
            If a file is uploaded or the "Update plot" button is triggered, this function will run.
        """
        if not granule_data_reactive_value.is_set(): # Ensure file has been uploaded 
            return
      
        granule_data_df: pd.DataFrame = granule_data_reactive_value.get() # Call reactive value to get its contents
        plt_params = parse_plot_parameters()
        fig, _ = create_fig(input=input, 
                        granule_data_df=granule_data_df, 
                        plot_function=plot_function,
                        plot_parameters=plt_params)
        return fig
        
    @reactive.Effect
    def update_axies_select(): 
        """
            Update axis selects with dataframe columns.
            Function is triggered when 'granule_data_reactive_value' is changed (a file is uploaded).
        """
        if not granule_data_reactive_value.is_set(): # Ensure file has been uploaded 
            return        
        
        granule_data_df: pd.DataFrame = granule_data_reactive_value.get() # Call reactive value to get its contents
        column_names: list[str] = granule_data_df.columns.to_list()
        filtered_column_names: list[str] = filter_columns(column_names)         # Remove blacklisted columns that should not be shown to user.
        column_alias_names: list[str] = columns_to_alias(filtered_column_names) # Get human readable names for df columns
               
        for k,v in plot_parameters['select_input_dataset_columns'].items():
            ui.update_select(id=k,                                      # Update select elements with column aliases
                             choices=column_alias_names, 
                             selected=column_to_alias(v['selected']))   # Get human readable name for the current selected value
    
    @reactive.Effect
    def update_axis_name_text_input():
        """Updates x and y-axis name/title inputs based on selected columns #TODO: Add error handling for plots not using 'select_input_dataset_columns'. Will it fail if element not found?
           When selecting a new axis to plot, the axis-title input field will auto-update to the new axis name.
        """
        if not granule_data_reactive_value.is_set(): # Ensure file has been uploaded 
            return 
        
        # Check for UI element existing, then update with current selected value
        if input.plot_title.is_set():
            ui.update_text(id='plot_title', value=input.plot_column())
        if input.row_title.is_set():
            ui.update_text(id='row_title', value=input.plot_row())
        if input.bin_title.is_set():
            ui.update_text(id='bin_title', value=input.bin_column())
        if input.plot_label.is_set():
            ui.update_text(id='plot_label', value=input.plot_column())

    @reactive.Effect 
    # @reactive.event(granule_data_reactive_value)
    def update_experiment_selectize_input():
        """ Updates the selectize ui element with experiment names contained in the uploaded dataframe. """
        if not granule_data_reactive_value.is_set(): # Ensure file has been uploaded 
            return 
        granule_data_df: pd.DataFrame = granule_data_reactive_value.get() # Call reactive value to get its contents
        choices: list[str] = granule_data_df['experiment'].unique().tolist()
        ui.update_selectize(id="experiment_selectize_input", choices=choices, selected=choices)

    @reactive.Effect
    @reactive.event(input.modal_download)
    def modal_download():
        internal_plot_download_button = ui.div() # Placeholder
        if plot_parameters['allow_internal_plot_data_download']: # If config set to True, display button
            internal_plot_download_button = ui.tooltip(
                ui.download_button("download_plot_internal_data", "Download figure data (.csv)"),
                "Data downloaded depends on figure type.",
                id="download_plot_internal_data_tool_tip",
            ) 

        m = ui.modal(
            ui.row(
                ui.column(6, 
                      ui.input_numeric(id="download_figure_dpi", label="Dpi", value=300, width="100px"),
                      ui.input_numeric(id="download_figure_padding", label="Padding", value=0.15, width="100px"),
                      ui.input_numeric(id="download_figure_tl_padding", label="Tl padding", value=1.08, width="100px"),
                      ),
                ui.column(6, 
                    #   ui.input_select(id="download_file_format", choices=["png", "svg", "jpeg"], selected="png", label="", width="100px"),
                      ui.input_switch(id="download_figure_despine_axis", label="Despine axis"),
                      ui.input_numeric(id="download_figure_height_inches", label="Height (inches)", value=5, width="100px"),
                      ui.input_numeric(id="download_figure_width_inches", label="Width (inches)", value=8, width="100px"),
                ),
            ),
            ui.download_button("download_plot_png", "Download png"),
            ui.download_button("download_plot_svg", "Download svg"),
            internal_plot_download_button,
            title="Download config",
            easy_close=True,
            footer=None,
        )
        ui.modal_show(m)

    @render.download(filename="plot.png")
    async def download_plot_png():  
        """
            File download implemented by yielding bytes, in this case all at
            once (the entire plot). Filename is determined in the @session.Download decorator ontop of function.
            This determines what the browser will name the downloaded file.     
        """
        if not granule_data_reactive_value.is_set(): # Ensure file has been uploaded 
                return
        
        with io.BytesIO() as buf:
            granule_data_df: pd.DataFrame = granule_data_reactive_value.get()
            fig = create_download_figure(input=input, 
                                         granule_data_df=granule_data_df, 
                                         plot_function=plot_function, 
                                         plot_parameters=parse_plot_parameters(),
                                         save_buffer=buf,
                                         filetype="png")
            yield buf.getvalue()
            plt.close(fig=fig)

    @render.download(filename="plot.svg")
    async def download_plot_svg():  
        if not granule_data_reactive_value.is_set(): # Ensure file has been uploaded 
                return
        
        with io.BytesIO() as buf:
            granule_data_df: pd.DataFrame = granule_data_reactive_value.get()
            fig = create_download_figure(input=input, 
                                         granule_data_df=granule_data_df, 
                                         plot_function=plot_function, 
                                         plot_parameters=parse_plot_parameters(),
                                         save_buffer=buf,
                                         filetype="svg")
            yield buf.getvalue()
            plt.close(fig=fig)


    @render.download(filename="plot_internal_data.csv")
    async def download_plot_internal_data():  
        """
            Downloads the internal data of {plot_function} as .csv
        """
        if not granule_data_reactive_value.is_set(): # Ensure file has been uploaded 
                return
        
        if not plot_parameters['allow_internal_plot_data_download']:
            raise Exception("'allow_internal_plot_data_download' config is set to False. Cannot download interal plot data.")

        with io.BytesIO() as buf:
            granule_data_df: pd.DataFrame = granule_data_reactive_value.get()
            fig, plot_data_df = create_fig(input=input, 
                                            granule_data_df=granule_data_df, 
                                            plot_function=plot_function, 
                                            plot_parameters=parse_plot_parameters())

        with io.BytesIO() as buf:
            plot_data_df.to_csv(buf)
            yield buf.getvalue()
            plt.close(fig=fig)

        





# TODO: Create a new class/file for this logic
column_aliases = { 
                "times":"Times(s)",
                "sigma": "Interfacial Tension (N/m)",
                "kappa_scale": "Bending Rigidity $(k_BT)$",
                "sigma_err": "Interfacial Tension Error (N/m)",
                "kappa_scale_err": "Bending Rigidity Error $(k_BT)$",
                "fitting_error": "Fitting Error",
                "q_2_mag": "Circularity",
                "mean_radius":"Mean Radius (µm)",
                "pass_rate":"Pass Rate",
                "mean_intensity":"Mean Intensity"}
column_filter = ['granule_id','image_path','x','y','bbox_left','bbox_bottom','bbox_right','bbox_top','figure_path', 'treatment', "experiment"]

def filter_columns(column_names: list[str]) -> list[str]:
    """
        Removes columns user should not see.
    """
    filtered_column_names = [column for column in column_names if column not in column_filter]
    return filtered_column_names

def columns_to_alias(column_names: list[str]) -> list[str]:
    """
        Returns list of column names replaced with human readable aliases.
        If no alias is found it defaults to returning column name 
    """
    filtered_names = filter_columns(column_names) # Remove columns user should not see

    for i in range(len(filtered_names)):
        if filtered_names[i] in column_aliases.keys():
            filtered_names[i] = column_aliases[filtered_names[i]]
    return filtered_names

def column_to_alias(column_name: str) -> str:
    """
        Returns alias name corresponding to given column. 
        If no alias is found, returns column_name.
    """
    if column_name in column_aliases.keys():
        return column_aliases[column_name]
    return column_name

def alias_to_column(alias: str) -> str:
    """ 
        Returns column name corresponding to given alias. 
        If no column is found, returns alias.
    """
    for k,v in column_aliases.items():
        if v == alias:
            return k # Return alias
    return alias # No alias for input




    
