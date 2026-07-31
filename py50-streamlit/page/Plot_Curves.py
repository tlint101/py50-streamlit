import streamlit as st
import pandas as pd
from page.functions.curve_func import Plot_Logic
from page.functions.plot_curves_page_helpers import (
    load_page_css,
    render_page_title,
    render_data_input,
    render_plot_page,
)

datasets = "https://github.com/tlint101/py50/tree/main/dataset"

# Load page styling
load_page_css()

# Render page title and description
render_page_title(datasets)

# User selects type of interface
option = st.radio(
    "Options are paste or .csv file upload",
    (
        "Paste Data",
        "Upload CSV File",
    ),
)

program = Plot_Logic()

# Handle data input
uploaded_file, paste = render_data_input(option)

if uploaded_file is not None:
    # Render plot program for uploaded file
    render_plot_page(program, uploaded_file, paste=False)

elif option == "Paste Data":
    # Render plot program for pasted data
    rendered_df, paste = render_data_input(option)
    render_plot_page(program, rendered_df, paste=True)
