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
from folium.features import DivIcon
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import base64
from app import db
from app.models import Iana_root_server


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

def create_root_image():
    '''
    Generates PNG Images with Root Servers per Caribbean country.
    '''
    # Stores Caribbean countries with landing points.
    ctry_lst = []

    # 'root_ctry' = contains all entries from 'Root_srv' database.
    root_ctry = Iana_root_server.query.all()

    # Loop over 'root_ctry' entries and add unique Caribbean countries to 'ctry_lst'.
    for j in root_ctry:
        if j not in ctry_lst:
            ctry_lst.append(j.country)

    # Loop over countries in 'ctry_lst'.
    for j in ctry_lst:
        # Extract lat, lon, and server name for country 'j'.
        # 'root_' = returns lat, lon, and server name as a tuple.
        root_ = db.session.query(Iana_root_server.lat, Iana_root_server.lon, Iana_root_server.name).filter_by(country=j).all()

        # Instantiate folium map.
        m = folium.Map(location=coords, zoom_control=False, zoom_start=11, tiles='cartodbpositron', max_bounds=True, )

        # 'min_lon' = minimum root server longitude.
        # 'min_lat' = minimum root server latitude.
        # 'max_lon' = maximum root server longitude.
        # 'max_lat' = maximum root server latitude.
        min_lat = 999999
        min_lon = 999999
        max_lat = -999999
        max_lon = -999999

        # Loop over 'root_' to add coordinates to map 'm'.
        for items in root_:
            # 'circle_lat' = latitude. 'circle_lon' = longitude.
            circle_lat = float(items[0])
            circle_lon = float(items[1])

            # Determines the max/min lon/lat coordinates
            # These are used to determine the root server geometries max bounds to fit optimally on the map.
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

            # Add root server circle (marker) to map 'm'.
            folium.CircleMarker([circle_lat, circle_lon], radius, fill=True, color='red', fill_opacity=1).add_to(m)
            
            # Label server coordinates on the map.
            folium.map.Marker(
            [circle_lat, circle_lon],
            icon=DivIcon(
                icon_size=(150,36),
                icon_anchor=(0,0),
                html='<div style="font-size: 11"; color:"red";>%s</div>' % items[2],
                )
            ).add_to(m)

        # 'offset' = ensures root server geometries have some clearance from the screen border.
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
        browser.save_screenshot("./app/static/images/infrastructure/root/" + j + ".png")

        # Close the tab and browser to close all firefox sessions.
        browser.close()
        browser.quit()