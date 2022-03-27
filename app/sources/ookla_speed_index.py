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
from app.models import Ookla_mobile_bband, Ookla_fixed_bband
from datetime import datetime, timezone, timedelta

def ookla_speed_index():
    '''
    Reading speed index data from a spreadsheet provided by OOKLA.
    Fixed and Mobile broadband data is filtered, extracted and stored into a database.
    '''
    # ---------------------------------------------------------------------------- #
    #                                OOKLA's Dataset                               #
    # ---------------------------------------------------------------------------- #

    # 'file' = Excel worksheet with OOKLA's Speed Index data.
    file = "./app/static/spreadsheets/OOKLA-Speedtest-Index.xlsx"


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

    # ----------------------- Timestamping Check Condition ----------------------- #

    # 'time' stores starting time of writing to the database.
    # The time in 'time' is used to compare against the database entry timestamps.
    # This is used to ensure only recent data is stored into the database. 
    time = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")


    # ----------------------------- Mobile Broadband ----------------------------- #

    # Loops over dataframes in 'mob_' and stores data into the 'Mob_br' database table
    for j in mob_:
        for k in range(len(j)):
            date = str(j.iloc[k]['Month']).split()[0]   # YYYY-MM-DD
            ctry = j.iloc[k]['Country']
            uni = ctry + '-' + str(j) + '-' + str(k)
            dls = j.iloc[k]['Download Mbps']            # Unit- Mbps
            ups = j.iloc[k]['Upload Mbps']              # Unit- Mbps
            ltcy = j.iloc[k]['Latency ms']              # Unit- ms
            jitt = j.iloc[k]['Jitter']                  # Unit- ms


            # -------------------- Store data to 'Mob_br' database table ------------------- #
            
            u = Ookla_mobile_bband(
                country = ctry,
                date = date,
                dl_spd = dls,
                up_spd = ups, 
                ltcy = ltcy, 
                jitt = jitt, 
                stamp = time
            )

            # Add entries to the database, and commit the changes.
            db.session.add(u)
            db.session.commit()

    # Remove outdated database entries.
    remove_outdated(Ookla_mobile_bband, time)


    # ------------------------------ Fixed Broadband ----------------------------- #

    # Loops over dataframes in 'fix_' and stores data into the 'fixed_br' database table
    for j in fix_:
        for k in range(len(j)):
            date = str(j.iloc[k]['Month']).split()[0]   # YYYY-MM-DD
            ctry = j.iloc[k]['Country']
            uni = ctry + '-' + str(j) + '-' + str(k)
            dls = j.iloc[k]['Download Mbps']            # Unit- Mbps
            ups = j.iloc[k]['Upload Mbps']              # Unit- Mbps
            ltcy = j.iloc[k]['Latency ms']              # Unit- ms
            jitt = j.iloc[k]['Jitter']                  # Unit- ms

            # -------------------- Store data to 'Fixed_br' database table ------------------- #

            u = Ookla_fixed_bband(
                country = ctry,
                date = date,
                dl_spd = dls,
                up_spd = ups, 
                ltcy = ltcy, 
                jitt = jitt, 
                stamp = time
            )

            # Add entries to the database, and commit the changes.
            db.session.add(u)
            db.session.commit()
            
    # Remove outdated database entries.
    remove_outdated(Ookla_fixed_bband, time)


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