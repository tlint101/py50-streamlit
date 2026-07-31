"""
Page-specific helpers for the Changelog page.
Extracted from page/Changelog.py for better maintainability.
"""

import streamlit as st


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


def render_changelog():
    """Render the changelog content."""
    st.markdown('# :red[**Changelog**]')

    st.markdown('## :rainbow[**2026.07.30**]')
    st.markdown('''
    ##### :green[**Major Changes**] 🎉
    - Updated py50 to **v1.1.0**
    - Updated streamlit to **v1.60.0**

    ##### :green[**Code Refactoring**] 🔧
    - Refactored page code for better maintainability
    - Extracted page-specific functions into dedicated helper modules
    - Removed thin wrapper files and consolidated shared styling

        ''')

    st.markdown('''  
    <br><br>
    :red[2024.12.14]

    ''', unsafe_allow_html=True)
    st.markdown('''
    :green[**Major Changes**] 🎉
    py50-streamlit has been updated to [py50 v1.0.9](https://github.com/tlint101/py50/releases)!

    Bugs have been fixed for box and violin plots! 
    ''')
