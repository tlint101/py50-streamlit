"""
Functions for statistics.
"""

import streamlit as st
import pandas as pd
from collections import namedtuple
import io
from matplotlib import pyplot as plt
from py50.stats import Plots, Stats

# namedtuple to extract test for plotting
TEST = namedtuple("STAT_TEST", ["test_selection", "py50_test"])

TEST_LIST = [
    TEST('Tukey', "tukey"),
    TEST("Games-Howell", "gameshowell"),
    TEST("Pairwise T-Tests", 'pairwise-parametric'),
    TEST("Wilcoxon", "wilcoxon"),
    TEST("Pairwise Mann-Whitney U", "mannu"),
    TEST("Pairwise T-Tests (Non-Parametric)", "pairwise-nonparametric")
]


# Pull test name from namedtuple list
def get_test(test_name):
    for model in TEST_LIST:
        if test_name == model.test_selection:
            return model.py50_test


"""
NOTE: Classes for Plots and Stats should be initialized AFTER processing the data.
"""


class Stats_Logic:

    def __init__(self):
        pass

    def stats_program(self, data: pd.DataFrame = None, paste: bool = False):
        """
        Function for statistics.
        :param data: pd.DataFrame
            Input pd.DataFrame
        :param paste: bool
            To determine if the stats program will be pasted or uploaded data.
        :return: editable DataFrame
        """

        global select, selected_data, test
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
        omnibus_tests = ['ANOVA', 'Welch-ANOVA', 'Kruskal-Wallis (Non-Parametric)', 'Cochran (Non-Parametric)',
                         'Friedman (Non-Parametric)']
        if omnibus:
            test = st.radio(label="Available Omnibus Test:", options=omnibus_tests, index=None)

            # Omnibus test
            self.omnibus_results(dv_col, group_col, subgroup_col, selected_data, test)

        # Run post-hoc tests
        post_hoc = st.toggle('Post-Hoc Tests')
        post_hoc_tests = ['Tukey', 'Games-Howell', 'Pairwise T-Tests', 'Wilcoxon', 'Pairwise Mann-Whitney U',
                          'Pairwise T-Tests (Non-Parametric)']
        captions = ['Parametric', 'Parametric', 'Parametric', 'Non-Parametric', 'Non-Parametric', 'Non-Parametric']
        plot_type = ['Box Plot', 'Bar Plot', 'Violin Plot', 'Swarm Plot', 'Strip Plot', "Boxen Plot"]
        if post_hoc:
            test = st.radio(label="Available Post-Hoc Test:", options=post_hoc_tests, captions=captions, index=None)

            self.post_hoc_results(dv_col, group_col, subgroup_col, selected_data, test)

        # Plot post-hoc results
        plot = st.toggle('Plot Test?')
        if plot:
            fig_type = st.radio(label="Available Plots:", options=plot_type, index=None)

            self.plot(dv_col, group_col, subgroup_col, selected_data, test, fig_type)

    def plot(self, dv_col, group_col, subgroup_col, selected_data, test, fig_type):
        pass

        # Uncomment when finished
        # st.pyplot(fig)
        # self.download_fig(fig, file_name='py50_stat_plot.png')

    def post_hoc_results(self, dv_col, group_col, subgroup_col, selected_data, test):
        global stat_df
        stats = Stats(selected_data)

        if test == 'Tukey':
            stat_df = stats.get_tukey(value_col=dv_col, group_col=group_col)

        elif test == 'Games-Howell':
            stat_df = stats.get_gameshowell(value_col=dv_col, group_col=group_col)

        # todo fix subgroup_col input
        elif test == "Pairwise T-Tests":
            if subgroup_col is None:
                stat_df = stats.get_pairwise_tests(value_col=dv_col, group_col=group_col)
            elif subgroup_col:
                stat_df = stats.get_pairwise_tests(value_col=dv_col, group_col=group_col, subject_col=subgroup_col)
            else:
                st.warning(f":red[🚨ERROR: Something wrong with {test}]🚨")

        elif test == "Wilcoxon":
            if subgroup_col == 'None':
                stat_df = stats.get_wilcoxon(value_col=dv_col, group_col=group_col)
                st.warning(
                    ":red[🚨ERROR: Wilcoxon Test needs a subgroup column]🚨")
            elif subgroup_col:
                stat_df = stats.get_wilcoxon(value_col=dv_col, group_col=group_col, subgroup_col=subgroup_col)
            else:
                st.warning(
                    ":red[🚨ERROR: The length of the groups in the Group Column are not equal for Wilcoxon Test!!]🚨")

        elif test == "Pairwise Mann-Whitney U":
            if subgroup_col is None:
                stat_df = stats.get_mannu(value_col=dv_col, group_col=group_col)
            else:
                stat_df = stats.get_mannu(value_col=dv_col, group_col=group_col, subgroup_col=subgroup_col)

        # todo this breaks and will not calculate?
        elif test == "Pairwise T-Tests (Non-Parametric)":
            if subgroup_col is None:
                stat_df = stats.get_pairwise_tests(value_col=dv_col, group_col=group_col, parametric=False)
            elif subgroup_col:
                st.warning(f":red[🚨ERROR: Subgroup column not needed for {test}]🚨")
                stat_df = stats.get_pairwise_tests(value_col=dv_col, group_col=group_col, within_subject_col=subgroup_col,
                                                   parametric=False)
            else:
                st.warning(f":red[🚨ERROR: Something wrong with {test}]🚨")
        else:
            st.write(":red[Select Post-Hoc Test]")

        st.data_editor(stat_df)
        self.download_csv(stat_df, file_name=f'py50_{test}.csv')

        # def post_hoc_test(self, dv_col, group_col, subgroup_col, selected_data, test):
        # get test name
        test_type = get_test(test)

        # if plot_style == 'Box Plot':
        #     fig = plots.boxplot(test=test_type, group_col=group_col, subgroup_col=subgroup_col,)

        # return fig

    def omnibus_results(self, dv_col, group_col, subgroup_col, selected_data, test):
        """
        Function for Omnibus Tests.
        :param dv_col:
        :param group_col:
        :param subgroup_col:
        :param selected_data:
        :param test:
        :return:
        """
        global stat_df
        # Initialize Stats() class
        stats = Stats(selected_data)

        # Omnibus test
        if test == 'ANOVA':
            if subgroup_col == 'None':
                stat_df = stats.get_anova(value_col=dv_col, group_col=group_col)
            else:
                st.write(":red[Warning: Subgroup Column not needed for calculation.]")
                stat_df = stats.get_anova(value_col=dv_col, group_col=group_col, )

        elif test == 'Welch-ANOVA':
            if subgroup_col == 'None':
                stat_df = stats.get_welch_anova(value_col=dv_col, group_col=group_col)
            else:
                st.write(":red[Warning: Subgroup Column not used calculation.]")
                stat_df = stats.get_welch_anova(value_col=dv_col, group_col=group_col)

        # REPEATED MEASURE AND MIXED ANOVA WILL NEED TO BE MODIFIED. MAY NOT USE IN PY50-STREAMLIT!
        # elif test == 'Repeated Measures':
        #     if subgroup_col is None:
        #         stat_df = stats.get_rm_anova(value_col=dv_col, within_subject_col=subgroup_col, subject_col=group_col)
        #     else:
        #         stat_df = stats.get_rm_anova(value_col=dv_col, subject_col=group_col)
        # elif test == 'Mixed-ANOVA':
        #     if subgroup_col is None:
        #         stat_df = stats.get_mixed_anova(value_col=dv_col, within_subject_col=subgroup_col,
        #                                         subject_col=group_col)
        #     else:
        #         stat_df = stats.get_mixed_anova(value_col=dv_col, subject_col=group_col)

        elif test == 'Kruskal-Wallis (Non-Parametric)':
            if subgroup_col == None:
                st.write('no subgroup')
                stat_df = stats.get_kruskal(value_col=dv_col, group_col=group_col)
            else:
                st.write(":red[Warning: Subgroup Column not used in calculation.]")
                stat_df = stats.get_kruskal(value_col=dv_col, group_col=group_col)

        elif test == 'Cochran (Non-Parametric)':
            if subgroup_col is None:
                st.write(":red[Cochran Test requires a subgroup column!]")
            else:
                stat_df = stats.get_cochran(value_col=dv_col, group_col=group_col, subgroup_col=subgroup_col)

        elif test == 'Friedman (Non-Parametric)':
            if subgroup_col is None:
                st.write(":red[Friedman Test requires a subgroup column!]")
                stat_df = stats.get_friedman(value_col=dv_col, group_col=group_col)
            else:
                stat_df = stats.get_friedman(value_col=dv_col, group_col=group_col, subgroup_col=subgroup_col)
        else:
            st.write(":red[Select Omnibus Test]")

        st.data_editor(stat_df)
        self.download_csv(stat_df, file_name=f'py50_{test}.csv')

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
            st.write('**Current Selection:**')
            select = data.copy()

            if subgroup_col == None:
                selected_data = select[[group_col, dv_col]]
            else:
                selected_data = select[[group_col, dv_col, subgroup_col]]

            st.write(selected_data)

            if paste:
                # Pasting data does not ensure correct format. Must enforce!
                selected_data['Group'] = select['Group'].astype(str)
                selected_data['Dependent Variable'] = select['Dependent Variable'].astype(float)
        else:
            st.write('**Current Selection:**')

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
