import platform
from shiny import App, render, ui, reactive
from shiny.types import ImgData, FileInfo
import webbrowser
# from pathlib import Path
from numpy import random 
import pandas as pd
import matplotlib.pyplot as plt
import shinyswatch
import sys
import pathlib
import os
import signal
plt2 = platform.system()
if plt2 == 'Windows': pathlib.PosixPath = pathlib.WindowsPath

# Modules
from modules.graph_module import graph_module_ui, graph_module_server
from modules.stats_module import stats_module_ui, stats_module_server
from modules.file_upload_module import file_upload_module_ui, file_upload_module_server

import flickerprint.analysis.plotting as plotting

twoDHist_plot_input_options={
    'plot_type': "histogram",
    'allow_internal_plot_data_download': True,
    'allow_multiple_experiments':False,
    'text_input': dict({
         "row_title":dict({
            'value':"Interfacial Tension (N/m)", 
            'label':"X-axis title"
        }),
        "plot_title":dict({
            'value':"Bending Rigidity $(k_BT)$", 
            'label':"Y-axis title"
        }),
    }),
    'numeric_input': dict({}),
    'bool_input':dict({
        #Sliders and such
        'legend':dict({
            'value':False, 
            'label':'legend'
        }),
        'log_scaleX':dict({
            'value':True, 
            'label':'log_scaleX'
        }),
        'log_scaleY':dict({
            'value':True, 
            'label':'log_scaleY'
        }),
        'above_res_threshold':dict({
            'value':True,
            'label':'Above resolution threshold'
        }),
    }),
    'select_input':dict({
        # Custom select inputs. Parameters are ui.input_select() parameters
        # "option1":dict({'label':'option1', 'choices':['option1', 'option2'], 'selected':"option1"}),
        # "option2":dict({'label':'option2', 'choices':['option1', 'option2'], 'selected':"option2"}),
    }),
    'select_input_dataset_columns':dict({
        # Select inputs that are automatically populated with the columns of the dataset
        # Parameters are ui.input_select() parameters
        "plot_row":dict({'label':'X-axis', 'choices':['Interfacial Tension (N/m)'], 'selected':"Interfacial Tension (N/m)"}),
        "plot_column":dict({'label':'Y-axis', 'choices':['Bending Rigidity $(k_BT)$'], 'selected':"Bending Rigidity $(k_BT)$"}),
    }),
    'static_input':dict({
        #Inputs that will not change. These will not create ui compenents and are only used server side.
    }),
}
    
scatter_plot_input_options={
    'plot_type': "scatter",
    'allow_internal_plot_data_download': True,
    'allow_multiple_experiments':False,
    'text_input': dict({
        "plot_title":dict({
            'value':"Interfacial Tension Error (N/m)", 
            'label':"Y-axis title"
        }),
        "row_title":dict({
            'value':"Interfacial Tension (N/m)", 
            'label':"X-axis title"
        }),
    }),
    'numeric_input': dict({}),
    'bool_input':dict({
        #Sliders and such
        'legend':dict({
            'value':True, 
            'label':'legend'
        }),
        'log_scaleX':dict({
            'value':True, 
            'label':'log_scaleX'
        }),
        'log_scaleY':dict({
            'value':True, 
            'label':'log_scaleY'
        }),
        'above_res_threshold':dict({
            'value':True,
            'label':'Above resolution threshold'
        }),
    }),
    'select_input':dict({
        # Custom select inputs. Parameters are ui.input_select() parameters
    }),
    'select_input_dataset_columns':dict({
        # Select inputs that are automatically populated with the columns of the dataset
        # Parameters are ui.input_select() parameters
        "plot_column":dict({'label':'Y-axis', 'choices':['Interfacial Tension Error (N/m)'], 'selected':"Interfacial Tension Error (N/m)"}),
        "plot_row":dict({'label':'X-axis', 'choices':['Interfacial Tension (N/m)'], 'selected':"Interfacial Tension (N/m)"})
    }),
    'static_input':dict({
        #Inputs that will not change. These will not create ui compenents and are only used server side.
    }),
}

