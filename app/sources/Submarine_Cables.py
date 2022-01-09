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
from bs4 import BeautifulSoup
import requests
from app import db
from app.models import Land
from datetime import datetime, timezone, timedelta


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
    # 'url_land' = root directory for landing points.
    url_ctry = "https://raw.githubusercontent.com/telegeography/www.submarinecablemap.com/master/web/public/api/v3/country/"
    url_sub = "https://raw.githubusercontent.com/telegeography/www.submarinecablemap.com/master/web/public/api/v3/cable/"
    url_land = "https://raw.githubusercontent.com/telegeography/www.submarinecablemap.com/master/web/public/api/v3/landing-point/"
    
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

    # 'url_his' = root directory for landing points commit history repo.
    # 'url_com' = root directory for submarine cable commit history repo.
    url_his = 'https://github.com/telegeography/www.submarinecablemap.com/commits/master/web/public/api/v3/landing-point/'
    url_com = 'https://github.com/telegeography/www.submarinecablemap.com/commits/master/web/public/api/v3/cable/'
    
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
        error = "Source: " + url_ctry + j + ".json\nError: " + str(e)
        return error


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
        error = "Source: " + url_sub + j + ".json\nError: " + str(e)
        return error


    # ------------------------- Read data from 'json_sub' ------------------------ #

    # Read data from 'json_sub' and store into 'df_sub_' dataframe.
    try:
        df_sub_ = gpd.read_file(json_sub)
    except Exception as e:
        error = "Source: " + json_sub + "\nError: " + str(e)
        return error

    # ------------------------ Read data from 'json_land' ------------------------ #

    # Read data from 'json_land' and store into 'df_land' dataframe.
    try:
        df_land = gpd.read_file(json_land)
    except Exception as e:
        error = "Source: " + json_land + "\nError: " + str(e)
        return error


    # ---------------------------------------------------------------------------- #
    #                                  Filter and Extract Data                     #
    # ---------------------------------------------------------------------------- #

    # ------------------------------ Landing Points ------------------------------ #
    root = 'https://github.com/telegeography/www.submarinecablemap.com/blob/master/web/public/api/v3/landing-point/'
    try:
        # Filter 'df_sub' for Caribbean landing point IDs and append to 'car_'.
        # Filter 'df_sub' for International landing point IDs and append to 'int_'.
        car_id = []
        int_id = []
        
        # 'updt_car' = Stores last updated date of Caribbean landing point JSON files.
        # 'int_car' = Stores last updated date of International landing point JSON files.
        updt_car = []
        updt_int = []
        
        sub_car = []
        sub_int = []

        for j in df_sub['landing_points'].values:
            for k in j:
                # 'chq' = condition to distinguish Caribbean and international landing points.
                x = k['id']
                
                # 'url_tel' = directory of the commit history for JSON file with an ID of 'j'.
                # Commit history contains last updated date of file.
                url_tel = url_his + x + '.json'

                try:
                    # Read HTML to 'html_tel' from URL in 'url_tel'.
                    html_tel = requests.get(url_tel).text

                    # Pass HTML to BeautifulSoup with an XML parser.
                    soup = BeautifulSoup(html_tel, 'lxml')

                    if 'Page not found' in soup.find('title').text:
                        raise Exception("HTTP Error 404: NOT FOUND")
                except Exception as e:
                    error = "Source: " + url_tel + "\nError: " + str(e)
                    return error

                # 'updt' = last updated data.
                updt = soup.find('h2', class_='f5 text-normal').text
                updt = updt.replace('Commits on ', '')


                chq = 0
                for l in ctry:
                    # 'dominican' = Dominican Republic which is not a Caribbean country considered.
                    if l in x and not('dominican' in x):
                        chq += 1
                if chq > 0:
                    if k['id'] in car_id:
                        continue
                    else:
                        car_id.append(k['id'])
                        updt_car.append(updt)

                        sub = pd.read_json(url_land + x + ".json", lines=True)
                        cables = sub['cables'].values[0]

                        tmp = ''
                        for cable in cables:
                            tmp += '"' + cable['name'] + '", '
                        sub_car.append('[' + tmp + ']')
                else:
                    if k['id'] in int_id:
                        continue
                    else:
                        int_id.append(k['id'])
                        updt_int.append(updt)

                        sub = pd.read_json(url_land + x + ".json", lines=True)
                        cables = sub['cables'].values[0]

                        tmp = ''
                        for cable in cables:
                            tmp += '"' + cable['name'] + '", '
                        sub_int.append('[' + tmp + ']')   


        # Filter 'df_land' for Caribbean landing points using IDs in 'car_id' and store into 'df_car' dataframe.
        # Filter 'df_land' for international landing points using IDs in 'int_id' and store into 'df_land' dataframe.
        df_car = df_land.loc[ [ any(i) for i in zip(*[df_land['id'] == word for word in car_id])] ]
        df_int = df_land.loc[ [ any(i) for i in zip(*[df_land['id'] == word for word in int_id])] ]

        feat = ''
        for j in range(len(df_car)):
            # Creating cable JSON properties.
            prop = f'{{"type": "Feature", "properties": {{"id": "{df_car.iloc[j]["id"]}", "updt": "{updt_car[j]}", "name": "{df_car.iloc[j]["name"]}", "ctry": "{df_car.iloc[j]["name"].split(" ,")[-1]}", "car": "Yes"}}, "geometry": {{"type": "Point", "coordinates": [{df_car.iloc[j].geometry.x},{df_car.iloc[j].geometry.y}] }} }}'
            
            # Adding all properties into one feature.
            if j == len(df_car) - 1:
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
        
        with open('./app/static/json/landing_point.json', 'w') as f:
            f.write(coll)

    
    except Exception as e:
        error = "Error extracting Landing Points.\nError: " + str(e)
        return error


    # ----------------------------- Submarine Cables ----------------------------- #

    try:
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

            # 'url_tel' = directory of the commit history for JSON file with an ID of 'x'.
            # Commit history contains last updated date of file.
            url_tel = url_com + src_id + '.json'

            try:
                # Read HTML to 'html_tel' from URL in 'url_tel'.
                html_tel = requests.get(url_tel).text

                # Pass HTML to BeautifulSoup with an XML parser.
                soup = BeautifulSoup(html_tel, 'lxml')

                if 'Page not found' in soup.find('title').text:
                    raise Exception("HTTP Error 404: NOT FOUND")
            except Exception as e:
                error = "Source: " + url_tel + "\nError: " + str(e)
                return error

            # 'updt' = last updated data.
            updt = soup.find('h2', class_='f5 text-normal').text
            updt = updt.replace('Commits on ', '')

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
            prop = f'{{"type": "Feature", "properties": {{"id": "{src_id}", "updt": "{updt}", "name": "{name}", "stat": "{stat}", "lnd": "{lnd}", "len_": "{len_}", "rfs": "{rfs}", "sup": "{sup}", "own": "{own}", "url": "{url}"}}, "geometry": {{"type": "MultiLineString", "coordinates": [{geo}] }} }}'
            
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
    except Exception as e:
        error = "Error extracting Submarine Cables Geometries or Details.\nError: " + str(e)
        return error

    # ---------------------------------------------------------------------------- #
    #                              Store Data into Database                             #
    # ---------------------------------------------------------------------------- #
    
    # ----------------------- Timestamping Check Condition ----------------------- #

    # 'time' stores starting time of writing to the database.
    # The time in 'time' is used to compare against the database entry timestamps.
    # This is used to ensure only recent data is stored into the database. 
    time = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")


    # ------------------------- Caribbean Landing Points ------------------------- #

    # Loop over 'df_car' and add data to 'Land' database table.
    for j in range(len(df_car)):
        uni = df_car.iloc[j]['id']
        name = df_car.iloc[j]['name']
        lat = df_car.iloc[j].geometry.y
        lon = df_car.iloc[j].geometry.x
        ctry = name.split(', ')[-1]
        car = "Yes"
        updt = updt_car[j]
        cab = sub_car[j] 
        
        # -------------------- Store data to 'Land' database table ------------------- #
            
        # 'exist' = Checks is a known value exists in the 'Land' table.
        # Returns None if the value does not exist.
        # Returns a tuple of ids if the value exist.
        exist = db.session.query(Land.id).filter_by(uni=uni).first()

        # If value does not exist in 'Land' table, then add the data to the table.
        if exist == None:
            u = Land(
                uni = uni,
                name = name,
                lat = lat,
                lon = lon,
                ctry = ctry, 
                car = car,
                cab = cab,
                updt = updt,
                stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
            )
            # Add entries to the database, and commit the changes.
            db.session.add(u)
            db.session.commit()
        
        # If value exists in 'Land' table, then overwrite the existing data.
        else:
            # 'u' = retrieves the existing data via id stored in index 1 of the tuple in 'exist'.
            u = Land.query.get(exist[0])
            # Overwriting of data in 'u'.
            u.uni = uni
            u.name = name
            u.lat = lat
            u.lon = lon
            u.ctry = ctry
            u.car = car
            u.cab = cab
            u.updt = updt
            u.stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

            # Commit changes in 'u' to the database.
            db.session.commit()
    
    
    # ----------------------- International Landing Points ----------------------- #

    # Loop over 'df_int' and add data to 'land' database table.
    for j in range(len(df_int)):
        uni = df_int.iloc[j]['id']
        name = df_int.iloc[j]['name']
        lat = df_int.iloc[j].geometry.y
        lon = df_int.iloc[j].geometry.x
        ctry = name.split(', ')[-1]
        car = "No"
        updt = updt_int[j]
        cab = sub_int[j] 
        
        # 'exist' = Checks is a known value exists in the 'Land' table.
        # Returns None if the value does not exist.
        # Returns a tuple of ids if the value exist.
        exist = db.session.query(Land.id).filter_by(uni=uni).first()

        # If value does not exist in 'Land' table, then add the data to the table.
        if exist == None:
            u = Land(
                uni = uni,
                name = name,
                lat = lat,
                lon = lon,
                ctry = ctry, 
                car = car,
                cab = cab,
                updt = updt,
                stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
            )
            # Add entries to the database, and commit the changes.
            db.session.add(u)
            db.session.commit()
        
        # If value exists in 'Land' table, then overwrite the existing data.
        else:
            # 'u' = retrieves the existing data via id stored in index 1 of the tuple in 'exist'.
            u = Land.query.get(exist[0])
            # Overwriting of data in 'u'.
            u.uni = uni
            u.name = name
            u.lat = lat
            u.lon = lon
            u.ctry = ctry
            u.car = car
            u.cab = cab
            u.updt = updt
            u.stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

            # Commit changes in 'u' to the database.
            db.session.commit()


    # -------------- Remove outdated data from 'Land' database table -------------- #

    # Checks if the table is empty by looking at the table's first entry.
    # 'exist' returns None is empty.
    exist = Land.query.all()

    # If table is full ...
    if exist != None:
        # Retrieve all data from 'Land' and store into 'u'.
        u = Land.query.all()
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