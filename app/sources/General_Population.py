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
from app.models import Gen_pop
from datetime import datetime, timezone, timedelta


def population():
    '''
    Reads and Scrape data general population, geographical and socioencomic data
    from CIA World Factbook source. This data is filtered and cleaned to add to
    a database.
    '''
    # ---------------------------------------------------------------------------- #
    #                                  CIA Source                                  #
    # ---------------------------------------------------------------------------- #

    # 'urls' contains the URLs of the CIA source per country to be scraped.
    urls = ['https://www.cia.gov/the-world-factbook/countries/anguilla/',
            'https://www.cia.gov/the-world-factbook/countries/antigua-and-barbuda/',
            'https://www.cia.gov/the-world-factbook/countries/bahamas-the/',
            'https://www.cia.gov/the-world-factbook/countries/barbados/',
            'https://www.cia.gov/the-world-factbook/countries/belize/',
            'https://www.cia.gov/the-world-factbook/countries/bermuda/',
            'https://www.cia.gov/the-world-factbook/countries/british-virgin-islands/',
            'https://www.cia.gov/the-world-factbook/countries/cayman-islands/',
            'https://www.cia.gov/the-world-factbook/countries/dominica/',
            'https://www.cia.gov/the-world-factbook/countries/grenada/',
            'https://www.cia.gov/the-world-factbook/countries/guyana/',
            'https://www.cia.gov/the-world-factbook/countries/haiti/',
            'https://www.cia.gov/the-world-factbook/countries/jamaica/',
            'https://www.cia.gov/the-world-factbook/countries/montserrat/',
            'https://www.cia.gov/the-world-factbook/countries/saint-kitts-and-nevis/',
            'https://www.cia.gov/the-world-factbook/countries/saint-vincent-and-the-grenadines/',
            'https://www.cia.gov/the-world-factbook/countries/saint-lucia/',
            'https://www.cia.gov/the-world-factbook/countries/suriname/',
            'https://www.cia.gov/the-world-factbook/countries/trinidad-and-tobago/',
            'https://www.cia.gov/the-world-factbook/countries/turks-and-caicos-islands/']


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
    
    # Loop over URLs in 'urls' to scrape data and generate them into HTML files.
    for index, url in enumerate(urls):
        # 'index' = current index of loop.
        # 'url' = URL in 'urls' at an index.
        
        try:
            # Read HTML to 'source' from URL in 'url'.
            source = requests.get(url).text

            # Pass HTML to BeautifulSoup with an XML parser.
            soup = BeautifulSoup(source, 'lxml')
            
            if soup.text.find('404 Error') != -1:
                raise Exception("HTTP Error 404: NOT FOUND")
        except Exception as e:
            error = "Source: " + url + "\nError: " + str(e)
            return error

        

        # 'x' = stores HTML in 'soup' as a string object.
        x = str(soup)


        # ---------------------------------------------------------------------------- #
        #                        Scraping, Extract and Clean Data                      #
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


        # ------------------------------- Capital field ------------------------------ #

        start = '<a href="/the-world-factbook/field/capital">Capital</a>'
        end = '<strong>etymology: </strong>'
        index1 = x.find(start) + len(start)
        index2 = x.find(end)
        index2 = x.find(end, index2 + 1)
        # 'gen' = general country info.
        gen = x[ index1 : index2 ]
        # Cleaning 'gen'.
        gen = gen.replace('name:', 'capital:')
        gen = gen.replace('<br/><br/>', '</p><p>') + '<h3>'
        gen = gen.replace('</h3>', '')
        gen = gen.replace('<p><h3>', '')


        # ------------------------------ Currency field ------------------------------ #

        start = '<a href="/the-world-factbook/field/exchange-rates">Exchange rates</a>'
        end = 'per US dollar'
        index1 = x.find(start) + len(start)
        index2 = x.find(end)
        # If 'index2' don't exist, then replace 'end' with new ending bounds.
        if index2 == -1:
            end = '<h2>Energy</h2>'
            index2 = x.find(end)
        # 'cur' = country's currency.
        cur = x[ index1 : index2 ]
        # Cleaning 'cur'.
        cur = cur.replace('</h3>', '') + '</p>'
        cur = cur.replace('<p></p>', '')
        cur = cur.replace('</div></div><div class="free-form-content__content wysiwyg-wrapper" id="energy"></p>', '')


        # ------------------------------ languages field ----------------------------- #

        start = '<a href="/the-world-factbook/field/languages">Languages</a>'
        end = '<a href="/the-world-factbook/field/religions">Religions</a>'
        index1 = x.find(start) + len(start)
        index2 = x.find(end)
        # 'lang' = languages.
        lang = x[ index1 : index2 ]
        # Cleaning 'lang'.round(number)
        lang = lang.replace('</div><div><h3 class="mt30">', '')
        lang = lang.replace('</h3>', '')
        lang = lang.replace('src="', 'src="https://www.cia.gov')


        # -------------------------- Population Number field ------------------------- #

        start = '<a href="/the-world-factbook/field/population">Population</a>'
        end = '<a href="/the-world-factbook/field/population/country-comparison/">country comparison to the world:'
        index1 = x.find(start) + len(start)
        index2 = x.find(end)
        # 'pop' = total population.
        pop = x[ index1 : index2 ]
        # Cleaning 'pop'.
        pop = pop.replace('</h3>', '')


        # ---------------------------- Country Area field ---------------------------- #

        start = '<a href="/the-world-factbook/field/area">Area</a>'
        end = '<strong>land: </strong>'
        index1 = x.find(start) + len(start)
        index2 = x.find(end)
        # 'area' = country's total area.
        area = x[ index1 : index2 ]
        # Cleaning 'area'.
        area = area.replace('</h3>', '')
        area = area.replace('total:', '')
        area = area.replace('<br/><br/>', '</p>')


        # ------------------------- Land Use Percentage field ------------------------ #

        start = '<a href="/the-world-factbook/field/land-use">Land use</a>'
        end = '<a href="/the-world-factbook/field/irrigated-land">Irrigated land</a>'
        index1 = x.find(start) + len(start)
        index2 = x.find(end)
        # 'land' = land use.
        land = x[ index1 : index2 ]
        # Cleaning 'land'.
        land = land.replace('</h3>', '')
        land = land.replace('<br/><br/>', '</p><p>')
        land = land.replace('</div><div><h3 class="mt30">', '')


        # ------------------------ Urbanization Percent field ------------------------ #

        start = '<a href="/the-world-factbook/field/urbanization">Urbanization</a>'
        end = '<strong>rate of urbanization: </strong>'
        index1 = x.find(start) + len(start)
        index2 = x.find(end)
        # 'urb' = Urbanization percent.
        urb = x[ index1 : index2 ]
        # Cleaning 'urb'.
        urb = urb.replace('</h3>', '')
        urb = urb.replace('<br/><br/>', '</p>')


        # ------------------------- Electricity Access field ------------------------- #

        start = '<a href="/the-world-factbook/field/electricity-access">Electricity access</a>'
        end = '<a href="/the-world-factbook/field/electricity-production">Electricity - production</a>'
        # If start bounds don't exist, then data is N/A.
        if x.find(start) != -1:
            index1 = x.find(start) + len(start)
            index2 = x.find(end)
            # 'elec' = Electricity access.
            elec = x[ index1 : index2 ]
            # Cleaning 'elec'.
            elec = elec.replace('</h3>', '')
            elec = elec.replace('</div><div><h3 class="mt30">', '')
        else:
            elec = 'NA'


        # ------------------------ Labour Force Percent field ------------------------ #

        start = '<a href="/the-world-factbook/field/labor-force">Labor force</a>'
        end = '<a href="/the-world-factbook/field/labor-force/country-comparison/">country comparison to the world:'
        index1 = x.find(start) + len(start)
        index2 = x.find(end)
        # 'lab' = labour force percent.
        lab = x[ index1 : index2 ]
        # Cleaning 'lab'.
        lab = lab.replace('</h3>', '')


        # --------------------- Labour Force by Occupation field --------------------- #

        start = '<a href="/the-world-factbook/field/labor-force-by-occupation">Labor force - by occupation</a>'
        end = '<a href="/the-world-factbook/field/unemployment-rate">Unemployment rate</a>'
        # If start bounds don't exist, then data is N/A.
        if x.find(start) != -1:
            index1 = x.find(start) + len(start)
            index2 = x.find(end)
            # 'occ' = Labour Force by Occupation.
            occ = x[ index1 : index2 ]
            # Cleaning 'occ'.
            occ = occ.replace('</h3>', '')
            occ = occ.replace('</div><div><h3 class="mt30">', '')
            occ = occ.replace('<br/><br/>', '</p><p>')
        else:
            occ = 'NA'


        # -------------------------- Unemployment Rate field ------------------------- #

        start = '<a href="/the-world-factbook/field/unemployment-rate">Unemployment rate</a>'
        end = '<a href="/the-world-factbook/field/unemployment-rate/country-comparison/">country comparison to the world'
        index1 = x.find(start) + len(start)
        index2 = x.find(end)
        # 'unem' = Unemployment rate.
        unem = x[ index1 : index2 ]
        # Cleaning 'unem'.
        unem = unem.replace('</h3>', '')
        unem = unem.replace('<br/><br/>', '</p><p>')


        # -------------------- Population below Povery Line field -------------------- #

        start = '<a href="/the-world-factbook/field/population-below-poverty-line">Population below poverty line</a>'
        end = '<a href="/the-world-factbook/field/gini-index-coefficient-distribution-of-family-income">Gini Index coefficient - distribution of family income</a>'
        index1 = x.find(start) + len(start)
        index2 = x.find(end)
        # If 'index2' don't exist, then replace 'end' with new bounds to search for.
        if index2 == -1:
            end = '<a href="/the-world-factbook/field/household-income-or-consumption-by-percentage-share">Household income or consumption by percentage share</a>'
            index2 = x.find(end)
        # 'pov' = population below poverty line.
        pov = x[ index1 : index2 ]
        # Cleaning 'pov'.
        pov = pov.replace('</h3>', '')
        pov = pov.replace('</div><div><h3 class="mt30">', '')


        # -------------------------- Literacy Percent field -------------------------- #

        start = '<a href="/the-world-factbook/field/literacy">Literacy</a>'
        end = '<a href="/the-world-factbook/field/school-life-expectancy-primary-to-tertiary-education">School life expectancy (primary to tertiary education)</a>'
        # If start bounds don't exist, then data is N/A.
        if x.find(start) != -1:
            index1 = x.find(start) + len(start)
            index2 = x.find(end)
            # If 'index2' don't exist, then replace 'end' with new bounds to search for.
            if index2 == -1:
                end = '<a href="/the-world-factbook/field/unemployment-youth-ages-15-24">Unemployment, youth ages 15-24</a>'
                index2 = x.find(end)
                # If 'index2' don't exist, then replace 'end' with new bounds to search for.
                if index2 == -1:
                    end = '<h2>Environment</h2>'
                    index2 = x.find(end)      
            # 'lit' = literacy percent.
            lit = x[ index1 : index2 ]
            # Cleaning 'lit'.
            lit = lit.replace('</h3>', '')
            lit = lit.replace('</div><div><h3 class="mt30">', '')
            lit = lit.replace('<br/><br/>', '</p><p>')
        else:
            lit = 'NA'

        
        # ------------------------------- Country field ------------------------------ #

        # 'ctry_' = contains country for each root server
        ctry_ =  ctry[index]
        

        # ----------------------------- Date Last Updated ---------------------------- #

        # 'updt' = last updated date of data.
        updt = soup.find('label', class_='header-subsection-date').text
        updt = updt.replace('Page last updated: ', '')


        # ---------------------------------------------------------------------------- #
        #                               Store to Database                              #
        # ---------------------------------------------------------------------------- #

        # Store data to 'gen_pop' database table.
       
        # If 'index' = 0, then store the current time into 'time'.
        # 'time' stores starting time of writing to the database.
        # The time in 'time' is used to compare against the database entry timestamps.
        # This is used to ensure only recent data is stored into the database. 
        if index == 0:
            time = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
        
        # 'exist' = Checks is a known value exists in the 'gen_pop' table.
        # Returns None if the value does not exist.
        # Returns a tuple of ids if the value exist.
        exist = db.session.query(Gen_pop.id).filter_by(ctry_=ctry_).first()

        # If value does not exist in 'gen_pop' table, then add the data to the table.
        if exist == None:
            # print('Empty')
            u = Gen_pop(
            ctry_ = ctry_,
            gen = gen,
            cur = cur,
            area = area,
            land = land, 
            lang = lang, 
            pop = pop, 
            urb = urb, 
            elec = elec, 
            lab = lab, 
            occ = occ, 
            unem = unem, 
            pov = pov, 
            lit = lit, 
            updt = updt,
            stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")
            )
            # Add entries to the database, and commit the changes.
            db.session.add(u)
            db.session.commit()
        
        # If value exists in 'gen_pop' table, then overwrite the existing data.
        else:
            # print('Full'); print(exist[0])
            # 'u' = retrieves the existing data via id stored in index 1 of the tuple in 'exist'.
            u = Gen_pop.query.get(exist[0])
            # Overwriting of data in 'u'.
            u.gen = gen
            u.cur = cur
            u.area = area
            u.land = land
            u.lang = lang
            u.pop = pop
            u.urb = urb
            u.elec = elec
            u.lab = lab
            u.occ = occ
            u.unem = unem
            u.pov = pov
            u.lit = lit
            u.updt = updt
            u.stamp = datetime.now(timezone(timedelta(seconds=-14400))).strftime("%Y-%m-%d %H:%M:%S %z")

            # Commit changes in 'u' to the database.
            db.session.commit()
    
    # Checks if the table is empty by looking at the table's first entry.
    # 'exist' returns None is empty.
    exist = Gen_pop.query.get(1)

    # If table is full ...
    if exist != None:
        # Retrieve all data from 'gen_pop' and store into 'u'.
        u = Gen_pop.query.all()
        # Loop over each data entry in 'u'.
        for j in u:
            # print(j.stamp)
            # 'j.stamp' contain the entry timestamp as a string.
            # 'past' converts 'j.stamp' into Datetime object for comparison.
            # 'present' converts 'time' into Datetime object for comparison.
            past = datetime.strptime(j.stamp, "%Y-%m-%d %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S %z")
            present = datetime.strptime(time, "%Y-%m-%d %H:%M:%S %z").strftime("%Y-%m-%d %H:%M:%S %z")
            
            # If entry timestamp (past) is earlier than the time of writing to the database (present) ...
            # ... then the entry is outdated and does not exist in the more recent batch of data.
            if past < present:
                # print(True)
                # Delete the outdated entry.
                db.session.delete(j)
        # Commit changes to the database.
        db.session.commit()