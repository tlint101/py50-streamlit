"""
Page-specific helpers for the Calculator page.
Extracted from page/Calculator.py for better maintainability.
"""

import streamlit as st
import pandas as pd
import numpy as np


def load_page_css():
    """Load the standard hyperlink color scheme used across pages."""
    links = """<style>
a:link , a:visited{
    color: 3081D0;
    background-color: transparent;
}

a:hover,  a:active {
    color: forestgreen;
    background-color: transparent;
}
"""
    st.markdown(links, unsafe_allow_html=True)


def render_page_title(tutorial, datasets):
    """Render the page title, description, and sample data links."""
    st.markdown('# Calculate Relative and Absolute IC50')
    st.write('This page will calculate a final table containing Relative and Absolute IC50 values for a queried drug.')
    st.write('The program requires at least three columns:')
    st.write('- Drug Name')
    st.write('- Drug Concentration')
    st.write('- Average Response')
    st.write('For more information about Relative vs. Absolute IC50, please see the tutorial [here](%s)' % tutorial)
    st.write('Sample datasets can be found [here](%s)' % datasets)
    st.write('')


def render_data_input(option):
    """Render the data input section based on the selected option.

    :param option: str
        One of 'Paste Data', 'Upload CSV File', 'IC50 to pIC50 Calculator'
    :return: tuple
        (uploaded_file or edited_df or data_frame, paste flag)
    """
    calc = None

    if option == 'Upload CSV File':
        uploaded_file = st.file_uploader('Upload .csv file')

        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file)
            st.write('## Input Table')
            st.data_editor(data, num_rows='dynamic')
            return uploaded_file, False

        else:
            st.warning('Please upload a .csv file.')
            return None, False

    elif option == 'Paste Data':
        st.markdown('### Paste Data in Table:')
        data = pd.DataFrame([{"Drug Name": '', 'Concentration': '', 'Response': ''}, ])

        def data_paste(data):
            data_info = st.data_editor(data, num_rows='dynamic')
            return data_info

        edited_df = data_paste(data)

        if (edited_df == '').all().all():
            st.write('Table is currently empty')
            return edited_df, True
        else:
            return edited_df, True

    else:
        st.markdown('### Insert your IC50 Value (in nM):')
        input_ic50 = st.number_input('Insert IC50 Value (in nM)', step=1e-6)

        if input_ic50 > 0:
            pic50 = -np.log10(input_ic50 * 0.000000001)
        else:
            st.write(':red[**Input cannot be 0 or a negative number!**]')

        data = pd.DataFrame([{'Notes': '', 'IC50 (nM)': input_ic50, 'pIC50': pic50}])

        def download_df(self, df, file_name=None):
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download table as CSV", data=csv, file_name=file_name, mime="text/csv"
            )

        def data_paste(data):
            data_info = st.data_editor(data, num_rows='dynamic')
            return data_info

        edited_df = data_paste(data)
        return edited_df, False


def render_calculation_results(calc, df, paste):
    """Render the IC50 calculation results and pIC50 conversion option."""
    calc.calculator_program(df=df, paste=paste)


def render_page_options():
    """Render the option radio button for data input method."""
    st.markdown('## Select an option to get started:')
    option = st.radio(
        'Options are paste or .csv file upload',
        ('Paste Data', 'Upload CSV File', 'IC50 to pIC50 Calculator'))
    return option
