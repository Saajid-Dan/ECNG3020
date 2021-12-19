'''
Name: Saajid Dan
Course: ECNG 3020
Project Title:
'''

# ---------------------------------------------------------------------------- #
#                                    Imports                                   #
# ---------------------------------------------------------------------------- #

import pandas as pd

def speedindex():
    '''
    Reading speed index data from a spreadsheet provided by OOKLA.
    Fixed and Mobile broadband data is filtered, extracted and stored into a database.
    '''
    # ---------------------------------------------------------------------------- #
    #                                OOKLA's Dataset                               #
    # ---------------------------------------------------------------------------- #

    # 'file' = Excel worksheet with OOKLA's Speed Index data.
    file = "./app/other/spreadsheets/OOKLA-Speedtest-Index.xlsx"


    # ---------------------------------------------------------------------------- #
    #                                 Read Dataset                                 #
    # ---------------------------------------------------------------------------- #

    # Read sheet 1 of 'file' into 'df_mob' dataframe.
    # Read shhet 2 of 'file' into 'df_fix' dataframe.
    # 'df_mob' = Data for fixed broadband.
    # 'df_fix' = Data for mobile broadband.
    df_mob = pd.read_excel(file, sheet_name=0)
    df_fix = pd.read_excel(file, sheet_name=1)


    # ---------------------------------------------------------------------------- #
    #                            Filter and Extract Data                           #
    # ---------------------------------------------------------------------------- #

    # Remove Columns from 'df_mob' with 'Platform', 'Metric', or 'Rank'.
    df_mob = df_mob[ df_mob.columns.drop(list(df_mob.filter(regex='Platform'))) ]
    df_mob = df_mob[ df_mob.columns.drop(list(df_mob.filter(regex='Metric'))) ]
    df_mob = df_mob[ df_mob.columns.drop(list(df_mob.filter(regex='Rank'))) ]

    # Remove Columns from 'df_fix' with 'Platform', 'Metric', or 'Rank'.
    df_fix = df_fix[ df_fix.columns.drop(list(df_fix.filter(regex='Platform'))) ]
    df_fix = df_fix[ df_fix.columns.drop(list(df_fix.filter(regex='Metric'))) ]
    df_fix = df_fix[ df_fix.columns.drop(list(df_fix.filter(regex='Rank'))) ]

    # Sort 'df_fix' and 'df_mob' entries by 'Country' and then 'Month' in ascending order.
    df_mob = df_mob.sort_values( ["Country", "Month"], ascending = (True, True) )
    df_fix = df_fix.sort_values( ["Country", "Month"], ascending = (True, True) )

    # Filters 'df_mob' for Caribbean countries and appends dataframes to 'mob_' list.
    # Caribbean countries are Haiti, Jamaica, Suriname, and Trinidad and Tobago.
    mob_ = []
    mob_.append(df_mob.loc[ [ any(i) for i in zip(*[df_mob['Country'] == 'Haiti'])] ])
    mob_.append(df_mob.loc[ [ any(i) for i in zip(*[df_mob['Country'] == 'Jamaica'])] ])
    mob_.append(df_mob.loc[ [ any(i) for i in zip(*[df_mob['Country'] == 'Suriname'])] ])
    mob_.append(df_mob.loc[ [ any(i) for i in zip(*[df_mob['Country'] == 'Trinidad and Tobago'])] ])

    # Filters 'df_fix' for Caribbean countries and appends dataframes to 'fix_' list.
    # Caribbean countries are Haiti, Jamaica, Suriname, and Trinidad and Tobago.
    fix_ = []
    fix_.append(df_fix.loc[ [ any(i) for i in zip(*[df_fix['Country'] == 'Haiti'])] ])
    fix_.append(df_fix.loc[ [ any(i) for i in zip(*[df_fix['Country'] == 'Jamaica'])] ])
    fix_.append(df_fix.loc[ [ any(i) for i in zip(*[df_fix['Country'] == 'Suriname'])] ])
    fix_.append(df_fix.loc[ [ any(i) for i in zip(*[df_fix['Country'] == 'Trinidad and Tobago'])] ])


    # ---------------------------------------------------------------------------- #
    #                             Stores into Database                             #
    # ---------------------------------------------------------------------------- #

    # ----------------------------- Mobile Broadband ----------------------------- #

    # Loops over dataframes in 'mob_' and stores data into the 'mob_br' database table
    for j in mob_:
        for k in range(len(j)):
            mnth = str(j.iloc[k]['Month']).split()[0]   # YYYY-MM-DD
            ctry = j.iloc[k]['Country']
            dls = j.iloc[k]['Download Mbps']            # Unit- Mbps
            ups = j.iloc[k]['Upload Mbps']              # Unit- Mbps
            ltcy = j.iloc[k]['Latency ms']              # Unit- ms
            jitt = j.iloc[k]['Jitter']                  # Unit- ms

            # Add 'mnth to database
            # Add 'ctry to database
            # Add 'dls to database
            # Add 'ups to database
            # Add 'ltcy to database
            # Add 'jitt to database


    # ------------------------------ Fixed Broadband ----------------------------- #

    # Loops over dataframes in 'fix_' and stores data into the 'fixed_br' database table
    for j in fix_:
        for k in range(len(j)):
            mnth = str(j.iloc[k]['Month']).split()[0]   # YYYY-MM-DD
            ctry = j.iloc[k]['Country']
            dls = j.iloc[k]['Download Mbps']            # Unit- Mbps
            ups = j.iloc[k]['Upload Mbps']              # Unit- Mbps
            ltcy = j.iloc[k]['Latency ms']              # Unit- ms
            jitt = j.iloc[k]['Jitter']                  # Unit- ms

            # Add 'mnth to database
            # Add 'ctry to database
            # Add 'dls to database
            # Add 'ups to database
            # Add 'ltcy to database
            # Add 'jitt to database