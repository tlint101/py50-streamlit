"""
Functions for statistics.
"""

import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
from py50.stats import Plots, Stats

"""
NOTE: Classes for Plots and Stats should be initialized AFTER processing the data.
"""


class Stats_Logic:

    def __init__(self):
        pass

    def download_button(self, df, file_name=None):
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button('Download table as CSV', data=csv, file_name=file_name, mime='text/csv')

    def stats_program(self, data: pd.DataFrame = None, paste: bool = False):
        """
        Function for statistics.
        :param data: pd.DataFrame
            Input pd.DataFrame
        :return: editable DataFrame
        """

        if paste:
            data = data.copy()
            col_header = data.columns.tolist()

            # Set selection columns
            col1, col2, col3 = st.columns(3)
            col_header.insert(0, 'None')  # Add None option
            with col1:
                group_col = st.selectbox('Group:', (col_header), index=1)
            with col2:
                dv_col = st.selectbox('Dependent Variable:', (col_header), index=2)  # Index to auto select column
            with col3:
                subgroup_col = st.selectbox('Subgroup (Optional):', (col_header), index=0,
                                            placeholder="None")  # Index to auto select column
        else:
            data = data.copy()
            col_header = data.columns.tolist()

            # Set selection columns
            col1, col2, col3 = st.columns(3)
            col_header.insert(0, 'None')  # Add None option
            with col1:
                group_col = st.selectbox('Group:', (col_header), index=None, placeholder="Select Group")
            with col2:
                dv_col = st.selectbox('Dependent Variable:', (col_header), index=None,
                                      placeholder="Select DV")  # Index to auto select column
            with col3:
                subgroup_col = st.selectbox('Subgroup (Optional):', (col_header), index=None,
                                            placeholder="Select Subgroup")  # Index to auto select column

        # Conditional after selecting columns for calculation
        if subgroup_col == "Group" and subgroup_col == "Dependent Variable" and subgroup_col == None:
            st.write("HELLO!")
            st.write(data)
        elif subgroup_col == None:
            st.write(data)
        elif subgroup_col == "None":
            st.write("Subgroup column set to None")
            st.write(data)

        if data.isnull().all().any():
            # Drop columns where all values are NaN
            data = data.drop(columns='Subgroup')
            # data.dropna(axis=1, how='all', inplace=True)
            st.write("there's null?")

        # st.write(data)
        # plot = Plots(data)
        stats = Stats(data)

        st.write('## Test for Normality?')
        normality = st.toggle('Test for Normality')

        if normality:

            normality = stats.get_normality(value_col=dv_col, group_col=group_col).round(3)
            st.write('**Note:** Check mark means True')

            st.data_editor(normality, num_rows='dynamic')
            self.download_button(normality, 'py50_normality.csv')
        else:
            st.write('# NOTHING IS HAPPENING!!!')
