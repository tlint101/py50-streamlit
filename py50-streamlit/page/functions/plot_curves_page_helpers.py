"""
Page-specific helpers for the Plot_Curves page.
Extracted from page/Plot_Curves.py for better maintainability.
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


def render_page_title(datasets):
    """Render the page title, description, and sample data links."""
    st.markdown("# Generate Dose-Response Curves")
    st.write(
        "This page will plot a dose-response curve. The plot points will be calculated for each query."
    )
    st.write("The program requires at least three columns:")
    st.write("- Drug Name")
    st.write("- Drug Concentration")
    st.write("- Average Response")
    st.write("Sample datasets can be found [here](%s)" % datasets)
    st.write("")


def render_data_input(option):
    """Render the data input section based on the selected option.

    :param option: str
        One of 'Paste Data' or 'Upload CSV File'
    :return: tuple
        (df or uploaded_file, paste flag)
    """
    if option == "Upload CSV File":
        uploaded_file = st.file_uploader("Upload .csv file")

        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write("## Input Table")
            st.data_editor(
                df, num_rows="dynamic"
            )  # visualize dataframe in streamlit app
            return uploaded_file, False

        else:
            st.warning("Please upload a .csv file.")
            return None, False

    elif option == "Paste Data":
        st.markdown("### Paste Data in Table:")
        df = pd.DataFrame(
            [
                {"Drug Name": "", "Concentration": "", "Response": ""},
            ]
        )

        edited_df = st.data_editor(df, num_rows="dynamic")

        if (edited_df == "").all().all():
            st.write("Table is currently empty")
            return edited_df, True
        else:
            return edited_df, True


def render_plot_page(program, df, paste):
    """Render the plot program for dose-response curves.

    :param program: Plot_Logic instance
    :param df: pandas DataFrame
    :param paste: bool
    """
    st.write("### Select Columns for Calculation")
    program.plot_program(df=df, paste=paste)
