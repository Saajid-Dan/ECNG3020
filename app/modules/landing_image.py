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
import pandas as pd
import folium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from app import db
from app.models import Land

# lat and long in decimal degrees
coords = [10.536421, -61.311951]

options = Options()
options.headless = True


ctry_lst = []

def create_land_image():
    ctry = Land.query.filter_by(car='Yes').with_entities(Land.ctry)
    for j in ctry:
        ctry_lst.append(j[0])

    ctry_lst_uni = []
    for items in ctry_lst:
        if items not in ctry_lst_uni:
            ctry_lst_uni.append(items)
    
    for items in ctry_lst_uni:
        land_pts = db.session.query(Land.lat, Land.lon).filter_by(ctry=items)

        
        m = folium.Map(location=coords, zoom_start=11, tiles=None, max_bounds=True, )

        # Add Base Map Tile to map 'm'.
        folium.TileLayer(
            tiles="cartodbpositron",
            name="Base Map",
            max_zoom=11,
            min_zoom=5,
            ).add_to(m)

        min_lat = 999999
        min_lon = 999999
        max_lat = -999999
        max_lon = -999999
        for index, j in enumerate(land_pts):
            circle_lat = j[0]
            circle_lon = j[1]

            if circle_lat > max_lat:
                max_lat = circle_lat
            if circle_lat < min_lat:
                min_lat = circle_lat
            if circle_lon > max_lon:
                max_lon = circle_lon
            if circle_lon < min_lon:
                min_lon = circle_lon
            
            text = str(index)

            radius = 1
            folium.CircleMarker([circle_lat, circle_lon], radius, fill=True, color='red', fill_opacity=1).add_to(m)

        offset = 0.025
        sw = [min_lat - offset, min_lon]
        ne = [max_lat + offset, max_lon]

        m.fit_bounds([sw, ne]) 

        m.save('./app/static/html/Landing Points/' + items + '.html')

        map_url = 'file://{path}/{mapfile}'.format(
            path=os.getcwd(),
            mapfile="./app/static/html/Landing Points/" + items + ".html"
            )

        browser = webdriver.Firefox(options=options, executable_path="./app/static/webdriver/geckodriver.exe")
        browser.set_window_size(600, 400)
        browser.get(map_url)
        time.sleep(5)
        browser.save_screenshot("./app/static/images/Landing Points/" + items + ".png")
        browser.close()
        browser.quit()
         
