import sqlite3
import streamlit as st
from app_pages.scope1 import scope1_page
from app_pages.scope2 import scope2_page
from app_pages.scope3 import scope3_page
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"..", "..", "data", "emissions.db")

def overview_page():
    # Check if user is logged in
    if "logged_in_user" not in st.session_state:
        st.error("Login is required")
        return

    st.subheader("🌍 Emissions Overview")
    st.write(
        "Emissions refer to the release of gases, particles, or pollutants into the atmosphere from various sources. "
        "These emissions can originate from natural processes (such as volcanic eruptions or wildfires) or human activities "
        "(such as burning fossil fuels, industrial processes, and agriculture)."
    )

    st.write("The emissions can be categorized into three scopes:")
    st.write(
        "These three categories are used in Greenhouse Gas (GHG) accounting to measure and report emissions from different sources. "
        "They help organizations track their carbon footprint and take action to reduce it."
    )

    # Scope 1
    with st.expander("🔍 **Scope 1: Direct Emissions**"):
        st.write(
            "Scope 1 emissions are direct emissions from sources owned or controlled by a company. "
            "Examples include emissions from company vehicles, on-site fuel combustion, and industrial processes."
        )
        st.image("https://via.placeholder.com/600x200.png?text=Scope+1+Example", use_container_width=True)

    # Scope 2
    with st.expander("🔍 **Scope 2: Indirect Emissions**"):
        st.write(
            "Scope 2 emissions are indirect emissions from the generation of purchased electricity, heating, or cooling consumed by a company. "
            "These emissions occur at the facility where the energy is generated but are attributed to the company that consumes the energy."
        )
        st.image("https://via.placeholder.com/600x200.png?text=Scope+2+Example", use_container_width=True)

    # Scope 3
    with st.expander("🔍 **Scope 3: Indirect Emissions from the Supply Chain**"):
        st.write(
            "Scope 3 emissions are indirect emissions from sources not owned or controlled by the company but related to its activities. "
            "Examples include emissions from employee commuting, business travel, and the production of purchased goods and services."
        )
        st.image("https://via.placeholder.com/600x200.png?text=Scope+3+Example", use_container_width=True)

    st.subheader("Why These Emissions Matter")
    st.write(
        "Addressing all three scopes is vital for achieving net-zero goals, improving sustainability, meeting regulatory requirements, "
        "and gaining consumer trust in an increasingly environmentally conscious world. 🌍💚"
    )

    st.subheader("How Do We Calculate These Emissions")
    st.markdown("<h4>Emissions = Activity Data x Emission Factor</h4>", unsafe_allow_html=True)

    st.subheader("Why Are Emissions Important?")
    st.write(
        """
        - **Climate Change:** GHGs trap heat in the atmosphere, contributing to global warming.
        - **Air Pollution & Health Risks:** Pollutants can cause respiratory issues, heart diseases, and other health problems.
        - **Environmental Impact:** Emissions lead to phenomena such as acid rain, ocean acidification, and ecosystem disruption.
        - **Mitigation Efforts:** Strategies like renewable energy adoption, energy efficiency, carbon capture, and policy initiatives (e.g., the Paris Agreement) are key to reducing emissions.
        """
    )

    # Add links to other pages
    st.markdown("---")
    st.subheader("Explore More")

    event_name =  st.text_input("Enter event name",key="event_name")
    if st.button("Save"):
        with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO Events (name) VALUES (?)",(event_name,))
                conn.commit()   
        st.success(f"Event {event_name} saved successfully")

    # Define page names
    overview = "Overview"
    scope1 = "Scope 1"
    scope2 = "Scope 2"
    scope3 = "Scope 3"

    # Initialize session state
    if "current_page" not in st.session_state:
        st.session_state.current_page = overview  # Default to Overview page

    # Navigation buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Scope 1 Calculator"):
            st.session_state.current_page = scope1
            st.rerun()

    with col2:
        if st.button("Scope 2 Calculator"):
            st.session_state.current_page = scope2
            st.rerun()

    with col3:
        if st.button("Scope 3 Calculator"):
            st.session_state.current_page = scope3
            st.rerun()

    # Display the selected page
    st.markdown("---")  # Divider for clarity

    if st.session_state.current_page == overview:
        return
    elif st.session_state.current_page == scope1:
        scope1_page()
    elif st.session_state.current_page == scope2:
        scope2_page()
    elif st.session_state.current_page == scope3:
        scope3_page()
