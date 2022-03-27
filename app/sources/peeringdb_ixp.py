from urllib.request import urlopen
import json
import pandas as pd

from app import db
from app.email import email_exception
import traceback
from app.models import Pdb_ixp, Pdb_facility, Pdb_network
from datetime import datetime, timezone, timedelta


# Disable chained assignments warning on pandas.
pd.options.mode.chained_assignment = None 

dict_ctry = {
        'AI':'Anguilla',
        'AG':'Antigua and Barbuda',
        'BS':'Bahamas',
        'BB':'Barbados',
        'BZ':'Belize',
        'BM':'Bermuda',
        'VG':'British Virgin Islands',
        'KY':'Cayman Islands',
        'DM':'Dominica',
        'GD':'Grenada',
        'GY':'Guyana',
        'HT':'Haiti',
        'JM':'Jamaica',
        'MS':'Montserrat',
        'KN':'Saint Kitts and Nevis',
        'LC':'Saint Lucia',
        'VC':'Saint Vincent and the Grenadines',
        'SR':'Suriname',
        'TT':'Trinidad and Tobago',
        'TC':'Turks & Caicos Is.'
    }


def peeringdb_ixp():
    # 'cc' = List of 2 letter Country Codes (ISO2).
    # Used to filter extracted data for these country codes.
    cc = ['AG', 'AI', 'BS', 'BB', 'BZ', 'BM', 'VG', 'KY', 'DM', 'GD', 'GY', 'HT', 'JM', 'MS', 'LC', 'KN', 'VC', 'SR', 'TT', 'TC']


    email_subject = 'peeringdb_ixp.py'


    source = 'https://www.peeringdb.com/'

    url_ix = 'https://www.peeringdb.com/api/ix'

    url_ixlan = 'https://www.peeringdb.com/api/ixlan/' # + {ix_id}

    url_ixpfx = 'https://www.peeringdb.com/api/ixpfx?ixlan_id=' # + {ixlan_id}

    url_org = 'https://www.peeringdb.com/api/org/' # + {ix_id}

    url_ixfac = 'https://www.peeringdb.com/api/ixfac'

    url_fac = 'https://www.peeringdb.com/api/fac'

    url_netfac = 'https://www.peeringdb.com/api/netfac'

    url_net = 'https://www.peeringdb.com/api/net'


    time = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

    try:
        # Open JSON from url.
        response = urlopen(url_ix)
        json_ix = json.loads(response.read())
    except Exception as e:
        email_exception(e, email_subject)
        return
        
    # Read JSON into a dataframe.
    df_ix = pd.json_normalize(json_ix['data'])

    # Filter 'df_ix' for Caribbean country codes in 'cc'.
    df_ix = df_ix.loc[ [ any(i) for i in zip(*[df_ix['country'].str.contains(word) for word in cc])] ]

    # Resetting indices.
    df_ix = df_ix.reset_index(drop=True)

    for j in range(len(df_ix)):
        # Extract org id from dataframe and convert into a string.
        org_id = str(df_ix.iloc[j]['org_id'])

        try:
            # Open JSON from url.
            response = urlopen(url_org + org_id)
            json_org = json.loads(response.read())
        except Exception as e:
            email_exception(e, email_subject)
            return

        # Extract name of organisation.
        org_name = json_org['data'][0]['name']
        
        # Replace org ids to org names.
        df_ix.loc[j, 'org_name'] = org_name

        # Extract ix id from dataframe and convert into a string.
        ix_id = str(df_ix.iloc[j]['id'])

        try:
            # Open JSON from url.
            response = urlopen(url_ixlan + ix_id)
            json_ixlan = json.loads(response.read())
        except Exception as e:
            email_exception(e, email_subject)
            return

        # Extract ixlan id ixlan JSON and convert into a string.
        ixlan_id = str(json_ixlan['data'][0]['id'])

        try:
            # Open JSON from url.
            response = urlopen(url_ixpfx + ixlan_id)
            json_ixpfx = json.loads(response.read())
        except Exception as e:
            email_exception(e, email_subject)
            return

        ips = ''
        # Loop over indices in ixpfx JSON and extract IPs using ixlan ids.
        for k in json_ixpfx['data']:
            ips += str(k['protocol']) + ': ' + str(k['prefix']) + ', '
            # print(k['protocol'], k['prefix'])
        
        # Replace fac_set df_ix with the ips.
        df_ix.loc[j, 'ips'] = ips

        try:
            # Open JSON from url.
            response = urlopen(url_ixfac + '?ix_id=' + ix_id)
            json_ixfac = json.loads(response.read())
        except Exception as e:
            email_exception(e, email_subject)
            return

        fac_ids = ''
        # Loop over indices in ixpfx JSON and extract IPs using ixlan ids.
        for k in json_ixfac['data']:
            fac_ids += str(k['fac_id']) + ', '
        
        # Replace fac_set df_ix with the fac_ids.
        df_ix.loc[j, 'fac_id'] = fac_ids


    for j in range(len(df_ix)):
        u = Pdb_ixp(
            ix_id = str(df_ix.iloc[j]['id']),
            fac_id = str(df_ix.iloc[j]['fac_id']),
            org_name = str(df_ix.iloc[j]['org_name']),
            name = str(df_ix.iloc[j]['name']),
            name_long = str(df_ix.iloc[j]['name_long']),
            city = str(df_ix.iloc[j]['city']), 
            country = dict_ctry[ str(df_ix.iloc[j]['country']) ],
            media = str(df_ix.iloc[j]['media']),
            prot_unicast = str(df_ix.iloc[j]['proto_unicast']),
            prot_multicast = str(df_ix.iloc[j]['proto_multicast']),
            prot_ipv6 = str(df_ix.iloc[j]['proto_ipv6']),
            url_home = str(df_ix.iloc[j]['website']),
            url_stats = str(df_ix.iloc[j]['url_stats']),
            tech_email = str(df_ix.iloc[j]['tech_email']),
            tech_phone = str(df_ix.iloc[j]['tech_phone']),
            policy_email = str(df_ix.iloc[j]['policy_email']),
            policy_phone = str(df_ix.iloc[j]['policy_phone']),
            sale_phone = str(df_ix.iloc[j]['sales_phone']),
            sale_email = str(df_ix.iloc[j]['sales_email']),
            svc_lvl = str(df_ix.iloc[j]['service_level']),
            terms = str(df_ix.iloc[j]['terms']),
            updated = str(df_ix.iloc[j]['updated']),
            status = str(df_ix.iloc[j]['status']),
            source = source,
            stamp = time
        )
        # Add entries to the database, and commit the changes.
        db.session.add(u)
        db.session.commit()

    # Remove outdated database entries.
    remove_outdated(Pdb_ixp, time)

    try:
        # Open JSON from url.
        response = urlopen(url_fac)
        json_fac = json.loads(response.read())
    except Exception as e:
        email_exception(e, email_subject)
        return

    # Read JSON into a dataframe.
    df_fac = pd.json_normalize(json_fac['data'])

    # Filter 'df_fac' for Caribbean country codes in 'cc'.
    df_fac = df_fac.loc[ [ any(i) for i in zip(*[df_fac['country'].str.contains(word) for word in cc])] ]

    # Resetting indices.
    df_fac = df_fac.reset_index(drop=True)

    # List of unique net ids.
    lst_net = []

    for j in range(len(df_fac)):
        #  Extract fac id from dataframe and convert into a string.
        fac_id = str(df_fac.iloc[j]['id'])
        try:
            # Open JSON from url.
            response = urlopen(url_ixfac + '?fac_id=' + fac_id)
            json_ixfac = json.loads(response.read())
        except Exception as e:
            email_exception(e, email_subject)
            return

        ix_ids = ''
        # Loop over indices in ixpfx JSON and extract IPs using ixlan ids.
        for k in json_ixfac['data']:
            ix_ids += str(k['ix_id']) + ', '
        
        # Replace fac_set df_fac with the ix_ids.
        df_fac.loc[j, 'ix_id'] = ix_ids

        try:
            # Open JSON from url.
            response = urlopen(url_netfac + '?fac_id=' + fac_id)
            json_netfac = json.loads(response.read())
        except Exception as e:
            email_exception(e, email_subject)
            return

        net_ids = ''
        # Loop over indices in ixpfx JSON and extract IPs using ixlan ids.
        for k in json_netfac['data']:
            # If net id not in the list, then append it.
            if k['net_id'] not in lst_net:
                lst_net.append(k['net_id'])

            # Append net ids to net_ids string.
            net_ids += str(k['net_id']) + ', '

        # Replace fac_set df_fac with the net_ids.
        df_fac.loc[j, 'net_id'] = net_ids
        

    for j in range(len(df_fac)):
        lat = df_fac.iloc[j]['latitude']
        # Correction to incorrect lon values.
        lon = df_fac.iloc[j]['longitude']
        if lon > 0:
            lon = lon * -1

        u = Pdb_facility(
            fac_id = str(df_fac.iloc[j]['id']),
            net_id = str(df_fac.iloc[j]['net_id']),
            org_name = str(df_fac.iloc[j]['org_name']),
            name = str(df_fac.iloc[j]['name']),
            name_long = str(df_fac.iloc[j]['name_long']),
            url_home = str(df_fac.iloc[j]['website']),
            sale_email = str(df_fac.iloc[j]['sales_email']),
            sale_phone = str(df_fac.iloc[j]['sales_phone']),
            tech_email = str(df_fac.iloc[j]['tech_email']),
            tech_phone = str(df_fac.iloc[j]['tech_phone']),
            updated = str(df_fac.iloc[j]['updated']),
            status = str(df_fac.iloc[j]['status']),
            address1 = str(df_fac.iloc[j]['address1']),
            address2 = str(df_fac.iloc[j]['address2']),
            city = str(df_fac.iloc[j]['city']),
            country = dict_ctry[ str(df_fac.iloc[j]['country']) ],
            state = str(df_fac.iloc[j]['state']),
            zipcode = str(df_fac.iloc[j]['zipcode']),
            lat = str(lat),
            lon = str(lon),
            source = source,
            stamp = time
        )
        # Add entries to the database, and commit the changes.
        db.session.add(u)
        db.session.commit()

    # Remove outdated database entries.
    remove_outdated(Pdb_facility, time)


    try:
        # Open JSON from url.
        response = urlopen(url_net)
        json_net = json.loads(response.read())
    except Exception as e:
        email_exception(e, email_subject)
        return

    # Read JSON into a dataframe.
    df_net = pd.json_normalize(json_net['data'])

    # Filter 'df_net' for net ids in 'lst_net'.
    df_net = df_net.loc[ [ any(i) for i in zip(*[df_net['id'] == word for word in lst_net])] ]

    # Resetting indices.
    df_net = df_net.reset_index(drop=True)

    for j in range(len(df_net)):
        # Extract org id from dataframe and convert into a string.
        org_id = str(df_net.iloc[j]['org_id'])

        try:
            # Open JSON from url.
            response = urlopen(url_org + org_id)
            json_org = json.loads(response.read())
        except Exception as e:
            email_exception(e, email_subject)
            return

        # Extract name of organisation.
        org_name = json_org['data'][0]['name']
        
        # Replace org ids to org names.
        df_net.loc[j, 'org_name'] = org_name


    for j in range(len(df_net)):
        u = Pdb_network(
            net_id = str(df_net.iloc[j]['id']),
            org_name = str(df_net.iloc[j]['org_name']),
            name = str(df_net.iloc[j]['name']),
            name_long = str(df_net.iloc[j]['name_long']),
            url_home = str(df_net.iloc[j]['website']),
            asn = str(df_net.iloc[j]['asn']),
            look_glass = str(df_net.iloc[j]['looking_glass']),
            route_srv = str(df_net.iloc[j]['route_server']),
            irr_as_set = str(df_net.iloc[j]['irr_as_set']),
            info_type = str(df_net.iloc[j]['info_type']),
            ipv4_prfs = str(df_net.iloc[j]['info_prefixes4']),
            ipv6_prfs = str(df_net.iloc[j]['info_prefixes6']),
            traf_lvl = str(df_net.iloc[j]['info_traffic']),
            traf_ratio = str(df_net.iloc[j]['info_ratio']),
            geo_scope = str(df_net.iloc[j]['info_scope']),
            prot_unicast = str(df_net.iloc[j]['info_unicast']),
            prot_multicast = str(df_net.iloc[j]['info_multicast']),
            prot_ipv6 = str(df_net.iloc[j]['info_ipv6']),
            prot_nvr_by_rt_srv = str(df_net.iloc[j]['info_never_via_route_servers']),
            policy_url = str(df_net.iloc[j]['policy_url']),
            policy_general = str(df_net.iloc[j]['policy_general']),
            policy_locations = str(df_net.iloc[j]['policy_locations']),
            policy_contracts = str(df_net.iloc[j]['policy_contracts']),
            updated = str(df_net.iloc[j]['updated']),
            status = str(df_net.iloc[j]['status']),
            source = source,
            stamp = time
        )
        # Add entries to the database, and commit the changes.
        db.session.add(u)
        db.session.commit()

    # Remove outdated database entries.
    remove_outdated(Pdb_network, time)


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