import os
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"..", "..", "data", "emissions.db")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@st.cache_data  # Cache the data to avoid redundant database calls
def fetch_transport_data(table):
    """Fetch transport emissions data from the database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"SELECT Mode, Vehicle, WeightOrDistance, Emission, Timestamp FROM {table}")
        data = cursor.fetchall()
        conn.close()
        return data
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        logging.error(f"Error fetching transport data: {e}")
        return []

def display_descriptive_analytics(df):
    """Display descriptive analytics for transport emissions."""
    total_emission = round(df["Emission (kg CO₂)"].sum(), 3)
    avg_emission = round(df["Emission (kg CO₂)"].mean(), 3)
    max_emission = round(df["Emission (kg CO₂)"].max(), 3)
    min_emission = round(df["Emission (kg CO₂)"].min(), 3)
    day_with_highest_emission = df["Timestamp"].max()
    no_of_emissions = df["Emission (kg CO₂)"].count()

    st.subheader("Descriptive Analysis")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label='Total Emission (kg CO₂)', value=total_emission, delta_color="off")
    with col2:
        st.metric(label='Average Emission (kg CO₂)', value=avg_emission, delta_color="off")
    with col3:
        st.metric(label='Highest Recorded Emission (kg CO₂)', value=max_emission, delta_color="off")

    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric(label='Lowest Recorded Emission (kg CO₂)', value=min_emission, delta_color="off")
    with col5:
        st.metric(label='Number of Emissions Recorded', value=no_of_emissions, delta_color="off")
    with col6:
        st.metric(label='Day with Highest Emission', value=day_with_highest_emission, delta_color="off")

def transport_visual(table):
    """Display transport emissions visualizations."""
    st.subheader("🚗 Transport Emission Data")

    # Fetch data (cached)
    data = fetch_transport_data(table)
    if not data:
        st.warning("No transport emission records found.")
        return

    # Convert data to DataFrame
    df = pd.DataFrame(data, columns=["Mode", "Vehicle", "Distance (km)", "Emission (kg CO₂)", "Timestamp"])
    df["Distance (km)"] = df["Distance (km)"].astype(float)
    df["Emission (kg CO₂)"] = df["Emission (kg CO₂)"].astype(float)

    # Display raw data
    st.write("### Raw Data")
    st.dataframe(df, use_container_width=True)

    # Descriptive analytics
    display_descriptive_analytics(df)

    # Interactive filters
    st.sidebar.header("Filters")
    vehicle_types = df["Vehicle"].unique()
    selected_vehicles = st.sidebar.multiselect(
        "Select Vehicle Types", vehicle_types, default=vehicle_types
    )
    emission_range = st.sidebar.slider(
        "Select Emission Range (kg CO₂)",
        float(df["Emission (kg CO₂)"].min()),
        float(df["Emission (kg CO₂)"].max()),
        (float(df["Emission (kg CO₂)"].min()), float(df["Emission (kg CO₂)"].max())),
    )

    # Filter data based on user selection
    filtered_df = df[
        (df["Vehicle"].isin(selected_vehicles)) &
        (df["Emission (kg CO₂)"] >= emission_range[0]) &
        (df["Emission (kg CO₂)"] <= emission_range[1])
    ]

    # Visualization options
    st.write("### Visualizations")
    chart_type = st.selectbox(
        "Select Chart Type", ["Bar Chart", "Scatter Plot", "Line Chart"]
    )

    if chart_type == "Bar Chart":
        fig = px.bar(
            filtered_df,
            x="Vehicle",
            y="Emission (kg CO₂)",
            color="Mode",
            title="Transport Emissions by Vehicle Type",
            labels={"Emission (kg CO₂)": "CO₂ Emission (kg)"},
        )
    elif chart_type == "Scatter Plot":
        fig = px.scatter(
            filtered_df,
            x="Distance (km)",
            y="Emission (kg CO₂)",
            color="Vehicle",
            title="Emission vs Distance by Vehicle Type",
        )
    elif chart_type == "Line Chart":
        fig = px.line(
            filtered_df,
            x="Timestamp",
            y="Emission (kg CO₂)",
            color="Vehicle",
            title="Emission Trend Over Time",
        )

    st.plotly_chart(fig, use_container_width=True)

# Example usage
if __name__ == "__main__":
    transport_visual("TransportEmissions")