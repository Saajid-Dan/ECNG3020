'''
Name: Saajid Dan
Course: ECNG 3020
Project Title:
'''

# ---------------------------------------------------------------------------- #
#                                    Imports                                   #
# ---------------------------------------------------------------------------- #

import pandas as pd
from bokeh.plotting import figure, show, output_file, save
from bokeh.models import Range1d, FuncTickFormatter, HoverTool, Panel, Tabs
from bokeh.io import export_png
from math import pi
from app import db
from app.models import ICT_fix, ICT_mob, ICT_per, ICT_bw


# ---------------------------------------------------------------------------- #
#                                 Create Graphs                                #
# ---------------------------------------------------------------------------- #


# 'cc' = ISO-3 country codes to label graphs.
cc = [
    'AIA',
    'ATG', 
    'BHS', 
    'BRB', 
    'BLZ', 
    'BMU', 
    'VGB', 
    'CYM', 
    'DMA', 
    'GRD', 
    'GUY', 
    'HTI', 
    'JAM', 
    'MSR', 
    'KNA', 
    'LCA', 
    'VCT', 
    'SUR', 
    'TTO', 
    'TCA'
]

dict_ctry = {
        'AIA':'Anguilla',
        'ATG':'Antigua and Barbuda',
        'BHS':'Bahamas',
        'BRB':'Barbados',
        'BLZ':'Belize',
        'BMU':'Bermuda',
        'VGB':'Virgin Islands U K ',
        'CYM':'Cayman Islands',
        'DMA':'Dominica',
        'GRD':'Grenada',
        'GUY':'Guyana',
        'HTI':'Haiti',
        'JAM':'Jamaica',
        'MSR':'Montserrat',
        'KNA':'Saint Kitts and Nevis',
        'LCA':'Saint Lucia',
        'VCT':'Saint Vincent and The Grenadines',
        'SUR':'Suriname',
        'TTO':'Trinidad and Tobago',
        'TCA':'Turks and Caicos Islands'
    }

