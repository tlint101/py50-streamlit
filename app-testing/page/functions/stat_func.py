"""
Functions for statistics.
"""

import streamlit as st
import pandas as pd
import io
from itertools import combinations
from collections import namedtuple
from matplotlib import pyplot as plt
import seaborn as sns
from py50.stats import Plots, Stats

# namedtuple to extract test for plotting
MODEL = namedtuple("STAT_TEST", ["test_selection", "py50_test"])

TEST_LIST = [
    MODEL('Tukey', "tukey"),
    MODEL("Games-Howell", "gameshowell"),
    MODEL("Pairwise T-Tests", 'pairwise-parametric'),
    MODEL("Wilcoxon", "wilcoxon"),
    MODEL("Pairwise Mann-Whitney U", "mannu"),
    MODEL("Pairwise T-Tests (Non-Parametric)", "pairwise-nonparametric")
]


# Pull test name from namedtuple list
def get_test(test_name):
    for model in TEST_LIST:
        if test_name == model.test_selection:
            return model.py50_test


def column_selection(data, dv_col, group_col, subgroup_col, paste):
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
        st.write('**Current Data Selection:**')
        select = data.copy()

        if subgroup_col is None:
            selected_data = select[[group_col, dv_col]]
        elif subgroup_col == 'None':
            selected_data = select[[group_col, dv_col]]
        else:
            selected_data = select[[group_col, dv_col, subgroup_col]]

        st.write(selected_data)

        if paste:
            # Pasting data does not ensure correct format. Must enforce!
            selected_data['Group'] = select['Group'].astype(str)
            selected_data['Dependent Variable'] = select['Dependent Variable'].astype(float)
    else:
        st.write('**Current Data Selection:**')


def _font_options(dv_col, group_col, test, orientation):
    # Font options
    font_option = st.toggle(label="Font Options")
    if font_option:
        style = st.text_input(label="Font Style", value="DejaVu Sans")
        title = st.text_input(label='Plot Title', value=f"Post Hoc {test} Results")
        x_label = st.text_input(label='Plot X Label', value=group_col)
        y_label = st.text_input(label='Plot Y Label', value=dv_col)
        title_fontsize = st.select_slider(label='Title Font Size', options=range(10, 31), value=16)
        axis_fontsize = st.select_slider(label='Axis Font Size', options=range(10, 31), value=14)
    else:
        style = "DejaVu Sans"
        title = f"Post Hoc {test} Results"
        title_fontsize = 16
        axis_fontsize = 14
        # orientation conditional
        if orientation == "v":
            x_label = group_col
            y_label = dv_col
        else:
            x_label = dv_col
            y_label = group_col

    return axis_fontsize, style, title, title_fontsize, x_label, y_label


def _color_option():
    # Plot color schemes
    color_option = st.toggle(label="Color Schemes")
    if color_option:
        st.write('Color Options:')
        color_options = ['Default', 'Greens', 'Blues', 'autumn', 'gist_earth', 'coolwarm', 'flare', 'icefire',
                         'mako', 'Paired', 'Pastel1', 'Pastel2', 'rainbow', 'Spectral', 'twilight', 'vlag']
        color = st.selectbox(label='Styles', options=color_options, index=0)
        if color == "Default":
            color = "tab10"

        color_option_list = st.checkbox(label='Custom Color Option', value=None)

        if color_option_list:
            st.write('Can use palette names, or a list of hex codes, color names (separate by comma)')
            st.caption("Example: green, blue, red")
            custom_color = st.text_input(label="Custom Color List:", value="Default")

            url = 'https://www.practicalpythonfordatascience.com/ap_seaborn_palette'
            st.caption("Additional color options can be found [here](%s)" % url)

            # conditional for custom_color list
            if custom_color == "":
                color = 'tab10'
                st.write(f":rainbow[Be sure to give a list of colors!]")
            elif custom_color == "Default":
                color = 'tab10'
            # assume input  is color palette
            elif ',' not in custom_color:
                color = custom_color
                st.write(f":red[input is color palette: {color}]")
            # assume input is a list of colors
            elif ',' in custom_color:
                color = [color.strip() for color in custom_color.split(',')]
            else:
                st.write(":red[Not a valid color list!]")
    else:
        color = None
    return color