filter_plot_input_options={
    'plot_type': "filter",
    'allow_internal_plot_data_download': True,
    'allow_multiple_experiments':False,
    'text_input': dict({
        "plot_title":dict({
            'value':"Interfacial Tension Error (N/m)", 
            'label':"Y-axis title"
        }),
        "bin_title":dict({
            'value':"Interfacial Tension (N/m)", 
            'label':"X-axis title"
        }),
    }),
    'numeric_input': dict({
        "n_bins":dict({
            'value':5, 
            'label':"Number of bins"
        })
    }),
    'bool_input':dict({
        #Sliders and such
        'legend':dict({
            'value':True, 
            'label':'legend'
        }),
        'x_log_scale':dict({
            'value':False, 
            'label':'log_scale'
        }),
        'y_log_scale':dict({
            'value':False, 
            'label':'log_scale'
        }),
        'errors':dict({
            'value':False, 
            'label':'errors'
        }),
        'above_res_threshold':dict({
            'value':True,
            'label':'Above resolution threshold'
        }),
    }),
    'select_input':dict({
        # Custom select inputs. Parameters are ui.input_select() parameters
        "bin_type":dict({'label':'Bin type', 'choices':['count', 'radius', 'log'], 'selected':"count"}),
    }),
    'select_input_dataset_columns':dict({
        # Select inputs that are automatically populated with the columns of the dataset
        # Parameters are ui.input_select() parameters
        "bin_column":dict({'label':'X-axis', 'choices':['Interfacial Tension (N/m)'], 'selected':"Interfacial Tension (N/m)"}),
        "plot_column":dict({'label':'Y-axis', 'choices':['Bending Rigidity $(k_BT)$'], 'selected':"Bending Rigidity $(k_BT)$"}),
    }),
    'static_input':dict({
        #Inputs that will not change. These will not create ui compenents and are only used server side.
    }),
}

overlap_hist_plot_input_options={
    'plot_type': "overlap_histogram",
    'allow_internal_plot_data_download': True,
    'allow_multiple_experiments':True, # Allow user to select mutiple experiment
    'text_input': dict({
        "plot_label":dict({
            'value':"Interfacial Tension (N/m)", 
            'label':"X-axis title"
        }),
    }),
    'numeric_input': dict({
        "n_bins":dict({
            'value':60, 
            'label':"Number of bins"
        }),
        "bin_start":dict({
            'value':5e-10, 
            'label':"Bin start value"
        }),
        "bin_end":dict({
            'value':1e4, 
            'label':"Bin end value"
        })
    }),
    'bool_input':dict({
        #Sliders and such
        'legend':dict({
            'value':True, 
            'label':'Legend'
        }),
        'density':dict({
            'value':False, 
            'label':'Density'
        }),
        'above_res_threshold':dict({
            'value':True,
            'label':'Above resolution threshold'
        }),
    
    }),
    'select_input':dict({
        # Custom select inputs. Parameters are ui.input_select() parameters
        "bin_type":dict({'label':'X-axis scale', 'choices':['linear','log'], 'selected':"log"}),
        "plot_errors":dict({'label': 'Error Bars', 'choices': {'None': 'None', 'sigma_err': 'Interfacial Tension Error (N/m)', "kappa_scale_err": "Bending Rigidity Error (KBT)"}, 'selected': 'None'}),
    }),
    'select_input_dataset_columns':dict({
        # Select inputs that are automatically populated with the columns of the dataset
        # Parameters are ui.input_select() parameters
        "plot_column":dict({'label':'X-axis', 'choices':['Interfacial Tension (N/m)'], 'selected':"Interfacial Tension (N/m)"}),
    }),
    'static_input':dict({
        #Inputs that will not change. These will not create ui compenents and are only used server side.
    }),
}

