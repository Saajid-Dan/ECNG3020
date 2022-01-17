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
from bokeh.models import ColumnDataSource, FactorRange, HoverTool, Panel, Tabs, Legend, LegendItem, Column, Row, MultiChoice, CustomJS, Button
from bokeh.events import ButtonClick
from bokeh.io import export_png
from math import pi
from app import db
from app.models import Mob_br, Fixed_br
import codecs


# ---------------------------------------------------------------------------- #
#                               Global Variables                               #
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
    '#7cd2c5': ['0', 'Anguilla'],
    '#713cc6': ['1', 'Antigua and Barbuda'],
    '#8cd847': ['2', 'Bahamas'],
    '#c849bd': ['3', 'Barbados'],
    '#71d487': ['4', 'Belize'],
    '#cd4574': ['5', 'Bermuda'],
    '#d6c244': ['6', 'British Virgin Islands'],
    '#6a70d0': ['7', 'Cayman Islands'],
    '#5e7e2f': ['8', 'Dominica'],
    '#4e2660': ['9', 'Grenada'],
    '#ceca96': ['10', 'Guyana'],
    '#d75033': ['11', 'Haiti'],
    '#8cb3d6': ['12', 'Jamaica'],
    '#ae7638': ['13', 'Montserrat'],
    '#c78ac5': ['14', 'Saint Kitts and Nevis'],
    '#527a60': ['15', 'Saint Lucia'],
    '#783333': ['16', 'Saint Vincent and the Grenadines'],
    '#586488': ['17', 'Suriname'],
    '#cd928f': ['18', 'Trinidad and Tobago'],
    '#39332a': ['19', 'Turks & Caicos Is.'],
}

# 'lst_glyph' = global variable that stores bokeh glyphs.
# Used to merge the legends from each glyph.
lst_glyph = []


lst = []


# ---------------------------------------------------------------------------- #
#                            Plot ICT Infrastructure Graphs                    #
# ---------------------------------------------------------------------------- #

def graph_infr():
    '''
    Adds a unified legend to all graphs.
    '''
    global lst_glyph            # Global variable.
    global lst


    # ---------------------------------- Graphs ---------------------------------- #

    # Graphs.
    tabs_mob = speed(Mob_br, 'Mobile Broadband')     # Mobile broadband speed index graphs.
    tabs_fix = speed(Fixed_br, 'Fixed Broadband')    # Fixed broadband speed index graphs.

    num = 2

    # Add graphs to a bokeh Column grid with responsive widths.
    column = Column(tabs_mob, tabs_fix)
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

    callback = CustomJS(args=dict(lst_glyph=lst_glyph, lst=lst, multi_choice=multi_choice, lkup=lkup), code="""
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

    output_file('./app/static/html/graph_infr.html')
    save(layout)

    graph = codecs.open('./app/static/html/graph_infr.html', 'r').read()
    graph = graph.replace('</title>', '</title>\n<style>html {overflow-y: scroll;} .bk { justify-content: end;}</style>')
    with open('./app/static/html/graph_infr.html', 'w') as f:
        f.write(graph)


def speed(cat, title):
    '''
    Plots Bokeh figures for download, upload, latency, and jitter vs date and add to a bokeh tabs group.
    '''
    global lst_glyph            # Global variable.
    global lst

    # 'mnth' is a dictionary that relates numerical month (key) to three letter abbreviated month (value).
    mnth = {'01':'Jan', '02':'Feb', '03':'Mar',
            '04':'Apr', '05':'May', '06':'Jun',
            '07':'Jul', '08':'Aug', '09':'Sep',
            '10':'Oct', '11':'Nov', '12':'Dec'
            }

    # Tab labels.
    tab_lab = [
        'Download', 'Upload', 'Latency', 'Jitter'
    ]

    # Graph units.
    unit = [
        'Download Speed (Mbps)',
        'Upload Speed (Mbps)',
        'Latency (ms)',
        'Jitter (ms)'
    ]

    # Stores a list of countries the the 'cat' database into 'ctry_lst'.
    ctry_lst = []
    ctry = cat.query.order_by(cat.ctry).with_entities(cat.ctry)
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
    # 'cat' contains 'Fixed_br' and 'Mob_br' database tables.
    hdrs = [cat.dls, cat.ups, cat.ltcy, cat.jitt]

    # Query dates in 'cat' and unpack resulting list of tuples.
    date = cat.query.filter_by(ctry=ctry_lst[0]).with_entities(cat.date).all()
    date = [value for value, in date]

    # Take dates (k) in 'date' and format YYYY-MM-DD into a tuple as (YYYY, MM DD).
    # Tuple is used for bokeh categorical axes labelling.
    # 'mnth' lookup table converts numerical month (MM) to 3-letter alphabetical abreviation.
    # Tuples appended to 'x' which stores the x-axis coordinates.
    x =[]
    for k in date:
        yr = k.split('-')[0]
        mm = mnth.get(k.split('-')[1])
        x.append((yr, mm + ' 1'))

    # Iterate over header (hdr) in headers (hdr).
    for i, hdr in enumerate(hdrs):

        # 'y' = stores a list of y-axis coordinates per country.
        y = []
        for ctry in ctry_lst:
            # Query header (hdr) in list headers (hdrs) for y-coordinates data per country in 'ctry_lst'. 
            # The query produces a list of tuples which must be unpacked into a list.
            data = cat.query.filter_by(ctry=ctry).with_entities(hdr)
            data = [value for value, in data]
            y.append(data)
            
        # Creates a bokeh figure to add plots.
        p = figure(
            title = title + ' - ' + tab_lab[i],
            x_range = FactorRange(*x), 
            x_axis_label ='Date', 
            y_axis_label = unit[i],
            width = 450, 
            height = 250
        )
        
        # Orient x-axis labels by 90 degrees.
        p.xaxis.major_label_orientation = pi/2

        # Iterate over the y coordinates per country to plot figures.
        for index, k in enumerate(y):
            # Plot scatter plot.
            # 'r1' = bokeh line plot glyph with the plot information.
            # 'r2' = bokeh circle plot glyph with the plot information.
            r1 = p.line(x=x, y=k, line_width=2, color=col[index], name=ctry_lst[index])
            r2 = p.circle(x, k, color=col[index], size=5, name=ctry_lst[index])

            # print(r1.name)

            # Add glyphs to 'lst_glyph'.
            lst_glyph += [r1]
            lst_glyph += [r2]

            lst += [ctry_lst[index]]
            lst += [ctry_lst[index]]

            # Remove toolbar to export as PNG.
            p.sizing_mode = 'fixed'
            p.toolbar_location = None

            # Export figure 'p' as a PNG.
            export_png(p, filename='./app/static/images/infrastructure/speed/' + title + ' - ' + tab_lab[i] +' - ' + ctry_lst[index] + '.png')

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