import streamlit as st

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


"""
CHANGELOG BELOW
"""

st.markdown('# :red[**Changelog**]')

st.markdown('## :rainbow[**2024.05.17**]')
st.markdown('''
##### :green[**Major Changes**] 🎉
py50-streamlit has been updated to [py50 v1.0.6](https://github.com/tlint101/py50/releases)!

Users can perform basic statistical tests and generate annotated plots!
            ''')