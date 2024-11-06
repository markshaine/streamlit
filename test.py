import streamlit as st
import geemap
import folium
from streamlit_folium import st_folium
import ee

ee.Authenticate()
# Initialize Earth Engine
ee.Initialize(project= 'ee-shainemark7')

# Streamlit app title
st.title("Interactive NDVI Map")

# Sidebar for user inputs
st.sidebar.title("Options")
year = st.sidebar.slider("Select Year:", 2000, 2023, 2022)
month = st.sidebar.slider("Select Month:", 1, 12, 6)

# Define a function to calculate NDVI
def get_ndvi_image(year, month):
    # Load Sentinel-2 image collection
    collection = ee.ImageCollection('COPERNICUS/S2') \
                    .filterDate(f'{year}-{month:02d}-01', f'{year}-{month:02d}-28') \
                    .filterBounds(ee.Geometry.Point([10.0, 20.0]))  # Adjust to your study area

    # Compute NDVI
    ndvi = collection.median().normalizedDifference(['B08', 'B04']).rename('NDVI')
    return ndvi

# Retrieve the NDVI image for the selected year and month
ndvi_image = get_ndvi_image(year, month)

# Define visualization parameters for NDVI
ndvi_params = {
    'min': -1,
    'max': 1,
    'palette': ['blue', 'white', 'green']
}

# Create a folium map
map = folium.Map(location=[20, 10], zoom_start=4)
map.add_child(folium.TileLayer('cartodbpositron'))

# Add NDVI layer to the map
ndvi_map = geemap.ee_tile_layer(ndvi_image, ndvi_params, 'NDVI')
map.add_child(ndvi_map)

# Display the map in Streamlit
st_folium(map, width=700, height=500)

# Additional NDVI information
st.sidebar.write("NDVI ranges from -1 to 1, where higher values indicate dense vegetation.")
