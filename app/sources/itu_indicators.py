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
from app.models import Itu_indicator
from datetime import datetime, timezone, timedelta

def itu_indicators():
    '''
    Reads, filters, and extracts indicators data from ITU's workbooks.
    Finallys, stores extracted data to a database.
    '''
    # ---------------------------------------------------------------------------- #
    #                             ITU Indicators Source                            #
    # ---------------------------------------------------------------------------- #

    source = "https://www.itu.int/en/ITU-D/Statistics/Pages/stat/default.aspx"

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

        # # Opens 'url_mob' to retrieve last modified date to 'updt_mob'.
        # with urlopen(url_mob) as f:
        #     updt_mob = dict(f.getheaders())['Last-Modified']
        #     updt_mob = updt_mob[5:16]
        #     # dict(f.getheaders()) gives all headers.
            
    except Exception as e:
        error = "Source: " + url_mob + "\nError: " + str(e)
        return error

    try:
        df_per = pd.read_excel(url_per)

        # # Opens 'url_per' to retrieve last modified date to 'updt_per'.
        # with urlopen(url_per) as f:
        #     updt_per = dict(f.getheaders())['Last-Modified']
        #     updt_per = updt_per[5:16]
        #     # dict(f.getheaders()) gives all headers.

    except Exception as e:
        error = "Source: " + url_per + "\nError: " + str(e)
        return error

    try:
        df_bw = pd.read_excel(url_bw)

        # # Opens 'url_bw' to retrieve last modified date to 'updt_bw'.
        # with urlopen(url_bw) as f:
        #     updt_bw = dict(f.getheaders())['Last-Modified']
        #     updt_bw = updt_bw[5:16]
        #     # dict(f.getheaders()) gives all headers.

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

        yrs = list(set(yrs_fix + yrs_mob + yrs_per + yrs_bw))
        

    except Exception as e:
        error = "Error extracting Indicators Data.\nError: " + str(e)
        return error


    time = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
    
    for j in range(len(yrs)):
        yr = str(yrs[j])

        for k in range(20):
            fix = df_fix.iloc[k][yr] if yr in df_fix.columns else float('nan')
            mob = df_mob.iloc[k][yr] if yr in df_mob.columns else float('nan')
            per = df_per.iloc[k][yr] if yr in df_per.columns else float('nan')
            bw = df_bw.iloc[k][yr] if yr in df_bw.columns else float('nan')

            u = Itu_indicator(
                date = yrs[j],
                country = df_fix.iloc[k]['Country'],
                fix = fix,
                mob = mob,
                per = per,
                bw = bw,
                updated = updt_fix,
                source = source,
                stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
            )
            # Add entries to the database, and commit the changes.
            db.session.add(u)
            db.session.commit()

    # Remove outdated database entries.
    remove_outdated(Itu_indicator, time)


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