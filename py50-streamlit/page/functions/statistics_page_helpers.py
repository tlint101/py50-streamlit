"""
Page-specific helpers for the Statistics page.
Extracted from page/Statistics.py for better maintainability.
"""

import streamlit as st
import pandas as pd


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
    st.markdown('# Statistics Calculator')
    st.write('The Statistics Calculator provides 3 columns:')
    st.write('- Group')
    st.write('- Dependent Variable')
    st.write('- Subgroup')
    st.write('Depending on the test selected, only Group and Dependent Variable is needed. Subgroup can be ignored.')
    st.write('For more information on how the statistics calculator works in py50, see the tutorial [here](%s)' % tutorial)
    st.write('Sample datasets can be found [here](%s)' % datasets)
    st.write('')


def render_data_input(option):
    """Render the data input section based on the selected option.

    :param option: str
        One of 'Paste Data' or 'Upload CSV File'
    :return: tuple
        (df or uploaded_file, paste flag)
    """
    if option == 'Upload CSV File':
        uploaded_file = st.file_uploader('Upload .csv file')

        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file)
            st.write('## Input Table')
            st.data_editor(data, num_rows='dynamic', key='uploaded_output')  # visualize dataframe in streamlit app
            return uploaded_file, False

        else:
            st.warning('Please upload a .csv file.')
            return None, False

    elif option == 'Paste Data':
        st.markdown('### Paste Data in Table:')
        data = pd.DataFrame([{"Group": '', 'Dependent Variable': '', 'Subgroup': ''}, ])

        edited_df = st.data_editor(data, num_rows='dynamic', key='paste_data')

        if (edited_df == '').all().all():
            st.write('Table is currently empty')
            return edited_df, True
        else:
            return edited_df, True


def render_statistics_page(stats, data, paste):
    """Render the statistics program.

    :param stats: Stats_Logic instance
    :param data: pandas DataFrame
    :param paste: bool
    """
    st.write("### Select Columns for Calculation")
    stats.stats_program(data=data, paste=paste)
