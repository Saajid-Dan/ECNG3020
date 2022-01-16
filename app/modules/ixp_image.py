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
from app.models import Ixp_dir


# ---------------------------------------------------------------------------- #
#                                 Configuration                                #
# ---------------------------------------------------------------------------- #

# lat and long in decimal degrees - Map coordinates.
coords = [10.536421, -61.311951]

# Selenium headless mode.
options = Options()
options.headless = True


# ---------------------------------------------------------------------------- #
#                              IXP Images Function                             #
# ---------------------------------------------------------------------------- #

def create_ixp_image():
    '''
    Generates PNG Images with IXPs per Caribbean country.
    '''
    # Stores Caribbean countries.
    ctry_lst = []

    # 'ixp_ctry' = contains all entries from 'Ixp_dir' database.
    ixp_ctry = Ixp_dir.query.all()

    # Loop over 'ixp_ctry' entries and add unique Caribbean countries to 'ctry_lst'.
    for j in ixp_ctry:
        if j not in ctry_lst:
            ctry_lst.append(j.ctry)

    # Loop over countries in 'ctry_lst'.
    for j in ctry_lst:
        # Extract lat, lon, and server name for country 'j'.
        # 'ixp_' = returns lat, lon, and ixp name as a tuple.
        ixp_ = db.session.query(Ixp_dir.lat, Ixp_dir.lon, Ixp_dir.name).filter_by(ctry=j).all()

        # Instantiate folium map.
        m = folium.Map(location=coords, zoom_control=False, zoom_start=11, tiles='cartodbpositron', max_bounds=True, )

        # 'min_lon' = minimum ixp longitude.
        # 'min_lat' = minimum ixp latitude.
        # 'max_lon' = maximum ixp longitude.
        # 'max_lat' = maximum ixp latitude.
        min_lat = 999999
        min_lon = 999999
        max_lat = -999999
        max_lon = -999999

         # Loop over 'ixp_' to add coordinates to map 'm'.
        for items in ixp_:
            # 'circle_lat' = latitude. 'circle_lon' = longitude.
            circle_lat = float(items[0])
            circle_lon = float(items[1])

            # Determines the max/min lon/lat coordinates
            # These are used to determine the ixp geometries max bounds to fit optimally on the map.
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

            # Add ixp circle (marker) to map 'm'.
            folium.CircleMarker([circle_lat, circle_lon], radius, fill=True, color='red', fill_opacity=1).add_to(m)
            
            # Label ixp coordinates on the map.
            folium.map.Marker(
            [circle_lat, circle_lon],
            icon=DivIcon(
                icon_size=(150,36),
                icon_anchor=(0,0),
                html='<div style="font-size: 11"; color:"red";>%s</div>' % items[2],
                )
            ).add_to(m)

        # 'offset' = ensures ixp geometries have some clearance from the screen border.
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
        browser.save_screenshot("./app/static/images/infrastructure/ixp/" + j + ".png")

        # Close the tab and browser to close all firefox sessions.
        browser.close()
        browser.quit()