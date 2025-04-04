import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.distance import geodesic
import openrouteservice
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# API Key for OpenRouteService (Replace with your actual key)
ORS_API_KEY = os.getenv("ORS_API_KEY", "5b3ce3597851110001cf6248afd4bb63fe3a470bb0061a1ac1d8a410")

# Initialize OpenRouteService Client
client = openrouteservice.Client(key=ORS_API_KEY)

# Function to get coordinates using OpenRouteService
def get_coordinates(place):
    """Get coordinates (latitude, longitude) for a given place."""
    try:
        response = client.pelias_search(place)
        if response and 'features' in response and len(response['features']) > 0:
            location = response['features'][0]['geometry']['coordinates']
            return (location[1], location[0])  # Return (lat, lon)
    except Exception as e:
        st.error(f"Geocoding error: {e}")
        logging.error(f"Geocoding error for {place}: {e}")
    return None

# Function to calculate distance via OpenRouteService
def calculate_distance_via_ors(origin, destination, profile):
    """Calculate distance between two locations using OpenRouteService."""
    coords_origin = get_coordinates(origin)
    coords_dest = get_coordinates(destination)

    if coords_origin and coords_dest:
        coordinates = [coords_origin[::-1], coords_dest[::-1]]  # ORS expects (lon, lat)
        try:
            routes = client.directions(coordinates=coordinates, profile=profile)
            distance_m = routes['routes'][0]['summary']['distance']
            return round(distance_m / 1000, 2)  # Convert meters to kilometers
        except Exception as e:
            st.error(f"Error fetching data from ORS: {e}")
            logging.error(f"ORS API error: {e}")
            return None
    else:
        st.error("Could not geocode the provided locations.")
        return None

# Function to calculate rail distance
def calculate_rail_distance(origin, destination):
    """Calculate rail distance between two locations."""
    raw_distance = calculate_distance_via_ors(origin, destination, 'driving-hgv')
    if raw_distance:
        return round(raw_distance * 0.968, 2)  # Adjust for rail efficiency
    return None

# Function to calculate air distance
def calculate_air_distance(origin, destination):
    """Calculate air distance between two locations using geodesic distance."""
    coords_origin = get_coordinates(origin)
    coords_dest = get_coordinates(destination)
    if coords_origin and coords_dest:
        return round(geodesic(coords_origin, coords_dest).km, 2)
    return None

# Constants
EMISSION_FACTOR = 1.58  # Emission factor per km per kg

# Transport modes and efficiency
TRANSPORT_MODES = {
    "Truck": {"profile": "driving-car", "efficiency": 1.9},
    "Rail": {"profile": "driving-hgv", "efficiency": 0.6},  # Heavy Goods Vehicle as a proxy
    "Air": {"profile": None, "efficiency": 3.0}  # Geodesic Distance for Air
}

# Streamlit UI
def logist_vis():
    """Display the logistics emission calculator."""
    st.title("📦 Logistics Emission Calculator")
    st.subheader("Auto-compute CO₂ emissions based on real-world distances")

    # User Inputs
    material = st.selectbox("Select Material", ["Steel", "Wood", "Plastic", "Concrete"])
    transport_mode = st.radio("Select Transport Mode", list(TRANSPORT_MODES.keys()))
    origin = st.text_input("Enter Origin City", "Delhi")
    destination = st.text_input("Enter Destination City", "Mumbai")
    weight = st.number_input("Enter Material Weight (kg)", min_value=1, value=1000)

    # Compute Distance
    distance = None
    if origin and destination:
        if transport_mode == "Air":
            distance = calculate_air_distance(origin, destination)
        elif transport_mode == "Rail":
            distance = calculate_rail_distance(origin, destination)
        else:
            profile = TRANSPORT_MODES[transport_mode]["profile"]
            distance = calculate_distance_via_ors(origin, destination, profile)

        if distance:
            st.write(f"🚗 Estimated Distance: **{distance} km**")
        else:
            st.error("Could not calculate distance. Check city names.")

    # Compute Emission
    if distance:
        efficiency_factor = TRANSPORT_MODES[transport_mode]["efficiency"]
        total_emission = round(distance * weight * EMISSION_FACTOR * efficiency_factor, 2)

        # Display Metrics
        st.metric(label="Total CO₂ Emission (kg)", value=total_emission)

        # Dataframe for comparison
        data = pd.DataFrame({
            "Transport Mode": list(TRANSPORT_MODES.keys()),
            "Emission (kg CO₂)": [
                round(distance * weight * EMISSION_FACTOR * TRANSPORT_MODES[mode]["efficiency"], 2)
                for mode in TRANSPORT_MODES.keys()
            ]
        })

        # Bar Chart
        st.subheader("Emission Comparison by Transport Mode")
        fig = px.bar(data, x="Transport Mode", y="Emission (kg CO₂)", color="Transport Mode", text="Emission (kg CO₂)")
        st.plotly_chart(fig, use_container_width=True)

        # Conclusion
        st.success(f"Transporting {weight} kg of {material} from {origin} to {destination} via {transport_mode} emits **{total_emission} kg CO₂**.")

# Run the app
if __name__ == "__main__":
    logist_vis()