def _annotation(post_hoc_table, fig_type):
    # Set variables so plots will be generated before annotation
    group_order = None
    pairs_select = None
    pvalue = None
    legend = None
    location = None
    position = None
    whisker = None
    bars = None
    capsize = None
    loc = None
    point_size = None

    # Annotation options
    annotation = st.toggle(label="Plot Annotations")

    if annotation:
        # Hide until update py50 with this parameter
        ns_group = st.checkbox(label="Hide Groups with No Significance?")

        if fig_type == "Swarm Plot":
            point_size = st.slider(label="Point Size", min_value=1.0, max_value=10.0, value=5.0, step=0.5)
            point_size = point_size
        else:
            point_size = None

        if fig_type == "Strip Plot":
            point_size = st.slider(label="Point Size", min_value=1.0, max_value=10.0, value=5.0, step=0.5)
            point_size = point_size
        else:
            point_size = None

        # Whisker for box plot
        if fig_type == 'Box Plot':
            whisker = st.slider(label="Whisker Length", min_value=0.0, max_value=5.0, value=1.5, step=0.5)
        else:
            whisker = None

        # Bar plot error bars
        if fig_type == 'Bar Plot':
            bar_type = ['sd', 'se', 'pi', 'ci']
            types = {'sd': 'Standard Deviation', 'se': 'Standard Deviation', 'pi': 'Pi', 'ci': 'Ci'}
            bars = st.selectbox(label="Error Bar:", options=bar_type, index=0, key=types)

            capsize = st.slider(label="Cap Size", min_value=0.0, max_value=1.0, value=0.1, step=0.1)
        else:
            bars = None
            capsize = None

        if fig_type == 'Violin Plot':
            placement = ['inside', 'outside']
            loc = st.selectbox(label="Annotation Location", options=placement, index=0)
            st.caption(":red[May Need to Remove Plot Title if Annotations are set to Outside]")
        else:
            loc = 'inside'

        # pair order
        group_order = None  # Plots need group_order variable to generate
        group_order = st.text_input(label='Group Order', value="Group1, Group2, etc")
        st.caption("Note: Be sure to write names exactly as they appear in table!")
        if group_order == "Group1, Group2, etc":
            group_order = None
        # elif group_order == "":
        #     group_order = None
        else:
            group_order = [value.strip() for value in group_order.split(',')]
            if len(group_order) > len(post_hoc_table):
                st.warning(":red[🚨Need more groups?🚨]")
                group_order = None
            elif len(group_order) < len(post_hoc_table):
                st.warning(":red[🚨Need less groups?🚨]")
                group_order = None
            else:
                group_order = group_order

        # pairs
        # Generate pairs from post_hoc_table
        groups = list(set(post_hoc_table['A'].tolist() + post_hoc_table['B'].tolist()))
        pairs = [(group1, group2) for group1, group2 in combinations(groups, 2) if group1 != group2]

        # Pair selection. Will return an empty list
        pairs_select = st.multiselect(label="Group Pairs", options=pairs, placeholder="Select Pairs")
        st.caption("Example: (pair1, pair2), (pair1, pair3), etc")
        if not pairs_select:
            pairs_select = None

        # pvalue
        pvalue = st.text_input(label='Custom P-Value', value="P-value")
        st.caption("Example: p ≤ 0.01, p ≤ 0.05, etc")

        if pvalue == 'P-value':
            pairs_select = None
            pvalue = None
        elif pvalue is str:
            pvalue = [value.strip() for value in pvalue.split(',')]
        elif pvalue == "":
            pvalue = None
        else:
            pvalue = None

        # Figure legend options
        if fig_type == 'Swarm Plot' or fig_type == 'Strip Plot':
            legend = st.toggle(label="Show Legend", value=False)
            if legend:
                location_options = ['best', 'upper right', 'upper left', 'lower left', 'lower right', 'right',
                                    'center left', 'center right', 'lower center', 'upper center', 'center']
                location = st.selectbox(label='Location', options=location_options, index=0)

                # position requires tuple. Split into list then convert as follows
                position_input = st.text_input(label='Position', value="1, 1")
                if position_input == "":
                    position = (0, 0)
                else:
                    input_split = position_input.split(',')
                    position = (float(input_split[0]), int(input_split[1]))
        else:
            legend = None
            location = None
            position = None

    return annotation, group_order, pairs_select, pvalue, legend, location, position, whisker, bars, capsize, loc, point_size


