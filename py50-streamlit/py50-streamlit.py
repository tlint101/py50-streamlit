"""
Main entry point for the py50-streamlit application.
Launches the multi-page Streamlit app with Home page as default.
"""

import os
import streamlit as st
from streamlit_activities_menu import get_available_activities, build_activities_menu

st.set_page_config(
    page_title="py50",
    page_icon="👋",
    layout='wide'
)


def run():
    working_directory = os.path.dirname(os.path.abspath(__file__))

    # add logo
    image = os.path.join(working_directory, "img/py50_logo_only.png")
    st.sidebar.image(image, width=200)

    # Load the available services
    page_settings_path = os.path.join(working_directory, "page_settings.yaml")
    page_path = os.path.join(working_directory, "page/")

    # Load the yaml with core services as activities
    core_activities = get_available_activities(
        activities_filepath=os.path.abspath(page_settings_path)
    )

    page_option, _ = build_activities_menu(
        activities_dict=core_activities,
        label='**Pages:**',
        key='activitiesMenu',
        activities_dirpath=os.path.abspath(page_path),
        disabled=False
    )

    # Render Home page when selected
    if page_option == 'Home':
        st.markdown('# Welcome to py50!')
        st.markdown(
            """
            py50 is a program to calculate IC50 values and to generate dose-response curves. The program utilizes the Four 
            parameter logistic (4PL) regression model. 
            
            """
        )
        st.markdown('Further information for py50 can be found on the GitHub repository [here](%s).' % 'https://github.com/tlint101/py50')
        st.markdown('Documentation can be found [here](%s).' % 'https://py50.readthedocs.io/en/latest/?badge=latest')
        st.markdown('If you are interested in citing py50, you are welcome to use the zenodo link [here](%s).' % 'https://zenodo.org/records/10183941')
    else:
        pass


if __name__ == '__main__':
    run()
else:
    st.error('The app failed initialization. Report issue to maintainers on github')