violin_plot_input_options={
    'plot_type': "violin",
    'allow_internal_plot_data_download': False,
    'allow_multiple_experiments':True, # Allow user to select mutiple experiment
    'text_input': dict({
        "plot_label":dict({
            'value':"Interfacial Tension (N/m)", 
            'label':"Y-axis title"
        }),
    }),
    'numeric_input': dict({}),
    'bool_input':dict({
        'above_res_threshold':dict({
            'value':True,
            'label':'Above resolution threshold'
        }),
    }),
    'select_input':dict({
        # Custom select inputs. Parameters are ui.input_select() parameters
        "bin_type":dict({'label':'Y-axis Scale', 'choices':['linear','log'], 'selected':"log"}),
    }),
    'select_input_dataset_columns':dict({
        # Select inputs that are automatically populated with the columns of the dataset
        # Parameters are ui.input_select() parameters
        "plot_column":dict({'label':'Y-axis', 'choices':['Interfacial Tension (N/m)'], 'selected':"Interfacial Tension (N/m)"}),
    }),
    'static_input':dict({
        #Inputs that will not change. These will not create ui compenents and are only used server side.
    }),
}
# UI
app_ui = ui.page_fluid(
        ui.page_sidebar(
            ui.sidebar(
                file_upload_module_ui("global_file_upload"),
                bg = "#F0F0F0",
                fillable=True,
            ),
        
        ui.panel_title("FlickerPrint Visualisation Tool", "FlickerPrint"),
        ui.navset_tab(
            # Nav elements
            ui.nav_panel("1D Histogram", 
                graph_module_ui(id="overlap_hist", label="1D Histogram", plot_input_options=overlap_hist_plot_input_options)
            ),
            ui.nav_panel("2D Histogram", 
                graph_module_ui(id="2dhistogram", label="2D Histogram", plot_input_options=twoDHist_plot_input_options)
            ),
            ui.nav_panel("Violin Plot", 
                graph_module_ui(id="violin_plot", label="Violin Plot", plot_input_options=violin_plot_input_options)
            ),
            ui.nav_panel("Population Statistics", 
                         stats_module_ui(id="population_stats"),
            ),
            #"Some text", ui.input_action_button(id="stats_download", label="Download Population Statistics as CSV")),#ui.output_text("This is a work in progress. Please check back later.")),
            ui.nav_spacer(),
            ui.nav_control(ui.input_action_button(id="exit", label="Close App", style = "color:#FF0000")),
            
        ),
        ),
)
   
# Server
def server(input, output, session):
    # Handle file upload
    granule_data_reactive_value: reactive.Value[list[pd.DataFrame]] = file_upload_module_server("global_file_upload")

    # Graph modules
    graph_module_server(id="overlap_hist", granule_data_reactive_value=granule_data_reactive_value, plot_function=plotting.overlap_hist, plot_parameters=overlap_hist_plot_input_options) # Pass data to graph module
    graph_module_server(id="2dhistogram", granule_data_reactive_value=granule_data_reactive_value, plot_function=plotting.histogram2D, plot_parameters=twoDHist_plot_input_options) # Pass data to graph module
    graph_module_server(id="violin_plot", granule_data_reactive_value=granule_data_reactive_value, plot_function=plotting.violin, plot_parameters=violin_plot_input_options) # Pass data to graph module

    # Population statistics
    stats_module_server(id="population_stats", granule_data_reactive_value=granule_data_reactive_value)

    # Handle shutting down the app
    @reactive.Effect
    @reactive.event(input.exit, ignore_none=True)
    async def stop_app():
        m = ui.modal(
            "You can safely close this browser tab.",
            title="Application Closed",
            easy_close=False,
            footer=None,
        )
        ui.modal_show(m)
        await session.app.stop()
        os.kill(os.getpid(), signal.SIGTERM)
        print("\n\nAppllication closed. It is now safe to close this terminal window. \n\n")
        
app = App(ui=app_ui, server=server)
webbrowser.open("http://127.0.0.1:8000", new=2) # Open web browser
