import os
import streamlit as st
import sqlite3
import json
import logging
from typing import List  # Only import what is needed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR,"..", "..", "data", "emissions.db")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 🍲 Food Emission Factors (kg CO₂ per kg)
FOOD_EMISSION_FACTORS = {
    "Beef": 27.0,
    "Chicken": 6.9,
    "Rice": 2.7,
    "Vegetables": 2.0,
    "Corn": 0.8,
    "Capsicum": 0.07,
    "Pine-apple": 0.12,
    "Curd": 2.66,
    "Sugar": 0.58,
    "Kaju": 2.13,
    "magach": 1.8,
    "tomato": 2.90,
    "onion": 0.5,
    "paneer": 5.1,
    "ghee": 4.2,
    "oil (l)": 1.98,
    "fresh cream": 3.94,
    "butter": 11.52,
}

# 🍲 Dishes Emission Factors (kg CO₂ per kg)
DISHES_EMISSION_FACTORS = {
    "Spicy corn salaad": 0.8 * 0.07,  # corn and capsicum
    "Pine apple raita": 0.12 * 2.66 * 0.58,  # pine apple, curd, sugar
    "Paneer tikka masala": 2.13 * 1.8 * 2.09 * 0.5 * 0.07 * 5.1,  # kaju, magach, tomato, onion, capsicum, paneer
    "Vegetable Jalfrez": 0.72,  # mix of vegetables
    "Kashmiri pulaao": 4.2 * 2.44 * 0.5,  # Ghee, rice, cocktail fruit
    "Strawberry ice cream": 1.98 * 3.94 * 11.52,  # oil, fresh cream, butter
}

# 🧮 Calculate Food Emission
def calculate_food_emission(food_item: str, quantity: float) -> float:
    """Calculate emissions based on food consumption."""
    return quantity * FOOD_EMISSION_FACTORS.get(food_item, 0)

# 🧮 Calculate Dish Emission
def calculate_dish_emission(dish: str, quantity: float) -> float:
    """Calculate emissions based on dish consumption."""
    return quantity * DISHES_EMISSION_FACTORS.get(dish, 0)

# 📌 Insert Food Data into DB
def insert_food_data(event: str, food_items: List[str], quantities: List[float], emissions: List[float], total_emission: float):
    """Insert multiple food entries into the database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()

            # Convert lists to JSON strings for storage
            food_items_json = json.dumps(food_items)
            quantities_json = json.dumps(quantities)
            emissions_json = json.dumps(emissions)

            c.execute("""
                INSERT INTO FoodItemsEmissions (event, food_items, quantity, emission, total_emission)
                VALUES (?, ?, ?, ?, ?)""",
                (event, food_items_json, quantities_json, emissions_json, total_emission)
            )

            conn.commit()
            st.success("Food emission data saved successfully!")
            logging.info(f"Inserted food data for event: {event}")
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        logging.error(f"Failed to insert food data: {e}")

# 📌 Insert Dish Data into DB
def insert_dish_data(event: str, dish: str, quantity: float, emission: float):
    """Insert dish emission data into the database."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO FoodItems (event, FoodItem, Quantity, Emission) VALUES (?, ?, ?, ?)",
                (event, dish, quantity, emission)
            )
            conn.commit()
            st.success("Dish emission data saved successfully!")
            logging.info(f"Inserted dish data for event: {event}")
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        logging.error(f"Failed to insert dish data: {e}")

# 🥗 Show Food Calculator
def show_food_calculator(event):
    """Display the food emission calculator."""


    tab1, tab2 = st.tabs(["Food Items", "Dishes"])

    with tab1:
        st.title("🥗 Food Emission Calculator")
        st.write("This tool calculates CO₂ emissions from different food items.")

        # Initialize session state for food entries
        if "food_entries" not in st.session_state:
            st.session_state.food_entries = [{"id": 0, "food_item": "Beef", "quantity": 1.0}]

        total_emission = 0  # Reset total emissions each time
        food_items, quantities, emissions = [], [], []

        # Display food entries dynamically
        for entry in st.session_state.food_entries:
            index = entry["id"]
            cols = st.columns([3, 3, 2])  # Set column widths

            with cols[0]:  # Food Item Selection
                food_item = st.selectbox(
                    f"Food Item {index + 1}:", FOOD_EMISSION_FACTORS.keys(),
                    key=f"food_{index}", index=list(FOOD_EMISSION_FACTORS.keys()).index(entry["food_item"])
                )

            with cols[1]:  # Quantity Input
                quantity = st.number_input(
                    f"Quantity {index + 1} (kg):",
                    min_value=0.1, step=0.1, value=entry["quantity"],
                    key=f"quantity_{index}"  # <-- Fixed: Removed extra parenthesis
                )

            with cols[2]:  # Remove Entry Button
                if st.button("Remove", key=f"remove_{index}"):
                    st.session_state.food_entries = [e for e in st.session_state.food_entries if e["id"] != index]
                    st.rerun()

            emission = calculate_food_emission(food_item, quantity)
            total_emission += emission

            # Store values for database insertion
            food_items.append(food_item)
            quantities.append(quantity)
            emissions.append(emission)

        # Display total emissions
        st.subheader(f"Total Emission: {total_emission:.3f} kg CO₂")

        # Save all food data
        if st.button("Save Emission Data"):
            if not event:
                st.error("Please enter an event name before saving!")
            else:
                insert_food_data(event, food_items, quantities, emissions, total_emission)

        # Add another food entry
        if st.button("Add Another Food Item"):
            new_id = max([e["id"] for e in st.session_state.food_entries], default=-1) + 1
            st.session_state.food_entries.append({"id": new_id, "food_item": "Beef", "quantity": 1.0})
            st.rerun()

    with tab2:
        st.subheader("Dishes & Curries")
        dish = st.selectbox(
            "Select the Item:",
            list(DISHES_EMISSION_FACTORS.keys()),
            key="dish_select"
        )
        quantity = st.number_input(
            "Enter Quantity (kg):", min_value=0.1, step=0.1, value=1.0, key="dish_quantity"
        )
        if st.button("Calculate & Save", key="calculate_dish"):
            emission = calculate_dish_emission(dish, quantity)
            insert_dish_data(event, dish, quantity, emission)
            st.success(f"Emission for {quantity} kg of {dish}: {emission:.3f} kg CO₂")