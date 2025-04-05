import ast
import json
import os
import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import plotly.graph_objects as go
import logging
from streamlit_autorefresh import st_autorefresh
from plotly.subplots import make_subplots

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"..", "..", "data", "emissions.db")


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")



######################## - GET THE LATEST EVENT DETAILS - #############################
def get_latest_event():
    """Fetch the latest event name from the Events table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM Events ORDER BY id DESC LIMIT 1")
    event = cursor.fetchone()
    return event[0] if event else None

st_autorefresh(interval=1000, key="latest_event_refres")
event_name = get_latest_event()



##############################################################################################
def fetch_emissions_data(event_name):
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM EmissionsSummary WHERE Event = ?"
    df = pd.read_sql_query(query, conn, params=(event_name,))
    conn.close()
    return df
## Calculate totals by scope
def calculate_scope_totals(df):
    scope_totals = df.groupby('Category')['Emission'].sum().to_dict()
    return scope_totals

# Create metric card
def create_metric_card(title, value, color):
    st.markdown(
        f"""
        <div style="background-color: {color}; padding: 20px; border-radius: 10px; text-align: center; margin: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
            <h3 style="color: white; font-family: 'Anime', sans-serif;">{title}</h3>
            <h2 style="color: white; font-size: 36px;">{value:.2f} tCO2e</h2>
        </div>
        """,
        unsafe_allow_html=True
    )


    
    # Sea background (using base64 encoded image)
    sea_background = """
    <style>
    .stApp {
        background-color: #343E49;
    h1 {
        color: #FFD700;
        font-family: 'Anime', sans-serif;
        text-shadow: 2px 2px 4px #000000;
    }
    </style>
    """
    st.markdown(sea_background, unsafe_allow_html=True)
    

# Main dashboard function
def vis():
    # Fetch and prepare data
    df = fetch_emissions_data(event_name)
    scope_totals = calculate_scope_totals(df)
    
    # Header
    st.title("Emissions Dashboard")
    st.markdown(f"### Track Your {event_name} Carbon Footprintss")
    
    # Metrics row
    col1, col2, col3 = st.columns(3)
    with col1:
        create_metric_card("Scope 1 - Direct Emissions", 
                         scope_totals.get('Scope 1', 0), 
                         "#1E90FF")  # Deep blue like the sea
    with col2:
        create_metric_card("Scope 2 - Electricity", 
                         scope_totals.get('Scope 2', 0), 
                         "#4682B4")  # Steel blue
    with col3:
        create_metric_card("Scope 3 - Indirect", 
                         scope_totals.get('Scope 3', 0), 
                         "#87CEEB")  # Sky blue
    
    # Charts section
    st.markdown("---")
    st.markdown("### Emissions Analysis - Activities")
    
    col4, col5 = st.columns(2)
    
    with col4:
        # Pie chart for emission distribution
        fig_pie = px.pie(
            df.groupby('Category')['Emission'].sum().reset_index(),
            values='Emission',
            names='Category',
            title=f"Emissions Distribution by Category in Event {event_name}",
            color_discrete_sequence=['#1E90FF', '#4682B4', '#87CEEB']
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_color='#FFD700'
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col5:
        # Bar chart for sources
        top_sources = (df.groupby('SourceTable')['Emission'].sum().reset_index().sort_values(by='Emission', ascending=False).head(5))
        fig_bar = px.bar(
            top_sources.groupby(['SourceTable'])['Emission'].sum().reset_index(),
            x='Emission',
            y='SourceTable',
            title=f"Top Highest Emissions Recorded In this Event {event_name}", 
            color='SourceTable',
            text='Emission',
            color_discrete_sequence=['#20B2AA', '#4169E1', '#00CED1', '#1E90FF', '#87CEFA', '#4682B4']
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_color='#FFD700',
            showlegend=False
        )
        fig_bar.update_traces(
            texttemplate='%{text:.2s}',  # Show short form (e.g., 2.1k)
            textposition='auto'          # 🟢 Place text on the bar
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    


# Run the dashboard
if __name__ == "__main__":
    vis()