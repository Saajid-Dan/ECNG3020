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
from bokeh.models import Range1d, FuncTickFormatter, HoverTool, Panel, Tabs, Legend, LegendItem, Column, Row, MultiChoice, CustomJS, Button
from bokeh.events import ButtonClick
from bokeh.io import export_png
from math import pi
from app import db
from app.models import indicators
import codecs


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
#                             Plot ICT Use Graphs                              #
# ---------------------------------------------------------------------------- #

def graph_use():
    '''
    Adds a unified legend to all graphs.
    '''
    global lst_glyph            # Global variable.


    # ---------------------------------- Graphs ---------------------------------- #

    # Graphs.
    tabs_ind = ict_indicators()             # ICT Indicators graphs.

    # Add graphs to a bokeh Column grid with responsive widths.
    column = Column(tabs_ind)
    column.sizing_mode = 'stretch_width'


    # -------------------------- Merge Legend and Graphs ------------------------- # 

    OPTIONS = []
    values = []
    for j in lst_glyph:
        if j.name not in OPTIONS:
            OPTIONS.append(j.name)
    OPTIONS.sort(key=lambda x: x, reverse=False)

    print(OPTIONS)
    
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

    output_file('./app/static/html/graph_use.html')
    save(layout)

    graph = codecs.open('./app/static/html/graph_use.html', 'r').read()
    graph = graph.replace('</title>', '</title>\n<style>html {overflow-y: scroll;} .bk { justify-content: end;}</style>')
    with open('./app/static/html/graph_use.html', 'w') as f:
        f.write(graph)

def ict_indicators():
    '''
    Plots Bokeh figures for fixed and mobile broadband total subscriptions, percent of 
    ICT users in a country, and total bandwidth usage and add to a bokeh tabs group.
    '''
    global lst_glyph            # Global variable.

    # Tab labels.
    tab_lab = [
        'Fixed', 'Mobile', 'Percent', 'Bandwidth'
    ]

    # Graphs titles.
    title = [
        'Fixed Broadband Total Subscriptions', 
        'Mobile Broadband Total Subscriptions', 
        'Percent of Internet Users', 
        'Total Bandwidth Usage'
    ]

    # Graph units.
    unit = [
        'Subscribers',
        'Subscribers',
        'Percent (%)',
        'Bandwidth (Mbps)'
    ]

    # 'tabs' = stores bokeh panel objects.
    # 'fig' = stores bokeh figures.
    # 'lst_col' = stores list of colours.
    tabs = []
    fig = []
    lst_col = []

    year = indicators.query.with_entities(indicators.year).all()
    x = [value for value, in year]          # x-axis coordinates.
    x = list(dict.fromkeys(x))

    # Stores a list of countries the the 'cat' database into 'ctry_lst'.
    ctry_lst = []
    ctry = indicators.query.order_by(indicators.ctry).with_entities(indicators.ctry)
    for j in ctry:
        if j[0] not in ctry_lst:
           ctry_lst.append(j[0])

    cat = [indicators.fix, indicators.mob, indicators.per, indicators.bw]

    # Loops over the four tables.
    # 'i' = iterator. 'j' = database table from 'cat'.
    for i, j in enumerate(cat):
        # Query the 'j' database table to retrieve data per table header and order it by the 'yrs' header.
        # The queries return a list of tuples.
        # 'year' = data from the 'yrs' header.
        # 'aia' to 'tca' = indicators data from Anguilla to Turks and Caicos Islands (ascending).

        aia = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[0]).with_entities(j).all()
        atg = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[1]).with_entities(j).all()
        bhs = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[2]).with_entities(j).all()
        brb = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[3]).with_entities(j).all()
        blz = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[4]).with_entities(j).all()
        bmu = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[5]).with_entities(j).all()
        vgb = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[6]).with_entities(j).all()
        cym = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[7]).with_entities(j).all()
        dma = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[8]).with_entities(j).all()
        grd = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[9]).with_entities(j).all()
        guy = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[10]).with_entities(j).all()
        hti = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[11]).with_entities(j).all()
        jam = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[12]).with_entities(j).all()
        msr = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[13]).with_entities(j).all()
        kna = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[14]).with_entities(j).all()
        lca = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[15]).with_entities(j).all()
        vct = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[16]).with_entities(j).all()
        sur = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[17]).with_entities(j).all()
        tto = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[18]).with_entities(j).all()
        tca = indicators.query.order_by(indicators.year).filter_by(ctry=ctry_lst[19]).with_entities(j).all()
        
        # Unpack tuples in a list.
        
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
        
        # Creates a bokeh figure to add plots.
        p = figure(
            title=title[i],
            x_range = Range1d(x[0], x[-1]),
            x_axis_label='Year', 
            y_axis_label= unit[i],
            width=450, 
            height= 250
        )

        # Iterate over the y coordinates per country to plot figures.
        for index, k in enumerate(y):
            # 'p.line' plots a line graph. 
            # 'p.circle' plots a scatter plot.
            # Overlaying both creates a scatter plot with visible markers.
            # Colour scheme: https://mokole.com/palette.html

            # 'r1' and 'r2' are bokeh glyphs which contain the plot information.
            # 'visible' = False to initially hide all plots.
            r1 = p.line(x, k, color=col_all[index], line_width=2, name=lkup[col_all[index]][1])
            r2 = p.circle(x, k, color=col_all[index], size=5, name=lkup[col_all[index]][1])
            
            # Add glyphs to 'lst_glyph'.
            lst_glyph += [r1]
            lst_glyph += [r2]

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
            
            # Remove toolbar to export as PNG.
            p.sizing_mode = 'fixed'
            p.toolbar_location = None

            # Export figures as a PNG.
            export_png(p, filename='./app/static/images/use/indicators/' + tab_lab[i] +' - ' + lkup[col_all[index]][1] + '.png')

            # Bokeh hovertool.
            hover = HoverTool(
                tooltips=[ ("Country", "$name"), ("Year", "$x{(0)}"), (unit[i], "$y{(0)}") ]
            )

            # Add tools on the right of figure 'p'.
            if index == 0:
                p.add_tools(hover)
            p.toolbar_location = 'right'


            # Initially hide scatter plot.
            # Plots can be shown by selecting Legend properties.
            r1.visible = False
            r2.visible = False
            
            # Makes figure 'p' responsive.
            p.sizing_mode = 'stretch_width'
        
        # Convert figure 'p' to a Panel object and append to 'tabs' list.
        tabs.append(Panel( child=p, title=tab_lab[i].split(' ')[0] ))
        
    # Merge bokeh panels in the 'tabs' list to bokeh tabs group.
    tabs = Tabs(tabs=tabs)

    return tabs