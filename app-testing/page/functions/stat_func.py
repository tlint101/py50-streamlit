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
        style = st.text_input(label="Font Style", value="DejaVu Sans", key='plot')
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
            custom_color = st.text_input(label="Custom Color List:", value="Default")
            st.caption("Example: green, blue, red")

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


def _annotation(post_hoc_table, fig_type, selected_data, group_col, subgroup_col):
    # Set variables so plots will be generated before annotation
    no_annotation = None
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
    legend_configuration = None
    bbox = None

    # Annotation options
    annotation = st.toggle(label="Plot Annotations")

    if annotation:
        # Hide until update py50 with this parameter
        no_annotation = st.checkbox(label="Hide Annotations")

        if no_annotation is False:
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
            if len(group_order) < len(selected_data[group_col].unique()):
                st.warning(":red[🚨 Need more groups?🚨]")
                group_order = None
            elif len(group_order) > len(selected_data[group_col].unique()):
                st.warning(":red[🚨 Need less groups?🚨]")
                group_order = None
            elif len(group_order) == len(selected_data[group_col].unique()):
                st.warning(f":red[🚨 Did you forget a comma? 🚨]")
            else:
                group_order = group_order

        # pairs
        if no_annotation is False:
            # Generate pairs from post_hoc_table
            groups = list(set(post_hoc_table['A'].tolist() + post_hoc_table['B'].tolist()))
            pairs = [(group1, group2) for group1, group2 in combinations(groups, 2) if group1 != group2]

            # Pair selection. Will return an empty list
            pairs_select = st.multiselect(label="Group Pairs", options=pairs, placeholder="Select Pairs")
            st.caption("Example: (pair1, pair2), (pair1, pair3), etc")
            if not pairs_select:
                pairs_select = None

        # pvalue
        if no_annotation is False:
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
        else:
            pvalue = None

        # Figure legend options
        location_options = ['best', 'upper right', 'upper left', 'lower left', 'lower right', 'right',
                            'center left', 'center right', 'lower center', 'upper center', 'center']
        if fig_type == 'Swarm Plot' or fig_type == 'Strip Plot':
            legend = st.toggle(label="Show Legend", value=False)
            if legend:
                location = st.selectbox(label='Legend Position', options=location_options, index=0)

                # position requires tuple. Split into list then convert as follows
                position_input = st.text_input(label='Position', value="1, 1")
                if position_input == "":
                    position = (0, 0)
                else:
                    input_split = position_input.split(',')
                    position = (float(input_split[0]), int(input_split[1]))
        # figure legend with subgroup column
        if subgroup_col != None or subgroup_col != "":
            st.subheader('Legend Position')
            legend_configuration = st.selectbox(label="Legend Position", options=location_options, index=0)
            left = st.slider(label='Left', min_value=0.0, max_value=3.0, value=0.95, step=0.05, key='plot_left')
            bottom = 0.35
            width = 0.05
            height = 0.3
            bbox = [left, bottom, width, height]
        else:
            legend = None
            location = None
            position = None

    return annotation, group_order, pairs_select, pvalue, legend, location, position, whisker, bars, capsize, loc, point_size, no_annotation, legend_configuration, bbox


