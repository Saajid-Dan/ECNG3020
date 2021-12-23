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

            # Append subnets to 'df_sub'.
            df_sub = df_sub.append(json_sub)
        except Exception as e:
            error = "Error extracting Subnet and Subnet Member data.\nError: " + str(e)
            return error

    # Remove columns with 'id', 'traffic_graph_url', or 'subnet_num' from 'df_sub'.
    df_sub = df_sub[df_sub.columns.drop(list(df_sub.filter(regex='id')))]
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
                    ipv4 = "Yes"
                    ipv6 = "No"

                    # 'row' = stores values from key:value pairs into a list to be added to 'df_det'.
                    row = [ctry, ip, fqdn, ping, asn, org, peer, prfs, ipv4, ipv6]
                    
                    # Add 'row' data to 'df_det'.
                    df_det = df_det.append(pd.Series(row, index=['ctry', 'ip', 'fqdn', 'ping', 'asn', 'org', 'peer', 'prfs', 'ipv4', 'ipv6']), ignore_index=True)
    except Exception as e:
        error = 'Error Cleaning Subnet Member Data\nError: ' + str(e)
        return error


    # ---------------------------------------------------------------------------- #
    #                              Store to Database                               #
    # ---------------------------------------------------------------------------- #
    
    # ------------------------------- IXP Directory ------------------------------ #

    # Loop over 'df_dir' and add data to 'ixp_dir' database table
    for j in range(len(df_dir)):
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


    # -------------------------------- IXP Subnets ------------------------------- #

    # Loop over 'df_sub' and add data to 'ixp_sub' database table
    for j in range(len(df_sub)):
        ctry = str(df_sub.iloc[j]['ctry'])
        stat = str(df_sub.iloc[j]['status'])
        name = str(df_sub.iloc[j]['short_name'])
        ver = str(df_sub.iloc[j]['version'])
        sub = str(df_sub.iloc[j]['subnet'])
        mlpa = str(df_sub.iloc[j]['mlpa'])
        traf = str(df_sub.iloc[j]['traffic'])
        prts = str(df_sub.iloc[j]['participants'])
        est = str(df_sub.iloc[j]['established'])
        url_traf = str(df_sub.iloc[j]['traffic_url'])

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

    # Loop over 'df_det' and add data to 'ixp_mem' database table
    for j in range(len(df_det)):
        ctry = str(df_det.iloc[j]['ctry'])
        ip = str(df_det.iloc[j]['ip'])
        fqdn = str(df_det.iloc[j]['fqdn'])
        ping = str(df_det.iloc[j]['ping'])
        asn = str(df_det.iloc[j]['asn'])
        org = str(df_det.iloc[j]['org'])
        peer = str(df_det.iloc[j]['peer'])
        prfs = str(df_det.iloc[j]['prfs'])
        ipv4 = str(df_det.iloc[j]['ipv4'])
        ipv6 = str(df_det.iloc[j]['ipv6'])

        # Add 'ctry' to database
        # Add 'ip' to database
        # Add 'fqdn' to database
        # Add 'ping' to database
        # Add 'asn' to database
        # Add 'org' to database
        # Add 'peer' to database
        # Add 'prfs' to database
        # Add 'ipv4' to database
        # Add 'ipv6' to database