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
from bokeh.models import Range1d, HoverTool, Panel, Tabs, Legend
from math import pi
from app import db
from app.models import GNI, PPP, USD


# ---------------------------------------------------------------------------- #
#                                 Create Graphs                                #
# ---------------------------------------------------------------------------- #

# 'ctry' = contains a list of Caribbean countries to filter the database data.
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

def create_baskets_graph():
    '''
    Retrieves ICT baskets data from the database and plots them into bokeh graphs.
    '''

    # 'cat' = contains the three database tables.
    cat = [GNI, PPP, USD]

    # 'unit' = stores units per category in 'cat'.
    unit = [
        'GNI pc (%)',
        'PPP',
        'USD ($)'
    ]

    # Loop 20 times as there are 20 Caribbean countries.
    for j in range(20):
        # 'tabs' = to store bokeh panels.
        tabs = []

        # Iterate over the three tables in 'cat' to filter each one at a time.
        for index, k in enumerate(cat):
            # 'yrs' = stores all year values for a country in 'ctry' at index 'j'.
            # 'fix' = stores all fixed broadband baskets for a country in 'ctry' at index 'j'.
            # 'mob' = stores all mobile broadband baskets for a country in 'ctry' at index 'j'.
            # 'low' = stores all mobile low usage baskets for a country in 'ctry' at index 'j'.
            # 'high' = stores all mobile high usage baskets for a country in 'ctry' at index 'j'.
            yrs = db.session.query(k.year).filter_by(ctry=ctry[j]).all()
            fix = db.session.query(k.fix).filter_by(ctry=ctry[j]).all()
            mob = db.session.query(k.mob).filter_by(ctry=ctry[j]).all()
            low = db.session.query(k.low).filter_by(ctry=ctry[j]).all()
            high = db.session.query(k.high).filter_by(ctry=ctry[j]).all()
            
            # Unpack tuples in list.
            # 'x' = x axis coordinates based on 'yrs'.
            # 'y1' = y axis coordinates based on 'fix'.
            # 'y2' = y axis coordinates based on 'mob'.
            # 'y3' = y axis coordinates based on 'low'.
            # 'y4' = y axis coordinates based on 'high'.
            x = [value for value, in yrs]
            y1 = [value for value, in fix]
            y2 = [value for value, in mob]
            y3 = [value for value, in low]
            y4 = [value for value, in high]
            
            # Replace NoneTypes or empty values with NaNs.
            # This is to prevent bokeh from interpretting empty values as 0.
            x = [float('NaN') if v is None else v for v in x]
            y1 = [float('NaN') if v is None else v for v in y1]
            y2 = [float('NaN') if v is None else v for v in y2]
            y3 = [float('NaN') if v is None else v for v in y3]
            y4 = [float('NaN') if v is None else v for v in y4]

            # Bokeh hovertool.
            hover = HoverTool(
                tooltips=[
                    ("Year", "$x{(0)}"),
                    (unit[index], "$y{(0)}"),
                ]
            )
            # Bokeh tools.
            tools = [hover, "pan,wheel_zoom,box_zoom,save,reset"]

            # 'p' = bokeh figure that will contain plots.
            p = figure(
                title='Price Baskets - ' + cc[j],
                x_range = Range1d(x[0], x[-1]),
                x_axis_label='Year', 
                y_axis_label= unit[index],
                tools = tools,
                width = 250
            )

            # 'p.line' plots a line graph. 
            # 'p.circle' plots a scatter plot.
            # Overlaying both creates a line plot with visible markers.
            # Colour scheme: https://mdigi.tools/color-shades/#0d6efd

            # Scatter plot with lines for Fixed broadband data
            p.line(x, y1, legend_label='Fixed Broadband', line_color='#011a3f', line_width=2)
            p.circle(x, y1, color='#011a3f', size=5, legend_label='Fixed Broadband')

            # Scatter plot with lines for Mobile broadband data
            p.line(x, y2, legend_label='Mobile Broadband', line_color='#024ebe', line_width=2)
            p.circle(x, y2, color='#024ebe', size=5, legend_label='Mobile Broadband')

            # Scatter plot with lines for Mobile Data and Voice low usage data
            p.line(x, y3, legend_label='Mobile Low Usage', line_color='#418dfd', line_width=2)
            p.circle(x, y3, color='#418dfd', size=5, legend_label='Mobile Low Usage')

            # Scatter plot with lines for Mobile Data and Voice low usage data
            p.line(x, y4, legend_label='Mobile High Usage', line_color='#c0d9fe', line_width=2)
            p.circle(x, y4, color='#c0d9fe', size=5, legend_label='Mobile High Usage')

            # Creates legend at the bottom of the figure and allows toggling of features on figure
            p.legend.location = 'left'
            p.legend.border_line_alpha = 0
            p.legend.click_policy = 'hide'
            p.add_layout(p.legend[0], 'below')

            # x axis label orientation by 90 degrees
            p.xaxis.major_label_orientation = pi/2
    
            # Makes figure 'p' responsive
            p.sizing_mode = 'stretch_both'

            # Adds figure 'p' to a panel object.
            # Panel objects can be combines into one bokeh tabs plot.
            # These objects are appended to 'tabs' list.
            tabs.append(Panel( child=p, title=unit[index].split(' ')[0] ))
        
        # 'tabs' = bokeh tabs object which combines the panel objects in 'tabs' list.
        tabs = Tabs(tabs=tabs)
        
        # Saves graphs to an output directory as an HTML file.
        output_file('./app/static/html/baskets' + str(j) + ".html")
        save(tabs)