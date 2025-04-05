import os
import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_autorefresh import st_autorefresh

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"..", "..", "data", "emissions.db")


def fetch_food_data(table):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        c = conn.cursor()
        cursor.execute(f"SELECT FoodItem, Quantity, Emission FROM {table}")
        c = conn.execute(f"SELECT name FROM Events ORDER BY id DESC LIMIT 1")
        data = cursor.fetchall()
        event = c.fetchone()
        conn.close()
        return data, event 
    except sqlite3.Error as e:
        st.error(f"An error occurred: {e}")
        return []

def fetch_event_data():
    c = sqlite3.connect(DB_PATH)
    cursor = c.cursor()
    cursor.execute("SELECT name FROM Events ORDER BY id DESC LIMIT 1")
    cursor.fetchone()
    c.close()
st_autorefresh(interval=1000, key="latest_refresh")
latest_event = fetch_event_data()


def food_visual():
    table = "food_choices"
    data = fetch_food_data(table)
    
    st.subheader("🍎 Food Emission Data")

    if data:
        df = pd.DataFrame(data, columns=["FoodItems", "Quantity", "Emission (kg CO₂)"])
        dataframe = dataframe_explorer(df)
        st.dataframe(dataframe, use_container_width=True)
        
        st.subheader("Descriptive Analysis")
        # Calculate insights
        total_emission = round(df["Emission (kg CO₂)"].sum(), 3)
        avg_emission = round(df["Emission (kg CO₂)"].mean(), 3)
        max_emission = round(df["Emission (kg CO₂)"].max(), 3)
        min_emission = round(df["Emission (kg CO₂)"].min(), 3)
        no_of_emissions = df["Emission (kg CO₂)"].count()

        # Display insights
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label='Total Emission (kg CO₂)', value=total_emission, border=True)
        with col2:
            st.metric(label='Average Emission (kg CO₂)', value=avg_emission, border=True)
        with col3:
            st.metric(label='Highest Recorded Emission (kg CO₂)', value=max_emission, border=True)

        col4, col5 = st.columns(2)
        with col4:
            st.metric(label='Lowest Recorded Emission (kg CO₂)', value=min_emission, border=True)
        with col5:
            st.metric(label='Number of Emissions Recorded', value=no_of_emissions, border=True)


        st.subheader("Quantity of Food items:")
        fig = px.scatter(df, x="Quantity", y="FoodItem",  color_continuous_scale="Blues", template="plotly_dark", size_max=15)
        fig.update_traces(marker=dict(size=12, line=dict(width=1, color="black")), hovertemplate="<b>Quantity:</b> %{x}")
        st.plotly_chart(fig, use_container_width=True)          

        st.subheader("Emissions")
        cat = st.selectbox("Select option:", ["Pi chart","Scatter", "Bar plot", "Line Graph"])
        
        if cat == "Pi chart":
            # pi chart
            fig = px.pie(df, names='FoodItem', values="Emission (kg CO₂)", title="Emissions Breakdown", hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
        
        
        elif cat == "Scatter":
            fig = px.scatter(df, x="FoodItem", y="Emission (kg CO₂)", title="Emission Distribution", color='Emission (kg CO₂)', color_continuous_scale="Blues", template="plotly_dark", size_max=15)
            fig.update_traces(marker=dict(size=12, line=dict(width=1, color="black")), hovertemplate="<b>Quantity:</b> %{x} kg<br><b>CO₂ Emission:</b> %{y} kg")
            st.plotly_chart(fig, use_container_width=True)
        
        elif cat == "Bar plot":
            fig = px.bar(df, x="FoodItem", y="Emission (kg CO₂)", text="Emission (kg CO₂)", color="Emission (kg CO₂)", color_continuous_scale="blues", labels={"FoodItem": "Food Item", "Emission (kg CO₂)": "CO₂ Emission (kg)"}, title="Emission Distribution")
            fig.update_traces(texttemplate='%{text}', textposition='outside')
            fig.update_layout(xaxis=dict(tickmode="linear"), plot_bgcolor="white", font=dict(size=14))
            st.plotly_chart(fig, use_container_width=True)
        elif cat == "Line Graph":
            fig = px.line(df,x="Emission (kg CO₂)", y="FoodItem", markers=True, title="Emission Trend by Food Item")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No food emission records found.")
