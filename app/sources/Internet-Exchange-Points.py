'''
Name: Saajid Dan
Course: ECNG 3020
Project Title:
'''

# ---------------------------------------------------------------------------- #
#                                    Imports                                   #
# ---------------------------------------------------------------------------- #
import pandas as pd
import math


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

    # 'df_dir' = Contains PCH's IXP directory
    df_dir = pd.read_json("https://www.pch.net/api/ixp/directory/Active")


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
        'Saint Vincent and Grenadines', # *
        'Suriname',                     # *
        'Trinidad and Tobago',
        'Turks'                         # *
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
        json_sub = pd.read_json( url_sub +  str(j) )
        json_mem = pd.read_json( url_mem +  str(j) )

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

        # Append subnets to 'df_sub'.
        df_sub = df_sub.append(json_sub)

    # Remove columns with 'id', 'traffic_graph_url', or 'subnet_num' from 'df_sub'.
    df_sub = df_sub[df_sub.columns.drop(list(df_sub.filter(regex='id')))]
    df_sub = df_sub[df_sub.columns.drop(list(df_sub.filter(regex='traffic_graph_url')))]
    df_sub = df_sub[df_sub.columns.drop(list(df_sub.filter(regex='subnet_num')))]


    # ---------------------------------------------------------------------------- #
    #                              Storing to Database                             #
    # ---------------------------------------------------------------------------- #
    
    # ------------------------------- IXP Directory ------------------------------ #

    df_dir.to_excel('./app/other/spreadsheets/ixp_dir.xlsx', index=None)
    df_sub.to_excel('./app/other/spreadsheets/ixp_sub.xlsx', index=None)
    # df_mem.to_excel('./app/other/spreadsheets/ixp_mem.xlsx', index=None)

    # Loop over 'df_dir' and add data to 'ixp_dir' database table
    for j in range(len(df_dir)):
        ctry = df_dir.iloc[j]['ctry']
        cit = df_dir.iloc[j]['cit']
        name = df_dir.iloc[j]['name']
        url = df_dir.iloc[j]['url']
        stat = df_dir.iloc[j]['stat']
        date = df_dir.iloc[j]['date']
        prfs = df_dir.iloc[j]['prfs']
        lat = df_dir.iloc[j]['lat']
        lon = df_dir.iloc[j]['lon']
        prts = df_dir.iloc[j]['prts']
        ipv4_avg = df_dir.iloc[j]['avg']
        ipv4_pk = df_dir.iloc[j]['trgh']
        ipv6_avg = df_dir.iloc[j]['ipv6_avg']
        updt = df_dir.iloc[j]['updt']

        # Add 'ctry' to database
        # Add 'cit' to database
        # Add 'name' to database
        # Add 'url' to database
        # Add 'stat' to database
        # Add 'date' to database
        # Add 'prfs' to database
        # Add 'lat' to database
        # Add 'lon' to database
        # Add 'prts' to database
        # Add 'ipv4_avg' to database
        # Add 'ipv4_pk' to database
        # Add 'ipv6_avg' to database


    # -------------------------------- IXP Subnets ------------------------------- #

    # Loop over 'df_sub' and add data to 'ixp_sub' database table
    for j in range(len(df_sub)):
        ctry = df_sub.iloc[j]['ctry']
        stat = df_sub.iloc[j]['status']
        name = df_sub.iloc[j]['short_name']
        ver = df_sub.iloc[j]['version']
        sub = df_sub.iloc[j]['subnet']
        mlpa = df_sub.iloc[j]['mlpa']
        traf = df_sub.iloc[j]['traffic']
        prts = df_sub.iloc[j]['participants']
        est = df_sub.iloc[j]['established']
        url_traf = df_sub.iloc[j]['traffic_url']

        # Add 'ctry' to database
        # Add 'stat' to database
        # Add 'name' to database
        # Add 'ver' to database
        # Add 'sub' to database
        # Add 'mlpa' to database
        # Add 'traf' to database
        # Add 'prts' to database
        # Add 'est' to database
        # Add 'url_traf' to database


    # ------------------------- IXP Subnet Member Details ------------------------ #

    df_exp = pd.DataFrame(columns=['ctry', 'ip', 'fqdn', 'ping', 'asn', 'org', 'peering_policy', 'prefixes', 'IPv4', 'IPv6'])
    # Loop over 'df_mem' and add data to 'ixp_mem' database table
    for j in range(len(df_mem)):
        # 'v4' = IPv4 data.
        # 'v6' = IPv6 data.
        v4 = df_mem.iloc[j]['IPv4']
        v6 = df_mem.iloc[j]['IPv6']

        # Checks if IPv4 data is not a NaN
        if type(v4) != float:
            for v in v4.values():
                # Add data to database
                ctry = df_mem.iloc[j]['ctry']
                ip = v['ip']
                ping = v['ping']
                asn = v['asn']
                org = v['org']
                prfs = v['prefixes']
                ipv4 = True
                ipv6 = False

                row = [ctry, ip, ping, asn, org, prfs, ipv4, ipv6]
                df_exp = df_exp.append(pd.Series(row, index=['ctry', 'ip', 'ping', 'asn', 'org', 'prefixes', 'IPv4', 'IPv6']), ignore_index=True)

        # Checks if IPv6 data is not a NaN
        elif type(v6) != float:
            for v in v6.values():
                # add data to database
                ctry = df_mem.iloc[j]['ctry']
                ip = v['ip']
                ping = v['ping']
                asn = v['asn']
                org = v['org']
                prfs = v['prefixes']
                ipv4 = False
                ipv6 = True

                row = [ctry, ip, ping, asn, org, prfs, ipv4, ipv6]
                df_exp = df_exp.append(pd.Series(row, index=['ctry', 'ip', 'ping', 'asn', 'org', 'prefixes', 'IPv4', 'IPv6']), ignore_index=True)

    df_exp.to_excel('./app/other/spreadsheets/ixp_mem.xlsx', index=None)