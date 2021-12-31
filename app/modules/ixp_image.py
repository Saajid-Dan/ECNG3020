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
from folium.features import DivIcon
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from app import db
from app.models import Ixp_dir

# lat and long in decimal degrees
coords = [10.536421, -61.311951]

options = Options()
options.headless = True


ctry_lst = []

def create_ixp_image():
    ctry_lst = []

    ixp_ctry = Ixp_dir.query.all()
    for j in ixp_ctry:
        if j not in ctry_lst:
            ctry_lst.append(j.ctry)

    for j in ctry_lst:
        ixp_ = db.session.query(Ixp_dir.lat, Ixp_dir.lon, Ixp_dir.name).filter_by(ctry=j).all()

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

        for items in ixp_:

            circle_lat = float(items[0])
            circle_lon = float(items[1])

            if circle_lat > max_lat:
                max_lat = circle_lat
            if circle_lat < min_lat:
                min_lat = circle_lat
            if circle_lon > max_lon:
                max_lon = circle_lon
            if circle_lon < min_lon:
                min_lon = circle_lon
        
            radius = 1
            folium.CircleMarker([circle_lat, circle_lon], radius, fill=True, color='red', fill_opacity=1).add_to(m)
            
            folium.map.Marker(
            [circle_lat, circle_lon],
            icon=DivIcon(
                icon_size=(150,36),
                icon_anchor=(0,0),
                html='<div style="font-size: 11"; color:"red";>%s</div>' % items[2],
                )
            ).add_to(m)

        offset = 0.025
        sw = [min_lat - offset, min_lon]
        ne = [max_lat + offset, max_lon]

        m.fit_bounds([sw, ne]) 

        m.save('./app/static/html/Internet Exchange Points/' + j + '.html')

        map_url = 'file://{path}/{mapfile}'.format(
            path=os.getcwd(),
            mapfile="./app/static/html/Internet Exchange Points/" + j + ".html"
            )

        browser = webdriver.Firefox(options=options, executable_path="./app/static/webdriver/geckodriver.exe")
        browser.set_window_size(600, 400)
        browser.get(map_url)
        time.sleep(5)
        browser.save_screenshot("./app/static/images/Internet Exchange Points/" + j + ".png")
        browser.close()
        browser.quit()

    # print(ctry_lst)
    # ctry = Land.query.filter_by(car='Yes').with_entities(Land.ctry)
    # for j in ctry:
    #     ctry_lst.append(j[0])

    # ctry_lst_uni = []
    # for items in ctry_lst:
    #     if items not in ctry_lst_uni:
    #         ctry_lst_uni.append(items)
    
    # for items in ctry_lst_uni:
    #     land_pts = db.session.query(Land.lat, Land.lon).filter_by(ctry=items)

        
    #     m = folium.Map(location=coords, zoom_start=11, tiles=None, max_bounds=True, )

    #     # Add Base Map Tile to map 'm'.
    #     folium.TileLayer(
    #         tiles="cartodbpositron",
    #         name="Base Map",
    #         max_zoom=11,
    #         min_zoom=5,
    #         ).add_to(m)

    #     min_lat = 999999
    #     min_lon = 999999
    #     max_lat = -999999
    #     max_lon = -999999
    #     for index, j in enumerate(land_pts):
    #         circle_lat = j[0]
    #         circle_lon = j[1]

    #         if circle_lat > max_lat:
    #             max_lat = circle_lat
    #         if circle_lat < min_lat:
    #             min_lat = circle_lat
    #         if circle_lon > max_lon:
    #             max_lon = circle_lon
    #         if circle_lon < min_lon:
    #             min_lon = circle_lon
            
    #         text = str(index)

    #         radius = 1
    #         folium.CircleMarker([circle_lat, circle_lon], radius, fill=True, color='red', fill_opacity=1).add_to(m)

    #     offset = 0.025
    #     sw = [min_lat - offset, min_lon]
    #     ne = [max_lat + offset, max_lon]

    #     m.fit_bounds([sw, ne]) 

    #     m.save('./app/static/html/Landing Points/' + items + '.html')

    #     map_url = 'file://{path}/{mapfile}'.format(
    #         path=os.getcwd(),
    #         mapfile="./app/static/html/Landing Points/" + items + ".html"
    #         )

    #     browser = webdriver.Firefox(options=options, executable_path="./app/static/webdriver/geckodriver.exe")
    #     browser.set_window_size(600, 400)
    #     browser.get(map_url)
    #     time.sleep(3)
    #     browser.save_screenshot("./app/static/images/Landing Points/" + items + ".png")
    #     browser.close()
    #     browser.quit()
         
