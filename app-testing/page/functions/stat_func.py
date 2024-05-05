"""
Functions for statistics.
"""

import streamlit as st

class Stats:

    def __init__(self):
        pass

    def download_button(self, df, file_name=None):
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button('Download table as CSV', data=csv, file_name=file_name, mime='text/csv')