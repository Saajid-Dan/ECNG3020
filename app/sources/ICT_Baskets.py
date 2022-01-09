'''
Name: Saajid Dan
Course: ECNG 3020
Project Title:
'''

# ---------------------------------------------------------------------------- #
#                                    Imports                                   #
# ---------------------------------------------------------------------------- #

import pandas as pd
from urllib.request import urlopen
from app import db
from app.models import GNI, PPP, USD
from datetime import datetime, timezone, timedelta


# ---------------------------------------------------------------------------- #
#                             Library Configuration                            #
# ---------------------------------------------------------------------------- #

# Disable chained assignments warning on pandas.
pd.options.mode.chained_assignment = None 

def baskets():
    '''
    Read, Filter, and Extract price basket data from an ITU workbook.
    Finally, store extracted data into a database.
    '''
    # ---------------------------------------------------------------------------- #
    #                            ITU Price Basket Source                           #
    # ---------------------------------------------------------------------------- #

    # 'url_ipb' = URL to ITU's Price Basket workbook.
    url_ipb = "https://www.itu.int/en/ITU-D/Statistics/Documents/publications/prices2020/ITU_ICTPriceBaskets_2008-2020.xlsx"

    
    # ---------------------------------------------------------------------------- #
    #                                 Read Sources                                 #
    # ---------------------------------------------------------------------------- #

    try:
        # 'df_s1' = Read sheet 1 of the 'url_ipb' into 'df_s1' dataframe.
        # Sheet 1 has baskets data from 2008-2017.
        df_s1 = pd.read_excel(url_ipb, sheet_name=0)
        
        # 'df_s2' = Read sheet 2 of the 'url_ipb' into 'df_s2' dataframe.
        # Sheet 2 has baskets data from 2018-2020.
        df_s2 = pd.read_excel(url_ipb, sheet_name=1)

        # 'df_s4' = Read sheet 4 of the 'url_ipb' into 'df_s4' dataframe.
        # Sheet 4 has info on data's source and last updated date.
        df_s4 = pd.read_excel(url_ipb, sheet_name=3)

        # Opens 'url_ipb' to retrieve last modified date to 'updt'.
        with urlopen(url_ipb) as f:
            updt = dict(f.getheaders())['Last-Modified']
            updt = updt[5:16]
            # dict(f.getheaders()) gives all headers.
            
    except Exception as e:
        error = "Source: " + url_ipb + "\nError: " + str(e)
        return error
    

    # ---------------------------------------------------------------------------- #
    #                            Filter and Extract Data                           #
    # ---------------------------------------------------------------------------- #

    # 'ctry' = contains a list of Caribbean countries to filter the data.
    ctry = [
        'Anguilla',
        'Antigua and Barbuda',
        'Bahamas',
        'Barbados',
        'Belize',
        'Bermuda',
        'British Virgin Islands',
        'Cayman Islands',
        'Dominica',
        'Grenada',
        'Guyana',
        'Haiti',
        'Jamaica',
        'Montserrat',
        'Saint Kitts and Nevis',
        'Saint Lucia',
        'Saint Vincent and the Grenadines',
        'Suriname',
        'Trinidad and Tobago',
        'Turks & Caicos Is.'
    ]

    try:
        # Filter 'df_s1' for Caribbean countries.
        # Filter 'df_s2' for Caribbean countries.
        # 'EntityName' is a header that contains countries.
        df_s1 = df_s1.loc[ [ any(i) for i in zip(*[df_s1['EntityName'] == word for word in ctry])] ]
        df_s2 = df_s2.loc[ [ any(i) for i in zip(*[df_s2['EntityName'] == word for word in ctry])] ]


        # ---------------------------- Cleaning Dataframes --------------------------- #

        # Remove Cols/Rows with 'ITU', 'IsoCode' and 'Mobile-cellular basket' from 'df_s1'.
        df_s1 = df_s1[df_s1.columns.drop(list(df_s1.filter(regex='ITU')))]
        df_s1 = df_s1[df_s1.columns.drop(list(df_s1.filter(regex='IsoCode')))]
        df_s1 = df_s1.loc[df_s1['Basket'] != "Mobile-cellular basket"]

        # Remove Cols/Rows with 'ITU', 'IsoCode', and 'Cellular' in 'df_s2'.
        df_s2 = df_s2[df_s2.columns.drop(list(df_s2.filter(regex='ITU')))]
        df_s2 = df_s2[df_s2.columns.drop(list(df_s2.filter(regex='IsoCode')))]
        df_s2 = df_s2[df_s2.columns.drop(list(df_s2.filter(regex='Cellular')))]


        # ----------------------------- Merge Dataframes ----------------------------- #

        # The 'merge' function merges 'df_s1' and 'df_s2' and separate them into 3 categories:
        # GNI per capita, Purchasing Parity Power, and US Dollar.
        # 'gni_pc' = contains GNI per capita.
        # 'ppp' = contains Purchasing Parity Power.
        # 'usd' = contains US Dollar.
        gni_pc = merge("GNIpc", "PPP", "USD", df_s1, df_s2)
        ppp = merge("PPP", "USD", "GNIpc", df_s1, df_s2)
        usd = merge("USD", "GNIpc", "PPP", df_s1, df_s2)

        # Export data in 'gni_pc', 'ppp', and 'usd' to CSV formats.
        gni_pc.to_csv(r'./app/static/csv/GNI.csv', encoding='utf-8', header=True, index=False)
        ppp.to_csv(r'./app/static/csv/PPP.csv', encoding='utf-8', header=True, index=False)
        usd.to_csv(r'./app/static/csv/USD.csv', encoding='utf-8', header=True, index=False)

        
    except Exception as e:
        error = "Error extracting Price Baskets Data.\nError: " + str(e)
        return error


    # ---------------------------------------------------------------------------- #
    #                               Store to Database                              #
    # ---------------------------------------------------------------------------- #

    # ------------------------------ GNI per capita ------------------------------ #

    # Loop over 'gni_pc' and add data to 'GNI' database table.
    for j in range(len(gni_pc)):
        ctry = gni_pc.iloc[j]['EntityName']
        year = int(gni_pc.iloc[j]['DataYear'])
        uni = str(ctry) + '-' + str(year)
        fix = float(gni_pc.iloc[j]['Fixed broadband 5GB'])
        mob = float(gni_pc.iloc[j]['Mobile broadband data only 1.5 GB'])
        low = float(gni_pc.iloc[j]['Mobile Data and Voice Low Usage'])
        high = float(gni_pc.iloc[j]['Mobile Data and Voice High Usage'])


        # -------------------- Store data to 'GNI' database table ------------------- #
       
        # If 'j' = 0, then store the current time into 'time'.
        # 'time' stores starting time of writing to the database.
        # The time in 'time' is used to compare against the database entry timestamps.
        # This is used to ensure only recent data is stored into the database. 
        if j == 0:
            time = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
        
        # 'exist' = Checks is a known value exists in the 'GNI' table.
        # Returns None if the value does not exist.
        # Returns a tuple of ids if the value exist.
        exist = db.session.query(GNI.id).filter_by(uni=uni).first()

        # If value does not exist in 'GNI' table, then add the data to the table.
        if exist == None:
            u = GNI(
            ctry = ctry,
            year = year,
            uni = uni,
            fix = fix,
            mob = mob,
            low = low, 
            high = high, 
            updt = updt, 
            stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
            )
            # Add entries to the database, and commit the changes.
            db.session.add(u)
            db.session.commit()
        
        # If value exists in 'GNI' table, then overwrite the existing data.
        else:
            # 'u' = retrieves the existing data via id stored in index 1 of the tuple in 'exist'.
            u = GNI.query.get(exist[0])
            # Overwriting of data in 'u'.
            u.ctry = ctry
            u.year = year
            u.fix = fix
            u.mob = mob
            u.low = low
            u.high = high
            u.updt = updt
            u.stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

            # Commit changes in 'u' to the database.
            db.session.commit()
    

    # -------------- Remove outdated data from 'GNI' database table -------------- #

    # Checks if the table is empty by looking at the table's first entry.
    # 'exist' returns None is empty.
    exist = GNI.query.all()

    # If table is full ...
    if exist != None:
        # Retrieve all data from 'GNI' and store into 'u'.
        u = GNI.query.all()
        # Loop over each data entry in 'u'.
        for j in u:
            # 'j.stamp' contain the entry timestamp as a string.
            # 'past' converts 'j.stamp' into Datetime object for comparison.
            # 'present' converts 'time' into Datetime object for comparison.
            past = datetime.strptime(j.stamp, "%Y-%m-%d %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S %z")
            present = datetime.strptime(time, "%Y-%m-%d %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S %z")
            
            # If entry timestamp (past) is earlier than the time of writing to the database (present) ...
            # ... then the entry is outdated and does not exist in the more recent batch of data.
            if past < present:
                # Delete the outdated entry.
                db.session.delete(j)
        # Commit changes to the database.
        db.session.commit()



    # -------------------------- Purchasing Parity Power ------------------------- #

    # Loop over 'ppp' and add data to 'PPP' database table.
    for j in range(len(ppp)):
        ctry = ppp.iloc[j]['EntityName']
        year = int(ppp.iloc[j]['DataYear'])
        uni = str(ctry) + '-' + str(year)
        fix = float(ppp.iloc[j]['Fixed broadband 5GB'])
        mob = float(ppp.iloc[j]['Mobile broadband data only 1.5 GB'])
        low = float(ppp.iloc[j]['Mobile Data and Voice Low Usage'])
        high = float(ppp.iloc[j]['Mobile Data and Voice High Usage'])


        # -------------------- Store data to 'PPP' database table ------------------- #
       
        # If 'j' = 0, then store the current time into 'time'.
        # 'time' stores starting time of writing to the database.
        # The time in 'time' is used to compare against the database entry timestamps.
        # This is used to ensure only recent data is stored into the database. 
        if j == 0:
            time = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

        # 'exist' = Checks is a known value exists in the 'PPP' table.
        # Returns None if the value does not exist.
        # Returns a tuple of ids if the value exist.
        exist = db.session.query(PPP.id).filter_by(uni=uni).first()

        # If value does not exist in 'PPP' table, then add the data to the table.
        if exist == None:
            u = PPP(
            ctry = ctry,
            year = year,
            uni = uni,
            fix = fix,
            mob = mob,
            low = low, 
            high = high, 
            updt = updt, 
            stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
            )
            # Add entries to the database, and commit the changes.
            db.session.add(u)
            db.session.commit()
        
        # If value exists in 'PPP' table, then overwrite the existing data.
        else:
            # 'u' = retrieves the existing data via id stored in index 1 of the tuple in 'exist'.
            u = PPP.query.get(exist[0])
            # Overwriting of data in 'u'.
            u.ctry = ctry
            u.year = year
            u.fix = fix
            u.mob = mob
            u.low = low
            u.high = high
            u.updt = updt
            u.stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

            # Commit changes in 'u' to the database.
            db.session.commit()


    # -------------- Remove outdated data from 'PPP' database table -------------- #

    # Checks if the table is empty by looking at the table's first entry.
    # 'exist' returns None is empty.
    exist = PPP.query.get(1)

    # If table is full ...
    if exist != None:
        # Retrieve all data from 'PPP' and store into 'u'.
        u = PPP.query.all()
        # Loop over each data entry in 'u'.
        for j in u:
            # print(j.stamp)
            # 'j.stamp' contain the entry timestamp as a string.
            # 'past' converts 'j.stamp' into Datetime object for comparison.
            # 'present' converts 'time' into Datetime object for comparison.
            past = datetime.strptime(j.stamp, "%Y-%m-%d %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S %z")
            present = datetime.strptime(time, "%Y-%m-%d %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S %z")
            
            # If entry timestamp (past) is earlier than the time of writing to the database (present) ...
            # ... then the entry is outdated and does not exist in the more recent batch of data.
            if past < present:
                # Delete the outdated entry.
                db.session.delete(j)
        # Commit changes to the database.
        db.session.commit()



    # --------------------------------- US Dollar -------------------------------- #

    # Loop over 'usd' and add data to 'USD' database table.
    for j in range(len(usd)):
        ctry = usd.iloc[j]['EntityName']
        year = int(usd.iloc[j]['DataYear'])
        uni = str(ctry) + '-' + str(year)
        fix = float(usd.iloc[j]['Fixed broadband 5GB'])
        mob = float(usd.iloc[j]['Mobile broadband data only 1.5 GB'])
        low = float(usd.iloc[j]['Mobile Data and Voice Low Usage'])
        high = float(usd.iloc[j]['Mobile Data and Voice High Usage'])


        # -------------------- Store data to 'USD' database table ------------------- #
       
        # If 'j' = 0, then store the current time into 'time'.
        # 'time' stores starting time of writing to the database.
        # The time in 'time' is used to compare against the database entry timestamps.
        # This is used to ensure only recent data is stored into the database. 
        if j == 0:
            time = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
        
        # 'exist' = Checks is a known value exists in the 'USD' table.
        # Returns None if the value does not exist.
        # Returns a tuple of ids if the value exist.
        exist = db.session.query(USD.id).filter_by(uni=uni).first()

        # If value does not exist in 'USD' table, then add the data to the table.
        if exist == None:
            u = USD(
            ctry = ctry,
            year = year,
            uni = uni,
            fix = fix,
            mob = mob,
            low = low, 
            high = high, 
            updt = updt, 
            stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
            )
            # Add entries to the database, and commit the changes.
            db.session.add(u)
            db.session.commit()
        
        # If value exists in 'USD' table, then overwrite the existing data.
        else:
            # 'u' = retrieves the existing data via id stored in index 1 of the tuple in 'exist'.
            u = USD.query.get(exist[0])
            # Overwriting of data in 'u'.
            u.year = year
            u.fix = fix
            u.mob = mob
            u.low = low
            u.high = high
            u.updt = updt
            u.stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

            # Commit changes in 'u' to the database.
            db.session.commit()
    

    # -------------- Remove outdated data from 'USD' database table -------------- #

    # Checks if the table is empty by looking at the table's first entry.
    # 'exist' returns None is empty.
    exist = USD.query.get(1)

    # If table is full ...
    if exist != None:
        # Retrieve all data from 'USD' and store into 'u'.
        u = USD.query.all()
        # Loop over each data entry in 'u'.
        for j in u:
            # 'j.stamp' contain the entry timestamp as a string.
            # 'past' converts 'j.stamp' into Datetime object for comparison.
            # 'present' converts 'time' into Datetime object for comparison.
            past = datetime.strptime(j.stamp, "%Y-%m-%d %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S %z")
            present = datetime.strptime(time, "%Y-%m-%d %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S %z")
            
            # If entry timestamp (past) is earlier than the time of writing to the database (present) ...
            # ... then the entry is outdated and does not exist in the more recent batch of data.
            if past < present:
                # Delete the outdated entry.
                db.session.delete(j)
        # Commit changes to the database.
        db.session.commit()
    

