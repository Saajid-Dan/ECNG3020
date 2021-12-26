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


def density():
    '''
    Read WorldPop's API for a JSON with the population density of unconstrained individual countries.
    A download link to the TIF files is retrieved from the JSON and saved to the project's directory.
    Details on the data's update date and population density year stored to a database.
    '''
    # ---------------------------------------------------------------------------- #
    #                                WorldPop Source                               #
    # ---------------------------------------------------------------------------- #

    # 'url_root' = root directory of WorldPop's population density data for unconstrained individual countries.
    # For more info on the API: https://www.worldpop.org/sdi/introapi
    url_root = 'https://www.worldpop.org/rest/data/pop_density/pd_ic_1km?iso3='


    # ---------------------------------------------------------------------------- #
    #                                  Read Source                                 #
    # ---------------------------------------------------------------------------- #

    # 'cc' = ISO-3 Country codes.
    # Subdirectories of 'url_root'
    cc = [
        'AIA',
        'ATG', 
        'BHS', 
        'BRB', 
        'BLZ', 
        'BMU', 
        'VGB', 
        'CYM', 
        'DMA', 
        'GRD', 
        'GUY', 
        'HTI', 
        'JAM', 
        'MSR', 
        'KNA', 
        'LCA', 
        'VCT', 
        'SUR', 
        'TTO', 
        'TCA'
    ]

    # Loop over 'cc' to append subdirectories to 'url_root' to read data.
    for j in cc:
        # 'url' = 'url_root' + 'j' = population density JSON for country 'j'.
        # 'j' = individual country codes.
        url = url_root + j
        

        # --------------------------------- Read JSON -------------------------------- #

        try:
            # 'json_pop' = stores JSON from 'url'.
            json_pop = pd.read_json(url)
        except Exception as e:
            error = "Source: " + url + "\nError: " + str(e)
            return error


        # ---------------------------------------------------------------------------- #
        #                                 Extract Data                                 #
        # ---------------------------------------------------------------------------- #

        try:
            # 'urls' = contains downloadable URLs for TIF and CSV file.
            # 'url_tif' = URL to TIF file embedded in 'json_pop'.
            # 'updt' = last updated date of TIF image.
            # 'pop_yr' = Population density year.
            urls = json_pop.iloc[-1]['data']['files']
            for link in urls:
                if link.find('.tif') != -1:
                    url_tif = link
            updt = json_pop.iloc[-1]['data']['date'][0]
            pop_yr = json_pop.iloc[-1]['data']['popyear'][0]
        except Exception as e:
            error = "Error Extracting TIF Data.\nError: " + str(e)
            return error

        try:
            # 'dataset' = Pass TIF URL from 'url_tif' to gdal.
            dataset = gdal.Open(url_tif, 1)
            
            # Read TIF file as an array of RGBA values.
            band = dataset.GetRasterBand(1)
            arr = band.ReadAsArray()
        except Exception as e:
            error = "Source: " + url_tif + "\nError: " + str(e)
            return error

        # 'stats' = contains min, max and mean population densities in a list.
        # format: [min, max, mean]
        stats = band.GetStatistics(True, True)

        # Store mean population density into 'dens'.
        dens = stats[2]
        

        # ---------------------------------------------------------------------------- #
        #                                Add to Database                               #
        # ---------------------------------------------------------------------------- #

        # ----------------------- Timestamping Check Condition ----------------------- #

        # 'time' stores starting time of writing to the database.
        # The time in 'time' is used to compare against the database entry timestamps.
        # This is used to ensure only recent data is stored into the database. 
        time = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")


        # -------------------------- Population Density Data ------------------------- #

        # 'exist' = Checks is a known value exists in the 'Pop_dens' table.
        # Returns None if the value does not exist.
        # Returns a tuple of ids if the value exist.
        exist = db.session.query(Pop_dens.id).filter_by(ctry=j).first()

        # If value does not exist in 'Pop_dens' table, then add the data to the table.
        if exist == None:
            u = Pop_dens(
                ctry = j,
                pop_yr = pop_yr,
                url = url_tif,
                dens = dens,
                updt = updt,
                stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
            )
            # Add entries to the database, and commit the changes.
            db.session.add(u)
            db.session.commit()
        
        # If value exists in 'Pop_dens' table, then overwrite the existing data.
        else:
            # 'u' = retrieves the existing data via id stored in index 1 of the tuple in 'exist'.
            u = Pop_dens.query.get(exist[0])
            # Overwriting of data in 'u'.
            u.pop_yr = pop_yr
            u.url = url_tif
            u.dens = dens
            u.updt = updt
            u.stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

            # Commit changes in 'u' to the database.
            db.session.commit()


    # -------------- Remove outdated data from 'Pop_dens' database table -------------- #

    # Checks if the table is empty by looking at the table's first entry.
    # 'exist' returns None is empty.
    exist = Pop_dens.query.get(1)

    # If table is full ...
    if exist != None:
        # Retrieve all data from 'Pop_dens' and store into 'u'.
        u = Pop_dens.query.all()
        # Loop over each data entry in 'u'.
        for i in u:
            # 'i.stamp' contain the entry timestamp as a string.
            # 'past' converts 'i.stamp' into Datetime object for comparison.
            # 'present' converts 'time' into Datetime object for comparison.
            past = datetime.strptime(i.stamp, "%Y-%m-%d %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S %z")
            present = datetime.strptime(time, "%Y-%m-%d %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S %z")
            
            # If entry timestamp (past) is earlier than the time of writing to the database (present) ...
            # ... then the entry is outdated and does not exist in the more recent batch of data.
            if past < present:
                # Delete the outdated entry.
                db.session.delete(i)
        # Commit changes to the database.
        db.session.commit()