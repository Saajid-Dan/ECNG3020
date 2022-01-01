'''
Name: Saajid Dan
Course: ECNG 3020
Project Title:
'''

# ---------------------------------------------------------------------------- #
#                                    Imports                                   #
# ---------------------------------------------------------------------------- #
from bs4 import BeautifulSoup
import requests
from app import db
from app.models import Root_srv
from datetime import datetime, timezone, timedelta


def root():
    '''
    Read, Filter, and Extract Root server data from IANA's archives.
    Finally, store the server data to a database.
    '''
    # ---------------------------------------------------------------------------- #
    #                            IANA Root Server Source                           #
    # ---------------------------------------------------------------------------- #
    
    # Root Server Archives root directory in 'url_root'.
    url_root = 'https://root-servers.org/archives/'


    # ---------------------------------------------------------------------------- #
    #                                  Read Source                                 #
    # ---------------------------------------------------------------------------- #

    try:
        # Read HTML to 'html_root' from URL in 'url_root'.
        html_root = requests.get(url_root).text

        # Pass HTML to BeautifulSoup with an XML parser.
        soup = BeautifulSoup(html_root, 'lxml')

        if soup.text.find('404 Not Found') != -1:
            raise Exception("HTTP Error 404: NOT FOUND")
    except Exception as e:
        error = "Source: " + url_root + "\nError: " + str(e)
        return error

    # Loop over <a> tags in 'soup' and store the text into 'sub'.
    # 'sub' = subdirectory of 'url_root'.
    # After looping, the most recent server subdirectory is stored into 'sub'.
    # 'sub' is also equal to the last updated date of server data.
    for j in soup.find_all('a'):
        sub = j.text

    # 'url_root' = directory for most recent root server data
    url_root = url_root + sub

    # Read HTML to 'html_root' from URL in 'url_root'
    html_root = requests.get(url_root).text

    # Pass HTML to BeautifulSoup with an XML parser 
    soup = BeautifulSoup(html_root, 'lxml')

    # 'cc' = List of 2 letter Country Codes.
    # Used to filter extracted data for these country codes.
    cc = ['AG', 'AI', 'BS', 'BB', 'BZ', 'BM', 'VG', 'KY', 'DM', 'GD', 'GY', 'HT', 'JM', 'MS', 'LC', 'KN', 'VC', 'SR', 'TT', 'TC']

    dict_ctry = {
        'AG':'Anguilla',
        'AI':'Antigua and Barbuda',
        'BS':'Bahamas',
        'BB':'Barbados',
        'BZ':'Belize',
        'BM':'Bermuda',
        'VG':'Virgin Islands U K ',
        'KK':'Cayman Islands',
        'DM':'Dominica',
        'GD':'Grenada',
        'GY':'Guyana',
        'HT':'Haiti',
        'JM':'Jamaica',
        'MS':'Montserrat',
        'KN':'Saint Kitts and Nevis',
        'LC':'Saint Lucia',
        'VC':'Saint Vincent and The Grenadines',
        'SR':'Suriname',
        'TT':'Trinidad and Tobago',
        'TC':'Turks and Caicos Islands'
    }


    # Loop through all <a> tags in 'soup'.
    for index, j in enumerate(soup.find_all('a')):
        # Ignore index directory - '../'
        if j.text == '../':
            continue

        # Store the URL of the nth root server in 'url_server'.
        # 'url_root' is the root directory.
        # 'j.text' is the subdirectory domain name.
        url_server = url_root + j.text

        try:
            # Read HTML to 'html_server' from URL in 'url_server'
            html_server = requests.get(url_server).text

            # Pass HTML to BeautifulSoup with an XML parser 
            soup_server = BeautifulSoup(html_server, 'lxml')

            if soup_server.text.find('404 Not Found') != -1:
                raise Exception("HTTP Error 404: NOT FOUND")
        except Exception as e:
            error = "Source: " + url_server + "\nError: " + str(e)
            return error


        # --------------------- Read Root Server Data --------------------- #
        
        # Read <p> tags from 'soup_server' into 'x'
        x = soup_server.p.text


        # ---------------------------------------------------------------------------- #
        #                      Filter Data for Caribbean Countries                     #
        # ---------------------------------------------------------------------------- #

        # 'pos1' = starting indices for data to scrape in 'x'.
        pos1 = [
                x.find('ASN:'),
                x.find('Contact Email:'),
                x.find('Homepage:'),
                x.find('IPv4:'),
                x.find('IPv6:'),
                x.find('Identifier Naming Convention:'),
                x.find('Operator:'),
                x.find('Peering Policy:'),
                x.find('RSSAC:'),
                x.find('Sites:'),
            ]

        # Starting indices for '- Country' string in 'x' is stored in 'res' list.
        # '- Country' is the start of a block of server data per country.
        res = [i for i in range(len(x)) if x.startswith('- Country', i)]


        # If 'index' = 1, then store the current time into 'time'.
        # 'time' stores starting time of writing to the database.
        # The time in 'time' is used to compare against the database entry timestamps.
        # This is used to ensure only recent data is stored into the database. 
        if index == 1:
            time = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

        # Read blocks of server data per country using indices in 'res' and store into 'root'.
        for k in range(len(res)):
            if k == len(res) - 1:
                root = x[ res[k] : x.find('Statistics') ]
            else:
                root = x[ res[k] : res[k + 1] ]

            # 'pos2' = starting indices for data to scrape in 'root'.
            pos2 = [
                root.find('- Country'),
                root.find('IPv4'),
                root.find('IPv6'),
                root.find('Identifiers'),
                root.find('Instances'),
                root.find('Latitude'),
                root.find('Longitude'),
                root.find('Town'),
                root.find('Type')
            ]

            # Checks if a block of server data has a Country Code from 'cc'.
            # 'tog' = condition to determine if block has country code.
            # 'ctry' = country for current root server.
            tog = 0
            for l in range(20):
                ctry = root[ pos2[0] + 11 : pos2[1] - 3 ]
                if ctry == cc[l]:
                    tog = 1
                    break
            # If 'tog' = 0, block has no country code. If 'tog' = 1, block has country code.
            if tog == 0:
                continue


        # ---------------------------------------------------------------------------- #
        #                                 Extract Data                                 #
        # ---------------------------------------------------------------------------- #

            # 'name' = Root Server Name.
            name = j.text[0].upper()
            
            # 'url' = server homepage.
            url = x[ pos1[2] + 10 : pos1[3] - 1 ] 

            # 'loc' = server location.
            loc = root[ pos2[7] + 6 : pos2[8] - 3 ]

            # 'oper' = server operator.
            oper = x[ pos1[6] + 10 : pos1[7] - 1 ]

            # 'type_' = server type.
            type_ = root[ pos2[8] + 6 : -1]

            # 'asn' = ASN number.
            asn = x[ pos1[0] + 5 : pos1[1] - 1 ]

            # 'ipv4' = IPv4 Address Data.
            if root[ pos2[1] + 6 : pos2[2] - 3 ] == 'true':
                ipv4 = x[ pos1[3] + 6 : pos1[4] - 1 ]
            else:
                ipv4 = 'NA'

            # 'ipv6' = IPv6 Address Data.
            if root[ pos2[2] + 6 : pos2[3] - 3 ] == 'true':
                ipv6 = x[ pos1[4] + 6 : pos1[5] - 1 ]
            else:
                ipv6 = 'NA'

            # 'inst' = number of instances.
            inst = root[ pos2[4] + 11 : pos2[5] - 3 ]

            # 'rssac' = Server RSSAC.
            rssac = '<a href = "' + x[ pos1[8] + 7 : pos1[9] - 1] + '"target="_blank" rel="noopener noreferrer">' + x[ pos1[8] + 7 : pos1[9] - 1] + '</a>'
            
            # 'con' = Server Contact Email.
            if x[ pos1[1] + 15 : pos1[2] - 1 ] == '\'\'':
                con = 'NA'
            else:
                con = x[ pos1[1] + 15 : pos1[2] - 1 ]

            # 'peer' = Peering Policy.
            if x[ pos1[7] + 16 : pos1[8] - 1 ] == '\'\'':
                peer = 'NA'
            else:
                peer = '<a href = "' + x[ pos1[7] + 16 : pos1[8] - 1 ] + '"target="_blank" rel="noopener noreferrer">' + x[ pos1[7] + 16 : pos1[8] - 1 ] + '</a>'
            
            # 'id_root' = Root Identifiers.
            if root[ pos2[3] + 13 : pos2[4] - 3 ] == '[]':
                id_root = 'NA'
            else:
                id_root = root[ pos2[3] + 13 : pos2[4] - 3 ]

            # 'id_nc' = Identifier Naming Convention.
            if x[ pos1[5] + 30 : pos1[6] - 1 ] == '\'\'':
                id_nc = 'NA'
            else:
                id_nc = x[ pos1[5] + 30 : pos1[6] - 1 ]
            
            # 'lat' and 'lon' contains latitude and longitude coordinates of root servers.
            lat = root[ pos2[5] + 10 : pos2[6] - 3 ]
            lon = root[ pos2[6] + 11 : pos2[7] - 3 ]
            

            # ---------------------------------------------------------------------------- #
            #                               Store to Database                              #
            # ---------------------------------------------------------------------------- #
            
            # 'uni' = Unique string identifier to distinguish between database entries.
            uni = ctry + '-' + str(index) + '-' + str(k)

            # -------------------- Store data to 'Root_srv' database table ------------------- #
            
            # 'exist' = Checks is a known value exists in the 'Root_srv' table.
            # Returns None if the value does not exist.
            # Returns a tuple of ids if the value exist.
            exist = db.session.query(Root_srv.id).filter_by(uni=uni).first()

            # If value does not exist in 'Root_srv' table, then add the data to the table.
            if exist == None:
                u = Root_srv(
                    name = name,
                    url = url,
                    ctry = dict_ctry[ctry],
                    uni = uni,
                    loc = loc,
                    oper = oper, 
                    type_ = type_, 
                    asn = asn, 
                    ipv4 = ipv4,
                    ipv6 = ipv6,
                    inst = inst,
                    rssac = rssac,
                    con = con,
                    peer = peer,
                    id_root = id_root,
                    id_nc = id_nc,
                    lat = lat,
                    lon = lon,
                    updt = sub.replace('/', ''),
                    stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
                )
                # Add entries to the database, and commit the changes.
                db.session.add(u)
                db.session.commit()
            
            # If value exists in 'Root_srv' table, then overwrite the existing data.
            else:
                # 'u' = retrieves the existing data via id stored in index 1 of the tuple in 'exist'.
                u = Root_srv.query.get(exist[0])
                # Overwriting of data in 'u'.
                u.name = name
                u.url = url
                u.ctry = dict_ctry[ctry]
                u.loc = loc
                u.oper = oper
                u.type_ = type_
                u.asn = asn
                u.ipv4 = ipv4
                u.ipv6 = ipv6
                u.inst = inst
                u.rssac = rssac
                u.con = con
                u.peer = peer
                u.id_root = id_root
                u.id_nc = id_nc
                u.updt = sub.replace('/', '')
                u.lat = lat
                u.lon = lon
                u.stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

                # Commit changes in 'u' to the database.
                db.session.commit()
    

    # -------------- Remove outdated data from 'Root_srv' database table -------------- #

    # Checks if the table is empty by looking at the table's first entry.
    # 'exist' returns None is empty.
    exist = Root_srv.query.get(1)

    # If table is full ...
    if exist != None:
        # Retrieve all data from 'Root_srv' and store into 'u'.
        u = Root_srv.query.all()
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