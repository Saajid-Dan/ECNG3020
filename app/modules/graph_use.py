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
from bokeh.models import Range1d, FuncTickFormatter, HoverTool, Panel, Tabs, Legend, LegendItem, Column, Row
from bokeh.io import export_png
from math import pi
from app import db
from app.models import ICT_fix, ICT_mob, ICT_per, ICT_bw


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
    tabs_ind = indicators()             # ICT Indicators graphs.

    # Add graphs to a bokeh Column grid with responsive widths.
    column = Column(tabs_ind)
    column.sizing_mode = 'stretch_width'


    # ---------------------------- Merge Plot Legends ---------------------------- #

    # 'legend_items' = list comprehension that extract legend data from the glyphs in 'lst_glyph'.
    # Each glyph has graphs with plots that use unique colours.
    # Plots with a certain colour has their legend data merged together.
    # Selecting the legend will allow visibility toggled of plots on all figures.
    # Credit: https://stackoverflow.com/questions/56825350/how-to-add-one-legend-for-that-controlls-multiple-bokeh-figures
    
    # 'col_pres' = to store unique colours used in the graphs.
    # This presents unused colours from writing to the Legend.
    col_pres = []
    # Iterates through all glyphs.
    for j in lst_glyph:
        # 'col_lin' = gets plot colour.
        col_lin = j.glyph.line_color
        # Append plot colour if it is not in 'col_pres'.
        if col_lin not in col_pres:
            col_pres.append(col_lin)
    
    # Merges plot legends together.
    legend_items = [
        # 'LegendItem' = Bokeh legend tool.
        LegendItem(
            # 'label' = legend label. The look up table is used to assign a country as the label.
            label=lkup[color][0],
            # 'renderers' = bokeh glyphs.
            renderers=[
                # Assign a glyph to a legend label by the type of colour.
                renderer for renderer in lst_glyph if renderer.glyph.line_color==color
            ]
        ) 
        for color in col_pres
    ]
    # Sort labels in 'legend_items' in ascending order. 
    legend_items.sort(key=lambda x: x.label['value'], reverse=False)
    

    # --------------------------- Create Legend Figure --------------------------- #

    # Legends are not non-standalone objects and has to be in a figure.
    # Legends in plots can obscure the plot so a dummy figure is used.
    # Credit: https://stackoverflow.com/questions/56825350/how-to-add-one-legend-for-that-controlls-multiple-bokeh-figures

    # 'dummy1' and 'dummy2' are dummy figures and follow the same process:
    # 1. Create a dummy plot.
    # 2. Set the components of the figure invisible
    # 3. The glyphs referred by the legend need to be present in the figure that holds the legend, so we must add them to the figure renderers.
    # 4. Set the figure range outside of the range of all glyphs
    # 5. Add the legend to the dummy figure.

    # 'leg_h' = height for a 2 column legend.
    leg_h = int(25 * len(legend_items) / 2) + 30
    
    # Half Number of Legend Items.
    count = int(len(legend_items) / 2)

    dummy1 = figure(plot_height=leg_h, plot_width=82, outline_line_alpha=0,toolbar_location=None)
    for fig_component in [dummy1.grid[0],dummy1.ygrid[0],dummy1.xaxis[0],dummy1.yaxis[0]]:
        fig_component.visible = False
    dummy1.renderers += lst_glyph
    dummy1.x_range.end = -1000
    dummy1.x_range.start = -999
    dummy1.add_layout( Legend(click_policy='hide',location='top_left',border_line_alpha=0,items=legend_items[:count]) )

    dummy2 = figure(plot_height=leg_h, plot_width=82, outline_line_alpha=0,toolbar_location=None)
    for fig_component in [dummy2.grid[0],dummy2.ygrid[0],dummy2.xaxis[0],dummy2.yaxis[0]]:
        fig_component.visible = False
    dummy2.renderers += lst_glyph
    dummy2.x_range.end = -1000
    dummy2.x_range.start = -999
    dummy2.add_layout( Legend(click_policy='hide',location='top_left',border_line_alpha=0,items=legend_items[count:]) )

    row = Row(dummy1, dummy2)
    

    # -------------------------- Merge Legend and Graphs ------------------------- # 

    # Add the legend and 'tabs' to a Column grid.
    layout = Column(row, column)
    # layout = gridplot([[row], [col]], merge_tools=False)
    layout.sizing_mode = 'stretch_width'

    output_file('./app/static/html/graph_use.html')
    save(layout)


def indicators():
    '''
    Plots Bokeh figures for fixed and mobile broadband total subscriptions, percent of 
    ICT users in a country, and total bandwidth usage and add to a bokeh tabs group.
    '''
    global lst_glyph            # Global variable.
    
    # 'cat' = contains the four database tables.
    cat = [ICT_fix, ICT_mob, ICT_per, ICT_bw]

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

    # Loops over the four tables.
    # 'i' = iterator. 'j' = database table from 'cat'.
    for i, j in enumerate(cat):
        # Query the 'j' database table to retrieve data per table header and order it by the 'yrs' header.
        # The queries return a list of tuples.
        # 'year' = data from the 'yrs' header.
        # 'aia' to 'tca' = indicators data from Anguilla to Turks and Caicos Islands (ascending).
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
        
        # Creates a bokeh figure to add plots.
        p = figure(
            title=title[i],
            x_range = Range1d(x[0], x[-1]),
            x_axis_label='Year', 
            y_axis_label= unit[i],
            width=450, 
            height= 350
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