def merge(c1, c2, c3, s1, s2):
    '''
    The 'merge' function has 5 parameters:
    c1 = category 1, c2, category 2, c3, category 3, s1 = sheet 1, s2 = sheet 2.
    This function takes 's1' and 's2', filters for 'c1' and filters out 'c1' and 'c2'.
    Finally, merges filtered 's1' and 's2' into one dataframe.
    '''

    # Filter s2 for the category 'c1' and store result into 'df_cat' dataframe.
    # Remove column with 'currency' from 'df_cat'.
    df_cat = s2.loc[s2['currency'] == c1]
    df_cat = df_cat[df_cat.columns.drop(list(df_cat.filter(regex='currency')))]

    # Removal of columns with 'c2' and 'c3' from 's1'.
    s1 = s1[s1.columns.drop(list(s1.filter(regex=c2,)))]
    s1 = s1[s1.columns.drop(list(s1.filter(regex=c3,)))]

    # Extract Fixed Broadband Basket data from 's1' and store in 'df_fix' dataframe.
    # Extract Mobile Broadband Basket data from 's1' and store in 'df_mob' dataframe.
    # Extract Mobile Low Usage data from 's1' and store in 'df_low' dataframe.
    df_fix = s1.loc[s1['Basket'] == "Fixed broadband basket"]
    df_mob = s1.loc[s1['Basket'] == "Mobile-broadband basket, postpaid computer-based (1GB)"]
    df_low = s1.loc[s1['Basket'] == "Mobile-broadband basket, prepaid handset-based (500MB)"]


    # ------------------------ Matching Dataframe Headers ------------------------ #

    # Renaming columns called 'c1' to match headers in 'df_cat'.
    df_fix.rename(columns={c1:'Fixed broadband 5GB'}, inplace=True)
    df_mob.rename(columns={c1:'Mobile broadband data only 1.5 GB'}, inplace=True)
    df_low.rename(columns={c1:'Mobile Data and Voice Low Usage'}, inplace=True)

    # Removing columns to match headers in 'df_cat'.
    df_fix = df_fix[df_fix.columns.drop(list(df_fix.filter(regex='Basket')))]
    df_mob = df_mob[df_mob.columns.drop(list(df_mob.filter(regex='Basket')))]
    df_mob = df_mob[df_mob.columns.drop(list(df_mob.filter(regex='EntityName')))]
    df_mob = df_mob[df_mob.columns.drop(list(df_mob.filter(regex='DataYear')))]
    df_low = df_low[df_low.columns.drop(list(df_low.filter(regex='Basket')))]
    df_low = df_low[df_low.columns.drop(list(df_low.filter(regex='EntityName')))]
    df_low = df_low[df_low.columns.drop(list(df_low.filter(regex='DataYear')))]

    # Resetting indices in 'df_fix', 'df_mob', and 'df_low' to eliminate conflicts when merging.
    df_fix = df_fix.reset_index(drop=True)
    df_mob = df_mob.reset_index(drop=True)
    df_low = df_low.reset_index(drop=True)

    # Merge 'df_fix', 'df_mob', and 'df_low' dataframes to match the 'df_cat' header structure.
    # Result stored in 'df_res'.
    df_res = pd.concat([df_fix, df_mob, df_low], axis=1)
    
    # Appends 'df_res' to 'df_cat'.
    # Sort 'df_cat' by 'DataYear' header in ascending order.
    df_cat = df_cat.append(df_res)
    df_cat = df_cat.sort_values(by=['DataYear'])
    
    return df_cat