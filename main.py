# main.py

import streamlit as st
import pandas as pd
import pydeck as pdk

# General locations in Puerto Rico
data = pd.DataFrame({
    'latitude': [18.2208, 18.4655, 18.4010],  # PR Center, San Juan, Ponce
    'longitude': [-66.5901, -66.1057, -66.6139]
})

# Highlight El Morro (San Juan)
highlight = pd.DataFrame({
    'latitude': [18.4706],  # El Morro
    'longitude': [-66.1239]
})

# Define the map layers
puerto_rico_layer = pdk.Layer(
    "ScatterplotLayer",
    data,
    get_position=["longitude", "latitude"],
    get_radius=2000,  # Adjust the circle size
    get_color=[0, 0, 255, 180],  # Blue color (RGBA)
    pickable=True,
)

el_morro_layer = pdk.Layer(
    "ScatterplotLayer",
    highlight,
    get_position=["longitude", "latitude"],
    get_radius=4000,  # Bigger highlight for visibility
    get_color=[255, 0, 0, 200],  # Red color (RGBA)
    pickable=True,
)

# Define the view settings (Zoom into Puerto Rico)
view_state = pdk.ViewState(
    latitude=18.45,  # Center the map near San Juan
    longitude=-66.12,
    zoom=10,  # Zoom into PR
    pitch=0,
)

# Render the map in Streamlit
st.pydeck_chart(pdk.Deck(
    layers=[puerto_rico_layer, el_morro_layer],
    initial_view_state=view_state,
    tooltip={"text": "Latitude: {latitude}\nLongitude: {longitude}"}
))
