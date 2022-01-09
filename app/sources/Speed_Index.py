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
from app.models import Mob_br, Fixed_br
from datetime import datetime, timezone, timedelta

def speedindex():
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


    # Export data in 'df_mob', and 'df_fix' to CSV formats.
    df_mob.to_csv(r'./app/static/csv/mobile_speed_index.csv', encoding='utf-8', header=True, index=False)
    df_fix.to_csv(r'./app/static/csv/fixed_speed_index.csv', encoding='utf-8', header=True, index=False)

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
            mnth = str(j.iloc[k]['Month']).split()[0]   # YYYY-MM-DD
            ctry = j.iloc[k]['Country']
            uni = ctry + '-' + str(j) + '-' + str(k)
            dls = j.iloc[k]['Download Mbps']            # Unit- Mbps
            ups = j.iloc[k]['Upload Mbps']              # Unit- Mbps
            ltcy = j.iloc[k]['Latency ms']              # Unit- ms
            jitt = j.iloc[k]['Jitter']                  # Unit- ms


            # -------------------- Store data to 'Mob_br' database table ------------------- #
            
            # 'exist' = Checks is a known value exists in the 'Mob_br' table.
            # Returns None if the value does not exist.
            # Returns a tuple of ids if the value exist.
            exist = db.session.query(Mob_br.id).filter_by(uni=uni).first()

            # If value does not exist in 'Mob_br' table, then add the data to the table.
            if exist == None:
                u = Mob_br(
                    uni = uni,
                    ctry = ctry,
                    mnth = mnth,
                    dls = dls,
                    ups = ups, 
                    ltcy = ltcy, 
                    jitt = jitt, 
                    stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
                )
                # Add entries to the database, and commit the changes.
                db.session.add(u)
                db.session.commit()
            
            # If value exists in 'Mob_br' table, then overwrite the existing data.
            else:
                # 'u' = retrieves the existing data via id stored in index 1 of the tuple in 'exist'.
                u = Mob_br.query.get(exist[0])
                # Overwriting of data in 'u'.
                u.uni = uni
                u.ctry = ctry
                u.mnth = mnth
                u.dls = dls
                u.ups = ups
                u.ltcy = ltcy
                u.jitt = jitt
                u.stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

                # Commit changes in 'u' to the database.
                db.session.commit()
    

    # -------------- Remove outdated data from 'Mob_br' database table -------------- #

    # Checks if the table is empty by looking at the table's first entry.
    # 'exist' returns None is empty.
    exist = Mob_br.query.get(1)

    # If table is full ...
    if exist != None:
        # Retrieve all data from 'Mob_br' and store into 'u'.
        u = Mob_br.query.all()
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

    

    # ------------------------------ Fixed Broadband ----------------------------- #

    # Loops over dataframes in 'fix_' and stores data into the 'fixed_br' database table
    for j in fix_:
        for k in range(len(j)):
            mnth = str(j.iloc[k]['Month']).split()[0]   # YYYY-MM-DD
            ctry = j.iloc[k]['Country']
            uni = ctry + '-' + str(j) + '-' + str(k)
            dls = j.iloc[k]['Download Mbps']            # Unit- Mbps
            ups = j.iloc[k]['Upload Mbps']              # Unit- Mbps
            ltcy = j.iloc[k]['Latency ms']              # Unit- ms
            jitt = j.iloc[k]['Jitter']                  # Unit- ms

            # -------------------- Store data to 'Fixed_br' database table ------------------- #
            
            # 'exist' = Checks is a known value exists in the 'Fixed_br' table.
            # Returns None if the value does not exist.
            # Returns a tuple of ids if the value exist.
            exist = db.session.query(Fixed_br.id).filter_by(uni=uni).first()

            # If value does not exist in 'Fixed_br' table, then add the data to the table.
            if exist == None:
                u = Fixed_br(
                    uni = uni,
                    ctry = ctry,
                    mnth = mnth,
                    dls = dls,
                    ups = ups, 
                    ltcy = ltcy, 
                    jitt = jitt, 
                    stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
                )
                # Add entries to the database, and commit the changes.
                db.session.add(u)
                db.session.commit()
            
            # If value exists in 'Fixed_br' table, then overwrite the existing data.
            else:
                # 'u' = retrieves the existing data via id stored in index 1 of the tuple in 'exist'.
                u = Fixed_br.query.get(exist[0])
                # Overwriting of data in 'u'.
                u.uni = uni
                u.ctry = ctry
                u.mnth = mnth
                u.dls = dls
                u.ups = ups
                u.ltcy = ltcy
                u.jitt = jitt
                u.stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

                # Commit changes in 'u' to the database.
                db.session.commit()
    

    # -------------- Remove outdated data from 'Fixed_br' database table -------------- #

    # Checks if the table is empty by looking at the table's first entry.
    # 'exist' returns None is empty.
    exist = Fixed_br.query.all()

    # If table is full ...
    if exist != None:
        # Retrieve all data from 'Fixed_br' and store into 'u'.
        u = Fixed_br.query.all()
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