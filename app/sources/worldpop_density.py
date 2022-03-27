'''
Name: Saajid Dan
Course: ECNG 3020
Project Title:
'''

# ---------------------------------------------------------------------------- #
#                                    Imports                                   #
# ---------------------------------------------------------------------------- #

import pandas as pd
from app import db
from app.email import email_exception
import traceback
from app.models import Wpop_density
from datetime import datetime, timezone, timedelta


def worldpop_density():
    '''
    Read WorldPop's API for a JSON with the population density of unconstrained individual countries.
    A download link to the TIF files is retrieved from the JSON and saved to the project's directory.
    Details on the data's update date and population density year stored to a database.
    '''
    # ---------------------------------------------------------------------------- #
    #                                WorldPop Source                               #
    # ---------------------------------------------------------------------------- #


    email_subject = 'worldpop_density.py'


    # 'url_root' = root directory of WorldPop's population density data for unconstrained individual countries.
    # For more info on the API: https://www.worldpop.org/sdi/introapi
    url_root = 'https://www.worldpop.org/rest/data/pop_density/pd_ic_1km?iso3='


    # ---------------------------------------------------------------------------- #
    #                                  Read Source                                 #
    # ---------------------------------------------------------------------------- #

    # 'cc' = ISO-3 Country codes.
    # Subdirectories of 'url_root'
    cc = [
        'AIA', 'ATG', 'BHS', 'BRB', 'BLZ', 'BMU', 'VGB', 'CYM', 'DMA', 'GRD', 
        'GUY', 'HTI', 'JAM', 'MSR', 'KNA', 'LCA', 'VCT', 'SUR', 'TTO', 'TCA'
    ]

    # A dictionary with key as ISO3 country codes, and value as full country name
    dict_ctry = {
        'AIA':'Anguilla', 'ATG':'Antigua and Barbuda', 'BHS':'Bahamas',
        'BRB':'Barbados', 'BLZ':'Belize', 'BMU':'Bermuda',
        'VGB':'British Virgin Islands', 'CYM':'Cayman Islands',
        'DMA':'Dominica', 'GRD':'Grenada', 'GUY':'Guyana', 'HTI':'Haiti',
        'JAM':'Jamaica', 'MSR':'Montserrat', 'KNA':'Saint Kitts and Nevis',
        'LCA':'Saint Lucia', 'VCT':'Saint Vincent and the Grenadines',
        'SUR':'Suriname', 'TTO':'Trinidad and Tobago', 'TCA':'Turks & Caicos Is.'
    }

    # Loop over 'cc' to append subdirectories to 'url_root' to read data.
    for index, j in enumerate(cc):
        # 'url' = 'url_root' + 'j' = population density JSON for country 'j'.
        # 'j' = individual country codes.
        url = url_root + j
        

        # --------------------------------- Read JSON -------------------------------- #

        try:
            # 'json_pop' = stores JSON from 'url'.
            json_pop = pd.read_json(url)
        except Exception as e:
            email_exception(e, email_subject)
            return

        
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
                elif link.find('.zip') != -1:
                    url_zip = link
            updt = json_pop.iloc[-1]['data']['date']
            pop_yr = json_pop.iloc[-1]['data']['popyear']

        except Exception as e:
            email_exception(e, email_subject)
            return

        try:
            df_zip = pd.read_csv(url_zip)
            max_dens = df_zip['Z'].max()
            min_dens = df_zip['Z'].min()
            avg_dens = df_zip['Z'].mean()
            max_lon = df_zip['X'].max()
            max_lat = df_zip['Y'].max()
            min_lon = df_zip['X'].min()
            min_lat = df_zip['Y'].min()
         

        except Exception as e:
            email_exception(e, email_subject)
            return


        # ---------------------------------------------------------------------------- #
        #                                Add to Database                               #
        # ---------------------------------------------------------------------------- #

        # ----------------------- Timestamping Check Condition ----------------------- #

        # 'time' stores starting time of writing to the database.
        # The time in 'time' is used to compare against the database entry timestamps.
        # This is used to ensure only recent data is stored into the database. 
        if index == 0:
            time = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
        
        # Add data to the database entity
        u = Wpop_density(
            country = dict_ctry[j],
            date = pop_yr,
            url_tif = url_tif,
            avg_dens = avg_dens,
            max_dens = max_dens,
            min_dens = min_dens,
            max_lat = max_lat,
            max_lon = max_lon,
            min_lat = min_lat,
            min_lon = min_lon,
            updated = updt,
            source = url,
            stamp = time
        )
        # Add entries to the database, and commit the changes.
        db.session.add(u)
        db.session.commit()
        
     # Remove outdated database entries.
    remove_outdated(Wpop_density, time)


# -------------- Remove outdated data from 'db_table' database table -------------- #

def remove_outdated(db_table, time):
    # Checks if the table is empty by looking at the table's first entry.
    # 'exist' returns None is empty.
    exist = db_table.query.all()

    # If table is full ...
    if exist != None:
        # Retrieve all data from 'db_table' and store into 'u'.
        u = db_table.query.all()
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