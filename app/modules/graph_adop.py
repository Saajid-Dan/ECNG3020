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
from bokeh.models import Range1d, HoverTool, Panel, Tabs, Legend, LegendItem, Column, Row, MultiChoice, CustomJS, Button
from bokeh.events import ButtonClick
from bokeh.io import export_png
from math import pi
from app import app, db
from app.models import Itu_basket_gni, Itu_basket_ppp, Itu_basket_usd
import codecs
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


# Selenium headless mode.
options = Options()
options.headless = True



# ---------------------------------------------------------------------------- #
#                                 Configuration                                #
# ---------------------------------------------------------------------------- #

# 'col_all' = 20 hex colours for graph plots.
# They correspond to the countries in the 'lkup' dictionary.
# http://medialab.github.io/iwanthue/
col_all = ["#7cd2c5","#713cc6","#8cd847","#c849bd",
           "#71d487","#cd4574","#d6c244","#6a70d0",
           "#5e7e2f","#4e2660","#ceca96","#d75033",
           "#8cb3d6","#ae7638","#c78ac5","#527a60",
           "#783333","#586488","#cd928f","#39332a"]

# 'lkup' = look up table that assigns hex colours to a Caribbean country.
lkup = {
    '#7cd2c5': ['AIA', 'Anguilla'],
    '#713cc6': ['ATG', 'Antigua and Barbuda'],
    '#8cd847': ['BHS', 'Bahamas'],
    '#c849bd': ['BRB', 'Barbados'],
    '#71d487': ['BLZ', 'Belize'],
    '#cd4574': ['BMU', 'Bermuda'],
    '#d6c244': ['VGB', 'British Virgin Islands'],
    '#6a70d0': ['CYM', 'Cayman Islands'],
    '#5e7e2f': ['DMA', 'Dominica'],
    '#4e2660': ['GRD', 'Grenada'],
    '#ceca96': ['GUY', 'Guyana'],
    '#d75033': ['HTI', 'Haiti'],
    '#8cb3d6': ['JAM', 'Jamaica'],
    '#ae7638': ['MSR', 'Montserrat'],
    '#c78ac5': ['KNA', 'Saint Kitts and Nevis'],
    '#527a60': ['LCA', 'Saint Lucia'],
    '#783333': ['VCT', 'Saint Vincent and the Grenadines'],
    '#586488': ['SUR', 'Suriname'],
    '#cd928f': ['TTO', 'Trinidad and Tobago'],
    '#39332a': ['TCA', 'Turks & Caicos Is.'],
}

# 'lst_glyph' = global variable that stores bokeh glyphs.
# Used to merge the legends from each glyph.
lst_glyph = []


# ---------------------------------------------------------------------------- #
#                           Plot ICT Adoption Graphs                           #
# ---------------------------------------------------------------------------- #

def graph_adop():
    '''
    Adds a unified legend to all graphs.
    '''
    global lst_glyph            # Global variable.


    # ---------------------------------- Graphs ---------------------------------- #

    # Graphs.
    tabs_gni = baskets(Itu_basket_gni, 'GNI pc', 'GNI per capita (%)')         # ICT Baskets graphs - GNI pc.
    tabs_ppp = baskets(Itu_basket_ppp, 'PPP', 'Purchasing Power Parity')       # ICT Baskets graphs - PPP.
    tabs_usd = baskets(Itu_basket_usd, 'USD', 'USD ($)')                       # ICT Baskets graphs - USD.

    # Add graphs to a bokeh Column grid with responsive widths.
    column = Column(tabs_gni, tabs_ppp, tabs_usd)
    column.sizing_mode = 'stretch_width'


    # -------------------------- Merge Legend and Graphs ------------------------- # 

    OPTIONS = []
    values = []
    for j in lst_glyph:
        if j.name not in OPTIONS:
            OPTIONS.append(j.name)
    OPTIONS.sort(key=lambda x: x, reverse=False)

    # print(OPTIONS)
    
    multi_choice = MultiChoice(value=[], options=OPTIONS, title='Select a Country:')

    btn_clr = Button(label='Clear Selection')
    callback_clr = CustomJS(args=dict(multi_choice=multi_choice), code="""multi_choice.value = []""")

    btn_all = Button(label='All Selection')
    callback_all = CustomJS(args=dict(multi_choice=multi_choice, OPTIONS=OPTIONS), code="""multi_choice.value = OPTIONS""")

    btn_clr.js_on_event(ButtonClick, callback_clr)
    btn_all.js_on_event(ButtonClick, callback_all)

    callback = CustomJS(args=dict(lst_glyph=lst_glyph, multi_choice=multi_choice, lkup=lkup), code="""
    for (let i = 0; i < lst_glyph.length; i++) {
        if (multi_choice.value.includes(lst_glyph[i].name)) {
            lst_glyph[i].visible = multi_choice.value.includes(lst_glyph[i].name);
        } else {
            lst_glyph[i].visible = multi_choice.value.includes("False");
        }
    }
    """)

    multi_choice.js_on_change('value', callback)
    multi_choice.sizing_mode = 'stretch_width'

    # Add the legend and 'tabs' to a Column grid.
    layout = Column(multi_choice, btn_clr, btn_all, column)
    # layout = gridplot([[row], [col]], merge_tools=False)
    layout.sizing_mode = 'stretch_width'

    output_file('./app/static/html/graph_adop.html')
    save(layout)

    graph = codecs.open('./app/static/html/graph_adop.html', 'r').read()
    graph = graph.replace('</title>', '</title>\n<style>html {overflow-y: scroll;} .bk { justify-content: end;}</style>')
    with open('./app/static/html/graph_adop.html', 'w') as f:
        f.write(graph)