def create_indic_graph():
    '''
    Retrieves ICT indicators data from the database and plots them into bokeh graphs.
    '''
    
    # 'cat' = contains the four database tables.
    cat = [ICT_fix, ICT_mob, ICT_per, ICT_bw]

    # 'lst_fix' = to store figures related to fixed broadband subscriptions.
    # 'lst_mob' = to store figures related to mobile broadband subscriptions.
    # 'lst_per' = to store figures related to percentaage of internet users.
    # 'lst_bw' = to store figures related to total bandwidth usage.
    lst_fix = []
    lst_mob = []
    lst_per = []
    lst_bw = []

    # Loops over the four tables.
    for j in cat:
        # Database query to retrieve the data by columns and ordered by the 'yrs' column.
        # The queries return a list of tuples.
        year = j.query.with_entities(j.yrs).all()
        aia = j.query.with_entities(j.ai).order_by(j.yrs).all()
        atg = j.query.with_entities(j.ag).order_by(j.yrs).all()
        bhs = j.query.with_entities(j.bs).order_by(j.yrs).all()
        brb = j.query.with_entities(j.bb).order_by(j.yrs).all()
        blz = j.query.with_entities(j.bz).order_by(j.yrs).all()
        bmu = j.query.with_entities(j.bm).order_by(j.yrs).all()
        vgb = j.query.with_entities(j.vg).order_by(j.yrs).all()
        cym = j.query.with_entities(j.ky).order_by(j.yrs).all()
        dma = j.query.with_entities(j.dm).order_by(j.yrs).all()
        grd = j.query.with_entities(j.gd).order_by(j.yrs).all()
        guy = j.query.with_entities(j.gy).order_by(j.yrs).all()
        hti = j.query.with_entities(j.ht).order_by(j.yrs).all()
        jam = j.query.with_entities(j.jm).order_by(j.yrs).all()
        msr = j.query.with_entities(j.ms).order_by(j.yrs).all()
        kna = j.query.with_entities(j.kn).order_by(j.yrs).all()
        lca = j.query.with_entities(j.lc).order_by(j.yrs).all()
        vct = j.query.with_entities(j.vc).order_by(j.yrs).all()
        sur = j.query.with_entities(j.sr).order_by(j.yrs).all()
        tto = j.query.with_entities(j.tt).order_by(j.yrs).all()
        tca = j.query.with_entities(j.tc).order_by(j.yrs).all()
        
        # Unpack tuples in a list.
        x = [value for value, in year]          # x-axis coordinates.
        aia = [value for value, in aia]
        atg = [value for value, in atg]
        bhs = [value for value, in bhs]
        brb = [value for value, in brb]
        blz = [value for value, in blz]
        bmu = [value for value, in bmu]
        vgb = [value for value, in vgb]
        cym = [value for value, in cym]
        dma = [value for value, in dma]
        grd = [value for value, in grd]
        guy = [value for value, in guy]
        hti = [value for value, in hti]
        jam = [value for value, in jam]
        msr = [value for value, in msr]
        kna = [value for value, in kna]
        lca = [value for value, in lca]
        vct = [value for value, in vct]
        sur = [value for value, in sur]
        tto = [value for value, in tto]
        tca = [value for value, in tca]
        
        # Replace NoneTypes or empty values with NaNs.
        # This is to prevent bokeh from interpretting empty values as 0.
        aia = [float('NaN') if v is None else v for v in aia]
        atg = [float('NaN') if v is None else v for v in atg]
        bhs = [float('NaN') if v is None else v for v in bhs]
        brb = [float('NaN') if v is None else v for v in brb]
        blz = [float('NaN') if v is None else v for v in blz]
        bmu = [float('NaN') if v is None else v for v in bmu]
        vgb = [float('NaN') if v is None else v for v in vgb]
        cym = [float('NaN') if v is None else v for v in cym]
        dma = [float('NaN') if v is None else v for v in dma]
        grd = [float('NaN') if v is None else v for v in grd]
        guy = [float('NaN') if v is None else v for v in guy]
        hti = [float('NaN') if v is None else v for v in hti]
        jam = [float('NaN') if v is None else v for v in jam]
        msr = [float('NaN') if v is None else v for v in msr]
        kna = [float('NaN') if v is None else v for v in kna]
        lca = [float('NaN') if v is None else v for v in lca]
        vct = [float('NaN') if v is None else v for v in vct]
        sur = [float('NaN') if v is None else v for v in sur]
        tto = [float('NaN') if v is None else v for v in tto]
        tca = [float('NaN') if v is None else v for v in tca]

        # 'y' = stores a list of y-axis coordinates per country.
        y = [aia, atg, bhs, brb, blz, bmu, vgb, cym, dma, grd, guy, hti, jam, msr, kna, lca, vct, sur, tto, tca]
        
        # Iterate over the y coordinates per country to plot figures.
        for index, k in enumerate(y):
            # If the current table is 'ICT_fix'.
            if j == ICT_fix:
                y_label = 'Fixed Broadband Subscriptions'
                unit = 'Subscribers'
            # If the current table is 'ICT_mob'.
            elif j == ICT_mob:
                y_label = 'Mobile Broadband Subscriptions'
                unit = 'Subscribers'
            # If the current table is 'ICT_per'.
            elif j == ICT_per:
                y_label = 'Percent of Internet Users'
                unit = 'Percent (%)'
            # If the current table is 'ICT_bw'.
            elif j == ICT_bw:
                y_label = 'Total Bandwidth Usage (Mbps)'
                unit = 'Bandwidth (Mbps)'

            # Bokeh hovertool.
            hover = HoverTool(
                tooltips=[
                    ("Year", "$x{(0)}"),
                    (unit, "$y{(0)}"),
                ]
            )
            # Bokeh tools.
            tools = [hover, "pan,wheel_zoom,box_zoom,save,reset"]

            # 'p' = bokeh figure that will contain plots.
            p = figure(
                title='Internet Indicators - ' + cc[index],
                x_range = Range1d(x[0], x[-1]),
                x_axis_label='Year', 
                y_axis_label= y_label,
                tools = tools,
                width=450, 
                height=340,
            )

            # 'p.line' plots a line graph. 
            # 'p.circle' plots a scatter plot.
            # Overlaying both creates a line plot with visible markers.
            # Colour scheme: https://mdigi.tools/color-shades/#0d6efd

            # Scatter plot with lines for Fixed broadband data.
            p.line(x, k, line_color='#0d6efd', line_width=2)
            p.circle(x, k, color='#011a3f', size=5)

            # Format y axis with prefixes.
            p.yaxis.formatter = FuncTickFormatter(code='''
            if (tick < 1e3){
                var unit = ''
                var num = (tick).toFixed(0)
            }
            else if (tick < 1e6){
                var unit = 'k'
                var num = (tick/1e3).toFixed(0)
            }
            else{
                var unit = 'M'
                var num = (tick/1e6).toFixed(0)
            }
            return `${num}${unit}`
            ''')

            # x-axis label orientation by 90 degrees.
            p.xaxis.major_label_orientation = pi/2

            # Export figures as a PNG.
            export_png(p, filename='./app/static/images/Indicators/' + y_label.split(' ')[0] + dict_ctry[cc[index]] + '.png')

            # Makes figure 'p' responsive.
            p.sizing_mode = 'stretch_both'
            

            # 'tab' = adds figure 'p' to a panel object.
            # Panel objects can be combines into one bokeh tabs plot.
            if j == ICT_fix:
                tab = Panel( child=p, title='Fixed')
                # Add Fixed Broadband figures to 'lst_fix'.
                lst_fix.append(tab)
            elif j == ICT_mob:
                tab = Panel( child=p, title='Mobile')
                # Add Mobile Broadband figures to 'lst_mob'.
                lst_mob.append(tab)
            elif j == ICT_per:
                tab = Panel( child=p, title='Percent')
                # Add Percent of ICT Users figures to 'lst_per'.
                lst_per.append(tab)
            elif j == ICT_bw:
                tab = Panel( child=p, title='Bandwidth')
                # Add Bandwidth Usage figures to 'lst_bw'.
                lst_bw.append(tab)
    
    # Iterate over range of 20 as there are 20 Caribbean countries.
    for j in range(20):
        # Add panel objects from 'lst_fix', 'lst_mob', 'lst_per', and 'lst_bw' to 'tabs' list grouped by country.
        tabs = [ lst_fix[j], lst_mob[j], lst_per[j], lst_bw[j] ]
        # 'tabs' = bokeh tabs object which combines the panels in the 'tabs' list to one graph.
        tabs = Tabs(tabs=tabs)

        # Saves graphs to an output directory as an HTML file.
        output_file('./app/static/html/indicators' + str(j) + ".html")
        save(tabs)