"""
Functions for statistics.
"""

import streamlit as st
import pandas as pd
from py50.stats import Plots


class Stats:

    def __init__(self):
        pass

    @staticmethod
    def download_button(df, file_name=None):
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button('Download table as CSV', data=csv, file_name=file_name, mime='text/csv')

    @staticmethod
    def stats_program(data: pd.DataFrame = None, paste: bool = False):
        """
        Function for statistics.
        :param data: pd.DataFrame
            Input pd.DataFrame
        :return: editable DataFrame
        """

        if paste:
            data = data.copy()
            col_header = data.columns.tolist()
            group_col = st.selectbox('Group:', (col_header))
            dv_col = st.selectbox('Dependent Variable:', (col_header), index=1)  # Index to auto select column
            subgroup_col = st.selectbox('Subgroup:', (col_header), index=2)  # Index to auto select column
        else:
            data = data.copy()
            col_header = data.columns.tolist()
            group_col = st.selectbox('Group:', (col_header))
            dv_col = st.selectbox('Dependent Variable:', (col_header), index=1)  # Index to auto select column
            subgroup_col = st.selectbox('Subgroup:', (col_header), index=2)  # Index to auto select column
