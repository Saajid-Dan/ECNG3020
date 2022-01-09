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
from app.models import ICT_fix, ICT_mob, ICT_per, ICT_bw
from datetime import datetime, timezone, timedelta

def indicators():
    '''
    Reads, filters, and extracts indicators data from ITU's workbooks.
    Finallys, stores extracted data to a database.
    '''
    # ---------------------------------------------------------------------------- #
    #                             ITU Indicators Source                            #
    # ---------------------------------------------------------------------------- #

    # 'url_fix' = fixed broadband subscription.
    # 'url_mob' = mobile broadband subscription.
    # 'url_per' = percent of individuals using the internet.
    # 'url_bw' = international bandwidth in Mbits per second.
    url_fix = "https://www.itu.int/en/ITU-D/Statistics/Documents/statistics/2021/July/FixedBroadbandSubscriptions_2000-2020.xlsx"
    url_mob = "https://www.itu.int/en/ITU-D/Statistics/Documents/statistics/2021/July/MobileBroadbandSubscriptions_2007-2020.xlsx"
    url_per = "https://www.itu.int/en/ITU-D/Statistics/Documents/statistics/2021/PercentIndividualsUsingInternet_Nov2021.xlsx"
    url_bw = "https://www.itu.int/en/ITU-D/Statistics/Documents/statistics/2021/July/InternationalBandwidthInMbits_2007-2020.xlsx"


    # ---------------------------------------------------------------------------- #
    #                                  Read Source                                 #
    # ---------------------------------------------------------------------------- #

    # 'df_fix' = read URL at 'url_fix' into 'df_fix' dataframe.
    # 'df_mob' = read URL at 'url_mob' into 'df_mob' dataframe.
    # 'df_per' = read URL at 'url_per' into 'df_per' dataframe.
    # 'df_bw' = read URL at 'url_bw' into 'df_bw' dataframe.
    
    try:
        df_fix = pd.read_excel(url_fix)

        # Opens 'url_fix' to retrieve last modified date to 'updt_fix'.
        with urlopen(url_fix) as f:
            updt_fix = dict(f.getheaders())['Last-Modified']
            updt_fix = updt_fix[5:16]
            # dict(f.getheaders()) gives all headers.

    except Exception as e:
        error = "Source: " + url_fix + "\nError: " + str(e)
        return error

    try:
        df_mob = pd.read_excel(url_mob)

        # Opens 'url_mob' to retrieve last modified date to 'updt_mob'.
        with urlopen(url_mob) as f:
            updt_mob = dict(f.getheaders())['Last-Modified']
            updt_mob = updt_mob[5:16]
            # dict(f.getheaders()) gives all headers.
            
    except Exception as e:
        error = "Source: " + url_mob + "\nError: " + str(e)
        return error

    try:
        df_per = pd.read_excel(url_per)

        # Opens 'url_per' to retrieve last modified date to 'updt_per'.
        with urlopen(url_per) as f:
            updt_per = dict(f.getheaders())['Last-Modified']
            updt_per = updt_per[5:16]
            # dict(f.getheaders()) gives all headers.

    except Exception as e:
        error = "Source: " + url_per + "\nError: " + str(e)
        return error

    try:
        df_bw = pd.read_excel(url_bw)

        # Opens 'url_bw' to retrieve last modified date to 'updt_bw'.
        with urlopen(url_bw) as f:
            updt_bw = dict(f.getheaders())['Last-Modified']
            updt_bw = updt_bw[5:16]
            # dict(f.getheaders()) gives all headers.

    except Exception as e:
        error = "Source: " + url_bw + "\nError: " + str(e)
        return error


    # ---------------------------------------------------------------------------- #
    #                            Filter and Extract Data                           #
    # ---------------------------------------------------------------------------- #

    # 'ctry' = List of Caribbean countries to filter data.
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
        # Filter 'df_fix', 'df_mob', 'df_per', and 'df_bw' for Caribbean countries in 'ctry'.
        df_fix = df_fix.loc[ [ any(i) for i in zip(*[df_fix['Country'] == word for word in ctry])] ]
        df_mob = df_mob.loc[ [ any(i) for i in zip(*[df_mob['Country'] == word for word in ctry])] ]
        df_per = df_per.loc[ [ any(i) for i in zip(*[df_per['Country'] == word for word in ctry])] ]
        df_bw = df_bw.loc[ [ any(i) for i in zip(*[df_bw['Country'] == word for word in ctry])] ]

        # Renaming and removing unnecessary columns from 'df_fix'.
        df_fix = df_fix.rename(columns = lambda x: x.strip('_value'))
        df_fix = df_fix[df_fix.columns.drop(list(df_fix.filter(regex='_')))]
        df_fix = df_fix[df_fix.columns.drop(list(df_fix.filter(regex='Indicator')))]

        # Renaming and removing unnecessary columns from 'df_mob'.
        df_mob = df_mob.rename(columns = lambda x: x.strip('_value'))
        df_mob = df_mob[df_mob.columns.drop(list(df_mob.filter(regex='_')))]
        df_mob = df_mob[df_mob.columns.drop(list(df_mob.filter(regex='Indicator',)))]

        # Renaming and removing unnecessary columns from 'df_per'.
        df_per = df_per.rename(columns = lambda x: x.strip('_value'))
        df_per = df_per[df_per.columns.drop(list(df_per.filter(regex='_')))]
        df_per = df_per[df_per.columns.drop(list(df_per.filter(regex='Indicator')))]

        # Renaming and removing unnecessary columns from 'df_bw'.
        df_bw = df_bw.rename(columns = lambda x: x.strip('_value'))
        df_bw = df_bw[df_bw.columns.drop(list(df_bw.filter(regex='_')))]
        df_bw = df_bw[df_bw.columns.drop(list(df_bw.filter(regex='Indicator')))]

        # 'yrs_fix', 'yrs_mob', 'yrs_per', and 'yrs_bw' contains the years in 'df_fix', 'df_mob', 'df_per', and 'df_bw'.
        yrs_fix = [int(i) for i in list(df_fix.columns[1:].values)]
        yrs_mob = [int(i) for i in list(df_mob.columns[1:].values)]
        yrs_per = [int(i) for i in list(df_per.columns[1:].values)]
        yrs_bw = [int(i) for i in list(df_bw.columns[1:].values)]

        #
        df_fix = df_fix.assign(updt = [updt_fix] * len(df_fix))
        df_mob = df_mob.assign(updt = [updt_mob] * len(df_mob))
        df_per = df_per.assign(updt = [updt_per] * len(df_per))
        df_bw = df_bw.assign(updt = [updt_bw] * len(df_bw))

        # Export data in 'df_fix', 'df_mob', 'df_per', and 'df_bw' to CSV formats.
        df_fix.to_csv(r'./app/static/csv/indicators_fixed.csv', encoding='utf-8', header=True, index=False)
        df_mob.to_csv(r'./app/static/csv/indicators_mobile.csv', encoding='utf-8', header=True, index=False)
        df_per.to_csv(r'./app/static/csv/indicators_percent.csv', encoding='utf-8', header=True, index=False)
        df_bw.to_csv(r'./app/static/csv/indicators_bandwidth.csv', encoding='utf-8', header=True, index=False)


    except Exception as e:
        error = "Error extracting Indicators Data.\nError: " + str(e)
        return error
    

    # ---------------------------------------------------------------------------- #
    #                               Store to Database                              #
    # ---------------------------------------------------------------------------- #

    # ----------------------- Fixed Broadband subscriptions ---------------------- #

    # Loop over 'df_fix' and 'yrs_fix' and add data to database.
    for j in range(len(yrs_fix)):
        
        # If 'j' = 0, then store the current time into 'time'.
        # 'time' stores starting time of writing to the database.
        # The time in 'time' is used to compare against the database entry timestamps.
        # This is used to ensure only recent data is stored into the database. 
        if j == 0:
            time = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")


        # Add year of subscription to 'ICT_fix' database
        yrs = yrs_fix[j]

        # 'exist' = Checks is a known value exists in the 'ICT_fix' table.
        # Returns None if the value does not exist.
        # Returns a tuple of ids if the value exist.
        exist = db.session.query(ICT_fix.id).filter_by(yrs=yrs).first()

        # If value does not exist in 'ICT_fix' table, then add the data to the table.
        if exist == None:
            # Add fixed broadband subscriptions for each country to database.
            # Note that the variables are entited by 2 letter country codes.
            u = ICT_fix(
                yrs = yrs,
                ai = float(df_fix.iloc[0, j+1]),
                ag = float(df_fix.iloc[1, j+1]),
                bs = float(df_fix.iloc[2, j+1]),
                bb = float(df_fix.iloc[3, j+1]),
                bz = float(df_fix.iloc[4, j+1]),
                bm = float(df_fix.iloc[5, j+1]),
                vg = float(df_fix.iloc[6, j+1]),
                ky = float(df_fix.iloc[7, j+1]),
                dm = float(df_fix.iloc[8, j+1]),
                gd = float(df_fix.iloc[9, j+1]),
                gy = float(df_fix.iloc[10, j+1]),
                ht = float(df_fix.iloc[11, j+1]),
                jm = float(df_fix.iloc[12, j+1]),
                ms = float(df_fix.iloc[13, j+1]),
                kn = float(df_fix.iloc[14, j+1]),
                lc = float(df_fix.iloc[15, j+1]),
                vc = float(df_fix.iloc[16, j+1]),
                sr = float(df_fix.iloc[17, j+1]),
                tt = float(df_fix.iloc[18, j+1]),
                tc = float(df_fix.iloc[19, j+1]),
                updt = updt_fix,
                stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
            )
            # Add entries to the database, and commit the changes.
            db.session.add(u)
            db.session.commit()

        # If value exists in 'ICT_fix' table, then overwrite the existing data.
        else:
            # 'u' = retrieves the existing data via id stored in index 1 of the tuple in 'exist'.
            u = ICT_fix.query.get(exist[0])
            # Overwriting of data in 'u'.
            u.yrs = yrs
            u.ai = float(df_fix.iloc[0, j+1])
            u.ag = float(df_fix.iloc[1, j+1])
            u.bs = float(df_fix.iloc[2, j+1])
            u.bb = float(df_fix.iloc[3, j+1])
            u.bz = float(df_fix.iloc[4, j+1])
            u.bm = float(df_fix.iloc[5, j+1])
            u.vg = float(df_fix.iloc[6, j+1])
            u.ky = float(df_fix.iloc[7, j+1])
            u.dm = float(df_fix.iloc[8, j+1])
            u.gd = float(df_fix.iloc[9, j+1])
            u.gy = float(df_fix.iloc[10, j+1])
            u.ht = float(df_fix.iloc[11, j+1])
            u.jm = float(df_fix.iloc[12, j+1])
            u.ms = float(df_fix.iloc[13, j+1])
            u.kn = float(df_fix.iloc[14, j+1])
            u.lc = float(df_fix.iloc[15, j+1])
            u.vc = float(df_fix.iloc[16, j+1])
            u.sr = float(df_fix.iloc[17, j+1])
            u.tt = float(df_fix.iloc[18, j+1])
            u.tc = float(df_fix.iloc[19, j+1])
            u.updt = updt_fix
            u.stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

            # Commit changes in 'u' to the database.
            db.session.commit()


    # -------------- Remove outdated data from 'ICT_fix' database table -------------- #

    # Checks if the table is empty by looking at the table's first entry.
    # 'exist' returns None is empty.
    exist = ICT_fix.query.get(1)

    # If table is full ...
    if exist != None:
        # Retrieve all data from 'ICT_fix' and store into 'u'.
        u = ICT_fix.query.all()
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



    # ----------------------- Mobile Broadband subscription ---------------------- #

    # Loop over 'df_mob' and 'yrs_mob' and add data to 'ICT_mob' database.
    for j in range(len(yrs_mob)):

        # If 'j' = 0, then store the current time into 'time'.
        # 'time' stores starting time of writing to the database.
        # The time in 'time' is used to compare against the database entry timestamps.
        # This is used to ensure only recent data is stored into the database. 
        if j == 0:
            time = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")


        # Add year of subscription to database
        yrs = yrs_mob[j]

        # 'exist' = Checks is a known value exists in the 'ICT_mob' table.
        # Returns None if the value does not exist.
        # Returns a tuple of ids if the value exist.
        exist = db.session.query(ICT_mob.id).filter_by(yrs=yrs).first()

        # If value does not exist in 'ICT_fix' table, then add the data to the table.
        if exist == None:
            # Add mobile broadband subscriptions for each country to database.
            # Note that the variables are entited by 2 letter country codes.
            u = ICT_mob(
                yrs = yrs,
                ai = float(df_mob.iloc[0, j+1]),
                ag = float(df_mob.iloc[1, j+1]),
                bs = float(df_mob.iloc[2, j+1]),
                bb = float(df_mob.iloc[3, j+1]),
                bz = float(df_mob.iloc[4, j+1]),
                bm = float(df_mob.iloc[5, j+1]),
                vg = float(df_mob.iloc[6, j+1]),
                ky = float(df_mob.iloc[7, j+1]),
                dm = float(df_mob.iloc[8, j+1]),
                gd = float(df_mob.iloc[9, j+1]),
                gy = float(df_mob.iloc[10, j+1]),
                ht = float(df_mob.iloc[11, j+1]),
                jm = float(df_mob.iloc[12, j+1]),
                ms = float(df_mob.iloc[13, j+1]),
                kn = float(df_mob.iloc[14, j+1]),
                lc = float(df_mob.iloc[15, j+1]),
                vc = float(df_mob.iloc[16, j+1]),
                sr = float(df_mob.iloc[17, j+1]),
                tt = float(df_mob.iloc[18, j+1]),
                tc = float(df_mob.iloc[19, j+1]),
                updt = updt_mob,
                stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
            )
            # Add entries to the database, and commit the changes.
            db.session.add(u)
            db.session.commit()

        # If value exists in 'ICT_mob' table, then overwrite the existing data.
        else:
            # 'u' = retrieves the existing data via id stored in index 1 of the tuple in 'exist'.
            u = ICT_mob.query.get(exist[0])
            # Overwriting of data in 'u'.
            u.yrs = yrs
            u.ai = float(df_mob.iloc[0, j+1])
            u.ag = float(df_mob.iloc[1, j+1])
            u.bs = float(df_mob.iloc[2, j+1])
            u.bb = float(df_mob.iloc[3, j+1])
            u.bz = float(df_mob.iloc[4, j+1])
            u.bm = float(df_mob.iloc[5, j+1])
            u.vg = float(df_mob.iloc[6, j+1])
            u.ky = float(df_mob.iloc[7, j+1])
            u.dm = float(df_mob.iloc[8, j+1])
            u.gd = float(df_mob.iloc[9, j+1])
            u.gy = float(df_mob.iloc[10, j+1])
            u.ht = float(df_mob.iloc[11, j+1])
            u.jm = float(df_mob.iloc[12, j+1])
            u.ms = float(df_mob.iloc[13, j+1])
            u.kn = float(df_mob.iloc[14, j+1])
            u.lc = float(df_mob.iloc[15, j+1])
            u.vc = float(df_mob.iloc[16, j+1])
            u.sr = float(df_mob.iloc[17, j+1])
            u.tt = float(df_mob.iloc[18, j+1])
            u.tc = float(df_mob.iloc[19, j+1])
            u.updt = updt_mob
            u.stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

            # Commit changes in 'u' to the database.
            db.session.commit()


    # -------------- Remove outdated data from 'ICT_mob' database table -------------- #

    # Checks if the table is empty by looking at the table's first entry.
    # 'exist' returns None is empty.
    exist = ICT_mob.query.get(1)

    # If table is full ...
    if exist != None:
        # Retrieve all data from 'ICT_mob' and store into 'u'.
        u = ICT_mob.query.all()
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



    # ------------------ Percent of Individuals using the Internet ------------------ #

    # Loop over 'df_per' and 'yrs_per' and add data to 'ICT_per' database.
    for j in range(len(yrs_per)):

        # If 'j' = 0, then store the current time into 'time'.
        # 'time' stores starting time of writing to the database.
        # The time in 'time' is used to compare against the database entry timestamps.
        # This is used to ensure only recent data is stored into the database. 
        if j == 0:
            time = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")


        # Add year of percentages to database
        yrs = yrs_per[j]

        # 'exist' = Checks is a known value exists in the 'ICT_per' table.
        # Returns None if the value does not exist.
        # Returns a tuple of ids if the value exist.
        exist = db.session.query(ICT_per.id).filter_by(yrs=yrs).first()

        # If value does not exist in 'ICT_per' table, then add the data to the table.
        if exist == None:
            # Add percent of internet users for each country to database.
            # Note that the variables are entited by 2 letter country codes.
            u = ICT_per(
                yrs = yrs,
                ai = float(df_per.iloc[0, j+1]),
                ag = float(df_per.iloc[1, j+1]),
                bs = float(df_per.iloc[2, j+1]),
                bb = float(df_per.iloc[3, j+1]),
                bz = float(df_per.iloc[4, j+1]),
                bm = float(df_per.iloc[5, j+1]),
                vg = float(df_per.iloc[6, j+1]),
                ky = float(df_per.iloc[7, j+1]),
                dm = float(df_per.iloc[8, j+1]),
                gd = float(df_per.iloc[9, j+1]),
                gy = float(df_per.iloc[10, j+1]),
                ht = float(df_per.iloc[11, j+1]),
                jm = float(df_per.iloc[12, j+1]),
                ms = float(df_per.iloc[13, j+1]),
                kn = float(df_per.iloc[14, j+1]),
                lc = float(df_per.iloc[15, j+1]),
                vc = float(df_per.iloc[16, j+1]),
                sr = float(df_per.iloc[17, j+1]),
                tt = float(df_per.iloc[18, j+1]),
                tc = float(df_per.iloc[19, j+1]),
                updt = updt_per,
                stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
            )
            # Add entries to the database, and commit the changes.
            db.session.add(u)
            db.session.commit()

        # If value exists in 'ICT_per' table, then overwrite the existing data.
        else:
            # 'u' = retrieves the existing data via id stored in index 1 of the tuple in 'exist'.
            u = ICT_per.query.get(exist[0])
            # Overwriting of data in 'u'.
            u.yrs = yrs
            u.ai = float(df_per.iloc[0, j+1])
            u.ag = float(df_per.iloc[1, j+1])
            u.bs = float(df_per.iloc[2, j+1])
            u.bb = float(df_per.iloc[3, j+1])
            u.bz = float(df_per.iloc[4, j+1])
            u.bm = float(df_per.iloc[5, j+1])
            u.vg = float(df_per.iloc[6, j+1])
            u.ky = float(df_per.iloc[7, j+1])
            u.dm = float(df_per.iloc[8, j+1])
            u.gd = float(df_per.iloc[9, j+1])
            u.gy = float(df_per.iloc[10, j+1])
            u.ht = float(df_per.iloc[11, j+1])
            u.jm = float(df_per.iloc[12, j+1])
            u.ms = float(df_per.iloc[13, j+1])
            u.kn = float(df_per.iloc[14, j+1])
            u.lc = float(df_per.iloc[15, j+1])
            u.vc = float(df_per.iloc[16, j+1])
            u.sr = float(df_per.iloc[17, j+1])
            u.tt = float(df_per.iloc[18, j+1])
            u.tc = float(df_per.iloc[19, j+1])
            u.updt = updt_per
            u.stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

            # Commit changes in 'u' to the database.
            db.session.commit()


    # -------------- Remove outdated data from 'ICT_per' database table -------------- #

    # Checks if the table is empty by looking at the table's first entry.
    # 'exist' returns None is empty.
    exist = ICT_per.query.all()

    # If table is full ...
    if exist != None:
        # Retrieve all data from 'ICT_per' and store into 'u'.
        u = ICT_per.query.all()
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



    # ---------------------- International Bandwidth in Mbps --------------------- #

    # Loop over 'df_bw' and 'yrs_bw' and add data to 'ICT_bw' database.
    for j in range(len(yrs_bw)):

        # If 'j' = 0, then store the current time into 'time'.
        # 'time' stores starting time of writing to the database.
        # The time in 'time' is used to compare against the database entry timestamps.
        # This is used to ensure only recent data is stored into the database. 
        if j == 0:
            time = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")


        # Add year of bandwidths to database
        yrs = yrs_bw[j]

        # 'exist' = Checks is a known value exists in the 'ICT_bw' table.
        # Returns None if the value does not exist.
        # Returns a tuple of ids if the value exist.
        exist = db.session.query(ICT_bw.id).filter_by(yrs=yrs).first()

        # If value does not exist in 'ICT_bw' table, then add the data to the table.
        if exist == None:
            # Add bandwidth usage for each country to database.
            # Note that the variables are entited by 2 letter country codes.
            u = ICT_bw(
                yrs = yrs,
                ai = float(df_bw.iloc[0, j+1]),
                ag = float(df_bw.iloc[1, j+1]),
                bs = float(df_bw.iloc[2, j+1]),
                bb = float(df_bw.iloc[3, j+1]),
                bz = float(df_bw.iloc[4, j+1]),
                bm = float(df_bw.iloc[5, j+1]),
                vg = float(df_bw.iloc[6, j+1]),
                ky = float(df_bw.iloc[7, j+1]),
                dm = float(df_bw.iloc[8, j+1]),
                gd = float(df_bw.iloc[9, j+1]),
                gy = float(df_bw.iloc[10, j+1]),
                ht = float(df_bw.iloc[11, j+1]),
                jm = float(df_bw.iloc[12, j+1]),
                ms = float(df_bw.iloc[13, j+1]),
                kn = float(df_bw.iloc[14, j+1]),
                lc = float(df_bw.iloc[15, j+1]),
                vc = float(df_bw.iloc[16, j+1]),
                sr = float(df_bw.iloc[17, j+1]),
                tt = float(df_bw.iloc[18, j+1]),
                tc = float(df_bw.iloc[19, j+1]),
                updt = updt_bw,
                stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
            )
            # Add entries to the database, and commit the changes.
            db.session.add(u)
            db.session.commit()


        # If value exists in 'ICT_bw' table, then overwrite the existing data.
        else:
            # 'u' = retrieves the existing data via id stored in index 1 of the tuple in 'exist'.
            u = ICT_bw.query.get(exist[0])
            # Overwriting of data in 'u'.
            u.yrs = yrs
            u.ai = float(df_bw.iloc[0, j+1])
            u.ag = float(df_bw.iloc[1, j+1])
            u.bs = float(df_bw.iloc[2, j+1])
            u.bb = float(df_bw.iloc[3, j+1])
            u.bz = float(df_bw.iloc[4, j+1])
            u.bm = float(df_bw.iloc[5, j+1])
            u.vg = float(df_bw.iloc[6, j+1])
            u.ky = float(df_bw.iloc[7, j+1])
            u.dm = float(df_bw.iloc[8, j+1])
            u.gd = float(df_bw.iloc[9, j+1])
            u.gy = float(df_bw.iloc[10, j+1])
            u.ht = float(df_bw.iloc[11, j+1])
            u.jm = float(df_bw.iloc[12, j+1])
            u.ms = float(df_bw.iloc[13, j+1])
            u.kn = float(df_bw.iloc[14, j+1])
            u.lc = float(df_bw.iloc[15, j+1])
            u.vc = float(df_bw.iloc[16, j+1])
            u.sr = float(df_bw.iloc[17, j+1])
            u.tt = float(df_bw.iloc[18, j+1])
            u.tc = float(df_bw.iloc[19, j+1])
            u.updt = updt_bw
            u.stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

            # Commit changes in 'u' to the database.
            db.session.commit()


    # -------------- Remove outdated data from 'ICT_bw' database table -------------- #

    # Checks if the table is empty by looking at the table's first entry.
    # 'exist' returns None is empty.
    exist = ICT_bw.query.all()

    # If table is full ...
    if exist != None:
        # Retrieve all data from 'ICT_bw' and store into 'u'.
        u = ICT_bw.query.all()
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