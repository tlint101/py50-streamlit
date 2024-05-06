import streamlit as st
import pandas as pd
from page.functions.stat_func import Stats

# # Set page config
# st.set_page_config(page_title='py50: Plot Curves', page_icon='📈', layout='centered')

# Adjust hyperlink colorscheme
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

'''
Page layout begins below
'''

tutorial = 'https://github.com/tlint101/py50/blob/main/tutorials/006_statistics_quickstart.ipynb'
datasets = 'https://github.com/tlint101/py50-streamlit/tree/main/dataset'
st.markdown('# Statistics Calculator')
st.write('The Statistics Calculator provides 3 columns:')
st.write('- Group')
st.write('- Dependent Variable')
st.write('- Subgroup')
st.write('Depending on the test selected, only Group and Dependent Variable is needed. Subgroup can be ignored.')
st.write('For more information on how the statistics calculator works in py50, see the tutorial [here](%s)' % tutorial)
st.write('Sample datasets can be found [here](%s)' % datasets)
st.write('')

st.markdown('## Select an option to get started:')
option = st.radio(
    'Paste Data or upload .csv file',
    ('Paste Data', 'Upload CSV File'))

"""
Code begins below
"""

stats = Stats()

# Data input
if option == 'Upload CSV File':
    # Upload the CSV file
    uploaded_file = st.file_uploader('Upload .csv file')

    # Check if a CSV file has been uploaded
    if uploaded_file is not None:
        # Read the CSV file into a DataFrame
        data = pd.read_csv(uploaded_file)
        st.write('## Input Table')
        st.data_editor(data, num_rows='dynamic', key='uploaded_output')  # visualize dataframe in streamlit app
    else:
        # Display a message if no CSV file has been uploaded
        st.warning('Please upload a .csv file.')

    # Select columns for calculation
    if uploaded_file is not None:  # nested in if/else to remove initial traceback error
        stats.stats_program(df=data, paste=False)

# Editable DataFrame
elif option == 'Paste Data':
    st.markdown('### Paste Data in Table:')
    # Make dummy dataframe
    data = pd.DataFrame([{"Group": '', 'Dependent Variable': '', 'Subgroup': ''}, ])

    edited_df = st.data_editor(data, num_rows='dynamic', key='paste_data')

    if (edited_df == '').all().all():
        st.write('Table is currently empty')
    else:
        stats.stats_program(df=edited_df, paste=True)

    # Output table
    edited_df = st.data_editor(data, num_rows='dynamic')
    stats.download_button(edited_df, file_name='py50_stats.csv')