def baskets(cat, title, unit):
    '''
    Plots Bokeh figures for fixed/mobile broadband, and low/high mobile data baskets vs year and add to a bokeh tabs group.
    '''
    global lst_glyph            # Global variable.

    # Tab labels.
    tab_lab = [
        'Fixed', 'Mobile', 'Low', 'High'
    ]

    # Graphs titles.
    title_ = [
        'Fixed Broadband Baskets', 
        'Mobile Broadband Baskets', 
        'Mobile Low Data Usage Baskets', 
        'Mobile High Data Usage Baskets'
    ]

    # Stores a list of countries the the 'cat' database into 'ctry_lst'.
    ctry_lst = []
    ctry = cat.query.order_by(cat.country).with_entities(cat.country)
    for j in ctry:
        if j[0] not in ctry_lst:
           ctry_lst.append(j[0])

    # Stores a list hex colours that correspond to the countries in 'ctry_lst' via 'lkup' dictionary.
    # 'col' = stores a list of hex colours.
    col = []
    lst_key = list(lkup.keys())                 # List of keys in 'lkup'.
    lst_val = list(lkup.values())               # List of values in 'lkup'.
    lst_val = [item[1] for item in lst_val]     # Unpack list of lists.
    for ctry in ctry_lst:   
        pos = lst_val.index(ctry)               # Get index of country in 'lkup'.
        col.append(lst_key[pos])                # Get value via index.

    # 'tabs' = store bokeh panels.
    tabs = []

    # 'hdr' = headers in the database table 'cat'.
    # 'cat' contains 'GNI', 'PPP', and 'USD' database tables.
    hdrs = [cat.fix, cat.mob, cat.low, cat.high]

    # Iterate over header (hdr) in headers (hdr).
    for i, hdr in enumerate(hdrs):
        # yrs = Years extracted from the 'cat' table via query.
        # 'yrs' used as the x-axis coordinates.
        # These queries are returned as a list of tuples.
        yrs = db.session.query(cat.date).filter_by(country=ctry_lst[0]).all()
        x = [value for value, in yrs]
        
        # 'y' = stores a list of y-axis coordinates per country.
        y = []
        for ctry in ctry_lst:
            # Query header (hdr) in list headers (hdrs) for y-coordinates data per country in 'ctry_lst'. 
            # The query produces a list of tuples which must be unpacked into a list.
            data = db.session.query(hdr).filter_by(country=ctry).all()
            data = [value for value, in data]
            data = [float('NaN') if v is None else v for v in data]
            y.append(data)

        # Creates a bokeh figure to add plots.
        p = figure(
            title = title_[i] + ' - ' + title,
            x_range = Range1d(x[0], x[-1]),
            x_axis_label='Year', 
            y_axis_label= unit,
            width=450, 
            height= 250
        )

        # Orient x-axis labels by 90 degrees.
        p.xaxis.major_label_orientation = pi/2

        # Iterate over the y coordinates per country to plot figures.
        for index, k in enumerate(y):
            # 'p.line' plots a line graph. 
            # 'p.circle' plots a scatter plot.
            # Overlaying both creates a scatter plot with visible markers.
            # Colour scheme: https://mokole.com/palette.html

            # 'r1' and 'r2' are bokeh glyphs which contain the plot information.
            # 'visible' = False to initially hide all plots.
            r1 = p.line(x, k, color=col[index], line_width=2, name=ctry_lst[index])
            r2 = p.circle(x, k, color=col[index], size=5, name=ctry_lst[index])

            # Add glyphs to 'lst_glyph'.
            lst_glyph += [r1]
            lst_glyph += [r2]

            # Makes figure 'p' fixed to export as PNG.
            # Remove toolbar to export as PNG.
            p.sizing_mode = 'fixed'
            p.toolbar_location = None

            browser = webdriver.Firefox(executable_path=app.config['WEB_DRIVER_PATH'], options=options)

            # Export figure 'p' as a PNG.
            export_png(
                p, 
                filename='./app/static/images/adoption/baskets/' + title_[i] + ' - ' +  title +' - ' + ctry_lst[index] + '.png', 
                webdriver=browser
                )

            # Close the tab and browser to close all firefox sessions.
            browser.close()
            browser.quit()

            # Bokeh hovertool.
            hover = HoverTool(
                tooltips=[ ("Country", "$name"), ("Date", "$x"), (unit[i], "$y{(0)}") ]
            )

            # Add tools on the right of figure 'p'.
            if index == 0:
                p.add_tools(hover)
            p.toolbar_location = 'right'

            
            # Initially hide scatter plot.
            # Plots can be shown by selecting Legend properties.
            r1.visible = False
            r2.visible = False

            # Makes figure 'p' responsive to overlay on a webpage.
            p.sizing_mode = 'stretch_width'

        # Convert figure 'p' to a Panel object and append to 'tabs' list.
        tabs.append(Panel( child=p, title=tab_lab[i] ))
    
    # Merge bokeh panels in the 'tabs' list to bokeh tabs group.
    tabs = Tabs(tabs=tabs)

    return tabs