def _plot_fig(annotation, color, dv_col, fig_type, group_col, group_order, orientation, pairs_select, plot,
              pvalue, selected_data, subgroup_col, test_type, whisker, bars, capsize, loc, point_size):
    global ax
    if fig_type == 'Box Plot':
        # must call ax. Thus, will need to plot "twice".
        if orientation == 'h':
            ax = sns.boxplot(x=selected_data[dv_col], y=selected_data[group_col], orient=orientation,
                             order=group_order, whis=whisker)
        else:
            ax = sns.boxplot(x=selected_data[group_col], y=selected_data[dv_col], orient=orientation,
                             order=group_order, whis=whisker)

        # Conditional to plot figure
        if annotation:
            plot.boxplot(test=test_type, group_col=group_col, value_col=dv_col, subject_col=subgroup_col,
                         palette=color, orient=orientation, pvalue_label=pvalue, pairs=pairs_select,
                         group_order=group_order, whis=whisker)
        else:
            plot.boxplot(test=test_type, group_col=group_col, value_col=dv_col, subject_col=subgroup_col,
                         palette=color, orient=orientation)

    elif fig_type == 'Bar Plot':
        # must call ax. Thus, will need to plot "twice".
        if orientation == 'h':
            ax = sns.barplot(x=selected_data[dv_col], y=selected_data[group_col], orient=orientation,
                             order=group_order, errorbar=bars, capsize=capsize)
        else:
            ax = sns.barplot(x=selected_data[group_col], y=selected_data[dv_col], orient=orientation,
                             order=group_order)

        # Conditional to plot figure
        if annotation:
            plot.barplot(test=test_type, group_col=group_col, value_col=dv_col, subject_col=subgroup_col,
                         palette=color, orient=orientation, pvalue_label=pvalue, pairs=pairs_select,
                         group_order=group_order, errorbar=bars, capsize=capsize)
        else:
            plot.barplot(test=test_type, group_col=group_col, value_col=dv_col, subject_col=subgroup_col,
                         palette=color, orient=orientation)

    elif fig_type == 'Violin Plot':
        # must call ax. Thus, will need to plot "twice".
        if orientation == 'h':
            ax = sns.violinplot(x=selected_data[dv_col], y=selected_data[group_col], orient=orientation,
                                order=group_order)
        else:
            ax = sns.violinplot(x=selected_data[group_col], y=selected_data[dv_col], orient=orientation,
                                order=group_order)

        # Conditional to plot figure
        if annotation:
            plot.violinplot(test=test_type, group_col=group_col, value_col=dv_col, subject_col=subgroup_col,
                            palette=color, orient=orientation, pvalue_label=pvalue, pairs=pairs_select,
                            group_order=group_order, loc=loc)
        else:
            plot.violinplot(test=test_type, group_col=group_col, value_col=dv_col, subject_col=subgroup_col,
                            palette=color,
                            orient=orientation)

    elif fig_type == 'Swarm Plot':
        if color is None:
            color = "tab10"

        # point_size = int(point_size)

        # must call ax. Thus, will need to plot "twice".
        if orientation == 'h':
            ax = sns.swarmplot(x=selected_data[dv_col], y=selected_data[group_col], orient=orientation,
                               order=group_order, palette=color)
        else:
            ax = sns.swarmplot(x=selected_data[group_col], y=selected_data[dv_col], orient=orientation,
                               order=group_order, palette=color)

        # Conditional to plot figure
        if annotation:
            plot.swarmplot(test=test_type, group_col=group_col, value_col=dv_col, subject_col=subgroup_col,
                           palette=color, orient=orientation, pvalue_label=pvalue, pairs=pairs_select,
                           group_order=group_order, size=point_size)
        else:
            plot.swarmplot(test=test_type, group_col=group_col, value_col=dv_col, subject_col=subgroup_col,
                           palette=color, orient=orientation, size=point_size)

    elif fig_type == 'Strip Plot':
        if color is None:
            color = "tab10"

        if point_size is None:
            point_size = 5

        # must call ax. Thus, will need to plot "twice".
        if orientation == 'h':
            ax = sns.stripplot(data=selected_data, x=dv_col, y=group_col, orient=orientation,
                               order=group_order, palette=color, size=point_size)
        else:
            print("this is the FIRST else:", point_size)
            ax = sns.stripplot(data=selected_data, x=group_col, y=dv_col, orient=orientation,
                               order=group_order, palette=color, size=point_size)

        # Conditional to plot figure
        if annotation:
            plot.stripplot(test=test_type, group_col=group_col, value_col=dv_col, subject_col=subgroup_col,
                           palette=color, orient=orientation, pvalue_label=pvalue, pairs=pairs_select,
                           group_order=group_order, size=point_size)
        else:
            print("This is the else for", point_size)
            plot.stripplot(test=test_type, group_col=group_col, value_col=dv_col, subject_col=subgroup_col,
                           palette=color, orient=orientation, size=point_size)

    elif fig_type == 'Boxen Plot':
        # must call ax. Thus, will need to plot "twice".
        if orientation == 'h':
            ax = sns.boxenplot(x=selected_data[dv_col], y=selected_data[group_col], orient=orientation,
                               order=group_order)
        else:
            ax = sns.boxenplot(x=selected_data[group_col], y=selected_data[dv_col], orient=orientation,
                               order=group_order)

        # Conditional to plot figure
        if annotation:
            plot.boxenplot(test=test_type, group_col=group_col, value_col=dv_col, subject_col=subgroup_col,
                           palette=color,
                           orient=orientation, pvalue_label=pvalue, pairs=pairs_select, group_order=group_order)
        else:
            plot.boxenplot(test=test_type, group_col=group_col, value_col=dv_col, subject_col=subgroup_col,
                           palette=color,
                           orient=orientation)
    return ax


