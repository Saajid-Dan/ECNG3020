'''
Name: Saajid Dan
Course: ECNG 3020
Project Title:
'''

# ---------------------------------------------------------------------------- #
#                                    Imports                                   #
# ---------------------------------------------------------------------------- #

import pandas as pd
import urllib.request


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
            # 'url_tif' = URL to TIF file embedded in 'json_pop'.
            url_tif = json_pop.iloc[-1]['data']['files'][0]
        except Exception as e:
            error = "Error Extracting TIF URLs.\nError: " + str(e)
            return error

        # 'dir_' = output directory + filename of TIF file.
        # output directory is located in project directory.
        dir_ = './app/static/images/Population-Density/' + j + '.tif'


        # -------------------------- Download to File System ------------------------- #
        try:
            # TIF file is downloaded to project directory.
            urllib.request.urlretrieve(url_tif, dir_)
        except Exception as e:
            error = "Error Downloading TIF.\nSource: " + url_tif + "\nError: " + str(e)
            return error
        

    # ---------------------------------------------------------------------------- #
    #                                Add to Database                               #
    # ---------------------------------------------------------------------------- #

    # Add data to 'pop_dens' table in database.
    # 'updt' = date updated.
    # 'pop_yr' = year of population density TIF files.
    updt = json_pop.iloc[-1]['data']['date']
    pop_yr = json_pop.iloc[-1]['data']['popyear']