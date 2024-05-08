"""
Functions for statistics.
"""

import streamlit as st
import pandas as pd
import io
from matplotlib import pyplot as plt
from py50.stats import Plots, Stats

"""
NOTE: Classes for Plots and Stats should be initialized AFTER processing the data.
"""


class Stats_Logic:

    def __init__(self):
        pass

    def download_csv(self, df, file_name=None, index=False):
        csv = df.to_csv(index=index).encode('utf-8')
        st.download_button('Download table as CSV', data=csv, file_name=file_name, mime='text/csv')

    def download_fig(self, fig, file_name):
        # Figure must be converted into a temporary file in memory
        buf = io.BytesIO()
        # plt.savefig(buf, format='png', dpi=300)
        fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        buf.seek(0)

        # Create a download button
        st.download_button("Download Figure", data=buf.read(), file_name=file_name, mime="image/png")

    def stats_program(self, data: pd.DataFrame = None, paste: bool = False):
        """
        Function for statistics.
        :param data: pd.DataFrame
            Input pd.DataFrame
        :param paste: bool
            To determine if the stats program will be pasted or uploaded data.
        :return: editable DataFrame
        """

        global select, selected_data
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
        self.run_normality(dv_col, group_col, selected_data=selected_data)

        # Run omnibus tests
        omnibus = st.toggle('Omnibus Tests')
        omnibus_tests = ['ANOVA', 'Welch-ANOVA', 'Repeated Measures', 'Mixed-ANOVA', 'Kruskal-Wallis (non-parametric)',
                         'Cochran (non-parametric)', 'Friedman (non-parametric)']
        if omnibus:
            test = st.radio(label="Available Omnibus Tests:", options=omnibus_tests)

            # Omnibus test
            self.omnibus_results(dv_col, group_col, subgroup_col, selected_data, test)

        # Run post-hoc tests
        post_hoc = st.toggle('Post-Hoc Tests')
        post_hoc_tests = ['Tukey', 'Games-Howell', 'Pairwise T-Tests', 'Wilcoxon', 'Mann-Whitney U', 'Pairwise T-Tests']
        captions = ['Parametric', 'Parametric', 'Parametric', 'Non-Parametric', 'Non-Parametric', 'Non-Parametric']
        if post_hoc:
            test = st.radio(label="Available Post-Hoc Tests:", options=post_hoc_tests, captions=captions)

    def run_normality(self, dv_col, group_col, selected_data):
        """
        Function to run normality test.
        :param dv_col:
        :param group_col:
        :param selected_data:
        :return:
        """
        st.write('## Test for Normality?')
        normality = st.toggle('Test for Normality')

        # Initialize py50
        stats = Stats(selected_data)
        plots = Plots(selected_data)

        if normality:
            col1, col2 = st.columns(2)

            with col1:
                normality = stats.get_normality(value_col=dv_col, group_col=group_col).round(3)
                st.write('**Note:** Check mark means True')

                st.data_editor(normality, num_rows='dynamic')
                self.download_csv(normality, index=True, file_name='py50_normality.csv')

            with col2:
                normality_plot = st.toggle('Plot for Normality')
                if normality_plot:

                    # Sub columns for title input
                    col1, col2 = st.columns(2)
                    with col1:
                        hist_title = st.text_input(label='Histogram Title', value=None, placeholder='Hist Plot')
                    with col2:
                        qq_title = st.text_input(label='QQ Plot Title', value=None, placeholder='QQ Plot')

                    # create subplot grid
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 4))
                    plots.distribution(val_col=dv_col, type='histplot', ax=ax1)
                    plots.distribution(val_col=dv_col, type='qqplot', ax=ax2)

                    # Conditionals for plot titles
                    if hist_title is None and qq_title is None:
                        ax1.set_title('Hist Plot')
                        ax2.set_title('QQ Plot')

                    elif hist_title is None and qq_title is not None:
                        ax1.set_title('Hist Plot')
                        ax2.set_title(qq_title)

                    elif hist_title is not None and qq_title is None:
                        ax1.set_title(hist_title)
                        ax2.set_title('QQ Plot')
                    else:
                        ax1.set_title(hist_title)
                        ax2.set_title(qq_title)

                    st.pyplot(fig)
                    self.download_fig(fig=fig, file_name="normality.png")

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
        global select, selected_data
        # Conditional after selecting columns for calculation
        if group_col is not None and dv_col is not None:
            st.write('Current Selection')
            select = data.copy()
            selected_data = select[[group_col, dv_col]]
            st.write(selected_data)

            if paste:
                # Pasting data does not ensure correct format. Must enforce!
                selected_data['Group'] = select['Group'].astype(str)
                selected_data['Dependent Variable'] = select['Dependent Variable'].astype(float)

        elif subgroup_col == None:
            st.write('Current Selection')
            selected_data = data.copy()

            # Pasting data does not ensure correct format. Must enforce!
            selected_data['Group'] = selected_data['Group'].astype(str)
            selected_data['Dependent Variable'] = selected_data['Dependent Variable'].astype(float)

        elif subgroup_col == "None":
            st.write("Subgroup column set to None")
            select = data.copy()
            selected_data = select.drop(columns=['Subgroup'])

            # Pasting data does not ensure correct format. Must enforce!
            selected_data['Group'] = selected_data['Group'].astype(str)
            selected_data['Dependent Variable'] = selected_data['Dependent Variable'].astype(float)
#
# def run_normality(data, group_col, dv_col):
