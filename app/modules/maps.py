'''
Name: Saajid Dan
Course: ECNG 3020
Project Title:
'''

# ---------------------------------------------------------------------------- #
#                                    Imports                                   #
# ---------------------------------------------------------------------------- #

import folium
from folium.plugins import MarkerCluster, Fullscreen, FeatureGroupSubGroup
import codecs
import pandas as pd
import geopandas as gpd
from osgeo import gdal
from shapely import wkt
import ast
from app import db
from app.models import Pch_ixp_dir, Pdb_facility, Wpop_density, Iana_root_server, Telegeography_landing, Telegeography_submarine


def create_map():

    # ---------------------------------------------------------------------------- #
    #                          Map and Layer Instantiation                         #
    # ---------------------------------------------------------------------------- #

    # Instantiate a map into 'm'.
    m = folium.Map(
        location=[15.7500, -70.5000],
        zoom_start=5,
        tiles=None,
        max_bounds=True,
        )
    
    # Add Base Map Tile to map 'm'.
    folium.TileLayer(
        tiles="cartodbpositron",
        name="Base Map",
        max_zoom=15,
        min_zoom=5
        ).add_to(m)

    # Add Topographical Map Tile to map 'm'.
    folium.TileLayer(
        tiles="https://api.mapbox.com/styles/v1/saajid-dan/ckt1awxvh0ljm17mxul50cjco/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1Ijoic2FhamlkLWRhbiIsImEiOiJja3QxOXFqbzYwYmN5MnBwa3BnMWJ2c3FmIn0.KNBPvDuAWZy6GAx89E6dAg", 
        attr='<a href="https://www.mapbox.com/about/maps/">© Mapbox</a>, <a href="http://www.openstreetmap.org/copyright">© OpenStreetMap</a>, <a href="https://www.mapbox.com/map-feedback/">Improve this map</a>', 
        name="Topographic Map",
        max_zoom=15,
        min_zoom=5
        ).add_to(m)

    # mcg = Folium Marker Cluster Group for all markers.
    mcg = MarkerCluster(control=False)
    m.add_child(mcg)


    # ---------------------------------------------------------------------------- #
    #                           Internet Exchange Points                           #
    # ---------------------------------------------------------------------------- #

    # ------------------------- Add IXP Directory to Map ------------------------- #

    # 'feature_ixp' = Folium feature group for Internet Exchange Points.
    feature_ixp = FeatureGroupSubGroup(mcg, 'Internet Exchange Points')
    m.add_child(feature_ixp)

    # Read IXP directory data from database to 'ixp'.
    ixp = Pch_ixp_dir.query.all()
    
    # Add IXP points to map 'm'.
    for j in ixp:
        # Create IXP marker.
        ixp_pt = folium.Marker(
            location = [float(j.lat), float(j.lon)],
            icon = folium.Icon(color='red')
        )

        # 'name' = IXP name
        name = '<a href = "' + j.url_home + '"target="_blank" rel="noopener noreferrer">' + j.name + '</a>'

        # 'ipv4_avg' = IPv4 Average Throughput
        ipv4_avg = float(j.ipv4_avg)
        if ipv4_avg == 0:
            ipv4_avg = 'N/A'
        elif ipv4_avg < 1e6:
            ipv4_avg = str(ipv4_avg/1e3) + ' Mbps'
        else:
            ipv4_avg = str(ipv4_avg/1e6) + ' Gbps'

        # 'ipv4_pk' = IPv4 Peak Throughput
        ipv4_pk = float(j.ipv4_pk)
        if ipv4_pk == 0:
            ipv4_pk = 'N/A'
        elif ipv4_pk < 1e6:
            ipv4_pk = str(ipv4_pk/1e3) + ' Mbps'
        else:
            ipv4_pk = str(ipv4_pk/1e6) + ' Gbps'

        # 'ipv6_avg' = IPv6 Average Throughput
        ipv6_avg = float(j.ipv6_avg)
        if ipv6_avg == 0:
            ipv6_avg = 'N/A'
        elif ipv6_avg < 1e6:
            ipv6_avg = str(ipv6_avg/1e3) + ' Mbps'
        else:
            ipv6_avg = str(ipv6_avg/1e6) + ' Gbps'

        # Create marker popup message.
        ixp_pt = ixp_pt.add_child(
            folium.Popup(
                f'''<h4>Internet Exchange Point</h4>
                <p style="line-height: 15px; margin-top: 0px; margin-bottom: 5px;"><b>Name: </b>{name}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Country: </b>{j.country}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>City: </b>{j.city}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Status: </b>{j.status}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Date Established: </b>{j.date}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>No. of Prefixes: </b>{j.num_prfs}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>No. of Participants: </b>{j.num_prts}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>IPv4 Average Throughput: </b>{ipv4_avg}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>IPv4 Peak Throughput: </b>{ipv4_pk}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>IPv6 Average Throughput: </b>{ipv6_avg}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Last Updated: </b>{j.updated}</p>''',
                max_width = 275,
                min_width = 275
            )
        )
        # Add marker to map 'm'.
        ixp_pt.add_to(feature_ixp)


    # ---------------------------------------------------------------------------- #
    #                                  Facilities                                  #
    # ---------------------------------------------------------------------------- #

    # -------------------------- Add Facilities to Map -------------------------- #

    # 'feature_fac' = Folium feature group for Facilities.
    feature_fac = FeatureGroupSubGroup(mcg, 'Facilities')
    m.add_child(feature_fac)

    # Read fac data from database to 'fac'.
    fac = Pdb_facility.query.all()

    # Add fac points to map 'm'.
    for j in fac:
        # print((j.lat), type(j.lat), float(j.lat), type(float(j.lat)))
        # print(float(j.lat) == float('nan'))
        if j.lat == 'nan' or j.lon == 'nan':
            continue
        
        # Create fac marker.
        fac_pt = folium.Marker(
            location = [float(j.lat), float(j.lon)],
            icon = folium.Icon(color='lightred')
        )

        # 'name' = Facility name and URL to homepage.
        name = '<a href = "' + j.url_home + '"target="_blank" rel="noopener noreferrer">' + j.name + '</a>'

        # Create marker popup message.
        fac_pt = fac_pt.add_child(
            folium.Popup(
                f'''<h4>Facility</h4>
                <p style="line-height: 15px; margin-top: 0px; margin-bottom: 5px;"><b>Facility Name: </b>{name}</p>
                <p style="line-height: 15px; margin-top: 0px; margin-bottom: 5px;"><b>Status: </b>{j.status}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Country: </b>{j.country}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>City: </b>{j.city}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Address Line 1: </b>{j.address1}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Address Line 2: </b>{j.address2}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>State: </b>{j.state}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Zip Code: </b>{j.zipcode}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Organisation: </b>{j.org_name}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Sales Email: </b>{j.sale_email}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Sales Phone: </b>{j.sale_phone}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Technical Email: </b>{j.tech_email}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Technical Phone: </b>{j.tech_phone}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Last Updated: </b>{j.updated}</p>''',
                max_width = 275,
                min_width = 275
            )
        )
        # Add marker to map 'm'.
        fac_pt.add_to(feature_fac)

    # ---------------------------------------------------------------------------- #
    #                              Population Density                              #
    # ---------------------------------------------------------------------------- #

    # Read Population Density data from database to 'dens'.
    dens = Wpop_density.query.all()

    # max_pop - Variable used to store maximum population density in all Caribbean countries.
    max_pop = 0

    # 'feature_density' = Folium Feature group for the Population Density.
    feature_density = folium.FeatureGroup('Population Density').add_to(m)
    
    # Loops over data in 'dens'.
    for j in dens:
        # 'dataset' = Pass TIF URL from 'j.url' to gdal.
        # 'width' and 'height' store width and height of image in the TIF file.
        # 'gt' = Extracts geospatial coordinates from the TIF file.
        dataset = gdal.Open(j.url_tif, 1)
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

        # 'stats' = contains min, max and mean population densities in a list.
        # format: [min, max, mean]
        stats = band.GetStatistics(True, True)

        # If 'stat[1]' > 'max_pop', then 'max_pop' = 'stat[1]'.TimeoutError()
        if stats[1] > max_pop:
            max_pop = int(stats[1])

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
        image.add_to(feature_density)


    # ----------------------- Add Suriname-Guyana boundary ----------------------- #
    
    # 'f' = opens text file with boundary coordinates.
    f = open('./app/static/txt/boundary.txt', 'r')
    
    # The coordinates in the text file is a string representation of a list of lat/long pairs.
    # These lists are comma delimited.
    # First must remove the commas, and then convert each string list to a list.
    # 'points' = stores the coordinates.
    points = []
    for j in f:
        # Removing commas before converting string to list.
        x = j.replace('],', ']')
        # Convert string to list in 'k'.
        k = ast.literal_eval(x)
        # Append coordinates to 'points'.
        points.append(k)
        
    # Adds boundary line to 'feature_density' layer.
    folium.PolyLine(points, color='gray').add_to(feature_density)


    # ---------------------------------------------------------------------------- #
    #                               Root Name Servers                              #
    # ---------------------------------------------------------------------------- #

    # -------------------------- Add Root Server to Map -------------------------- #

    # 'feature_root' = Folium feature group for Root Servers.
    feature_root = FeatureGroupSubGroup(mcg, 'Root Name Servers')
    m.add_child(feature_root)

    # Read root server data from database to 'root'.
    root = Iana_root_server.query.all()

    # Add root server points to map 'm'.
    for j in root:
        # Create root server marker.
        root_pt = folium.Marker(
            location = [float(j.lat), float(j.lon)],
            icon = folium.Icon(color='orange')
        )

        # 'name' = Server name and URL to homepage.
        name = '<a href = "' + j.url_home + '"target="_blank" rel="noopener noreferrer">' + j.name + ' Root</a>'

        # Create marker popup message.
        root_pt = root_pt.add_child(
            folium.Popup(
                f'''<h4>Root Name Server</h4>
                <p style="line-height: 15px; margin-top: 0px; margin-bottom: 5px;"><b>Server Name: </b>{name}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Country: </b>{j.country}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Location: </b>{j.location}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Operator: </b>{j.srv_operator}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Server Type: </b>{j.srv_type}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Autonomous Server Number: </b>{j.asn}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>IPv4 Address: </b>{j.ipv4}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>IPv6 Address: </b>{j.ipv6}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>No. of Instances: </b>{j.num_inst}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>RSSAC: </b>{j.rssac}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Contact Email: </b>{j.srv_contact}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Peering Policy: </b>{j.peer_pol}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Indentifiers: </b>{j.id_root}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Identifier Naming Convention: </b>{j.id_nc}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Last Updated: </b>{j.updated}</p>''',
                max_width = 275,
                min_width = 275
            )
        )
        # Add marker to map 'm'.
        root_pt.add_to(feature_root)


    # ---------------------------------------------------------------------------- #
    #                               Submarine Cables                               #
    # ---------------------------------------------------------------------------- #

    # ------------------------- Add Landing Points to Map ------------------------ #

    # 'feature_car' = Folium feature group for Caribbean landing points.
    feature_car = FeatureGroupSubGroup(mcg, 'Caribbean Landing Points')
    m.add_child(feature_car)

    # 'feature_int' = Folium feature group for International landing points.
    feature_int = FeatureGroupSubGroup(mcg, 'International Landing Points')
    m.add_child(feature_int)

    # Read landing points data from database to 'land'.
    land = Telegeography_landing.query.all()
    for j in land:
        # If landing point is situated in the Caribbean
        if j.in_caribbean == 'Yes':
            # Create landing point marker.
            car_land = folium.Marker(
                location = [j.lat, j.lon],
                icon = folium.Icon(color = 'darkblue')
            )
            # Create marker popup message.
            car_land = car_land.add_child(
                folium.Popup(
                    f'''<h4>Caribbean Landing Point</h4>
                    <p style="line-height: 15px; margin-top: 0px; margin-bottom: 5px;"><b>Location: </b>{j.name}</p>
                    <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Country: </b>{j.country}</p>
                    <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Last Updated: </b>{j.updated}</p>''',
                    max_width = 275,
                    min_width = 275
                )
            )
            # Add marker to map 'm'.
            car_land.add_to(feature_car)

        # If landing point is not situated in the Caribbean
        elif j.in_caribbean == 'No':
            # Create landing point marker.
            car_land = folium.Marker(
                location = [j.lat, j.lon],
                icon = folium.Icon(color = 'blue')
            )
            # Create marker popup message.
            car_land = car_land.add_child(
                folium.Popup(
                    f'''<h4>International Landing Point</h4>
                    <p style="line-height: 15px; margin-top: 0px; margin-bottom: 5px;"><b>Location: </b>{j.name}</p>
                    <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Country: </b>{j.country}</p>
                    <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Last Updated: </b>{j.updated}</p>''',
                    max_width = 275,
                    min_width = 275
                )
            )
            # Add marker to map 'm'.
            car_land.add_to(feature_int)

    

    # ---------------------- Add Submarine Cables to the Map --------------------- #

    # 'dir' = location of submarine cable JSON file within project directory.
    dir = './app/static/json/submarine.json'

    # Opens JSON in 'dir' into 'file_sub.
    file_sub = open(dir, 'r')
    
    # Add data in 'sub' to a GeoPandas dataframe 'gdf_sub'.
    gdf_sub = gpd.read_file(file_sub)


    # Submarine Cable Visual Styles.
    # Colour Sample = https://colorbrewer2.org/#type=sequential&scheme=OrRd&n=3
    style1 = {'color':'#756bb1', 'opacity':0.5, 'weight':2.25}
    style2 = {'color':'#e34a33', 'opacity':0.5, 'weight':2.25}


    # 'feature_sub' = Folium feature group for submarine cables 
    feature_sub = folium.FeatureGroup('Submarine Cables').add_to(m)

    # Read submarine cable data from database to 'sub'.
    sub = Telegeography_submarine.query.all()

    # Add cable geometries to map 'm'.
    for j in sub:
        # String representation of cable geometry.
        geo = j.geometry
        
        # Read into a pandas dataframe.
        df_geo = pd.DataFrame({'geometry':[geo]})
        # Convert pandas geometry column data into WKT object.
        df_geo['geometry'] = df_geo['geometry'].apply(wkt.loads)
        # Convert pandas dataframe to a geopandas dataframe.
        gdf = gpd.GeoDataFrame(df_geo)
        # WKT object is now a shapely geometry object.
        geo = gdf.geometry[0]
        # print(j.status, type(j.status))
        if j.status == 'False':
            # If cable's status is 'False', then the cable is 'Active'.
            stat = 'Active'

            # 'cable' = Folium geometry element with cable's coordinates.
            cable = folium.GeoJson(
                geo,
                style_function = lambda x:style1,
                name = j.name
            )

        # If cable's status is 'True', then the cable is 'Planned'.
        else:
            stat = 'Planned'

            # 'cable' = Folium geometry element with cable's coordinates.
            cable = folium.GeoJson(
                geo,
                style_function = lambda x:style2,
                name = j.name
            )
        
        # 'lnd_pt' = string representation of a landing points list
        # 'lnd_pt' needs to be converted into a list.
        lnd_pt = j.land_pts
        lnd_pt = ast.literal_eval(lnd_pt)

        # 'lnd_dat' = to store a string of landing points.
        lnd_dat = ''

        # 'lnd_pt' list contains dictionaries with the landing points data.
        # The landing points will be concat into 'lnd_dat' to add to map 'm'.
        for index, k in enumerate( range(len(lnd_pt)) ):
            lnd_dat += str(index+1) + '. ' + lnd_pt[k]['name'] + '<br>'

        # 'name' = name of submarine cable with URL.
        # 'length' = length of cable.
        # 'rfs' = cable's ready for service.
        # 'sup' = cable suppliers.
        # 'own' = cable owners.
        # 'updt' = last updated date.'
        if j.url_home == None:
            name = j.name
        else:
            name = '<a href = "' + j.url_home + '"target="_blank" rel="noopener noreferrer">' + j.name + '</a>'
        length = j.length
        rfs = j.rfs
        sup = j.suppliers
        own = j.owners
        updt = j.updated
        
        # iframe = folium.element.Iframe(html=html, width=275)
        # Add popup messages to cable geometries
        cable = cable.add_child(
            folium.Popup(
                f'''<h4>Submarine Cable:</h4>
                <p style="line-height: 15px; margin-top: 0px; margin-bottom: 5px;"><b>Name:</b> {name}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Status:</b> {stat}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Length:</b> {length}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Ready for Service:</b> {rfs}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Suppliers:</b> {sup}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Owners: </b>
                <br>{own}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Landing Points: </b>
                <br>{lnd_dat}</p>
                <p style="line-height: 15px; margin-top: 5px; margin-bottom: 5px;"><b>Last Updated:</b> {updt}</p>''',
                max_width = 275,
                min_width = 275
            )
        )
        # Add marker to map 'm'.
        cable.add_to(feature_sub)
    
    # Returns a list with of min/max lat/long coordinates.
    # Form: [min lon, min lat, max lon, max lat]
    map_bounds = gdf_sub.total_bounds
    
    # 'min_lon' = minimum longitude coordinate
    # 'min_lat' = minimum latitude coordinate
    # 'max_lon' = maximum longitude coordinate
    # 'max_lat' = maximum latitude coordinate
    min_lon = map_bounds[0]
    min_lat = map_bounds[1]
    max_lon = map_bounds[2]
    max_lat = map_bounds[3]


    # ---------------------------------------------------------------------------- #
    #                         Map Additional Configuration                         #
    # ---------------------------------------------------------------------------- #
    
    # Folium Layer Control
    folium.LayerControl().add_to(m)

    # Folium Fullscreen
    Fullscreen().add_to(m)

    # Save map to map.html
    m.save("./app/static/html/map.html")


    # ---------------------------------------------------------------------------- #
    #                        Add Extra Leaflet Functionality                       #
    # ---------------------------------------------------------------------------- #

    # Folium is a python wrapper for Leaflet.js Mapping Tool.
    # Folium barely has enough functionality to do what is required for this project.
    # The extra functionality can be achieved by adding the Leaflet code to the map's HTML.
    # Overwriting Leaflet code in the map's HTML is another route.
    # Functionality added from Leaflet is:
    # 1) Max/Min bounds to limit panning
    # 2) maxHeight in popups to get scrollbar


    # ------------------------------- Open Map File ------------------------------ #

    # Read map.html contents into m_file.
    m_file = codecs.open('./app/static/html/map.html', 'r').read()


    # -------------------------------- Map Bounds -------------------------------- #

    # Read indices for maxBounds limits in 'm_file'.
    m_start = m_file.find('maxBounds')
    m_end = m_file.find(']],') + 2

    # 'map_m' = Stores the maxbounds code from 'm_file'.
    map_m = m_file[m_start:m_end]
    
    # 'limits' = Store Leaflet code to replace maxbounds coords in with 'min_lat', 'min_lon', 'max_lat', 'max_lon'.
    limits = f'''maxBounds: [[{min_lat - 6}, {min_lon - 7}], [{max_lat + 6}, {max_lon + 7}]]'''

    # Replace 'map_m' in 'm_file' with 'limits'.
    m_file = m_file.replace(map_m, limits)


    # ---------------------------- Max Height in Popup --------------------------- #

    # Add in maxHeight leafet code to 'm_file'.
    m_file = m_file.replace('"maxWidth"', '"maxHeight": 275, "maxWidth"')
    
    
    # ------------------------- Write Changes to the Map ------------------------- #

    # Write m_file contents to map.html
    with open('./app/static/html/map.html', 'w') as f:
        f.write(m_file)