"""
Logic for statistics calculator
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

        global select, selected_data, test, post_hoc_table
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
                                      placeholder="Select Dependent Variable")  # Index to auto select column
            with col3:
                subgroup_col = st.selectbox('Subgroup (Optional):', col_header, index=None,
                                            placeholder="Select Subgroup")  # Index to auto select column

        # Select columns
        column_selection(data, dv_col, group_col, subgroup_col, paste)

        # run_normality
        self.run_normality(dv_col, group_col, selected_data=selected_data)

        # Run omnibus tests
        omnibus = st.toggle('Omnibus Tests')
        omnibus_tests = ['ANOVA', 'Welch-ANOVA', 'Kruskal-Wallis (Non-Parametric)', 'Cochran (Non-Parametric)',
                         'Friedman (Non-Parametric)']

        col1, col2 = st.columns(2)
        with col1:
            if omnibus:
                test = st.radio(label="Available Omnibus Test:", options=omnibus_tests, index=None)

                # Omnibus test
                if test is None:
                    st.write(":red[Please select a Omnibus Test above]")
                else:
                    st.write(":green[🥳 Stat Results:]")
                    self.omnibus_results(dv_col, group_col, subgroup_col, selected_data, test)

        with col2:
            if omnibus:
                if test:
                    significance = Stats.explain_significance()
                    st.write(":green[🔎 Significance Values:]")
                    st.write(significance)

        # Run post-hoc tests
        post_hoc = st.toggle('Post-Hoc Tests')
        post_hoc_tests = ['Tukey', 'Games-Howell', 'Pairwise T-Tests', 'Wilcoxon', 'Pairwise Mann-Whitney U',
                          'Pairwise T-Tests (Non-Parametric)']
        captions = ['Parametric', 'Parametric', 'Parametric', 'Non-Parametric', 'Non-Parametric', 'Non-Parametric']
        plot_type = ['Box Plot', 'Bar Plot', 'Violin Plot', 'Swarm Plot', 'Strip Plot', "Boxen Plot"]

        col1, col2 = st.columns(2)
        with col1:
            if post_hoc:
                test = st.radio(label="Available Post-Hoc Test:", options=post_hoc_tests, captions=captions, index=None)
                if test is None:
                    st.write(":red[Please select a post-hoc test]")

        with col2:
            if post_hoc:
                if test:
                    significance = Stats.explain_significance()
                    st.write(":green[🔎 Significance Values:]")
                    st.write(significance)

        # post-hoc test
        if post_hoc:
            if test:
                st.write(":green[🥳 Stat Results:]")
                post_hoc_table = self.post_hoc_results(dv_col, group_col, subgroup_col, selected_data, test)

        # Plot post-hoc results
        plot = st.toggle('Generate Plot')
        if plot:

            # Warning to select post-hoc test before plot generation
            if post_hoc is False:
                st.write(":red[🚨Select a Post-Hoc test first‼️]")

            fig_type = st.radio(label="Available Plots:", options=plot_type, index=None)

            if fig_type is None:
                st.write(":red[Please select a plot type!]")
            else:
                self.plot(dv_col, group_col, subgroup_col, selected_data, test, fig_type, post_hoc_table)

    def plot(self, dv_col, group_col, subgroup_col, selected_data, test, fig_type, post_hoc_table):
        global test_type
        plot = Plots(selected_data)

        if test:
            test_type = get_test(test)
        else:
            st.error(":red[🚨Please select a post-hoc test type!🚨]")

        # Figure options
        st.sidebar.subheader("Plot Options")

        with st.sidebar:
            # Orientation
            orientation = st.radio(label="Orientation:", options=['Vertical', 'Horizontal'], index=0)
            if orientation == 'Horizontal':
                orientation = "h"
            elif orientation == 'Vertical':
                orientation = "v"

            # font options
            axis_fontsize, style, title, title_fontsize, x_label, y_label = _font_options(dv_col, group_col, test,
                                                                                          orientation)

            # color options
            color = _color_option()

            # annotation options
            annotation, group_order, pairs_select, pvalue, legend, location, position, whisker, bars, capsize, loc, point_size = _annotation(
                post_hoc_table,
                fig_type)

        # Set font type:
        plt.rcParams['font.family'] = style

        # Generate plots
        ax = _plot_fig(annotation, color, dv_col, fig_type, group_col, group_order, orientation, pairs_select,
                       plot, pvalue, selected_data, subgroup_col, test_type, whisker, bars, capsize, loc, point_size)

        # Modify plot
        ax.set_title(title, fontsize=title_fontsize)
        ax.set_xlabel(x_label, fontsize=axis_fontsize)
        ax.set_ylabel(y_label, fontsize=axis_fontsize)

        col1, col2 = st.columns(2)
        with col1:
            if legend and location:
                plt.legend(loc=location, bbox_to_anchor=position)
                plt.tight_layout()
            else:
                plt.tight_layout()
            # Get underlying matplotlib figure
            fig = plt.gcf()
            st.pyplot(fig)
            self.download_fig(fig, file_name='py50_stat_plot.png')

        # Matrix figure
            if fig:
                plt.clf()
                matrix = st.toggle(label='Plot Matrix', value=False)
                if matrix:
                    stats = Stats(selected_data)
                    matrix_pvalues = stats.get_p_matrix(data=post_hoc_table, test=get_test(test))
                    plots = Plots(matrix_pvalues)
                    fig = plots.p_matrix()[0]

                    st.pyplot(fig.figure)

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
                try:
                    stat_df = stats.get_wilcoxon(value_col=dv_col, group_col=group_col)
                    st.warning(":red[🚨ERROR: Wilcoxon Test needs a subgroup column]🚨")
                except ValueError:
                    st.error(
                        ":red[🚨ERROR: The length of the groups in the Group Column are not equal for Wilcoxon Test!!]🚨")
                    stat_df = None
            elif subgroup_col:
                try:
                    stat_df = stats.get_wilcoxon(value_col=dv_col, group_col=group_col, subgroup_col=subgroup_col)
                except ValueError:
                    st.error(
                        ":red[🚨ERROR: The length of the groups in the Group Column are not equal for Wilcoxon Test!!]🚨")
                    stat_df = None
            else:
                st.error(
                    ":red[🚨ERROR: The length of the groups in the Group Column are not equal for Wilcoxon Test!!]🚨")
                stat_df = None

        elif test == "Pairwise Mann-Whitney U":
            if subgroup_col is None:
                stat_df = stats.get_mannu(value_col=dv_col, group_col=group_col)
            else:
                stat_df = stats.get_mannu(value_col=dv_col, group_col=group_col, subgroup_col=subgroup_col)

        elif test == "Pairwise T-Tests (Non-Parametric)":
            if subgroup_col is None:
                stat_df = stats.get_pairwise_tests(value_col=dv_col, group_col=group_col, parametric=False)
            elif subgroup_col:
                stat_df = stats.get_pairwise_tests(value_col=dv_col, group_col=group_col, subject_col=subgroup_col,
                                                   parametric=False)
            else:
                st.warning(f":red[🚨ERROR: Something wrong with {test}]🚨")
        else:
            st.write(":red[Select Post-Hoc Test]")

        # Output table
        st.data_editor(stat_df)
        st.write(":red[NOTE: ]",
                 "very small p-values may appear as 0. Please download .csv file to view specific value.")
        self.download_csv(stat_df, file_name=f'py50_{test}.csv')

        return stat_df

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
            if subgroup_col == None:
                stat_df = stats.get_anova(value_col=dv_col, group_col=group_col)
            else:
                st.write(":red[Warning: Subgroup Column not needed for calculation.]")
                stat_df = stats.get_anova(value_col=dv_col, group_col=group_col)

        elif test == 'Welch-ANOVA':
            if subgroup_col == None:
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
                stat_df = stats.get_kruskal(value_col=dv_col, group_col=group_col)
            else:
                st.write(":red[Warning: Subgroup Column not used in calculation.]")
                stat_df = stats.get_kruskal(value_col=dv_col, group_col=group_col)

        elif test == 'Cochran (Non-Parametric)':
            if subgroup_col is None:
                st.write(":red[Cochran Test requires a subgroup column!]")
                stat_df = stats.get_cochran(value_col=dv_col, group_col=group_col)
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
        st.write('## :green[Available Tests]')  # tied to function to appear after data selected
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
