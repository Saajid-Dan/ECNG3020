'''
Name: Saajid Dan
Course: ECNG 3020
Project Title:
'''

# ---------------------------------------------------------------------------- #
#                                    Imports                                   #
# ---------------------------------------------------------------------------- #


import os
import time
import ast
import pandas as pd
import folium
import geopandas as gpd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import base64
from app import db
from app.models import Land


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

    # Extract map bounds for all geometries in 'gdf_sub'.
    map_bounds = gdf_sub.bounds

    # Loop over 'gdf_sub' to plot a cable per map and export to a PNG.
    for j in range(len(gdf_sub)):
        # Instantiate folium map.
        m = folium.Map(location=coords, zoom_control=False, zoom_start=11, tiles='cartodbpositron', max_bounds=True, )

        # Extract cable name.
        name = gdf_sub.iloc[j]['name']

        # Extract cable landing points as a list of dictionaries.
        x = gdf_sub.iloc[j]['lnd']
        k = ast.literal_eval(x)
        
        # Loop over the landing points list to extract the landing point IDs.
        for index in k:
            # Landing point ID.
            cable_id = index['id']
            
            # Query ID in the 'Land' database and get the properties for that ID.
            land_id = db.session.query(Land.id).filter_by(uni=cable_id).first()
            u = Land.query.get(land_id)
            
            # 'red' = Caribbean landing points. 'darkblue' = International landing points.
            colour = 'red' if u.car == 'Yes' else 'darkblue'

            # Landing point lat and lon coordinates.
            circle_lat = u.lat
            circle_lon = u.lon

            # Landing points circle radius.
            radius = 2.5
            
            # Add landing point circle (marker) to map 'm'.
            folium.CircleMarker([circle_lat, circle_lon], radius, fill=True, color=colour, fill_opacity=1).add_to(m)

        # Add submarine cable to map 'm'.
        cable = folium.GeoJson(
            gdf_sub.iloc[j].geometry,
            name = name,
            style_function = lambda x:style1
        ).add_to(m)

        # 'min_lon' = minimum cable longitude.
        # 'min_lat' = minimum cable latitude.
        # 'max_lon' = maximum cable longitude.
        # 'max_lat' = maximum cable latitude.
        # These are used to determine the cable geometries max bounds to fit optimally on the map.
        min_lon = map_bounds.iloc[j]['minx']
        min_lat = map_bounds.iloc[j]['miny']
        max_lon = map_bounds.iloc[j]['maxx']
        max_lat = map_bounds.iloc[j]['maxy']

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
        browser = webdriver.Firefox(options=options)
        # Set browser window size.
        browser.set_window_size(600, 400)
        # Pass base64 HTML of map with cable geometry to firefox simulated browser.
        browser.get("data:text/html;base64," + html_bs64)
        # Wait 5 seconds for webpage to load properly.
        time.sleep(5)
        # Screenshot the map.
        browser.save_screenshot("./app/static/images/submarine/" + name + ".png")

        # Close the tab and browser to close all firefox sessions.
        browser.close()
        browser.quit()
            
