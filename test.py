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

# Define a method for displaying Earth Engine image tiles on a folium map.
def add_ee_layer(self, ee_object, vis_params, name):
    
    try:    
        # display ee.Image()
        if isinstance(ee_object, ee.image.Image):    
            map_id_dict = ee.Image(ee_object).getMapId(vis_params)
            folium.raster_layers.TileLayer(
            tiles = map_id_dict['tile_fetcher'].url_format,
            attr = 'Google Earth Engine',
            name = name,
            overlay = True,
            control = True
            ).add_to(self)

        # display ee.ImageCollection()
        elif isinstance(ee_object, ee.imagecollection.ImageCollection):    
            ee_object_new = ee_object.mosaic()
            map_id_dict = ee.Image(ee_object_new).getMapId(vis_params)
            folium.raster_layers.TileLayer(
            tiles = map_id_dict['tile_fetcher'].url_format,
            attr = 'Google Earth Engine',
            name = name,
            overlay = True,
            control = True
            ).add_to(self)

        # display ee.Geometry()
        elif isinstance(ee_object, ee.geometry.Geometry):    
            folium.GeoJson(
            data = ee_object.getInfo(),
            name = name,
            overlay = True,
            control = True
        ).add_to(self)

        # display ee.FeatureCollection()
        elif isinstance(ee_object, ee.featurecollection.FeatureCollection):  
            ee_object_new = ee.Image().paint(ee_object, 0, 2)
            map_id_dict = ee.Image(ee_object_new).getMapId(vis_params)
            folium.raster_layers.TileLayer(
            tiles = map_id_dict['tile_fetcher'].url_format,
            attr = 'Google Earth Engine',
            name = name,
            overlay = True,
            control = True
        ).add_to(self)
    
    except:
        print("Could not display {}".format(name))


# Add EE drawing method to folium.
folium.Map.add_ee_layer = add_ee_layer

# Define a function to calculate NDVI
def get_ndvi_image(year, month):
    # Load Sentinel-2 image collection
    collection = ee.ImageCollection('COPERNICUS/S2') \
                    .filterDate(f'{year}-{month:02d}-01', f'{year}-{month:02d}-28') \
                    .filterBounds(ee.Geometry.Point([10.0, 20.0]))  # Adjust to your study area

    # Compute NDVI
    ndvi = collection.median().normalizedDifference(['B8', 'B4']).rename('NDVI')
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

# Add NDVI layer to the folium map
map.add_ee_layer(ndvi_image, ndvi_params, 'Sential NDVI')

#initialize folium map into streamlit session
st.session_state.Map = folium.Map()

# Display the map in Streamlit
#rendered_map = st_folium(st.session_state.Map)
st_folium(map, width=700, height=500)


# Additional NDVI information
st.sidebar.write("NDVI rangess from -1 to 1, where higher values indicate dense vegetation.")