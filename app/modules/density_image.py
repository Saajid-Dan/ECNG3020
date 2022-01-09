'''
Name: Saajid Dan
Course: ECNG 3020
Project Title:
'''

# ---------------------------------------------------------------------------- #
#                                    Imports                                   #
# ---------------------------------------------------------------------------- #

import pandas as pd
from osgeo import gdal
from app import db
from app.models import Pop_dens
from datetime import datetime, timezone, timedelta
import os
import folium
import branca
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# lat and long in decimal degrees
coords = [10.536421, -61.311951]

options = Options()
options.headless = True

def create_density_image():
    # Read Population Density data from database to 'dens'.
    dens = Pop_dens.query.all()

    # Loops over data in 'dens'.
    for j in dens:
        m = folium.Map(location=coords, zoom_start=11, tiles=None, max_bounds=True, )

        # Add Base Map Tile to map 'm'.
        folium.TileLayer(
            tiles="cartodbpositron",
            name="Base Map",
            max_zoom=11,
            min_zoom=5,
            ).add_to(m)

        # 'dataset' = Pass TIF URL from 'j.url' to gdal.
        # 'width' and 'height' store width and height of image in the TIF file.
        # 'gt' = Extracts geospatial coordinates from the TIF file.
        dataset = gdal.Open(j.url, 1)
        width = dataset.RasterXSize
        height = dataset.RasterYSize
        gt = dataset.GetGeoTransform()

        # Geospatial lat/long coordinates of TIF file.
        # Used to determine where on the map the density overlay is.
        lon_min = gt[0]
        lat_min = gt[3] + width*gt[4] + height*gt[5]
        lon_max = gt[0] + width*gt[1] + height*gt[2]
        lat_max = gt[3]

        # Read TIF file as an array of RGBA values.
        band = dataset.GetRasterBand(1)
        arr = band.ReadAsArray()

        # 'image' - Converts TIF file array as a raster to overlay onto map.
        image = folium.raster_layers.ImageOverlay(
                image = arr, 
                opacity = 1, 
                bounds=[[lat_min, lon_min], [lat_max, lon_max]],    # bounds = bounding coordinates of overlay.
                interactive=True,                                   # Grids adjust depending on Zoom level.
                
                # Manipulation of RGBA colours of density grids depending on density ranges.
                colormap=lambda x: (1 if x < 2500 else (0.7 if x < 5000 else (0.4 if x < 10000 else 0.15)),
                                    1 if x < 50 else (0.5 if x < 100 else (0.2 if x < 1000 else 0)),
                                    0,
                                    1 if x > 0 else 0),
                zindex=1,
            )
        # 'image' overlay added to map 'm'.
        image.add_to(m)

        legend_html = f'''
        {{% macro html(this, kwargs) %}}
        <div style="
            position: fixed; 
            bottom: 115px;
            left: 0px;
            width: 250px;
            height: 80px;
            z-index:9999;
            font-size:14px;
            ">
            <p style="line-height:1;margin-left:20px;font-size:105%">Population Density <br>(100 km resolution)</p>
            <p style="line-height:0.3"><a style="color:#ffff00;font-size:200%;margin-left:20px;">&#9632;</a>&emsp;1 - 50</p>
            <p style="line-height:0.3"><a style="color:#ff8000;font-size:200%;margin-left:20px;">&#9632;</a>&emsp;50 - 100</p>
            <p style="line-height:0.3"><a style="color:#ff3300;font-size:200%;margin-left:20px;">&#9632;</a>&emsp;100 - 1000</p>
            <p style="line-height:0.3"><a style="color:#ff0000;font-size:200%;margin-left:20px;">&#9632;</a>&emsp;1000 - 2500</p>
            <p style="line-height:0.3"><a style="color:#b30000;font-size:200%;margin-left:20px;">&#9632;</a>&emsp;2500 - 5000</p>
            <p style="line-height:0.3"><a style="color:#660000;font-size:200%;margin-left:20px;">&#9632;</a>&emsp;5000 - 10000</p>
            <p style="line-height:0.3"><a style="color:#260000;font-size:200%;margin-left:20px;">&#9632;</a>&emsp;> 10000</p>
        </div>
        <div style="
            position: fixed; 
            bottom: 10px;
            left: 10px;
            width: 150px;
            height: 190px; 
            z-index:9998;
            font-size:14px;
            background-color: #ffffff;

            opacity: 0.9;
            ">
        </div>
        {{% endmacro %}}
        '''
        legend = branca.element.MacroElement()
        legend._template = branca.element.Template(legend_html)
        m.get_root().add_child(legend)

        offset_lon = 0.4
        offset_lat = 0.01
        sw = [lat_min - offset_lat, lon_min - offset_lon]
        ne = [lat_max, lon_max]

        m.fit_bounds([sw, ne])

        m.save('./app/static/html/Population Density/' + j.ctry + '.html')
        
        map_url = 'file://{path}/{mapfile}'.format(
            path=os.getcwd(),
            mapfile="./app/static/html/Population Density/" + j.ctry + ".html"
            )

        browser = webdriver.Firefox(options=options, executable_path="./app/static/webdriver/geckodriver.exe")
        browser.set_window_size(820, 450)
        browser.get(map_url)
        # time.sleep(5)
        browser.save_screenshot("./app/static/images/Population Density/" + j.ctry + ".png")
        browser.close()
        browser.quit()
   