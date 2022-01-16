'''
Name: Saajid Dan
Course: ECNG 3020
Project Title:
'''

# ---------------------------------------------------------------------------- #
#                                    Imports                                   #
# ---------------------------------------------------------------------------- #

import time
import pandas as pd
import folium
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


# ---------------------------------------------------------------------------- #
#                         Landing Point Images Function                        #
# ---------------------------------------------------------------------------- #

def create_land_image():
    '''
    Generates PNG Images with Landing Points per Caribbean country.
    '''
    # Stores Caribbean countries with landing points.
    ctry_lst = []

    # 'ctry' = stores list of tuples that contain countries associated to Caribbean landing points.
    ctry = Land.query.filter_by(car='Yes').with_entities(Land.ctry)
    for j in ctry:
        # 'j[0]' = first element of tuple is the country.
        ctry_lst.append(j[0])

    # Filter 'ctry_lst' for unique values.db
    ctry_lst = list(set(ctry_lst))

    # Loop over 'ctry_lst' and query 'Land' database for countries in 'ctry_lst'.
    for items in ctry_lst:
        # 'land_pts' = contains a tuple of lat and lon coords for a country (items) in 'ctry_lst'.
        land_pts = db.session.query(Land.lat, Land.lon).filter_by(ctry=items)

        # Instantiate folium map.
        m = folium.Map(location=coords, zoom_control=False, zoom_start=11, tiles='cartodbpositron', max_bounds=True, )

        # 'min_lon' = minimum landing point longitude.
        # 'min_lat' = minimum landing point latitude.
        # 'max_lon' = maximum landing point longitude.
        # 'max_lat' = maximum landing point latitude.
        min_lat = 999999
        min_lon = 999999
        max_lat = -999999
        max_lon = -999999

        # Loop over 'land_pts' to add coordinates to map 'm'.
        for index, j in enumerate(land_pts):
            # 'circle_lat' = latitude. 'circle_lon' = longitude.
            circle_lat = j[0]
            circle_lon = j[1]

            # Determines the max/min lon/lat coordinates
            # These are used to determine the landing point geometries max bounds to fit optimally on the map.
            if circle_lat > max_lat:
                max_lat = circle_lat
            if circle_lat < min_lat:
                min_lat = circle_lat
            if circle_lon > max_lon:
                max_lon = circle_lon
            if circle_lon < min_lon:
                min_lon = circle_lon

            # Landing points circle radius.
            radius = 2.5

            # Add landing point circle (marker) to map 'm'.
            folium.CircleMarker([circle_lat, circle_lon], radius, fill=True, color='red', fill_opacity=1).add_to(m)
        
        # 'offset' = ensures landing point geometries have some clearance from the screen border.
        offset = 0.025
        
        # 'sw' = South west corner. 'ne' = North east corner.
        sw = [min_lat - offset, min_lon]
        ne = [max_lat + offset, max_lon]

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
        browser.save_screenshot("./app/static/images/infrastructure/landing/" + items + ".png")

        # Close the tab and browser to close all firefox sessions.
        browser.close()
        browser.quit()
         
