from shiny import App, Inputs, Outputs, Session, module, render, ui, reactive
from shiny.types import ImgData, FileInfo
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as co
import io
from typing import Callable

from plotting_tools.create_plot import filter_dataset

from flickerprint.analysis.statistics import population_statistics, create_stats_csv

pd.options.mode.copy_on_write = True

allow_multiple_experiments = False

@module.ui
def stats_module_ui():

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
                ui.page_bootstrap(ui.input_action_button("update_stats", "Update Statistics", style="background-color: #b6e0b1"),),
                ui.page_bootstrap(ui.download_button(id="pop_stats_download", label="Save Statistics"),),
                ui.hr(),

                # Unpack ui elemets from list
                ui.input_selectize(id="experiment_selectize_input", label="Select experiments", choices=[""], multiple=allow_multiple_experiments, width="100%"),
                ui.input_switch(id="above_res_threshold", label="Above resolution threshold", value=True),
                ui.row(),
                ui.row(
                # Filter
                ui.layout_column_wrap(#"450px",
                    ui.card(
                        ui.card_header("Dataset filters"),
                        *rows,
                        fill=False
                    ),
                    )
                )
                
            ),
            ui.column(8,
                ui.card(
                    ui.card_header("Population Statistics"),
                    ui.output_table(id="table", label="Statistics", width="100%"),
                    "Statistics provided are based on the selected dataset filters. ",
                    ui.br(),
                    ui.br(),
                    "Where applicable, the geometric mean is used. ",
                    "This is indicated by the 'Geometirc Distribution' column.",
                    ui.br(), 
                    "The range between 'Mean - 1SD' and 'Mean + 1SD' contains 67% of the samples. ",
                    "This is the linear Standard Deviation or the equivalent metric for a geometirc distribution.",
                    id = "table_card"
                ),
                # {"style": "background-color: #eee;"}
            )
    ),
        ui.row(
            
             
            
            )
        )




@module.server
def stats_module_server(input: Inputs,
                        output: Outputs,
                        session: Session,
                        granule_data_reactive_value: reactive.value[pd.DataFrame]
                        ):
        

    @output
    @render.table
    @reactive.event(input.update_stats, input.experiment_selectize_input)
    def table():
        if not granule_data_reactive_value.is_set(): # Ensure file has been uploaded 
            return
        granule_data_df: pd.DataFrame = granule_data_reactive_value.get()
        granule_data_df = filter_dataset(input, granule_data_df)
        if not allow_multiple_experiments:
            expt = str(input.experiment_selectize_input())
            granule_data_df.query("experiment == @expt", inplace=True)
        summary_table = population_statistics(granule_data_df, _gui = True)
        return summary_table[list(summary_table.keys())[0]]
    
    @reactive.Effect 
    def update_experiment_selectize_input():
        """ Updates the selectize ui element with experiment names contained in the uploaded dataframe. """
        if not granule_data_reactive_value.is_set(): # Ensure file has been uploaded 
            return 
        granule_data_df: pd.DataFrame = granule_data_reactive_value.get() # Call reactive value to get its contents
        choices: list[str] = granule_data_df['experiment'].unique().tolist()
        ui.update_selectize(id="experiment_selectize_input", choices=choices, selected=choices)
    

    @render.download(filename="stats_data.csv")
    async def pop_stats_download():  
        """
            Downloads the statistics as .csv
        """
        if not granule_data_reactive_value.is_set(): # Ensure file has been uploaded 
                print("No data loaded")
                return

        with io.BytesIO() as buf:
            granule_data_df: pd.DataFrame = granule_data_reactive_value.get()
            granule_data_df = filter_dataset(input, granule_data_df)
            summary_table = population_statistics(granule_data_df, _gui = False)
            create_stats_csv(summary_table, buf)
            yield buf.getvalue()