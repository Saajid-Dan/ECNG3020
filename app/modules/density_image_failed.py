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
import geopandas as gpd
from osgeo import gdal
import folium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

# from app import db
# from app.models import Root_srv

Density_tif = [
    "./app/static/images/Density/GUY.tif",
    # r"./app/static/images/Density/ATG.tif",
    # r"./app/static/images/Density/BHS.tif",
    # r"./app/static/images/Density/BLZ.tif",
    # r"./app/static/images/Density/BMU.tif",
    # r"./app/static/images/Density/BRB.tif",
    # r"./app/static/images/Density/CYM.tif",
    # r"./app/static/images/Density/DMA.tif",
    # r"./app/static/images/Density/GRD.tif",
    # r"./app/static/images/Density/GUY.tif",
    # r"./app/static/images/Density/HTI.tif",
    # r"./app/static/images/Density/JAM.tif",
    # r"./app/static/images/Density/KNA.tif",
    # r"./app/static/images/Density/LCA.tif",
    # r"./app/static/images/Density/MSR.tif",
    # r"./app/static/images/Density/SUR.tif",
    # r"./app/static/images/Density/TCA.tif",
    r"./app/static/images/Density/TTO.tif",
    # r"./app/static/images/Density/VCT.tif",
    # r"./app/static/images/Density/VGB.tif",
]
import os

ctry = [
    'AIA',
    'ATG',
    'BHS',
    'BLZ',
    'BMU',
    'BRB',
    'CYM',
    'DMA',
    'GRD',
    'GUY',
    'HTI',
    'JAM',
    'KNA',
    'LCA',
    'MSR',
    'SUR',
    'TCA',
    'TTO',
    'VCT',
    'VGB',
]

dict_ctry = {
        'AIA':'Anguilla',
        'ATG':'Antigua and Barbuda',
        'BHS':'Bahamas',
        'BRB':'Barbados',
        'BLZ':'Belize',
        'BMU':'Bermuda',
        'VGB':'Virgin Islands U K ',
        'CYM':'Cayman Islands',
        'DMA':'Dominica',
        'GRD':'Grenada',
        'GUY':'Guyana',
        'HTI':'Haiti',
        'JAM':'Jamaica',
        'MSR':'Montserrat',
        'KNA':'Saint Kitts and Nevis',
        'LCA':'Saint Lucia',
        'VCT':'Saint Vincent and The Grenadines',
        'SUR':'Suriname',
        'TTO':'Trinidad and Tobago',
        'TCA':'Turks and Caicos Islands'
    }

# lat and long in decimal degrees
coords = [10.536421, -61.311951]

options = Options()
options.headless = True

def create_density_image():
    # Loops over data in 'dens'.
    for index, j in enumerate(Density_tif):
        m = folium.Map(location=coords, zoom_start=11, tiles=None, max_bounds=True, )
        print(os.path.isfile(j))
        print(j)
        # Add Base Map Tile to map 'm'.
        folium.TileLayer(
            tiles="cartodbpositron",
            name="Base Map",
            max_zoom=11,
            min_zoom=5,
            ).add_to(m)

        driver = gdal.GetDriverByName('GTiff')
        driver.Register()

        # 'dataset' = Pass TIF URL from 'j.url' to gdal.
        # 'width' and 'height' store width and height of image in the TIF file.
        # 'gt' = Extracts geospatial coordinates from the TIF file.
        dataset = gdal.Open(j, 1)
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

        offset = 0
        sw = [lat_min - offset, lon_min]
        ne = [lat_max + offset, lon_max]

        m.fit_bounds([sw, ne]) 

        print(m)

        m.save('./app/static/html/Population Density/' + ctry[index] + '.html')
create_density_image()