# main.py


import streamlit as st
import pandas as pd
 
## Create a sample DataFrame with latitude and longitude values
data = pd.DataFrame({
    'latitude': [37.7749, 34.0522, 40.7128],
    'longitude': [-122.4194, -118.2437, -d74.0060]
})

highlight = pd.DataFrame({
    'latitude': [38.8977],
    'longitude': [-77.0365]
})

# Create a map with the data and highlight
st.map(data)
st.map(highlight, color="red")