'''
Name: Saajid Dan
Course: ECNG 3020
Project Title:
'''

# ---------------------------------------------------------------------------- #
#                                    Imports                                   #
# ---------------------------------------------------------------------------- #

import time
import ast
import pandas as pd
import folium
import geopandas as gpd
from shapely import wkt
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import base64
from app import app, db
from app.models import Telegeography_landing, Telegeography_submarine


# ---------------------------------------------------------------------------- #
#                                 Configuration                                #
# ---------------------------------------------------------------------------- #

# lat and long in decimal degrees - Map coordinates.
coords = [10.536421, -61.311951]

# Selenium headless mode.
options = Options()
options.headless = True

# 'style1' = Submarine cable geometry styles.
style1 = {'color':'#756bb1', 'opacity':0.5, 'weight':2.25}


# ---------------------------------------------------------------------------- #
#                             Cable Images Function                            #
# ---------------------------------------------------------------------------- #

def create_sub_image():
    # Open submarine cable's JSON into a geopandas dataframe, 'gdf_sub'.
    file_sub = open('./app/static/json/submarine.json', 'r')
    gdf_sub = gpd.read_file(file_sub)

    geo = Telegeography_submarine.query.with_entities(Telegeography_submarine.geometry)
    geo = [value for value, in geo]
    
    # sub = Telegeography_submarine.query.all()
    # # Read into a pandas dataframe.
    df_geo = pd.DataFrame({'geometry':geo})
    # Convert pandas geometry column data into WKT object.
    df_geo['geometry'] = df_geo['geometry'].apply(wkt.loads)
    # Convert pandas dataframe to a geopandas dataframe.
    gdf = gpd.GeoDataFrame(df_geo)
    # WKT object is now a shapely geometry object.
    # Extract map bounds for all geometries in 'gdf_sub'.
    map_bounds = gdf.bounds

    sub = Telegeography_submarine.query.all()
    # Loop over 'gdf_sub' to plot a cable per map and export to a PNG.
    for i, j in enumerate(sub):
        # Instantiate folium map.
        m = folium.Map(location=coords, zoom_control=False, zoom_start=11, tiles='cartodbpositron', max_bounds=True, )

        # Extract cable name.
        name = j.name

        # Extract cable landing points as a list of dictionaries.
        x = j.land_pts
        k = ast.literal_eval(x)
        
        # Loop over the landing points list to extract the landing point IDs.
        for index in k:
            # Landing point ID.
            cable_id = index['id']
            
            # Query ID in the 'Land' database and get the properties for that ID.
            land_id = db.session.query(Telegeography_landing.id).filter_by(id_ref=cable_id).first()
            u = Telegeography_landing.query.get(land_id)
            
            # 'red' = Caribbean landing points. 'darkblue' = International landing points.
            colour = 'red' if u.in_caribbean == 'Yes' else 'darkblue'

            # Landing point lat and lon coordinates.
            circle_lat = u.lat
            circle_lon = u.lon

            # Landing points circle radius.
            radius = 2.5
            
            # Add landing point circle (marker) to map 'm'.
            folium.CircleMarker([circle_lat, circle_lon], radius, fill=True, color=colour, fill_opacity=1).add_to(m)


        # Add submarine cable to map 'm'.
        cable = folium.GeoJson(
            gdf.geometry[i],
            name = name,
            style_function = lambda x:style1
        ).add_to(m)

        # 'min_lon' = minimum cable longitude.
        # 'min_lat' = minimum cable latitude.
        # 'max_lon' = maximum cable longitude.
        # 'max_lat' = maximum cable latitude.
        # These are used to determine the cable geometries max bounds to fit optimally on the map.
        min_lon = map_bounds.iloc[i]['minx']
        min_lat = map_bounds.iloc[i]['miny']
        max_lon = map_bounds.iloc[i]['maxx']
        max_lat = map_bounds.iloc[i]['maxy']

        # 'offset' = ensures cable geometries have some clearance from the screen border.
        offset = 0.01

        # 'sw' = South west corner. 'ne' = North east corner.
        sw = [min_lat - offset, min_lon - offset]
        ne = [max_lat + offset, max_lon + offset]

        # Add geometry bounds to map 'm'.
        m.fit_bounds([sw, ne]) 

        # Extract map 'm' HTML as a string.
        html_string = m.get_root().render()
       
        # Convert 'html_string' to base64 to ensure script elements can load on Selenium.
        html_bs64 = base64.b64encode(html_string.encode('utf-8')).decode()
        
        # Create and open a headless firefox browser session.
        browser = webdriver.Firefox(executable_path=app.config['WEB_DRIVER_PATH'], options=options)
        # Set browser window size.
        browser.set_window_size(600, 400)
        # Pass base64 HTML of map with cable geometry to firefox simulated browser.
        browser.get("data:text/html;base64," + html_bs64)
        # Wait 5 seconds for webpage to load properly.
        time.sleep(5)
        # Screenshot the map.
        browser.save_screenshot("./app/static/images/infrastructure/submarine/" + name + ".png")

        # Close the tab and browser to close all firefox sessions.
        browser.close()
        browser.quit()
            
