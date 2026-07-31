import streamlit as st
import pandas as pd
import numpy as np
from page.functions.calculator_func import Calc_Logic
from page.functions.calculator_page_helpers import (
    load_page_css,
    render_page_title,
    render_data_input,
    render_calculation_results,
    render_page_options,
)

tutorial = 'https://github.com/tlint101/py50/blob/main/tutorials/002_absolute_ic50.ipynb'
datasets = 'https://github.com/tlint101/py50/tree/main/dataset'

# Load page styling
load_page_css()

# Render page title and description
render_page_title(tutorial, datasets)

# Render data input options
option = render_page_options()

# Create Calc_Logic instance
calc = Calc_Logic()

# Handle data input and calculation
uploaded_file, paste = render_data_input(option)

if uploaded_file is not None:
    # Render calculation results for uploaded file
    render_calculation_results(calc, uploaded_file, paste=False)

elif option == 'Paste Data':
    # Render calculation results for pasted data
    rendered_df, paste = render_data_input(option)
    if paste:
        render_calculation_results(calc, rendered_df, paste=True)

else:
    # Render IC50 to pIC50 calculator
    rendered_df, _ = render_data_input(option)
    calc.download_button(rendered_df, file_name='py50_pic50.csv')
