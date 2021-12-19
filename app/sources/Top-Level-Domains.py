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


def tld():
    '''
    Read, Scrape and Store TLD data from IANA's website to a database.
    '''
    # ---------------------------------------------------------------------------- #
    #                         IANA Top Level Domain Source                         #
    # ---------------------------------------------------------------------------- #

    # 'urls' contains the URLs of the IANA source per country to be scraped.
    urls = [
        'https://www.iana.org/domains/root/db/ag.html',
        'https://www.iana.org/domains/root/db/ai.html',
        'https://www.iana.org/domains/root/db/bs.html',
        'https://www.iana.org/domains/root/db/bb.html',
        'https://www.iana.org/domains/root/db/bz.html',
        'https://www.iana.org/domains/root/db/bm.html',
        'https://www.iana.org/domains/root/db/vg.html',
        'https://www.iana.org/domains/root/db/ky.html',
        'https://www.iana.org/domains/root/db/dm.html',
        'https://www.iana.org/domains/root/db/gd.html',
        'https://www.iana.org/domains/root/db/gy.html',
        'https://www.iana.org/domains/root/db/ht.html',
        'https://www.iana.org/domains/root/db/jm.html',
        'https://www.iana.org/domains/root/db/ms.html',
        'https://www.iana.org/domains/root/db/lc.html',
        'https://www.iana.org/domains/root/db/kn.html',
        'https://www.iana.org/domains/root/db/vc.html',
        'https://www.iana.org/domains/root/db/sr.html',
        'https://www.iana.org/domains/root/db/tt.html',
        'https://www.iana.org/domains/root/db/tc.html',
    ]


    # ---------------------------------------------------------------------------- #
    #                      Declaration of Caribbean Countries                      #
    # ---------------------------------------------------------------------------- #

    # 'ctry' = contains a list of Caribbean countries to add to database entries.
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


    # ---------------------------------------------------------------------------- #
    #                                  Read Source                                 #
    # ---------------------------------------------------------------------------- #

    for index, url in enumerate(urls):
        # 'index' = current index of loop.
        # 'url' = URL in 'urls' at an index.
        
        # Read HTML to 'source' from URL in 'url'.
        source = requests.get(url).text

        # Pass HTML to BeautifulSoup with an XML parser.
        soup = BeautifulSoup(source, 'lxml')

        # 'x' = stores HTML in 'soup' as a string object.
        x = str(soup)


        # ---------------------------------------------------------------------------- #
        #                         Scraping and Extracting Data                         #
        # ---------------------------------------------------------------------------- #

        # 'start' = starting bounds of data.
            # 'end' = ending bounds of data.
            # 'index1' = starting index of data.
            # 'index2' = ending index of data.

            # example:
            # text = "Alpha Beta Gamma"
            # data of interest = Beta
            # start = "Alpha "
            # end = " Gamma"

        
        # ---------------------------- ccTLD Manager field --------------------------- #

        start = '<h2>ccTLD Manager</h2>'
        end = '<h2>Administrative Contact</h2>'
        index1 = x.find(start) + len(start)
        index2 = x.find(end)
        # 'cctld' = ccTLD Manager data.
        cctld = ('<p>' + x[ index1 : index2 ] + '</p>')


        # ----------------------- Administrative Contact field ----------------------- #

        start = '<h2>Administrative Contact</h2>'
        end = '<h2>Technical Contact</h2>'
        index1 = x.find(start) + len(start)
        index2 = x.find(end)
        # 'ad_con' = Administrative Contact data.
        ad_con = ('<p>' + x[ index1 : index2 ] + '</p>')


        # -------------------------- Technical Contact field ------------------------- #

        start = '<h2>Technical Contact</h2>'
        end = '<h2>Name Servers</h2>'
        index1 = x.find(start) + len(start)
        index2 = x.find(end)
        # 'tch_con' = Technical Contact data.
        tch_con = ('<p>' + x[ index1 : index2 ] + '</p>')


        # ----------------------------- Name Server table ---------------------------- #

        start = '<table class="iana-table">'
        end = '</table>'
        index1 = x.find(start) + len(start)
        index2 = x.find(end)
        # 'nm_svr' = Name Server table data.
        nm_svr = ('<table>' + x[ index1 : index2 ] + '</table>')


        # ------------------------ Registry Information field ------------------------ #

        start = '<h2>Registry Information</h2>'
        end = '</i></p>'
        index1 = x.find(start) + len(start)
        index2 = x.find(end)
        # 'reg' = Registry Information data.
        reg = (x[ index1 : index2 ] + '</i></p>')


        # ------------------------------- Country field ------------------------------ #

        # 'ctry_' = contains country for each TLD
        ctry_ =  ctry[index]


        # ---------------------------------------------------------------------------- #
        #                               Store to Database                              #
        # ---------------------------------------------------------------------------- #

        # Store data to 'tld' database table.
        # Store 'ctry_' to database
        # Store 'cctld' to database
        # Store 'ad_con' to database
        # Store 'tch_con' to database
        # Store 'nm_svr' to database
        # Store 'reg' to database