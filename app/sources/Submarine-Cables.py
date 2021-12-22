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


# ---------------------------------------------------------------------------- #
#                             Library Configuration                            #
# ---------------------------------------------------------------------------- #

# Disable chained assignments warning on pandas.
pd.options.mode.chained_assignment = None 


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


    # -------------------------- Submarine JSON Creation ------------------------- #
    
    # 'df_crd' has 4 headers that corresponds to a JSON format.
    # One column is called 'geometry' which stores MULTILINESTRING classes.
    # 'geometry' must remain as a MULTILINESTRING to be read properly.
    # Storing 'geometry' into a spreadsheet or text file changes the data type to string which is undesirable.
    # The logical goal remains to create a JSON file.
    # Main issues is that 'df_crd' has multiple IDs of same name, but different geometries.
    # The goal is to merge the geometries under one ID.
    # It is difficult to merge MULTILINESTRING classes.
    # Instead, convert them into a string and merge using string operations which can be added to a JSON format.
    
    # This process has 4 parts:
    # 1. Extracting geometry from 'df_crd'.
    # 2. Extracting geometry details from 'df_sub'.
    # 3. Merging Steps 1 and 2 into a JSON format.
    # 4. Writing JSON file.
    
    
    # ---------------------------------- Step 1 ---------------------------------- #

    # 'geo_id' = Stores MULTILINESTRINGs for unique geometry IDs in 'df_crd'.
    # 'j' = index interator.
    # 'tog' = condition used to determine when to merge geometries into a single ID.
    geo_id = []
    j = 1
    tog = 0

    # Loops over 'df_crd's geometry and compares to indices at a time.
    # If the indice values are different, then add the first index value to 'geo_id'.
    # If the indice values are the same, then do not add the first index value to 'geo_id'.
    # Instead, replace the value of the first index value with a new value.
    # This new value comprises of the MULTILINESTRING of the first index and the second index joined together.
    # The second index value will not get added to the 'geo_id' list as it will already be merged to the first index value.
    # 'geo_id' will be used to create the geometry part of the JSON file shown below.
    while (True):
        # If 'tog' == 0 (values are different), then add first index [j-1] values to 'geo_id'.
        if tog == 0:
            geo_id.append(str(df_crd.iloc[j-1]['geometry']))

        # Resets 'tog' to 0 if 'tog' is not at '0'.
        tog = 0

        # If 'j' (current iterator), exceeds maximum iteration limit (lenge of 'df_crd'),
        # then exit the loop.
        if j == len(df_crd):
            break

        # 'first' = first index value. Note j-1 th term.
        # 'second' = second index value. Note j th term.
        first = df_crd.iloc[j-1]['id']
        second = df_crd.iloc[j]['id']

        # If the index values are the same.
        if second == first:
            # 'k' is used to ensure that all index references to 'geo_id' are valid and exists in 'geo_id'.
            k = j-1
            while k >= len(geo_id):
                k -= 1

            # 'first_mod' = modifies geometry in 'first' by removing end of MULTILINESTRING.
            # 'sec_mod' = modifies geometry in 'second' by removing MULTILINESTRING header.
            # 'merge' = merges 'first_mod' and 'sec_mod' by 'first_mod' + 'sec_mod'.
            # 'merge' stores the MULTILINE representation of 'first' and 'second' combined.
            first_mod = str(df_crd.iloc[j-1]['geometry']).replace('))', '), ')
            sec_mod = str(df_crd.iloc[j]['geometry']).replace('MULTILINESTRING (', '')
            merge = first_mod + sec_mod
            
            # Replaces value of the first index value with the new merged value.
            # 'k' points to first index at this line.
            geo_id[k] = str(merge)

            # 'tog' is set to 1 to indicate that in the next iteration not to append new values.
            tog = 1
        # Increment iterator 'j'.
        j += 1


    # ---------------------------------- Step 2 ---------------------------------- #

    # Step 2 deals with extracting cable geometry details from 'df_sub' to add to JSON file with
    # geometries from 'df_crd'. Unlike 'df_crd', 'df_sub' contains unique IDs without repitition.
    # This means little string manipulation will be required.
    # Firstly, loop over 'df_sub' and to extract geometry details.
    # Then format MULTILINESTRING in 'geo_id' in a JSON array format.
    # Pandas store as a MULTILINESTRING instead of an array format so string manipulation is required.
    # Finally, format geometry details into JSON format.

    # 'feat' = stores JSON features of all cable details and geometries.
    feat = ''
    # Loop over 'df_sub' and extract details.
    # The manipulate format of 'geo_id' into JSON format.
    # Format geometry details into JSON format.
    # Add both formats above into a JSON properties ('prop').
    # Add all JSON features to together in 'feat'.
    # Add JSON features into a feature collection ('coll').
    # Write feature collection to a JSON file.
    for j in range(len(df_sub)):
        # Extracting geometry details.
        src_id = df_sub.iloc[j]['id']
        stat = df_sub.iloc[j]['is_planned']
        lnd = df_sub.iloc[j]['landing_points']
        name = df_sub.iloc[j]['name']
        len_ = df_sub.iloc[j]['length']
        rfs = df_sub.iloc[j]['rfs']
        sup = df_sub.iloc[j]['suppliers']
        own = df_sub.iloc[j]['owners']
        url = df_sub.iloc[j]['url']

        # Manipulate 'geo_id' geometries into JSON array format stored into 'geo'.
        geo = geo_id[j]
        geo = geo.replace('MULTILINESTRING ', '')
        geo = geo.replace('(', '[[')
        geo = geo.replace(')', ']]')
        geo = geo.replace(' ', ', ')
        geo = geo.replace(',,', ' ], [')
        geo = geo.replace('] ], [', '],')
        geo = geo.replace('[[[[', '[[')
        geo = geo.replace(']]]]', ']]')


        # ---------------------------------- Step 3 ---------------------------------- #

        # Creating cable JSON properties.
        prop = f'{{"type": "Feature", "properties": {{"id": "{src_id}", "name": "{name}", "stat": "{stat}", "lnd": "{lnd}", "len_": "{len_}", "rfs": "{rfs}", "sup": "{sup}", "own": "{own}", "url": "{url}"}}, "geometry": {{"type": "MultiLineString", "coordinates": [{geo}] }} }}'
        
        # Adding all properties into one feature.
        if j == len(df_sub) - 1:
            feat += prop + f'''
'''
        else:
            feat += prop + f''',
'''
    
    # 'coll' = stores feature collection.
    coll = f'''{{
        "type": "FeatureCollection", 
        "features": [
            {feat}
            ]
            }}'''


    # ---------------------------------- Step 4 ---------------------------------- #

    # Write feature collection to a JSON file.
    with open('./app/static/json/submarine.json', 'w') as f:
        f.write(coll)


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