'''
Name: Saajid Dan
Course: ECNG 3020
Project Title:
'''

# ---------------------------------------------------------------------------- #
#                                    Imports                                   #
# ---------------------------------------------------------------------------- #

import pandas as pd
import geopandas as gpd


def submarine():
    '''
    Reading, Filtering, Extracting Data from Telegeography's Submarine Cable Map Repo.
    Finally, the data is stored into a database.
    '''
    # ---------------------------------------------------------------------------- #
    #                             Telegeography Sources                            #
    # ---------------------------------------------------------------------------- #

    # 'url_ctry' = root directory for submarine cables/landing points.
    # 'url_sub' = root directory for submarine cables.
    url_ctry = "https://raw.githubusercontent.com/telegeography/www.submarinecablemap.com/master/web/public/api/v3/country/"
    url_sub = "https://raw.githubusercontent.com/telegeography/www.submarinecablemap.com/master/web/public/api/v3/cable/"
    
    # 'ctry' = sub directories for 'url_ctry'
    ctry = [
        'anguilla',
        'antigua-and-barbuda',
        'bahamas',
        'barbados',
        'belize',
        'bermuda',
        'virgin-islands-u-k-',
        'cayman-islands',
        'dominica',
        'grenada',
        'guyana',
        'haiti',
        'jamaica',
        'montserrat',
        'saint-kitts-and-nevis',
        'saint-lucia',
        'saint-vincent-and-the-grenadines',
        'suriname',
        'trinidad-and-tobago',
        'turks-and-caicos-islands'
    ]

    # 'json_sub' = submarine cables JSON with geometries.
    # 'json_land' = landing points JSON with geometries.
    json_sub = "https://raw.githubusercontent.com/telegeography/www.submarinecablemap.com/master/web/public/api/v3/cable/cable-geo.json"
    json_land = "https://raw.githubusercontent.com/telegeography/www.submarinecablemap.com/master/web/public/api/v3/landing-point/landing-point-geo.json"


    # ---------------------------------------------------------------------------- #
    #                                 Read Sources                                 #
    # ---------------------------------------------------------------------------- #

    # ---------------- Read data from 'url_ctry' + 'ctry' indices ---------------- #

    # Read 'url_ctry' + 'ctry' indices and store into a 'df_ctry' dataframe.
    try:
        df_ctry = pd.DataFrame()
        for j in ctry:
            x = pd.read_json(url_ctry + j + ".json", lines=True)
            df_ctry = df_ctry.append(x)
    except Exception as e:
        return e


    # ------------------------- Read data from 'url_sub' ------------------------- #

    # Extract Caribbean cable IDs from 'df' dataframe and store into 'id_' list.
    id_ = []
    for j in df_ctry['cables'].values:
        for k in j:
            id_.append( k['id'] )
    # sort 'id_' in ascending order and remove duplicate entries
    id_ = sorted(list(set(id_)), reverse=False)

    # Read cable data from 'url_sub' + 'id_' indices and store into 'df_sub' dataframe.
    try:
        df_sub = pd.DataFrame()
        for j in id_:
            x = pd.read_json(url_sub + j + ".json", lines=True)
            df_sub = df_sub.append(x)
    except Exception as e:
        return e


    # ------------------------- Read data from 'json_sub' ------------------------ #

    # Read data from 'json_sub' and store into 'df_sub_' dataframe.
    try:
        df_sub_ = gpd.read_file(json_sub)
    except Exception as e:
        return e

    # ------------------------ Read data from 'json_land' ------------------------ #

    # Read data from 'json_land' and store into 'df_land' dataframe.
    try:
        df_land = gpd.read_file(json_land)
    except Exception as e:
        return e

    # ---------------------------------------------------------------------------- #
    #                                  Filter and Extract Data                     #
    # ---------------------------------------------------------------------------- #

    # ------------------------------ Landing Points ------------------------------ #

    # Filter 'df_sub' for Caribbean landing point IDs and append to 'car_'.
    # Filter 'df_sub' for International landing point IDs and append to 'int_'.
    car_id = []
    int_id = []
    for j in df_sub['landing_points'].values:
        for k in j:
            # 'chq' = condition to distinguish Caribbean and international landing points.
            x = k['id']
            chq = 0
            for l in ctry:
                # 'dominican' = Dominican Republic which is not a Caribbean country considered.
                if l in x and not('dominican' in x):
                    chq += 1
            if chq > 0:
                car_id.append(k['id'])
            else:
                int_id.append(k['id'])

    # Remove duplicates from 'car_' and 'int_' and sort them in ascending order.
    car_id = sorted(list(set(car_id)), reverse=False)
    int_id = sorted(list(set(int_id)), reverse=False)

    # Filter 'df_land' for Caribbean landing points using IDs in 'car_id' and store into 'df_car' dataframe.
    # Filter 'df_land' for international landing points using IDs in 'int_id' and store into 'df_land' dataframe.
    df_car = df_land.loc[ [ any(i) for i in zip(*[df_land['id'] == word for word in car_id])] ]
    df_int = df_land.loc[ [ any(i) for i in zip(*[df_land['id'] == word for word in int_id])] ]

    # Remove columns called 'id' and 'is_tbd' from 'df_car'.
    # Remove columns called 'id' and 'is_tbd' from 'df_int'.
    df_car = df_car[df_car.columns.drop(list(df_car.filter(regex='id')))]
    df_car = df_car[df_car.columns.drop(list(df_car.filter(regex='is_tbd')))]
    df_int = df_int[df_int.columns.drop(list(df_int.filter(regex='id')))]
    df_int = df_int[df_int.columns.drop(list(df_int.filter(regex='is_tbd')))]


    # ----------------------------- Submarine Cables ----------------------------- #

    # Filter 'df_sub_' for Caribbean cable coordinates using cable IDs == 'id_'.
    # Store coordinates into 'df_crd' dataframe and sort in ascending order.
    df_crd = df_sub_.loc[
        [any(i) for i in zip(* [df_sub_['id'] == word for word in id_]) ]
        ].sort_values("id")

    # Remove columns called 'name', 'feature_id' and 'color' from 'df_crd'.
    df_crd = df_crd[df_crd.columns.drop(list(df_crd.filter(regex='name')))]
    df_crd = df_crd[df_crd.columns.drop(list(df_crd.filter(regex='color')))]
    df_crd = df_crd[df_crd.columns.drop(list(df_crd.filter(regex='feature_id')))]

    # Remove columns called 'notes' and 'rfs_year' from 'df_sub'.
    df_sub = df_sub[df_sub.columns.drop(list(df_sub.filter(regex='rfs_year')))]
    df_sub = df_sub[df_sub.columns.drop(list(df_sub.filter(regex='notes')))]


    # ---------------------------------------------------------------------------- #
    #                              Store Data into Database                             #
    # ---------------------------------------------------------------------------- #

    # ------------------------- Caribbean Landing Points ------------------------- #

    # Loop over 'df_car' and add data to 'car_land' database table.
    for j in range(len(df_car)):
        name = df_car.iloc[j]['name']
        lat = df_car.iloc[j].geometry.y
        lon = df_car.iloc[j].geometry.x
        ctry = name.split(', ')[-1]

        # Add 'name to database
        # Add 'lat' to database
        # Add 'lon' to database
        # Add 'ctry' to database
    
    # ----------------------- International Landing Points ----------------------- #

    # Loop over 'df_int' and add data to 'int_land' database table.
    for j in range(len(df_int)):
        name = df_int.iloc[j]['name']
        lat = df_int.iloc[j].geometry.y
        lon = df_int.iloc[j].geometry.x
        ctry = name.split(', ')[-1]

        # Add 'name to database
        # Add 'lat' to database
        # Add 'lon' to database
        # Add 'ctry' to database


    # -------------------------- Submarine Cable Details ------------------------- #

    # Loop over 'df_sub' and add data to 'sub_det' database table.
    for j in range(len(df_sub)):
        src_id = df_sub.iloc[j]['id']
        stat = df_sub.iloc[j]['is_planned']
        lnd = df_sub.iloc[j]['landing_points']
        name = df_sub.iloc[j]['name']
        len_ = df_sub.iloc[j]['length']
        rfs = df_sub.iloc[j]['rfs']
        sup = df_sub.iloc[j]['suppliers']
        own = df_sub.iloc[j]['owners']
        url = df_sub.iloc[j]['url']

        # Add 'src_id to database
        # Add 'stat' to database
        # Add 'lnd' to database
        # Add 'name to database
        # Add 'len_' to database
        # Add 'rfs' to database
        # Add 'sup to database
        # Add 'own' to database
        # Add 'url' to database


    # ------------------------ Submarine Cable Geometries ------------------------ #

    # Loop over 'df_crd' and add data to 'sub_geo' database table.
    for j in range(len(df_crd)):
        src_id = df_crd.iloc[j]['id']
        geo = df_crd.iloc[j]['geometry']

        # Add 'src_id to database
        # Add 'geo' to database