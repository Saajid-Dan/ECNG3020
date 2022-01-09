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
from app.models import Ixp_dir, Ixp_sub, Ixp_mem
from datetime import datetime, timezone, timedelta


def ixp():
    '''
    Reads, Filters and Extract IXP data from Packet Clearing House.
    Data for IXP directory, subnets and subnet members are stored a database.
    '''
    # ---------------------------------------------------------------------------- #
    #                         Packet Clearing House Source                         #
    # ---------------------------------------------------------------------------- #

    # 'url_dir' = root directory for IXPs.
    # 'url_sub' = root directory for IXP subnets.
    # 'url_mem' = root directory for IXP subnet members.
    url_dir = 'https://www.pch.net/api/ixp/directory/Active'
    url_sub = 'https://www.pch.net/api/ixp/subnets/'
    url_mem = 'https://www.pch.net/api/ixp/subnet_details/'


    # ---------------------------------------------------------------------------- #
    #                                 Read Sources                                 #
    # ---------------------------------------------------------------------------- #

    try:
        # 'df_dir' = Contains PCH's IXP directory
        df_dir = pd.read_json(url_dir)
    except Exception as e:
        error = "Source: " + url_dir + "\nError: " + str(e)
        return error
        

    # ---------------------------------------------------------------------------- #
    #                            Filter and Extract Data                           #
    # ---------------------------------------------------------------------------- #


    # 'ctry' = Contains a list of Caribbean countries for filtering.
    # Note that countries marked with a * are not on PCH's database.
    # Assumed that no IXP data is available.
    ctry = [
        'Anguilla',                     # *
        'Antigua and Barbuda',          # *
        'Bahamas',                      # *
        'Barbados',
        'Belize',
        'Bermuda',                      # *
        'British Virgin Islands',
        'Cayman Islands',               # *
        'Dominica',
        'Grenada',
        'Guyana',                       # *
        'Haiti',
        'Jamaica',
        'Montserrat',                   # *
        'Saint Kitts and Nevis',
        'Saint Lucia',
        'Saint Vincent and the Grenadines', # *
        'Suriname',                     # *
        'Trinidad and Tobago',
        'Turks & Caicos Is.'            # *
    ]

    # Filter 'df_dir' for Caribbean countries in 'ctry'.
    # Not interested in Dominican Republic.
    df_dir = df_dir.loc[ [ any(i) for i in zip(*[df_dir['ctry'].str.contains(word) for word in ctry])] ]
    df_dir = df_dir[df_dir['ctry'] != 'Dominican Republic']

    # Removal of unnecessary columns in 'df_dir'
    df_dir = df_dir[df_dir.columns.drop(list(df_dir.filter(regex='reg')))]
    df_dir = df_dir[df_dir.columns.drop(list(df_dir.filter(regex='pch')))]
    df_dir = df_dir[df_dir.columns.drop(list(df_dir.filter(regex='tc_rank')))]
    df_dir = df_dir[df_dir.columns.drop(list(df_dir.filter(regex='tw_rank')))]
    df_dir = df_dir[df_dir.columns.drop(list(df_dir.filter(regex='pc_rank')))]
    df_dir = df_dir[df_dir.columns.drop(list(df_dir.filter(regex='pr_rank')))]
    df_dir = df_dir[df_dir.columns.drop(list(df_dir.filter(regex='pw_rank')))]
    df_dir = df_dir[df_dir.columns.drop(list(df_dir.filter(regex='tr_rank')))]
    df_dir = df_dir[df_dir.columns.drop(list(df_dir.filter(regex='q9')))]
    df_dir = df_dir[df_dir.columns.drop(list(df_dir.filter(regex='iata')))]
    df_dir = df_dir[df_dir.columns.drop(list(df_dir.filter(regex='regct')))]
    df_dir = df_dir[df_dir.columns.drop(list(df_dir.filter(regex='traf')))]


    # ---------------------------------------------------------------------------- #
    #                       Reading Subnet and Subnet Members                      #
    # ---------------------------------------------------------------------------- #

    # 'df_sub' stores IXP subnets.
    # 'df_mem' stores IXP subnet member details.
    df_sub = pd.DataFrame()
    df_mem = pd.DataFrame()

    # Loops over 'df_dir' to extract IDs in j.
    # These IDs are the subdirectories for 'url_sub' and 'url_mem'.
    for i, j in enumerate(df_dir['id']):
        # 'json_sub' = reads JSON file at directory - 'url_sub' + 'j'.
        # 'json_mem' = reads JSON file at directory - 'url_mem' + 'j'. 
        
        try:
            json_sub = pd.read_json( url_sub + str(j) )
        except Exception as e:
            error = "Source: " + url_sub + str(j) + "\nError: " + str(e)
            return error

        try:
            json_mem = pd.read_json( url_mem + str(j) )
        except Exception as e:
            error = "Source: " + url_mem + str(j) + "\nError: " + str(e)
            return error
        
        try:
            # Checks for errored data in 'json_mem'
            if 'error' not in json_mem:
                # Add columns 'id' and 'ctry' to 'mem' dataframe.
                # Used to link 'json_mem' for reference.
                # json_mem = json_mem.assign(id = j)
                json_mem = json_mem.assign(ctry = df_dir.iloc[i]['ctry'])
                
                # Append subnet member details to 'df_mem'.
                df_mem = df_mem.append(json_mem)

            # Add columns 'ctry' to 'json_sub' dataframe.
            # Used to link 'json_mem' for reference.
            json_sub = json_sub.assign(ctry = df_dir.iloc[i]['ctry'])

            # Add columns 'long_nm' to 'json_sub' dataframe.
            # 'long_nm' corresponds to the full corresponding IXP name from 'df_dir' dataframe.
            # Used to link short IXP name in 'df_sub' to the long name.
            json_sub = json_sub.assign(long_nm = df_dir.iloc[i]['name'])

            # Append subnets to 'df_sub'.
            df_sub = df_sub.append(json_sub)
        except Exception as e:
            error = "Error extracting Subnet and Subnet Member data.\nError: " + str(e)
            return error

    # Remove columns with 'traffic_graph_url', or 'subnet_num' from 'df_sub'.
    df_sub = df_sub[df_sub.columns.drop(list(df_sub.filter(regex='traffic_graph_url')))]
    df_sub = df_sub[df_sub.columns.drop(list(df_sub.filter(regex='subnet_num')))]


    # ------------------------- Cleaning IXP Member Details ------------------------ #

    # 'df_mem' stores data under IPv4 and IPv6 headers as a dictionary of data with same keys.
    # The database cannot store data as a dict object.
    # The values in these dicts must be extracted as strings to create a cleaner table (or dataframe).

    try:
        # 'df_det' = New dataframe with column headers to match the keys in 'df_mem' dict objects.
        df_det = pd.DataFrame(columns=['ctry', 'ip', 'fqdn', 'ping', 'asn', 'org', 'peer', 'prfs', 'ipv4', 'ipv6'])
        
        # Loop over 'df_mem' to extract values from dict key:value pairs and add to 'df_det' dataframe.
        for j in range(len(df_mem)):
            # 'v4' = IPv4 data.
            # 'v6' = IPv6 data.
            v4 = df_mem.iloc[j]['IPv4']
            v6 = df_mem.iloc[j]['IPv6']

            # Checks if IPv4 data is not a NaN
            if type(v4) != float:
                for v in v4.values():
                    ctry = str(df_mem.iloc[j]['ctry'])
                    ip = str(v['ip'])
                    fqdn = str(v['fqdn'])
                    ping = str(v['ping'])
                    asn = str(v['asn'])
                    org = str(v['org'])
                    peer = str(v['peering_policy'])
                    prfs = str(v['prefixes'])
                    ipv4 = "Yes"
                    ipv6 = "No"

                    # 'row' = stores values from key:value pairs into a list to be added to 'df_det'.
                    row = [ctry, ip, fqdn, ping, asn, org, peer, prfs, ipv4, ipv6]
                    
                    # Add 'row' data to 'df_det'.
                    df_det = df_det.append(pd.Series(row, index=['ctry', 'ip', 'fqdn', 'ping', 'asn', 'org', 'peer', 'prfs', 'ipv4', 'ipv6']), ignore_index=True)

            # Checks if IPv6 data is not a NaN
            elif type(v6) != float:
                for v in v6.values():
                    ctry = str(df_mem.iloc[j]['ctry'])
                    ip = str(v['ip'])
                    fqdn = str(v['fqdn'])
                    ping = str(v['ping'])
                    asn = str(v['asn'])
                    org = str(v['org'])
                    peer = str(v['peering_policy'])
                    prfs = str(v['prefixes'])
                    ipv4 = "No"
                    ipv6 = "Yes"

                    # 'row' = stores values from key:value pairs into a list to be added to 'df_det'.
                    row = [ctry, ip, fqdn, ping, asn, org, peer, prfs, ipv4, ipv6]
                    
                    # Add 'row' data to 'df_det'.
                    df_det = df_det.append(pd.Series(row, index=['ctry', 'ip', 'fqdn', 'ping', 'asn', 'org', 'peer', 'prfs', 'ipv4', 'ipv6']), ignore_index=True)
    except Exception as e:
        error = 'Error Cleaning Subnet Member Data\nError: ' + str(e)
        return error


    # ---------------------------------------------------------------------------- #
    #                               Create CSV Files                               #
    # ---------------------------------------------------------------------------- #

    # Export data in 'df_dir', 'df_sub', and 'df_det' to CSV formats.
    df_dir.to_csv(r'./app/static/csv/ixp_dir.csv', encoding='utf-8', header=True, index=False)
    df_sub.to_csv(r'./app/static/csv/ixp_sub.csv', encoding='utf-8', header=True, index=False)
    df_det.to_csv(r'./app/static/csv/ixp_mem.csv', encoding='utf-8', header=True, index=False)


    # ---------------------------------------------------------------------------- #
    #                              Store to Database                               #
    # ---------------------------------------------------------------------------- #
    
    # ------------------------------- IXP Directory ------------------------------ #

    # Loop over 'df_dir' and add data to 'ixp_dir' database table
    for j in range(len(df_dir)):
        uni = str(df_dir.iloc[j]['id'])
        ctry = str(df_dir.iloc[j]['ctry'])
        cit = str(df_dir.iloc[j]['cit'])
        name = str(df_dir.iloc[j]['name'])
        url = str(df_dir.iloc[j]['url'])
        stat = str(df_dir.iloc[j]['stat'])
        date = str(df_dir.iloc[j]['date'])
        prfs = str(df_dir.iloc[j]['prfs'])
        lat = str(df_dir.iloc[j]['lat'])
        lon = str(df_dir.iloc[j]['lon'])
        prts = str(df_dir.iloc[j]['prts'])
        ipv4_avg = str(df_dir.iloc[j]['avg'])
        ipv4_pk = str(df_dir.iloc[j]['trgh'])
        ipv6_avg = str(df_dir.iloc[j]['ipv6_avg'])
        updt = str(df_dir.iloc[j]['updt'])


        # -------------------- Store data to 'Ixp_dir' database table ------------------- #
       
        # If 'j' = 0, then store the current time into 'time'.
        # 'time' stores starting time of writing to the database.
        # The time in 'time' is used to compare against the database entry timestamps.
        # This is used to ensure only recent data is stored into the database. 
        if j == 0:
            time = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
        
        # 'exist' = Checks is a known value exists in the 'Ixp_dir' table.
        # Returns None if the value does not exist.
        # Returns a tuple of ids if the value exist.
        exist = db.session.query(Ixp_dir.id).filter_by(uni=uni).first()

        # If value does not exist in 'Ixp_dir' table, then add the data to the table.
        if exist == None:
            u = Ixp_dir(    
                uni = uni,
                ctry = ctry,
                city = cit,
                name = name,
                url = url,
                stat = stat,
                date = date,
                prfs = prfs, 
                lat = lat, 
                lon = lon, 
                prts = prts,
                ipv4_avg = ipv4_avg,
                ipv4_pk = ipv4_pk,
                ipv6_avg = ipv6_avg,
                updt = updt,
                stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
            )
            # Add entries to the database, and commit the changes.
            db.session.add(u)
            db.session.commit()
        
        # If value exists in 'Ixp_dir' table, then overwrite the existing data.
        else:
            # 'u' = retrieves the existing data via id stored in index 1 of the tuple in 'exist'.
            u = Ixp_dir.query.get(exist[0])
            # Overwriting of data in 'u'.
            u.ctry = ctry
            u.city = cit
            u.name = name
            u.url = url
            u.stat = stat
            u.date = date
            u.prfs = prfs
            u.lat = lat
            u.lon = lon
            u.prts = prts
            u.ipv4_avg = ipv4_avg
            u.ipv4_pk = ipv4_pk
            u.ipv6_avg = ipv6_avg
            u.updt = updt
            u.stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

            # Commit changes in 'u' to the database.
            db.session.commit()
    

    # -------------- Remove outdated data from 'Ixp_dir' database table -------------- #

    # Checks if the table is empty by looking at the table's first entry.
    # 'exist' returns None is empty.
    exist = Ixp_dir.query.get(1)

    # If table is full ...
    if exist != None:
        # Retrieve all data from 'Ixp_dir' and store into 'u'.
        u = Ixp_dir.query.all()
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



    # -------------------------------- IXP Subnets ------------------------------- #

    # Loop over 'df_sub' and add data to 'ixp_sub' database table
    for j in range(len(df_sub)):
        uni = str(df_sub.iloc[j]['id'])
        ctry = str(df_sub.iloc[j]['ctry'])
        stat = str(df_sub.iloc[j]['status'])
        name = str(df_sub.iloc[j]['short_name'])
        name_lng = str(df_sub.iloc[j]['long_nm'])
        ver = str(df_sub.iloc[j]['version'])
        sub = str(df_sub.iloc[j]['subnet'])
        mlpa = str(df_sub.iloc[j]['mlpa'])
        traf = str(df_sub.iloc[j]['traffic'])
        prts = str(df_sub.iloc[j]['participants'])
        est = str(df_sub.iloc[j]['established'])
        url_traf = str(df_sub.iloc[j]['traffic_url'])


        # -------------------- Store data to 'Ixp_sub' database table ------------------- #
       
        # If 'j' = 0, then store the current time into 'time'.
        # 'time' stores starting time of writing to the database.
        # The time in 'time' is used to compare against the database entry timestamps.
        # This is used to ensure only recent data is stored into the database. 
        if j == 0:
            time = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
        
        # 'exist' = Checks is a known value exists in the 'Ixp_sub' table.
        # Returns None if the value does not exist.
        # Returns a tuple of ids if the value exist.
        exist = db.session.query(Ixp_sub.id).filter_by(uni=uni).first()

        # If value does not exist in 'Ixp_sub' table, then add the data to the table.
        if exist == None:
            u = Ixp_sub(
                uni = uni,
                ctry = ctry,
                stat = stat,
                name = name,
                name_lng = name_lng,
                ver = ver, 
                sub = sub, 
                mlpa = mlpa, 
                traf = traf,
                prts = prts,
                est = est,
                url_traf = url_traf,
                stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
            )
            # Add entries to the database, and commit the changes.
            db.session.add(u)
            db.session.commit()
        
        # If value exists in 'Ixp_sub' table, then overwrite the existing data.
        else:
            # 'u' = retrieves the existing data via id stored in index 1 of the tuple in 'exist'.
            u = Ixp_sub.query.get(exist[0])
            # Overwriting of data in 'u'.
            u.ctry = ctry
            u.stat = stat
            u.name = name
            u.name_lng = name_lng
            u.ver = ver
            u.sub = sub
            u.mlpa = mlpa
            u.traf = traf
            u.prts = prts
            u.est = est
            u.url_traf = url_traf
            u.stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

            # Commit changes in 'u' to the database.
            db.session.commit()
    

    # -------------- Remove outdated data from 'Ixp_sub' database table -------------- #

    # Checks if the table is empty by looking at the table's first entry.
    # 'exist' returns None is empty.
    exist = Ixp_sub.query.all()

    # If table is full ...
    if exist != None:
        # Retrieve all data from 'Ixp_sub' and store into 'u'.
        u = Ixp_sub.query.all()
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



    # ------------------------- IXP Subnet Member Details ------------------------ #

    # Loop over 'df_det' and add data to 'ixp_mem' database table
    for j in range(len(df_det)):
        ctry = str(df_det.iloc[j]['ctry'])
        uni = ctry + '-' + str(j)
        ip = str(df_det.iloc[j]['ip'])
        fqdn = str(df_det.iloc[j]['fqdn'])
        ping = str(df_det.iloc[j]['ping'])
        asn = str(df_det.iloc[j]['asn'])
        org = str(df_det.iloc[j]['org'])
        peer = str(df_det.iloc[j]['peer'])
        prfs = str(df_det.iloc[j]['prfs'])
        ipv4 = str(df_det.iloc[j]['ipv4'])
        ipv6 = str(df_det.iloc[j]['ipv6'])

        
        # -------------------- Store data to 'Ixp_mem' database table ------------------- #
       
        # If 'j' = 0, then store the current time into 'time'.
        # 'time' stores starting time of writing to the database.
        # The time in 'time' is used to compare against the database entry timestamps.
        # This is used to ensure only recent data is stored into the database. 
        if j == 0:
            time = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
        
        # 'exist' = Checks is a known value exists in the 'Ixp_mem' table.
        # Returns None if the value does not exist.
        # Returns a tuple of ids if the value exist.
        exist = db.session.query(Ixp_mem.id).filter_by(uni=uni).first()

        # If value does not exist in 'Ixp_mem' table, then add the data to the table.
        if exist == None:
            u = Ixp_mem(
                uni = uni,
                ctry = ctry,
                ip = ip,
                fqdn = fqdn,
                ping = ping, 
                asn = asn, 
                org = org, 
                peer = peer,
                prfs = prfs,
                ipv4 = ipv4,
                ipv6 = ipv6,
                stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
            )
            # Add entries to the database, and commit the changes.
            db.session.add(u)
            db.session.commit()
        
        # If value exists in 'Ixp_mem' table, then overwrite the existing data.
        else:
            # 'u' = retrieves the existing data via id stored in index 1 of the tuple in 'exist'.
            u = Ixp_mem.query.get(exist[0])
            # Overwriting of data in 'u'.
            u.ctry = ctry
            u.ip = ip
            u.fqdn = fqdn
            u.ping = ping
            u.asn = asn
            u.org = org
            u.peer = peer
            u.prfs = prfs
            u.ipv4 = ipv4
            u.ipv6 = ipv6
            u.stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

            # Commit changes in 'u' to the database.
            db.session.commit()
    

    # -------------- Remove outdated data from 'Ixp_mem' database table -------------- #

    # Checks if the table is empty by looking at the table's first entry.
    # 'exist' returns None is empty.
    exist = Ixp_mem.query.get(1)

    # If table is full ...
    if exist != None:
        # Retrieve all data from 'Ixp_mem' and store into 'u'.
        u = Ixp_mem.query.all()
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