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

    # Loop through all <a> tags in 'soup'.
    for j in soup.find_all('a'):
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

            # 'name' = Root Server Name
            name = '<a href = "' + x[ pos1[2] + 10 : pos1[3] - 1 ] + '"target="_blank" rel="noopener noreferrer">' + j.text[0].upper() + ' Root</a>'
            
            # 'loc' = server location
            loc = root[ pos2[7] + 6 : pos2[8] - 3 ]

            # 'oper' = server operator
            oper = x[ pos1[6] + 10 : pos1[7] - 1 ]

            # 'type_' = server type
            type_ = root[ pos2[8] + 6 : -1]

            # 'asn' = ASN number
            asn = x[ pos1[0] + 5 : pos1[1] - 1 ]

            # 'ipv4' = IPv4 Address Data
            if root[ pos2[1] + 6 : pos2[2] - 3 ] == 'true':
                ipv4 = x[ pos1[3] + 6 : pos1[4] - 1 ]
            else:
                ipv4 = 'NA'

            # 'ipv6' = IPv6 Address Data
            if root[ pos2[2] + 6 : pos2[3] - 3 ] == 'true':
                ipv6 = x[ pos1[4] + 6 : pos1[5] - 1 ]
            else:
                ipv6 = 'NA'

            # 'inst' = number of instances
            inst = root[ pos2[4] + 11 : pos2[5] - 3 ]

            # 'rssac' = Server RSSAC
            rssac = '<a href = "' + x[ pos1[8] + 7 : pos1[9] - 1] + '"target="_blank" rel="noopener noreferrer">' + x[ pos1[8] + 7 : pos1[9] - 1] + '</a>'
            
            # 'con' = Server Contact Email
            if x[ pos1[1] + 15 : pos1[2] - 1 ] == '\'\'':
                con = 'NA'
            else:
                con = '<a href = "' + x[ pos1[1] + 15 : pos1[2] - 1 ] + '"target="_blank" rel="noopener noreferrer">' + x[ pos1[1] + 15 : pos1[2] - 1 ] + '</a>'

            # 'peer' = Peering Policy
            if x[ pos1[7] + 16 : pos1[8] - 1 ] == '\'\'':
                peer = 'NA'
            else:
                peer = '<a href = "' + x[ pos1[7] + 16 : pos1[8] - 1 ] + '"target="_blank" rel="noopener noreferrer">' + x[ pos1[7] + 16 : pos1[8] - 1 ] + '</a>'
            
            # 'id_root' = Root Identifiers
            if root[ pos2[3] + 13 : pos2[4] - 3 ] == '[]':
                id_root = 'NA'
            else:
                id_root = '<br>' + root[ pos2[3] + 13 : pos2[4] - 3 ]

            # 'id_nc' = Identifier Naming Convention
            if x[ pos1[5] + 30 : pos1[6] - 1 ] == '\'\'':
                id_nc = 'NA'
            else:
                id_nc = '<br>' + x[ pos1[5] + 30 : pos1[6] - 1 ]
            

            # ---------------------------------------------------------------------------- #
            #                               Store to Database                              #
            # ---------------------------------------------------------------------------- #
            
            # Store to 'root_srv' database table. 
            # Add 'name' to database
            # Add 'ctry' to database
            # Add 'loc' to database
            # Add 'oper' to database
            # Add 'type_' to database
            # Add 'asn' to database
            # Add 'ipv4' to database
            # Add 'ipv6' to database
            # Add 'inst' to database
            # Add 'rssac' to database
            # Add 'con' to database
            # Add 'peer' to database
            # Add 'id_root' to database
            # Add 'id_nc' to database
            # Add 'sub' to database