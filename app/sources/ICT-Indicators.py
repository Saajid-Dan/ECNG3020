'''
Name: Saajid Dan
Course: ECNG 3020
Project Title:
'''

# ---------------------------------------------------------------------------- #
#                                    Imports                                   #
# ---------------------------------------------------------------------------- #

import pandas as pd
from bs4 import BeautifulSoup
import requests

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
    df_fix = pd.read_excel(url_fix)
    df_mob = pd.read_excel(url_mob)
    df_per = pd.read_excel(url_per)
    df_bw = pd.read_excel(url_bw)


    # ---------------------------------------------------------------------------- #
    #                            Filter and Extract Data                           #
    # ---------------------------------------------------------------------------- #

    # 'ctry' = List of Caribbean countries to filtering data.
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


    # ---------------------------------------------------------------------------- #
    #                               Store to Database                              #
    # ---------------------------------------------------------------------------- #

    # ----------------------- Fixed Broadband subscriptions ---------------------- #

    # Loop over 'df_fix' and 'yrs_fix' and add data to database.
    for j in range(len(yrs_fix)):
        # Add year of subscription to 'ICT_fix' database
        yrs = yrs_fix[j]

        # Add fixed broadband subscriptions for each country to database.
        # Note that the variables are entited by 2 letter country codes.
        ai = float(df_fix.iloc[0, j+1])
        ag = float(df_fix.iloc[1, j+1])
        bs = float(df_fix.iloc[2, j+1])
        bb = float(df_fix.iloc[3, j+1])
        bz = float(df_fix.iloc[4, j+1])
        bm = float(df_fix.iloc[5, j+1])
        vg = float(df_fix.iloc[6, j+1])
        ky = float(df_fix.iloc[7, j+1])
        dm = float(df_fix.iloc[8, j+1])
        gd = float(df_fix.iloc[9, j+1])
        gy = float(df_fix.iloc[10, j+1])
        ht = float(df_fix.iloc[11, j+1])
        jm = float(df_fix.iloc[12, j+1])
        ms = float(df_fix.iloc[13, j+1])
        kn = float(df_fix.iloc[14, j+1])
        lc = float(df_fix.iloc[15, j+1])
        vc = float(df_fix.iloc[16, j+1])
        sr = float(df_fix.iloc[17, j+1])
        tt = float(df_fix.iloc[18, j+1])
        tc = float(df_fix.iloc[19, j+1])


    # ----------------------- Mobile Broadband subscription ---------------------- #

    # Loop over 'df_mob' and 'yrs_mob' and add data to 'ICT_mob' database.
    for j in range(len(yrs_mob)):
        # Add year of subscription to database
        yrs = yrs_mob[j]

        # Add mobile broadband subscriptions for each country to database.
        # Note that the variables are entited by 2 letter country codes.
        ai = float(df_mob.iloc[0, j+1])
        ag = float(df_mob.iloc[1, j+1])
        bs = float(df_mob.iloc[2, j+1])
        bb = float(df_mob.iloc[3, j+1])
        bz = float(df_mob.iloc[4, j+1])
        bm = float(df_mob.iloc[5, j+1])
        vg = float(df_mob.iloc[6, j+1])
        ky = float(df_mob.iloc[7, j+1])
        dm = float(df_mob.iloc[8, j+1])
        gd = float(df_mob.iloc[9, j+1])
        gy = float(df_mob.iloc[10, j+1])
        ht = float(df_mob.iloc[11, j+1])
        jm = float(df_mob.iloc[12, j+1])
        ms = float(df_mob.iloc[13, j+1])
        kn = float(df_mob.iloc[14, j+1])
        lc = float(df_mob.iloc[15, j+1])
        vc = float(df_mob.iloc[16, j+1])
        sr = float(df_mob.iloc[17, j+1])
        tt = float(df_mob.iloc[18, j+1])
        tc = float(df_mob.iloc[19, j+1])


    # ------------------ Percent of Individuals using the Internet ------------------ #

    # Loop over 'df_per' and 'yrs_per' and add data to 'ICT_per' database.
    for j in range(len(yrs_per)):
        # Add year of percentages to database
        yrs = yrs_per[j]

        # Add percent of internet users for each country to database.
        # Note that the variables are entited by 2 letter country codes.
        ai = float(df_per.iloc[0, j+1])
        ag = float(df_per.iloc[1, j+1])
        bs = float(df_per.iloc[2, j+1])
        bb = float(df_per.iloc[3, j+1])
        bz = float(df_per.iloc[4, j+1])
        bm = float(df_per.iloc[5, j+1])
        vg = float(df_per.iloc[6, j+1])
        ky = float(df_per.iloc[7, j+1])
        dm = float(df_per.iloc[8, j+1])
        gd = float(df_per.iloc[9, j+1])
        gy = float(df_per.iloc[10, j+1])
        ht = float(df_per.iloc[11, j+1])
        jm = float(df_per.iloc[12, j+1])
        ms = float(df_per.iloc[13, j+1])
        kn = float(df_per.iloc[14, j+1])
        lc = float(df_per.iloc[15, j+1])
        vc = float(df_per.iloc[16, j+1])
        sr = float(df_per.iloc[17, j+1])
        tt = float(df_per.iloc[18, j+1])
        tc = float(df_per.iloc[19, j+1])


    # ---------------------- International Bandwidth in Mbps --------------------- #

    # Loop over 'df_bw' and 'yrs_bw' and add data to 'ICT_bw' database.
    for j in range(len(yrs_bw)):
        # Add year of bandwidths to database
        yrs = yrs_bw[j]

        # Add bandwidth usage for each country to database.
        # Note that the variables are entited by 2 letter country codes.
        ai = float(df_bw.iloc[0, j+1])
        ag = float(df_bw.iloc[1, j+1])
        bs = float(df_bw.iloc[2, j+1])
        bb = float(df_bw.iloc[3, j+1])
        bz = float(df_bw.iloc[4, j+1])
        bm = float(df_bw.iloc[5, j+1])
        vg = float(df_bw.iloc[6, j+1])
        ky = float(df_bw.iloc[7, j+1])
        dm = float(df_bw.iloc[8, j+1])
        gd = float(df_bw.iloc[9, j+1])
        gy = float(df_bw.iloc[10, j+1])
        ht = float(df_bw.iloc[11, j+1])
        jm = float(df_bw.iloc[12, j+1])
        ms = float(df_bw.iloc[13, j+1])
        kn = float(df_bw.iloc[14, j+1])
        lc = float(df_bw.iloc[15, j+1])
        vc = float(df_bw.iloc[16, j+1])
        sr = float(df_bw.iloc[17, j+1])
        tt = float(df_bw.iloc[18, j+1])
        tc = float(df_bw.iloc[19, j+1])