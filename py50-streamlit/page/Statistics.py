import streamlit as st
import pandas as pd
from page.functions.stat_func import Stats_Logic
from page.functions.statistics_page_helpers import (
    load_page_css,
    render_page_title,
    render_data_input,
    render_statistics_page,
)

tutorial = 'https://github.com/tlint101/py50/blob/main/tutorials/006_statistics_quickstart.ipynb'
datasets = 'https://github.com/tlint101/py50-streamlit/tree/main/dataset'

# Load page styling
load_page_css()

# Render page title and description
render_page_title(tutorial, datasets)

# User selects data input method
option = st.radio(
    'Paste Data or upload .csv file',
    ('Paste Data', 'Upload CSV File'))

stats = Stats_Logic()

# Handle data input
uploaded_file, paste = render_data_input(option)

if uploaded_file is not None:
    # Render statistics page for uploaded file
    render_statistics_page(stats, uploaded_file, paste=False)

elif option == 'Paste Data':
    # Render statistics page for pasted data
    rendered_df, paste = render_data_input(option)
    render_statistics_page(stats, rendered_df, paste=True)