def _plot_fig(annotation, color, dv_col, fig_type, group_col, group_order, orientation, pairs_select, plot,
              pvalue, selected_data, subgroup_col, test_type, whisker, bars, capsize, loc, point_size, no_annotation):
    global ax
    if fig_type == 'Box Plot':
        # must call ax. Thus, will need to plot "twice".
        if orientation == 'h':
            ax = sns.boxplot(data=selected_data, x=dv_col, y=group_col, orient=orientation,
                             order=group_order, whis=whisker, hue=subgroup_col)

        else:
            ax = sns.boxplot(data=selected_data, x=group_col, y=dv_col, orient=orientation,
                             order=group_order, whis=whisker, hue=subgroup_col)
        # todo fix plotting to include subgroup column annotations. Maybe combine the sns with the py50 plots below?
        # elif orientation == 'v' and subgroup_col:
        #     ax = sns.boxplot(data=selected_data, x=group_col, y=dv_col, orient=orientation,
        #                      order=group_order, whis=whisker, hue=subgroup_col)

        # todo fix plotting for subgroup columns
        # Conditional to plot figure
        if annotation:
            if no_annotation is True:
                pass
            # elif test_type == "Pairwise T-Tests":
            #     st.warning(f"""
            #                 Annotations not supported for {test_type} and Subgroups!
            #                 **Suggest supplementing figure with the Matrix Plot!**
            #                            """)
            #     plot.boxplot(test=test_type, group_col=group_col, value_col=dv_col, subgroup_col=subgroup_col,
            #                  palette=color, orient=orientation, pvalue_label=pvalue, pairs=pairs_select,
            #                  group_order=group_order, whis=whisker)
            else:
                st.warning("""
                            🚨 Annotations and Color options are not supported with Pairwise data with Subgroup Column‼️          
                            **Suggest supplementing figure with the Matrix Plot below and turning off Plot Annotations**
                                       """)
                plot.boxplot(test=test_type, group_col=group_col, value_col=dv_col, subgroup_col=subgroup_col,
                             palette=color, orient=orientation, pvalue_label=pvalue, pairs=pairs_select,
                             group_order=group_order, whis=whisker)
        elif subgroup_col:
            st.warning("""
            🚨 Annotations not supported with Pairwise data with Subgroup Column‼️          
            **Suggest supplementing figure with the Matrix Plot below**
                       """)
            # plot.boxplot(test=test_type, group_col=group_col, value_col=dv_col, subgroup_col=subgroup_col,
            #              palette=color, orient=orientation, color=color)
            ax = sns.boxplot(data=selected_data, x=group_col, y=dv_col, orient=orientation,
                             order=group_order, whis=whisker, hue=subgroup_col)
        else:
            plot.boxplot(test=test_type, group_col=group_col, value_col=dv_col, subgroup_col=subgroup_col,
                         palette=color, orient=orientation, color=color)

    elif fig_type == 'Bar Plot':
        # must call ax. Thus, will need to plot "twice".
        if orientation == 'h':
            ax = sns.barplot(data=selected_data, x=dv_col, y=group_col, orient=orientation,
                             order=group_order, errorbar=bars, capsize=capsize, hue=subgroup_col)
        else:
            ax = sns.barplot(data=selected_data, x=group_col, y=dv_col, orient=orientation,
                             order=group_order, hue=subgroup_col)

        # Conditional to plot figure
        if annotation:
            if no_annotation is True:
                pass
            else:
                st.warning("""
                            🚨 Annotations and Color options are not supported with Pairwise data with Subgroup Column‼️          
                            **Suggest supplementing figure with the Matrix Plot below and turning off Plot Annotations**
                                                       """)
                plot.barplot(test=test_type, group_col=group_col, value_col=dv_col, subgroup_col=subgroup_col,
                             palette=color, orient=orientation, pvalue_label=pvalue, pairs=pairs_select,
                             group_order=group_order, errorbar=bars, capsize=capsize)
        elif subgroup_col:
            st.warning("""
                        🚨 Annotations not supported with Pairwise data with Subgroup Column‼️          
                        **Suggest supplementing figure with the Matrix Plot below**
                                   """)
        else:
            plot.barplot(test=test_type, group_col=group_col, value_col=dv_col, subgroup_col=subgroup_col,
                         palette=color, orient=orientation)

    # todo violin plot works fine with subgroup column?
    elif fig_type == 'Violin Plot':
        if subgroup_col:
            st.error(f"🚨 {fig_type} currently **NOT supporting** calculations with Subgroup Column‼️")

        # must call ax. Thus, will need to plot "twice".
        if orientation == 'h':
            ax = sns.violinplot(data=selected_data, x=dv_col, y=group_col, orient=orientation,
                                order=group_order, hue=subgroup_col, palette=color)
        else:
            ax = sns.violinplot(data=selected_data, x=group_col, y=dv_col, orient=orientation,
                                order=group_order, hue=subgroup_col, palette=color)

        # Conditional to plot figure
        if annotation:
            if no_annotation is True:
                pass
            else:
                plot.violinplot(test=test_type, group_col=group_col, value_col=dv_col, subgroup_col=subgroup_col,
                                palette=color, orient=orientation, pvalue_label=pvalue, pairs=pairs_select,
                                group_order=group_order, loc=loc)
        else:
            plot.violinplot(test=test_type, group_col=group_col, value_col=dv_col, subgroup_col=subgroup_col,
                            palette=color, orient=orientation)

    elif fig_type == 'Swarm Plot':
        if color is None:
            color = "tab10"

        # point_size = int(point_size)

        if subgroup_col:
            st.error(f"🚨 {fig_type} currently **NOT supporting** calculations with Subgroup Column‼️")

        # must call ax. Thus, will need to plot "twice".
        if orientation == 'h':
            ax = sns.swarmplot(data=selected_data, x=dv_col, y=group_col, orient=orientation,
                               order=group_order, palette=color)
        else:
            ax = sns.swarmplot(data=selected_data, x=group_col, y=dv_col, orient=orientation,
                               order=group_order, palette=color)

        # Conditional to plot figure
        if annotation:
            if no_annotation is True:
                pass
            else:
                plot.swarmplot(test=test_type, group_col=group_col, value_col=dv_col, subgroup_col=subgroup_col,
                               palette=color, orient=orientation, pvalue_label=pvalue, pairs=pairs_select,
                               group_order=group_order, size=point_size)
        else:
            plot.swarmplot(test=test_type, group_col=group_col, value_col=dv_col, subgroup_col=subgroup_col,
                           palette=color, orient=orientation, size=point_size)

    elif fig_type == 'Strip Plot':
        if color is None:
            color = "tab10"

        if point_size is None:
            point_size = 5

        if subgroup_col:
            st.error(f"🚨 {fig_type} currently **NOT supporting** calculations with Subgroup Column‼️")

        # must call ax. Thus, will need to plot "twice".
        if orientation == 'h':
            ax = sns.stripplot(data=selected_data, x=dv_col, y=group_col, orient=orientation,
                               order=group_order, palette=color, size=point_size, hue=subgroup_col)
        else:
            ax = sns.stripplot(data=selected_data, x=group_col, y=dv_col, orient=orientation,
                               order=group_order, palette=color, size=point_size, hue=subgroup_col)

        # Conditional to plot figure
        if annotation:
            if no_annotation is True:
                pass
            else:
                st.warning("""
                            🚨 Annotations and Color options are not supported with Pairwise data with Subgroup Column‼️          
                            **Suggest supplementing figure with the Matrix Plot below and turning off Plot Annotations**
                                                       """)
                plot.stripplot(test=test_type, group_col=group_col, value_col=dv_col, subgroup_col=subgroup_col,
                               palette=color, orient=orientation, pvalue_label=pvalue, pairs=pairs_select,
                               group_order=group_order, size=point_size)
        else:
            plot.stripplot(test=test_type, group_col=group_col, value_col=dv_col, subgroup_col=subgroup_col,
                           palette=color, orient=orientation, size=point_size)

    elif fig_type == 'Boxen Plot':
        if subgroup_col:
            st.error(f"🚨 {fig_type} currently **NOT supporting** calculations with Subgroup Column‼️")

        # must call ax. Thus, will need to plot "twice".
        if orientation == 'h':
            ax = sns.boxenplot(data=selected_data, x=dv_col, y=group_col, orient=orientation,
                               order=group_order)
        else:
            ax = sns.boxenplot(data=selected_data, x=group_col, y=dv_col, orient=orientation,
                               order=group_order)

        # Conditional to plot figure
        if annotation:
            if no_annotation is True:
                pass
            else:
                plot.boxenplot(test=test_type, group_col=group_col, value_col=dv_col, subgroup_col=subgroup_col,
                               palette=color, orient=orientation, pvalue_label=pvalue, pairs=pairs_select,
                               group_order=group_order)
        else:
            plot.boxenplot(test=test_type, group_col=group_col, value_col=dv_col, subgroup_col=subgroup_col,
                           palette=color, orient=orientation)
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
            st.error(":red[🚨 Please select a post-hoc test type‼️]")

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
            annotation, group_order, pairs_select, pvalue, legend, location, position, whisker, bars, capsize, loc, point_size, no_annotation, legend_configuration, bbox = _annotation(
                post_hoc_table,
                fig_type,
                selected_data,
                group_col,
                subgroup_col)

        # Set font type:
        plt.rcParams['font.family'] = style

        # Generate plots
        ax = _plot_fig(annotation, color, dv_col, fig_type, group_col, group_order, orientation, pairs_select,
                       plot, pvalue, selected_data, subgroup_col, test_type, whisker, bars, capsize, loc, point_size,
                       no_annotation)

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

            # legend configuration if there are subgroups
            if legend_configuration is None:
                self._final_legend(subgroup_col)
            else:
                self._final_legend(subgroup_col, loc=legend_configuration, bbox_to_anchor=bbox)

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

                    # Matrix plot conditions
                    st.sidebar.subheader("Matrix Plot Options")
                    with st.sidebar:
                        title = st.text_input(label='Matrix Title', value=f"Matrix of P-Values for {test}")

                        # cmap conditions
                        cmap = st.text_input(label='Color Options', value="Separate By Comma")
                        cmap_default = ["1", "#fbd7d4", "#005a32", "#238b45", "#a1d99b"]
                        if cmap == "Separate By Comma":
                            cmap = cmap_default
                        elif cmap == "":
                            st.warning(f":red[🚨 Input must be list separated by comma‼️]")
                            cmap = cmap_default
                        # assume input  is color palette
                        elif ',' not in cmap:
                            st.warning(f":red[🚨 Input must be list separated by comma‼️]")
                            cmap = cmap_default
                        # assume input is a list of colors
                        elif ',' in cmap:
                            cmap = [color.strip() for color in cmap.split(',')]
                            if len(cmap) < 5:
                                cmap = cmap_default
                                st.warning(f":red[🚨 Input must be 5 colors‼️]")
                        else:
                            st.write(":red[Not a valid color list!]")
                        st.caption("Can be color name or hex code")

                        # Additional matrix conditions
                        square = st.checkbox(label='Square', value=False)
                        linewidths = st.slider(label='Line Width', min_value=0.0, max_value=2.0, value=0.01, step=0.01)
                        linecolor = st.color_picker(label="Line Color", value="#808080")
                        st.write(":rainbow[Color Bar Options]")
                        left = st.slider(label='Left', min_value=0.0, max_value=2.0, value=0.95, step=0.05,
                                         key='matrix_left')
                        bottom = st.slider(label='Bottom', min_value=0.0, max_value=3.0, value=0.35, step=0.05,
                                           key='matrix_bottom')
                        width = st.slider(label='Width', min_value=0.0, max_value=1.0, value=0.05, step=0.05,
                                          key='matrix_width')
                        height = st.slider(label='Height', min_value=0.0, max_value=1.0, value=0.3, step=0.05,
                                           key='matrix_height')

                    fig = plots.p_matrix(cmap=cmap, title=title, linewidths=linewidths, linecolor=linecolor,
                                         square=square, cbar_ax_bbox=[left, bottom, width, height])[0]

                    st.pyplot(fig.figure)
                    self.download_fig(fig.figure, file_name='py50_matrix_plot.png')

    def _final_legend(self, subgroup_col, loc=None, bbox_to_anchor=None):
        """Plot legend and remove duplicates due to repeat sns and py50 plots"""
        # Get the current axes
        ax = plt.gca()
        # Get the handles and labels of the current axes
        handles, labels = ax.get_legend_handles_labels()
        # Combine the labels and handles
        unique_labels = []
        unique_handles = []
        for handle, label in zip(handles, labels):
            if label not in unique_labels:
                unique_labels.append(label)
                unique_handles.append(handle)
        # Create the legend from unique handles and labels
        plt.legend(unique_handles, unique_labels, title=subgroup_col, loc=loc, bbox_to_anchor=bbox_to_anchor)

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
                st.warning(f":red[🚨 ERROR: Something wrong with {test}]‼️")

        elif test == "Wilcoxon":
            if subgroup_col == 'None':
                try:
                    stat_df = stats.get_wilcoxon(value_col=dv_col, group_col=group_col)
                    st.warning(":red[🚨 ERROR: Wilcoxon Test needs a subgroup column]‼️")
                except ValueError:
                    st.error(
                        ":red[🚨 ERROR: The length of the groups in the Group Column are not equal for **Wilcoxon "
                        "Test**‼️]")
                    stat_df = None
            elif subgroup_col:
                try:
                    stat_df = stats.get_wilcoxon(value_col=dv_col, group_col=group_col, subgroup_col=subgroup_col)
                except ValueError:
                    st.error(
                        ":red[🚨 ERROR: The length of the groups in the Group Column are not equal for **Wilcoxon "
                        "Test**‼️]")
                    stat_df = None
            else:
                st.error(
                    ":red[🚨 ERROR: The length of the groups in the Group Column are not equal for **Wilcoxon Test**‼️]")
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
                st.warning(f":red[🚨 ERROR: Something wrong with **{test}**‼️]")
        else:
            st.write(":red[Select Post-Hoc Test]")

        # Output table
        st.data_editor(stat_df)
        st.write(":red[NOTE: ]",
                 "Very small *p-values* may **appear as 0**. Please download .csv file to view specific value.")
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
            if subgroup_col is None or subgroup_col == 'None':
                stat_df = stats.get_anova(value_col=dv_col, group_col=group_col)
            else:
                st.write(":blue[Select Subgroup Column for Two-Way ANOVA.]")
                stat_df = stats.get_anova(value_col=dv_col, group_col=[group_col, subgroup_col])

        elif test == 'Welch-ANOVA':
            if subgroup_col is None or subgroup_col == 'None':
                stat_df = stats.get_welch_anova(value_col=dv_col, group_col=group_col)
            else:
                st.write(":blue[Warning: Subgroup Column needed for calculation.]")
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
            if subgroup_col is None:
                stat_df = stats.get_kruskal(value_col=dv_col, group_col=group_col)
            else:
                st.write(":vluw[Warning: Subgroup Column not needed for calculation.]")
                stat_df = stats.get_kruskal(value_col=dv_col, group_col=group_col)

        elif test == 'Cochran (Non-Parametric)':
            if subgroup_col is None:
                st.warning(":red[🚨 Cochran Test requires a **Subgroup Column**‼️]")
                stat_df = stats.get_cochran(value_col=dv_col, group_col=group_col)
            else:
                stat_df = stats.get_cochran(value_col=dv_col, group_col=group_col, subgroup_col=subgroup_col)

        elif test == 'Friedman (Non-Parametric)':
            if subgroup_col is None:
                st.warning(":red[🚨 Friedman Test requires a **Subgroup Column**‼️]")
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
