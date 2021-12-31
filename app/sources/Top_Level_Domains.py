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
from app.models import Tld
from datetime import datetime, timezone, timedelta


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
        
        try:
            # Read HTML to 'source' from URL in 'url'.
            source = requests.get(url).text

            # Pass HTML to BeautifulSoup with an XML parser.
            soup = BeautifulSoup(source, 'lxml')

            if soup.text.find('This page does not exist.') != -1:
                raise Exception("HTTP Error 404: NOT FOUND")
        except Exception as e:
            error = "Source: " + url + "\nError: " + str(e)
            return error

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

        
        # ---------------------------- Country Code field ---------------------------- #

        # Find country code on page in first h1 tag.
        # Store resulting text into 'cc'.
        # Clean unnecessary text from 'cc'.
        cc = soup.find('h1').text
        cc = cc.replace('Delegation Record for ', '')


        # -------------------------------- Domain Type ------------------------------- #

        # Find country code type on page in first p tag.
        # Store resulting text into 'type_'.
        # Clean unnecessary text from 'type_'.
        type_ = soup.find('p').text
        type_ = type_.replace('(', '')
        type_ = type_.replace(')', '')


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
        # Add bootstrap styles to 'nm_svr' html table format.
        nm_svr = nm_svr.replace('<table>', "<table class='table table-sm table-hover'>")
        nm_svr = nm_svr.replace('<tr>', "<tr class='table-primary'>", 1)


        # ------------------------ Registry Information field ------------------------ #

        start = '<h2>Registry Information</h2>'
        end = '<h2>IANA Reports</h2>'
        index1 = x.find(start) + len(start)
        index2 = x.find(end)
        # If first instance of 'end' not on page ...
        if index2 == -1:
            # Replace 'end' with another key to look for.
            end = '<i>'
            index2 = x.find(end)
            # 'reg' = Registry Information data.
            reg = (x[ index1 : index2 ] + '</i></p>')
            # Cleaning 'reg'.
            reg = reg.replace('<p></i></p>', '')


        # -------------------- Registration and Update Dates field ------------------- #
        
        # 'dates' = store Registration and last updated date.
        dates = soup.find('i').text


        # ------------------------------- Country field ------------------------------ #

        # 'ctry_' = contains country for each TLD
        ctry_ =  ctry[index]


        # ---------------------------------------------------------------------------- #
        #                               Store to Database                              #
        # ---------------------------------------------------------------------------- #

        # Store data to 'Tld' database table.
       
        # If 'index' = 0, then store the current time into 'time'.
        # 'time' stores starting time of writing to the database.
        # The time in 'time' is used to compare against the database entry timestamps.
        # This is used to ensure only recent data is stored into the database. 
        if index == 0:
            time = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
        
        # 'exist' = Checks is a known value exists in the 'Tld' table.
        # Returns None if the value does not exist.
        # Returns a tuple of ids if the value exist.
        exist = db.session.query(Tld.id).filter_by(ctry_=ctry_).first()

        # If value does not exist in 'Tld' table, then add the data to the table.
        if exist == None:
            u = Tld(
            ctry_ = ctry_,
            cc = cc,
            type_ = type_,
            cctld = cctld,
            ad_con = ad_con,
            tch_con = tch_con,
            nm_svr = nm_svr, 
            reg = reg, 
            dates = dates,
            stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
            )
            # Add entries to the database, and commit the changes.
            db.session.add(u)
            db.session.commit()
        
        # If value exists in 'Tld' table, then overwrite the existing data.
        else:
            # 'u' = retrieves the existing data via id stored in index 1 of the tuple in 'exist'.
            u = Tld.query.get(exist[0])
            # Overwriting of data in 'u'.
            u.cc = cc
            u.type_ = type_
            u.cctld = cctld
            u.ad_con = ad_con
            u.tch_con = tch_con
            u.nm_svr = nm_svr
            u.reg = reg
            u.dates = dates
            u.stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

            # Commit changes in 'u' to the database.
            db.session.commit()
    
    # Checks if the table is empty by looking at the table's first entry.
    # 'exist' returns None is empty.
    exist = Tld.query.get(1)

    # If table is full ...
    if exist != None:
        # Retrieve all data from 'Tld' and store into 'u'.
        u = Tld.query.all()
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