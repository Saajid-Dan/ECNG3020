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
from bokeh.models import Range1d, HoverTool, Panel, Tabs, Legend, LegendItem, Column, Row
from bokeh.io import export_png
from math import pi
from app import db
from app.models import GNI, PPP, USD


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
    tabs_gni = baskets(GNI, 'GNI pc', 'GNI per capita (%)')         # ICT Baskets graphs - GNI pc.
    tabs_ppp = baskets(PPP, 'PPP', 'Purchasing Power Parity')       # ICT Baskets graphs - PPP.
    tabs_usd = baskets(USD, 'USD', 'USD ($)')                       # ICT Baskets graphs - USD.

    # Add graphs to a bokeh Column grid with responsive widths.
    column = Column(tabs_gni, tabs_ppp, tabs_usd)
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

    output_file('./app/static/html/graph_adop.html')
    save(layout)


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
    # 'cat' contains 'GNI', 'PPP', and 'USD' database tables.
    hdrs = [cat.fix, cat.mob, cat.low, cat.high]

    # Iterate over header (hdr) in headers (hdr).
    for i, hdr in enumerate(hdrs):
        # yrs = Years extracted from the 'cat' table via query.
        # 'yrs' used as the x-axis coordinates.
        # These queries are returned as a list of tuples.
        yrs = db.session.query(cat.year).filter_by(ctry=ctry_lst[0]).all()
        x = [value for value, in yrs]
        
        # 'y' = stores a list of y-axis coordinates per country.
        y = []
        for ctry in ctry_lst:
            # Query header (hdr) in list headers (hdrs) for y-coordinates data per country in 'ctry_lst'. 
            # The query produces a list of tuples which must be unpacked into a list.
            data = db.session.query(hdr).filter_by(ctry=ctry).all()
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
            height= 200
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

            # Export figure 'p' as a PNG.
            export_png(p, filename='./app/static/images/adoption/baskets/' + title_[i] + ' - ' +  title +' - ' + ctry_lst[index] + '.png')

            # Bokeh hovertool.
            hover = HoverTool(
                tooltips=[ ("Country", "$name"), ("Date", "$x"), (unit[i], "$y{(0)}") ]
            )

            # Add tools on the right of figure 'p'.
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