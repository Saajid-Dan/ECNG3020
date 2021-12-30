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
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

from app import db
from app.models import Land

# lat and long in decimal degrees
coords = [10.536421, -61.311951]

options = Options()
options.headless = True

ctry_lst = []

style1 = {'color':'#756bb1', 'opacity':0.5, 'weight':2.25}

def create_sub_image():
    file_sub = open('./app/static/json/submarine.json', 'r')
    gdf_sub = gpd.read_file(file_sub)

    map_bounds = gdf_sub.bounds

    for j in range(len(gdf_sub)):

        m = folium.Map(location=coords, zoom_start=11, tiles=None, max_bounds=True, )

         # Add Base Map Tile to map 'm'.
        folium.TileLayer(
            tiles="cartodbpositron",
            name="Base Map",
            max_zoom=11,
            ).add_to(m)

        name = gdf_sub.iloc[j]['name']

        x = gdf_sub.iloc[j]['lnd']
        k = ast.literal_eval(x)
        
        for index in k:
            cable_id = index['id']
            
            land_id = db.session.query(Land.id).filter_by(uni=cable_id).first()
            u = Land.query.get(land_id)
            
            colour = 'red' if u.car == 'Yes' else 'darkblue'

            circle_lat = u.lat
            circle_lon = u.lon

            radius = 2.5
            folium.CircleMarker([circle_lat, circle_lon], radius, fill=True, color=colour, fill_opacity=1).add_to(m)

        cable = folium.GeoJson(
            gdf_sub.iloc[j].geometry,
            name = name,
            style_function = lambda x:style1
        ).add_to(m)

        min_lon = map_bounds.iloc[j]['minx']
        min_lat = map_bounds.iloc[j]['miny']
        max_lon = map_bounds.iloc[j]['maxx']
        max_lat = map_bounds.iloc[j]['maxy']

        offset = 0.01

        sw = [min_lat - offset, min_lon - offset]
        ne = [max_lat + offset, max_lon + offset]

        m.fit_bounds([sw, ne]) 

        folium.LayerControl().add_to(m)
        m.save('./app/static/html/Submarine Cables/' + name + '.html')

        map_url = 'file://{path}/{mapfile}'.format(
            path=os.getcwd(),
            mapfile="./app/static/html/Submarine Cables/" + name + ".html"
            )

        browser = webdriver.Firefox(options=options, executable_path="./app/static/webdriver/geckodriver.exe")
        browser.set_window_size(600, 400)
        browser.get(map_url)
        time.sleep(3)
        browser.save_screenshot("./app/static/images/Submarine Cables/" + name + ".png")
        browser.close()
        browser.quit()
            
