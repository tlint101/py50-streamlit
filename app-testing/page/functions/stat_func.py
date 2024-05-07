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

    def download_button(self, df, file_name=None, index=False):
        csv = df.to_csv(index=index).encode('utf-8')
        st.download_button('Download table as CSV', data=csv, file_name=file_name, mime='text/csv')

    def stats_program(self, data: pd.DataFrame = None, paste: bool = False):
        """
        Function for statistics.
        :param data: pd.DataFrame
            Input pd.DataFrame
        :param paste: bool
            To determine if the stats program will be pasted or uploaded data.
        :return: editable DataFrame
        """

        global select, selected
        if paste:
            col_header = data.columns.tolist()

            # Set selection columns
            col1, col2, col3 = st.columns(3)

            col_header.insert(0, 'None')  # Add None option
            with col1:
                group_col = st.selectbox('Group:', col_header, index=1)
            with col2:
                dv_col = st.selectbox('Dependent Variable:', col_header, index=2)  # Index to auto select column
            with col3:
                subgroup_col = st.selectbox('Subgroup (Optional):', col_header, index=0,
                                            placeholder="None")  # Index to auto select column
        else:
            col_header = data.columns.tolist()

            # Set selection columns
            col1, col2, col3 = st.columns(3)

            col_header.insert(0, 'None')  # Add None option
            with col1:
                group_col = st.selectbox('Group:', col_header, index=None, placeholder="Select Group")
            with col2:
                dv_col = st.selectbox('Dependent Variable:', col_header, index=None,
                                      placeholder="Select DV")  # Index to auto select column
            with col3:
                subgroup_col = st.selectbox('Subgroup (Optional):', col_header, index=None,
                                            placeholder="Select Subgroup")  # Index to auto select column

        # Select columns
        self.column_selection(data, dv_col, group_col, subgroup_col, paste)

        # run_normality
        self.run_normality(dv_col, group_col, selected)

    def run_normality(self, dv_col, group_col, selected):
        """
        Function to run normality test.
        :param dv_col:
        :param group_col:
        :param selected:
        :return:
        """
        st.write('## Test for Normality?')
        normality = st.toggle('Test for Normality')
        stats = Stats(selected)
        if normality:
            col1, col2 = st.columns(2)

            with col1:
                normality = stats.get_normality(value_col=dv_col, group_col=group_col).round(3)
                st.write('**Note:** Check mark means True')

                st.data_editor(normality, num_rows='dynamic')
                self.download_button(normality, index=True, file_name='py50_normality.csv')

            with col2:
                normality_plot = st.toggle('Plot for Normality')
                st.write('PLACEHOLDER')

    def column_selection(self, data, dv_col, group_col, subgroup_col, paste):
        """
        Function to select columns for statistics calculator.
        :param data:
        :param dv_col:
        :param group_col:
        :param subgroup_col:
        :param paste:
        :return:
        """
        global select, selected
        # Conditional after selecting columns for calculation
        if group_col is not None and dv_col is not None:
            st.write('Current Selection')
            select = data.copy()
            selected = select[[group_col, dv_col]]
            st.write(selected)

            if paste:
                # Pasting data does not ensure correct format. Must enforce!
                selected['Group'] = select['Group'].astype(str)
                selected['Dependent Variable'] = select['Dependent Variable'].astype(float)

        elif subgroup_col == None:
            st.write('Current Selection')
            selected = data.copy()

            # Pasting data does not ensure correct format. Must enforce!
            selected['Group'] = selected['Group'].astype(str)
            selected['Dependent Variable'] = selected['Dependent Variable'].astype(float)

        elif subgroup_col == "None":
            st.write("Subgroup column set to None")
            select = data.copy()
            selected = select.drop(columns=['Subgroup'])

            # Pasting data does not ensure correct format. Must enforce!
            selected['Group'] = selected['Group'].astype(str)
            selected['Dependent Variable'] = selected['Dependent Variable'].astype(float)
#
# def run_normality(data, group_col, dv_col):